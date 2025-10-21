"""Mappings for converting Llama3 weights to the vLLM JAX backend."""

from __future__ import annotations

import os
from typing import Any, Dict, Tuple

Sharding = Tuple[str | None, ...]
MappingEntry = Tuple[str, Sharding]


def _to_hf_mappings() -> Dict[str, MappingEntry]:
  """The parameter key mapping between Tunix vanilla model and vLLM Jax backend"""
  if os.environ.get('NEW_MODEL_DESIGN') == 'True':
    return {
        'lm_head.w': ('lm_head.input_embedding_table_DV', (None, 'model')),
        'embedder.input_embedding': (
            'embedder.input_embedding_table_VD',
            ('model', None),
        ),
        'layers.*.input_layernorm.w': (
            'layers.*.pre_attention_norm.scale',
            (None,),
        ),
        'layers.*.mlp.down_proj.kernel': (
            'layers.*.mlp.kernel_down_proj_FD',
            ('model', None),
        ),
        'layers.*.mlp.gate_proj.kernel': (
            'layers.*.mlp.kernel_gating_DF',
            (None, 'model'),
        ),
        'layers.*.mlp.up_proj.kernel': (
            'layers.*.mlp.kernel_up_proj_DF',
            (None, 'model'),
        ),
        'layers.*.post_attention_layernorm.w': (
            'layers.*.pre_mlp_norm.scale',
            (None,),
        ),
        'layers.*.attn.k_proj.w': (
            'layers.*.attn.kernel_k_proj_DKH',
            (None, 'model', None),
        ),
        'layers.*.attn.o_proj.w': (
            'layers.*.attn.kernel_o_proj_NHD',
            ('model', None, None),
        ),
        'layers.*.attn.q_proj.w': (
            'layers.*.attn.kernel_q_proj_DNH',
            (None, 'model', None),
        ),
        'layers.*.attn.v_proj.w': (
            'layers.*.attn.kernel_v_proj_DKH',
            (None, 'model', None),
        ),
        'final_norm.w': ('final_norm.scale', (None,)),
    }

  return {
      'lm_head.w': ('model.lm_head', (None, 'model')),
      'embedder.input_embedding': (
          'model.embed.embedding',
          ('model', None),
      ),
      'layers.*.input_layernorm.w': (
          'model.layers.*.input_layernorm.scale',
          (None,),
      ),
      'layers.*.mlp.down_proj.kernel': (
          'model.layers.*.mlp.down_proj.kernel',
          ('model', None),
      ),
      'layers.*.mlp.gate_proj.kernel': (
          'model.layers.*.mlp.gate_proj.kernel',
          (None, 'model'),
      ),
      'layers.*.mlp.up_proj.kernel': (
          'model.layers.*.mlp.up_proj.kernel',
          (None, 'model'),
      ),
      'layers.*.post_attention_layernorm.w': (
          'model.layers.*.post_attention_layernorm.scale',
          (None,),
      ),
      'layers.*.attn.k_proj.w': (
          'model.layers.*.self_attn.k_proj.kernel',
          (None, 'model', None),
      ),
      'layers.*.attn.o_proj.w': (
          'model.layers.*.self_attn.o_proj.kernel',
          ('model', None, None),
      ),
      'layers.*.attn.q_proj.w': (
          'model.layers.*.self_attn.q_proj.kernel',
          (None, 'model', None),
      ),
      'layers.*.attn.v_proj.w': (
          'model.layers.*.self_attn.v_proj.kernel',
          (None, 'model', None),
      ),
      'final_norm.w': ('model.norm.scale', (None,)),
  }


