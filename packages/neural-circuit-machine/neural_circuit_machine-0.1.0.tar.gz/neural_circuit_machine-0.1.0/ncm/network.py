# torch implementation of Neobert
from tuneapi import tu
from typing import List, Dict, Optional, Literal

import torch
import torch.nn as nn
import torch.optim as optim

from dataclasses import dataclass, field


@dataclass
class ModelArgs:
    model_type: str
    hidden_size: int = 768
    num_hidden_layers: int = 28
    num_attention_heads: int = 12
    intermediate_size: int = 3072
    dropout: float = 0
    embedding_init_range: float = 0.02
    decoder_init_range: float = 0.02
    rms_norm: bool = True
    rope: bool = True
    rope_theta: float = 10000.0
    norm_eps: float = 1e-06
    hidden_act: str = "SwiGLU"
    vocab_size: int = 32064
    pad_token_id: int = 0
    max_length: int = 1024
    ngpt: bool = False
    architectures: List[str] = field(default_factory=lambda: ["NeoBERTLMHead"])

    # pipeline args, mostly for classification
    classifier_pooling: Literal["cls", "mean"] = "mean"
    is_regression: Optional[bool] = None  # for Sequence Classification
    label2id: Optional[Dict[str, int]] = None  # for Sequence Classification
    id2label: Optional[Dict[int, str]] = None  # for Sequence Classification
    classifier_dropout: float = 0.1
    classifier_init_range: float = 0.02

    @property
    def dim_head(self) -> int:
        """Dimension of each attention head."""
        if self.hidden_size % self.num_attention_heads != 0:
            raise ValueError(
                f"hidden_size ({self.hidden_size}) must be divisible by num_attention_heads ({self.num_attention_heads})"
            )
        return self.hidden_size // self.num_attention_heads

    @property
    def num_labels(self) -> int:  # for Sequence Classification
        """
        Number of labels is determined by:
        - For zero-shot classification: length of label_candidates
        - For regression or binary with sigmoid: 1
        - For classification: length of id2label mapping
        """

        if self.is_regression:
            return 1

        if self.pipeline_config and self.pipeline_config.get("binary_sigmoid", False):
            return 1

        if self.id2label is None:
            raise ValueError(
                "id2label mapping must be provided for categorical classification. "
                "For regression or binary classification with sigmoid output, "
                "set is_regression=True or binary_sigmoid=True in pipeline_config."
            )

        return len(self.id2label)


@dataclass
class ModelOutput:
    last_hidden_state: torch.Tensor
    text_embeds: torch.Tensor
    pooler_output: torch.Tensor


# Can't use nn.RoPE here bacause of the shape of freqs_cis so we implement it manually
def precompute_freqs_cis(dim: int, end: int, theta: float) -> torch.Tensor:
    freqs = 1.0 / (theta ** (torch.arange(0, dim, 2, dtype=torch.float32) / dim))
    t = torch.arange(end, dtype=torch.float32)
    freqs = torch.outer(t, freqs)

    freqs_cos = torch.cos(freqs)
    freqs_sin = torch.sin(freqs)
    return (freqs_cos, freqs_sin)


def apply_rotary_emb(
    x: torch.Tensor,
    freqs: tuple[torch.Tensor, torch.Tensor],
) -> torch.Tensor:

    freqs_cos, freqs_sin = freqs

    x_r = x.reshape(*x.shape[:-1], -1, 2)

    # Split into the two parts for rotation
    x1 = x_r[..., 0]
    x2 = x_r[..., 1]

    # freqs have shape (L, D_h/2)
    freqs_cos = freqs_cos.reshape(1, *freqs_cos.shape)
    freqs_cos = freqs_cos.reshape(1, freqs_cos.shape[1], 1, freqs_cos.shape[2])
    freqs_sin = freqs_sin.reshape(1, *freqs_sin.shape)
    freqs_sin = freqs_sin.reshape(1, freqs_sin.shape[1], 1, freqs_sin.shape[2])

    # Perform the rotation
    x_out1 = x1 * freqs_cos - x2 * freqs_sin
    x_out2 = x1 * freqs_sin + x2 * freqs_cos

    # Re-assemble the rotated tensor
    x_rotated = torch.stack([x_out1, x_out2], dim=-1)

    # Flatten the last two dimensions to restore the original shape
    return x_rotated.reshape(*x.shape)


# ====== Layers


class SwiGLU(nn.Module):
    """TBC when model weights are available"""

    def __init__(
        self,
        input_dim: int,
        hidden_dim: int,
        output_dim: int,
        bias: bool = False,
    ):
        super().__init__()
        # The first linear layer projects from the input dimension to twice the hidden
        # dimension to create both the gate and the up-projection in one pass.
        self.w12 = nn.Linear(input_dim, 2 * hidden_dim, bias=bias)
        self.w3 = nn.Linear(hidden_dim, output_dim, bias=bias)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        gate_up: torch.Tensor = self.w12(x)

        # Split the tensor into two halves along the last dimension
        gate, up = gate_up.chunk(2, dim=-1)
        fused_output = nn.functional.silu(gate) * up

        return self.w3(fused_output)


