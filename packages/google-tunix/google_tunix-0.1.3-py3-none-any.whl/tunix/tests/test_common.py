# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Common test utilities."""

from typing import List, Tuple, Any
from collections.abc import Iterable
import dataclasses

from flax import config as flax_config
from flax import nnx
import jax
import jax.numpy as jnp
import numpy as np
import qwix

import sentencepiece as spm
import huggingface_hub
import os
import shutil
import gc

if hasattr(flax_config, 'flax_always_shard_variable'):
  flax_config.update('flax_always_shard_variable', False)


def assert_equal(path, x, y):
  np.testing.assert_array_equal(x, y, err_msg=f'Mismatch at path: {path}')


def assert_not_equal(path, x, y):
  np.testing.assert_(
      np.any(np.not_equal(x, y)), msg=f'Unexpected match at path: {path}'
  )


def assert_close(path, x, y, atol=1e-5, rtol=1e-5):
  np.testing.assert_allclose(
      x, y, atol, rtol, err_msg=f'Mismatch at path: {path}'
  )


class Decoder(nnx.Module):
  """Toy decoder for testing."""

  def __init__(self, rngs: nnx.Rngs):
    self.attn = nnx.MultiHeadAttention(
        num_heads=4,
        in_features=16,
        qkv_features=16,
        use_bias=False,
        decode=False,
        rngs=rngs,
    )
    kernel_init_fn = nnx.initializers.lecun_normal()
    self.w1 = nnx.Linear(
        in_features=16,
        out_features=32,
        rngs=rngs,
        kernel_init=nnx.with_partitioning(kernel_init_fn, ('fsdp', 'tp')),
    )
    self.w2 = nnx.Linear(
        in_features=32,
        out_features=16,
        rngs=rngs,
        kernel_init=nnx.with_partitioning(kernel_init_fn, ('tp', 'fsdp')),
    )

  def __call__(self, x):
    x = self.attn(x) + x
    h = nnx.relu(self.w1(x))
    h = self.w2(h) + x
    return h


@dataclasses.dataclass(kw_only=True, frozen=True)
class ModelConfig:
  """Model config for testing."""

  num_layers: int
  num_kv_heads: int
  head_dim: int


class ToyTransformer(nnx.Module, pytree=False):
  """Toy transformer for testing."""

  def __init__(
      self,
      rngs: nnx.Rngs,
      vocab_size: int = 256,
      num_layers: int = 4,
  ):
    self.config = ModelConfig(
        num_layers=num_layers, num_kv_heads=4, head_dim=16
    )
    self.emb = nnx.Embed(vocab_size, 16, rngs=rngs)
    self.layers = [Decoder(rngs=rngs) for _ in range(num_layers)]
    self.lm_head = nnx.Linear(
        in_features=16, out_features=vocab_size, rngs=rngs
    )

    self.head_dim = 16

  def __call__(
      self, x, positions, cache, attention_mask, output_hidden_states=False
  ):
    x = self.emb(x)
    for layer in self.layers:
      x = layer(x)
    if output_hidden_states:
      self.sow(
          nnx.Intermediate,
          'all_hidden_states',
          x,
      )
    return self.lm_head(x), cache

  @property
  def num_embed(self) -> int:
    return self.emb.num_embeddings


def get_dummy_inputs_for_lora_toy_transformer_tests():
  return {
      'x': jnp.ones((1, 1), dtype=jnp.int32),
      'positions': jnp.ones((1, 1), dtype=jnp.int32),
      'cache': None,
      'attention_mask': jnp.ones((1, 1, 1), dtype=jnp.bool),
  }


def get_lora_model(
    model: nnx.Module,
    module_path: str = '.*w1|.*w2',
    mesh: jax.sharding.Mesh | None = None,
    rank: int = 4,
    alpha: float = 2.0,
) -> nnx.Module:
  """Apply LoRA to ToyTransformer."""
  lora_provider = qwix.LoraProvider(
      module_path=module_path,
      rank=rank,
      alpha=alpha,
  )
  dummy_model_input = get_dummy_inputs_for_lora_toy_transformer_tests()
  lora_model = qwix.apply_lora_to_model(
      model, lora_provider, **dummy_model_input
  )
  if mesh is not None:
    with mesh:
      state = nnx.state(lora_model)
      pspecs = nnx.get_partition_spec(state)
      sharded_state = jax.lax.with_sharding_constraint(state, pspecs)
      nnx.update(lora_model, sharded_state)
  return lora_model