def _lora_to_hf_mappings() -> Dict[str, MappingEntry] | None:
  """The lora parameter key mapping between Tunix vanilla model and vLLM Jax backend"""
  if os.environ.get('NEW_MODEL_DESIGN') == 'True':
    return {
        'layers.*.mlp.gate_proj.kernel_lora_a': (
            'layers.*.mlp.kernel_gating_DF_lora_a',
            (None, None),
        ),
        'layers.*.mlp.gate_proj.kernel_lora_b': (
            'layers.*.mlp.kernel_gating_DF_lora_b',
            (None, 'model'),
        ),
        'layers.*.mlp.up_proj.kernel_lora_a': (
            'layers.*.mlp.kernel_up_proj_DF_lora_a',
            (None, None),
        ),
        'layers.*.mlp.up_proj.kernel_lora_b': (
            'layers.*.mlp.kernel_up_proj_DF_lora_b',
            (None, 'model'),
        ),
        'layers.*.mlp.down_proj.kernel_lora_a': (
            'layers.*.mlp.kernel_down_proj_FD_lora_a',
            ('model', None),
        ),
        'layers.*.mlp.down_proj.kernel_lora_b': (
            'layers.*.mlp.kernel_down_proj_FD_lora_b',
            (None, None),
        ),
        'layers.*.attn.q_proj.w_lora_a': (
            'layers.*.attn.kernel_q_proj_DNH_lora_a',
            ('model', None),
        ),
        'layers.*.attn.q_proj.w_lora_b': (
            'layers.*.attn.kernel_q_proj_DNH_lora_b',
            (None, None),
        ),
        'layers.*.attn.k_proj.w_lora_a': (
            'layers.*.attn.kernel_k_proj_DKH_lora_a',
            ('model', None),
        ),
        'layers.*.attn.k_proj.w_lora_b': (
            'layers.*.attn.kernel_k_proj_DKH_lora_b',
            (None, None),
        ),
        'layers.*.attn.v_proj.w_lora_a': (
            'layers.*.attn.kernel_v_proj_DKH_lora_a',
            ('model', None),
        ),
        'layers.*.attn.v_proj.w_lora_b': (
            'layers.*.attn.kernel_k_proj_DKH_lora_b',
            (None, None),
        ),
        'layers.*.attn.o_proj.w_lora_a': (
            'layers.*.attn.kernel_o_proj_NHD_lora_a',
            ('model', None),
        ),
        'layers.*.attn.o_proj.w_lora_b': (
            'layers.*.attn.kernel_o_proj_NHD_lora_b',
            (None, None),
        ),
    }

  return {
      'layers.*.mlp.gate_proj.kernel_lora_a': (
          'model.layers.*.mlp.gate_proj.kernel_lora_a',
          (None, None),
      ),
      'layers.*.mlp.gate_proj.kernel_lora_b': (
          'model.layers.*.mlp.gate_proj.kernel_lora_b',
          (None, 'model'),
      ),
      'layers.*.mlp.up_proj.kernel_lora_a': (
          'model.layers.*.mlp.up_proj.kernel_lora_a',
          (None, None),
      ),
      'layers.*.mlp.up_proj.kernel_lora_b': (
          'model.layers.*.mlp.up_proj.kernel_lora_b',
          (None, 'model'),
      ),
      'layers.*.mlp.down_proj.kernel_lora_a': (
          'model.layers.*.mlp.down_proj.kernel_lora_a',
          ('model', None),
      ),
      'layers.*.mlp.down_proj.kernel_lora_b': (
          'model.layers.*.mlp.down_proj.kernel_lora_b',
          (None, None),
      ),
      'layers.*.attn.q_proj.w_lora_a': (
          'model.layers.*.self_attn.q_proj.kernel_lora_a',
          ('model', None),
      ),
      'layers.*.attn.q_proj.w_lora_b': (
          'model.layers.*.self_attn.q_proj.kernel_lora_b',
          (None, None),
      ),
      'layers.*.attn.k_proj.w_lora_a': (
          'model.layers.*.self_attn.k_proj.kernel_lora_a',
          ('model', None),
      ),
      'layers.*.attn.k_proj.w_lora_b': (
          'model.layers.*.self_attn.k_proj.kernel_lora_b',
          (None, None),
      ),
      'layers.*.attn.v_proj.w_lora_a': (
          'model.layers.*.self_attn.v_proj.kernel_lora_a',
          ('model', None),
      ),
      'layers.*.attn.v_proj.w_lora_b': (
          'model.layers.*.self_attn.v_proj.kernel_lora_b',
          (None, None),
      ),
      'layers.*.attn.o_proj.w_lora_a': (
          'model.layers.*.self_attn.o_proj.kernel_lora_a',
          ('model', None),
      ),
      'layers.*.attn.o_proj.w_lora_b': (
          'model.layers.*.self_attn.o_proj.kernel_lora_b',
          (None, None),
      ),
  }


def _to_hf_transpose_keys() -> Dict[str, Tuple[int, int]] | None:
  """The parameter key transposition mapping between Tunix vanilla model and vLLM Jax backend"""
  return {
      'embedding': (1, 0),
  }


def _to_hf_hook_fns() -> Dict[str, Any] | None:
  """Additional parameter manipulation hook between Tunix vanilla model and vLLM Jax backend"""
  return None


VLLM_JAX_MAPPING: Dict[str, Any] = {
    'to_hf_mappings': _to_hf_mappings(),
    'lora_to_hf_mappings': _lora_to_hf_mappings(),
    'to_hf_transpose_keys': _to_hf_transpose_keys(),
    'to_hf_hook_fns': _to_hf_hook_fns(),
}

__all__ = [
    'VLLM_JAX_MAPPING',
]