class EncoderBlock(nn.Module):
    def __init__(self, config: ModelArgs):
        super().__init__()

        self.config = config

        # Attention
        self.qkv = nn.Linear(config.hidden_size, config.hidden_size * 3, bias=False)
        self.wo = nn.Linear(config.hidden_size, config.hidden_size, bias=False)
        self.resid_dropout = nn.Dropout(p=config.dropout)

        # Feedforward network
        # To keep the number of parameters and the amount of computation constant, we reduce the number of
        # hidden units by a factor of 2/3 (https://arxiv.org/pdf/2002.05202.pdf) and make it a multiple of 8 to
        # avoid RuntimeError due to misaligned operand
        multiple_of = 8
        intermediate_size = int(2 * config.intermediate_size / 3)
        intermediate_size = multiple_of * (
            (intermediate_size + multiple_of - 1) // multiple_of
        )
        self.ffn = SwiGLU(
            config.hidden_size,
            intermediate_size,
            config.hidden_size,
            bias=False,
        )
        self.attention_norm = nn.RMSNorm(config.hidden_size, config.norm_eps)
        self.ffn_norm = nn.RMSNorm(config.hidden_size, config.norm_eps)
        self.ffn_dropout = nn.Dropout(config.dropout)

    def forward(
        self,
        hidden_states: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        freqs: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        hidden_states = (
            hidden_states
            + self._att_block(
                self.attention_norm(hidden_states), attention_mask, freqs=freqs
            )[0]
        )
        hidden_states = hidden_states + self._ff_block(self.ffn_norm(hidden_states))[0]
        return (hidden_states,)

    def _att_block(
        self,
        hidden_states: torch.Tensor,
        attention_mask: Optional[torch.Tensor] = None,
        freqs: Optional[torch.Tensor] = None,
    ) -> torch.Tensor:
        B, L, _ = hidden_states.shape

        qkv_x = self.qkv(hidden_states)  # (B, L, 3 * num_attention_heads * dim_head)
        qkv_x = torch.reshape(
            qkv_x, (B, L, self.config.num_attention_heads, self.config.dim_head * 3)
        )  # (B, L, num_attention_heads, dim_head * 3)
        # qkv_x = mx.transpose(qkv_x, (0, 2, 1, 3))  # (B, num_attention_heads, L, dim_head * 3)
        # TODO : check transpose above (different from original repo but may be due to how rope is implemented in mlx)
        # Split QKV along the last dimension into 3 equal parts of size dim_head
        queries, keys, values = qkv_x.chunk(
            3, dim=-1
        )  # (B, L, num_attention_heads, dim_head)

        # Applying rotary embeddings
        # queries = self.rotary_emb(queries)
        # keys = self.rotary_emb(keys)
        if self.config.rope and freqs is not None:
            queries = apply_rotary_emb(queries, freqs)
            keys = apply_rotary_emb(keys, freqs)

        # transpose to attention after RoPE
        # Permute to (B, num_attention_heads, L, dim_head) for attention
        queries = queries.permute(0, 2, 1, 3)
        keys = keys.permute(0, 2, 1, 3)
        values = values.permute(0, 2, 1, 3)

        output = torch.nn.functional.scaled_dot_product_attention(
            queries,
            keys,
            values,
            attn_mask=attention_mask,
            # dropout_p=self.config.dropout_prob if self.training else 0.0,
        )

        output = output.permute(0, 2, 1, 3).reshape(B, L, -1)

        hidden_states = self.wo(output)
        hidden_states = self.resid_dropout(hidden_states)

        return (hidden_states,)

    def _ff_block(self, hidden_states: torch.Tensor) -> torch.Tensor:
        hidden_states = self.ffn(hidden_states)
        hidden_states = self.ffn_dropout(hidden_states)
        return (hidden_states,)


class NeoBERTModel(nn.Module):
    def __init__(self, config: ModelArgs):
        super().__init__()
        self.config = config

        self.vocab_size = config.vocab_size
        self.num_hidden_layers = config.num_hidden_layers
        assert self.vocab_size > 0
        self.encoder = nn.Embedding(config.vocab_size, config.hidden_size)

        if self.config.rope:
            self.freqs = precompute_freqs_cis(
                config.dim_head, config.max_length, config.rope_theta
            )

        self.transformer_encoder = [
            EncoderBlock(config=config) for _ in range(config.num_hidden_layers)
        ]
        self.layer_norm = (
            nn.RMSNorm(config.hidden_size, eps=config.norm_eps)
            if config.rms_norm
            else nn.LayerNorm(config.hidden_size, config.norm_eps)
        )

    def _update_attention_mask(self, attention_mask: Optional[torch.Tensor] = None):
        """
        Creates a causal mask and combines it with the padding mask.
        """
        dtype = attention_mask.to(torch.float32)
        B, L = attention_mask.shape

        # Reshape padding mask from (B, L) to (B, 1, 1, L) to be broadcastable
        padding_mask = attention_mask[:, None, None, :]
        additive_padding_mask = torch.where(padding_mask == 1, 0.0, -1e9).to(dtype)

        return additive_padding_mask

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor = None,
        position_ids: Optional[torch.Tensor] = None,
    ):
        attention_mask = self._update_attention_mask(
            attention_mask,
        )

        hidden_states = self.encoder(input_ids)

        freqs = (
            self.freqs[0][: input_ids.shape[1]] if self.config.rope else None,
            self.freqs[1][: input_ids.shape[1]] if self.config.rope else None,
        )

        for layer in self.transformer_encoder:
            layer_outputs = layer(hidden_states, attention_mask, freqs=freqs)
            hidden_states = layer_outputs[0]

        hidden_states = self.layer_norm(hidden_states)

        return {
            "last_hidden_state": hidden_states,
        }