class MockVocab(spm.SentencePieceProcessor):
  """Mock vocabulary for testing."""

  def __init__(self):
    super().__init__()
    self._start_id = 3
    self._mapping_text_to_id = {
        '<pad>': 0,
        '<s>': 1,
        '</s>': 2,
        'input': 3,
        'string': 4,
        'hello': 5,
        'world': 6,
        'Hello': 7,
        'there': 8,
        '!': 9,
        'My': 10,
        'name': 11,
        'is': 12,
        'Morgane': 13,
        'Tunix': 14,
        'Parallax': 15,
        'PT': 16,
        'library': 17,
        'distributed': 18,
        'training': 19,
        'optimizer': 20,
        'quantization': 21,
    }
    self._vocab_size = len(self._mapping_text_to_id)

  def pad_id(self) -> int:
    return 0

  def bos_id(self) -> int:
    return 1

  def eos_id(self) -> int:
    return 2

  def GetPieceSize(self) -> int:  # pylint: disable=invalid-name
    return self._vocab_size

  def DecodeIds(self, ids: Iterable[int]) -> str:  # pylint: disable=invalid-name
    reverse_mapping = {v: k for k, v in self._mapping_text_to_id.items()}
    return ' '.join(reverse_mapping[e] for e in ids)

  def EncodeAsIds(self, text: str) -> list[int]:  # pylint: disable=invalid-name
    words = text.split(' ')
    return [self._mapping_text_to_id[word] for word in words]


class MockTransformerWithScoreHead(nnx.Module):
  """Gemma transformer with a score head."""

  def __init__(self, transformer: nnx.Module, rngs: nnx.Rngs):
    """Initializes the transformer with a score head.

    Args:
      transformer: The transformer backbone.
      rngs: The random number generator.
    """

    self.transformer = transformer
    self.score = nnx.Linear(
        in_features=transformer.head_dim,
        out_features=1,
        use_bias=False,
        rngs=rngs,
    )

  def __call__(self, *args, **kwargs):
    self.transformer(*args, **kwargs, output_hidden_states=True)
    hidden_states = nnx.pop(self.transformer, nnx.Intermediate)[
        'all_hidden_states'
    ].value[-1]
    score = self.score(hidden_states)
    return score


def download_from_huggingface(repo_id: str, model_path: str):
  """Download checkpoint files from huggingface."""
  print('Make sure you logged in to the huggingface cli.')
  all_files = huggingface_hub.list_repo_files(repo_id)
  filtered_files = [f for f in all_files if not f.startswith('original/')]

  for filename in filtered_files:
    huggingface_hub.hf_hub_download(
        repo_id=repo_id, filename=filename, local_dir=model_path
    )
  print(f'Downloaded {filtered_files} to: {model_path}')


def batch_templatize(prompts: List[str], tokenizer: Any):
  """Use tokenizer to batch templatize the prompts."""
  assert hasattr(tokenizer, 'apply_chat_template')
  out = []
  for p in prompts:
    out.append(
        tokenizer.apply_chat_template(
            [
                {'role': 'user', 'content': p},
            ],
            tokenize=False,
            add_generation_prompt=True,
        )
    )
  return out


def validate_llm_outputs(
    expected_output_pattern: List[Tuple[str, List[str]]],
    serving_outputs: List[str],
):
  for (prompt, expectations), generated in zip(
      expected_output_pattern, serving_outputs
  ):
    normalized = generated.strip().lower()
    for keyword in expectations:
      assert keyword.lower() in normalized, (
          f"Response '{generated}' for prompt '{prompt}' does not contain "
          f"expected keyword '{keyword}'."
      )


def delete_directory(path: str):
  """Safely delete directory from filesystem."""
  if os.path.exists(path):
    if os.path.isdir(path):
      shutil.rmtree(path)
      print(f'Deleted directory: {path}')
    else:
      print(f'Path exists but is not a directory: {path}')
  else:
    print(f'Directory does not exist: {path}')


def clear_jax_arrays():
  """Clear all the Jax arrays from hbm."""
  for name, obj in list(globals().items()):
    if isinstance(obj, jnp.ndarray):
      del globals()[name]
  gc.collect()