class Model(nn.Module):
    def __init__(self, config: ModelArgs):
        super().__init__()
        self.config = config
        self.model_type = config.model_type
        self.model = NeoBERTModel(config)

        if config.architectures == ["NeoBERTLMHead"]:
            self.decoder = nn.Linear(config.hidden_size, config.vocab_size)

        elif config.architectures == ["NeoBERTForSequenceClassification"]:
            self.num_labels = config.num_labels
            self.is_regression = config.is_regression
            self.dense = nn.Linear(self.config.hidden_size, self.config.hidden_size)
            self.dropout = nn.Dropout(p=config.classifier_dropout)
            self.classifier = nn.Linear(config.hidden_size, config.num_labels)

    def _process_outputs(self, logits: torch.Tensor) -> torch.Tensor:
        """Apply the appropriate activation function to the logits for classification tasks."""
        if self.is_regression:
            return logits  # No activation for regression
        elif self.num_labels == 1:
            return torch.sigmoid(logits)  # Binary classification
        else:
            # Using softmax for multi-class classification
            return torch.softmax(logits, dim=-1)

    def forward(
        self,
        input_ids: torch.Tensor,
        attention_mask: torch.Tensor = None,
        position_ids: Optional[torch.Tensor] = None,
        return_dict: Optional[bool] = False,
    ) -> ModelOutput:

        if attention_mask is None:
            batch_size, seq_len = input_ids.shape
            attention_mask = torch.ones(
                (batch_size, seq_len),
                dtype=self.model.encoder.weight.dtype,
            )

        out = self.model(input_ids, attention_mask, position_ids=position_ids)

        last_hidden_state = (
            out["last_hidden_state"] if isinstance(out, dict) else out[0]
        )

        # Pooling strategy using config
        if self.config.classifier_pooling == "cls":
            pooled_embeddings = last_hidden_state[:, 0]
        else:
            # Fallback to last token pooling
            pooled_embeddings = torch.mean(last_hidden_state, dim=1)

        text_embeds = torch.nn.functional.normalize(pooled_embeddings, dim=-1)

        pooled_output = None
        # placeholder for masked LM and sequence classification heads
        if self.config.architectures == ["NeoBERTLMHead"]:
            pooled_output = self.decoder(last_hidden_state)
        elif self.config.architectures == ["NeoBERTForSequenceClassification"]:
            pooled_output = self.dropout(pooled_embeddings)
            pooled_output = self.dense(pooled_output)
            pooled_output = nn.tanh(pooled_output)
            pooled_output = self.dropout(pooled_output)
            pooled_output = self.classifier(pooled_output)
            pooled_output = self._process_outputs(pooled_output)

        return ModelOutput(
            last_hidden_state=last_hidden_state,
            text_embeds=text_embeds,
            pooler_output=pooled_output,
        )


if __name__ == "__main__":
    config = ModelArgs(
        model_type="neobert_ndc",
        hidden_size=16,
        num_hidden_layers=8,
        num_attention_heads=4,
        intermediate_size=1024,
        vocab_size=32,
    )
    print(f"config:\n{config}")
    model = Model(config)
    print(f"Total parameters: {sum(p.numel() for p in model.parameters())}")

    input = torch.randint(0, 10, (1, 10))
    print(f"input:\n{input}")
    attention_mask = torch.ones((1, 10))
    attention_mask[0, 8:] = 0
    print(f"attention_mask:\n{attention_mask}")
    # print(f"attention_mask:\n{attention_mask.T @ attention_mask}")
    position_ids = torch.arange(10)
    print(f"position_ids:\n{position_ids}")
    output = model(input, attention_mask, position_ids)
    print(f"last_hidden_state:\n{output.last_hidden_state.shape}")
    print(f"text_embeds:\n{output.text_embeds.shape}")
    print(f"pooler_output:\n{output.pooler_output.shape}")
