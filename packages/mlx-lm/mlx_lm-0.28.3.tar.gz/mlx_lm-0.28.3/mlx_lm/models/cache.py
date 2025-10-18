# Copyright © 2023-2024 Apple Inc.

import copy
from typing import Any, Dict, List, Optional

import mlx.core as mx
import mlx.nn as nn
from mlx.utils import tree_flatten, tree_map, tree_unflatten

from .base import create_causal_mask


def make_prompt_cache(
    model: nn.Module,
    max_kv_size: Optional[int] = None,
) -> List[Any]:
    """
    Construct the model's cache for use in generation.

    This function will defer the cache construction to the model if it has a
    ``make_cache`` method, otherwise it will make a default KV cache.

    Args:
        model (nn.Module): The language model.
        max_kv_size (Optional[int]): If provided and the model does not have a
            ``make_cache`` method, a ``RotatingKVCache`` is used with a maximum
            size of ``max_kv_size``
    """
    if hasattr(model, "make_cache"):
        return model.make_cache()

    num_layers = len(model.layers)
    if max_kv_size is not None:
        return [
            RotatingKVCache(max_size=max_kv_size, keep=4) for _ in range(num_layers)
        ]
    else:
        return [KVCache() for _ in range(num_layers)]


def save_prompt_cache(file_name: str, cache: List[Any], metadata: Dict[str, str] = {}):
    """
    Save a pre-computed prompt cache to a file.

    Args:
        file_name (str): The ``.safetensors`` file name.
        cache (List[Any]): The model state.
        metadata (Dict[str, str]): Optional metadata to save along with model
            state.
    """
    cache_data = [c.state for c in cache]
    cache_info = [c.meta_state for c in cache]
    cache_data = dict(tree_flatten(cache_data))
    cache_classes = [type(c).__name__ for c in cache]
    cache_metadata = [cache_info, metadata, cache_classes]
    cache_metadata = dict(tree_flatten(cache_metadata))
    mx.save_safetensors(file_name, cache_data, cache_metadata)


def load_prompt_cache(file_name, return_metadata=False):
    """
    Load a prompt cache from a file.

    Args:
        file_name (str): The ``.safetensors`` file name.
        return_metadata (bool): Whether or not to return metadata.
            Default: ``False``.

    Returns:
        List[Any] or Tuple[List[Any], Dict[str, str]]: The prompt cache and
            the metadata if requested.
    """
    arrays, cache_metadata = mx.load(file_name, return_metadata=True)
    arrays = tree_unflatten(list(arrays.items()))
    cache_metadata = tree_unflatten(list(cache_metadata.items()))
    info, metadata, classes = cache_metadata
    cache = [
        globals()[c].from_state(state, meta_state)
        for c, state, meta_state in zip(classes, arrays, info)
    ]
    if return_metadata:
        return cache, metadata
    return cache


def can_trim_prompt_cache(cache: List[Any]) -> bool:
    """
    Check if model's cache can be trimmed.
    """
    return all(c.is_trimmable() for c in cache)


def trim_prompt_cache(cache: List[Any], num_tokens: int) -> List[Any]:
    """
    Trim the model's cache by the given number of tokens.

    This function will trim the cache if possible (in-place) and return the
    number of tokens that were trimmed.

    Args:
        cache (List[Any]): The model's cache.
        num_tokens (int): The number of tokens to trim.

    Returns:
        (int): The number of tokens that were trimmed.
    """
    if not can_trim_prompt_cache(cache) or len(cache) == 0:
        return 0
    return [c.trim(num_tokens) for c in cache][0]


def create_attention_mask(
    N: int, offset: int, return_array: bool, window_size: Optional[int]
):
    if N == 1:
        return None
    if return_array:
        return create_causal_mask(N, offset, window_size=window_size)
    else:
        return "causal"


class _BaseCache:
    @property
    def state(self):
        return []

    @state.setter
    def state(self, v):
        if v is not None and v:
            raise ValueError("This cache has no state but a state was set.")

    @property
    def meta_state(self):
        return ""

    @meta_state.setter
    def meta_state(self, v):
        if v is not None and v:
            raise ValueError("This cache has no meta_state but a meta_state was set.")

    def is_trimmable(self):
        return False

    @classmethod
    def from_state(cls, state, meta_state):
        # Create an instance of cls without calling __init__
        obj = cls.__new__(cls)
        obj.state = state
        obj.meta_state = meta_state
        return obj


class ConcatenateKVCache(_BaseCache):
    """ConcatenateKVCache the simplest KV cache implementation.

    Can be used as a mock KV cache or when large blocks are being processed at
    a time in which case KVCache isn't necessarily faster. Consider using the
    KVCache with a larger step size before using this cache.
    """

    def __init__(self):
        self.keys = None
        self.values = None
        self.offset = 0

    def update_and_fetch(self, keys, values):
        if self.keys is None:
            self.keys = keys
            self.values = values
        else:
            self.keys = mx.concatenate([self.keys, keys], axis=-2)
            self.values = mx.concatenate([self.values, values], axis=-2)
        self.offset = self.keys.shape[-2]

        return self.keys, self.values

    @property
    def state(self):
        return self.keys, self.values

    @state.setter
    def state(self, v):
        self.keys, self.values = v
        self.offset = self.keys.shape[-2]

    def is_trimmable(self):
        return True

    def trim(self, n):
        n = min(self.offset, n)
        self.offset -= n
        return n

    def make_mask(self, *args, **kwargs):
        return create_attention_mask(*args, offset=self.offset, **kwargs)


class QuantizedKVCache(_BaseCache):
    step = 256

    def __init__(self, group_size: int = 64, bits: int = 8):
        self.keys = None
        self.values = None
        self.offset = 0
        self.group_size = group_size
        self.bits = bits

    def update_and_fetch(self, keys, values):
        B, n_kv_heads, num_steps, k_head_dim = keys.shape
        v_head_dim = values.shape[-1]
        prev = self.offset

        if self.keys is None or (prev + num_steps) > self.keys[0].shape[-2]:
            el_per_int = 8 * mx.uint32.size // self.bits
            new_steps = (self.step + num_steps - 1) // self.step * self.step
            shape = (B, n_kv_heads, new_steps)

            def init_quant(dim):
                return (
                    mx.zeros((*shape, dim // el_per_int), dtype=mx.uint32),
                    mx.zeros((*shape, dim // self.group_size), dtype=keys.dtype),
                    mx.zeros((*shape, dim // self.group_size), dtype=keys.dtype),
                )

            def expand_quant(x):
                new_x = mx.zeros((*shape, x.shape[-1]), dtype=x.dtype)
                return mx.concatenate([x, new_x], axis=-2)

            if self.keys is not None:
                if prev % self.step != 0:
                    self.keys, self.values = tree_map(
                        lambda x: x[..., :prev, :], (self.keys, self.values)
                    )

                self.keys, self.values = tree_map(
                    expand_quant, (self.keys, self.values)
                )
            else:
                self.keys, self.values = init_quant(k_head_dim), init_quant(v_head_dim)

        self.offset += num_steps

        keys = mx.quantize(keys, group_size=self.group_size, bits=self.bits)
        values = mx.quantize(values, group_size=self.group_size, bits=self.bits)
        for i in range(len(self.keys)):
            self.keys[i][..., prev : self.offset, :] = keys[i]
            self.values[i][..., prev : self.offset, :] = values[i]

        return tree_map(lambda x: x[..., : self.offset, :], (self.keys, self.values))

    @property
    def state(self):
        if self.offset == self.keys[0].shape[2]:
            return self.keys, self.values
        else:
            return tree_map(
                lambda x: x[..., : self.offset, :], (self.keys, self.values)
            )

    @state.setter
    def state(self, v):
        self.keys, self.values = v

    @property
    def meta_state(self):
        return tuple(map(str, (self.offset, self.group_size, self.bits)))

    @meta_state.setter
    def meta_state(self, v):
        self.offset, self.group_size, self.bits = map(int, v)

    def is_trimmable(self):
        return True

    def trim(self, n):
        n = min(self.offset, n)
        self.offset -= n
        return n

    def make_mask(self, *args, **kwargs):
        return create_attention_mask(*args, offset=self.offset, **kwargs)


class KVCache(_BaseCache):
    step = 256

    def __init__(self):
        self.keys = None
        self.values = None
        self.offset = 0

    def update_and_fetch(self, keys, values):
        prev = self.offset
        if self.keys is None or (prev + keys.shape[2]) > self.keys.shape[2]:
            B, n_kv_heads, _, k_head_dim = keys.shape
            v_head_dim = values.shape[3]
            n_steps = (self.step + keys.shape[2] - 1) // self.step
            k_shape = (B, n_kv_heads, n_steps * self.step, k_head_dim)
            v_shape = (B, n_kv_heads, n_steps * self.step, v_head_dim)
            new_k = mx.zeros(k_shape, keys.dtype)
            new_v = mx.zeros(v_shape, values.dtype)
            if self.keys is not None:
                if prev % self.step != 0:
                    self.keys = self.keys[..., :prev, :]
                    self.values = self.values[..., :prev, :]
                self.keys = mx.concatenate([self.keys, new_k], axis=2)
                self.values = mx.concatenate([self.values, new_v], axis=2)
            else:
                self.keys, self.values = new_k, new_v

        self.offset += keys.shape[2]
        self.keys[..., prev : self.offset, :] = keys
        self.values[..., prev : self.offset, :] = values
        return self.keys[..., : self.offset, :], self.values[..., : self.offset, :]

    @property
    def state(self):
        if self.offset == self.keys.shape[2]:
            return self.keys, self.values
        else:
            return (
                self.keys[..., : self.offset, :],
                self.values[..., : self.offset, :],
            )

    @state.setter
    def state(self, v):
        self.keys, self.values = v
        self.offset = self.keys.shape[2]

    def is_trimmable(self):
        return True

    def trim(self, n):
        n = min(self.offset, n)
        self.offset -= n
        return n

    def to_quantized(self, group_size: int = 64, bits: int = 4) -> QuantizedKVCache:
        quant_cache = QuantizedKVCache(group_size=group_size, bits=bits)
        quant_cache.offset = self.offset
        if self.keys is not None:
            quant_cache.keys = mx.quantize(self.keys, group_size=group_size, bits=bits)
            quant_cache.values = mx.quantize(
                self.values, group_size=group_size, bits=bits
            )
        return quant_cache

    def make_mask(self, *args, **kwargs):
        return create_attention_mask(*args, offset=self.offset, **kwargs)


class RotatingKVCache(_BaseCache):
    step = 256

    def __init__(self, max_size, keep=0):
        self.keep = keep
        self.keys = None
        self.values = None
        self.offset = 0
        self.max_size = max_size
        self._idx = 0

    def _trim(self, trim_size, v, append=None):
        to_cat = []
        if trim_size > 0:
            to_cat = [v[..., : self.keep, :], v[..., trim_size + self.keep :, :]]
        else:
            to_cat = [v]
        if append is not None:
            to_cat.append(append)
        return mx.concatenate(to_cat, axis=2)

    def _temporal_order(self, v):
        """
        Rearrange the cache into temporal order, slicing off the end if unused.
        """
        if self._idx == v.shape[2]:
            return v
        elif self._idx < self.offset:
            return mx.concatenate(
                [
                    v[..., : self.keep, :],
                    v[..., self._idx :, :],
                    v[..., self.keep : self._idx, :],
                ],
                axis=2,
            )
        else:
            return v[..., : self._idx, :]

    def _update_concat(self, keys, values):
        if self.keys is None:
            self.keys = keys
            self.values = values
        else:
            # Put the keys/values in temporal order to
            # preserve context
            self.keys = self._temporal_order(self.keys)
            self.values = self._temporal_order(self.values)
            self._idx = self.keys.shape[2]

            # The largest size is self.max_size + S - 1 to ensure
            # every token gets at least self.max_size context
            trim_size = self._idx - self.max_size + 1
            self.keys = self._trim(trim_size, self.keys, keys)
            self.values = self._trim(trim_size, self.values, values)
        self.offset += keys.shape[2]
        self._idx = self.keys.shape[2]
        return self.keys, self.values

    def _update_in_place(self, keys, values):
        # May not have hit the max size yet, so potentially
        # keep growing the cache
        B, n_kv_heads, S, k_head_dim = keys.shape
        prev = self.offset
        if self.keys is None or (
            prev >= self.keys.shape[2] and self.keys.shape[2] < self.max_size
        ):
            v_head_dim = values.shape[3]
            new_size = min(self.step, self.max_size - prev)
            k_shape = (B, n_kv_heads, new_size, k_head_dim)
            v_shape = (B, n_kv_heads, new_size, v_head_dim)
            new_k = mx.zeros(k_shape, keys.dtype)
            new_v = mx.zeros(v_shape, values.dtype)
            if self.keys is not None:
                self.keys = mx.concatenate([self.keys, new_k], axis=2)
                self.values = mx.concatenate([self.values, new_v], axis=2)
            else:
                self.keys, self.values = new_k, new_v
            self._idx = prev

        # Trim if needed
        trim_size = self.keys.shape[2] - self.max_size
        if trim_size > 0:
            self.keys = self._trim(trim_size, self.keys)
            self.values = self._trim(trim_size, self.values)
            self._idx = self.max_size

        # Rotate
        if self._idx == self.max_size:
            self._idx = self.keep

        # Assign
        self.keys[..., self._idx : self._idx + S, :] = keys
        self.values[..., self._idx : self._idx + S, :] = values
        self.offset += S
        self._idx += S

        # If the buffer is not full, slice off the end
        if self.offset < self.max_size:
            return self.keys[..., : self.offset, :], self.values[..., : self.offset, :]
        return self.keys, self.values

    def update_and_fetch(self, keys, values):
        if keys.shape[2] == 1:
            return self._update_in_place(keys, values)
        return self._update_concat(keys, values)

    @property
    def state(self):
        if self.offset < self.keys.shape[2]:
            return self.keys[..., : self.offset, :], self.values[..., : self.offset, :]
        else:
            return self.keys, self.values

    @state.setter
    def state(self, v):
        self.keys, self.values = v

    @property
    def meta_state(self):
        return tuple(map(str, (self.keep, self.max_size, self.offset, self._idx)))

    @meta_state.setter
    def meta_state(self, v):
        self.keep, self.max_size, self.offset, self._idx = map(
            int,
            v,
        )

    def is_trimmable(self):
        return self.offset < self.max_size

    def trim(self, n):
        n = min(self.offset, n)
        self.offset -= n
        self._idx -= n
        return n

    def to_quantized(self, group_size: int = 64, bits: int = 4) -> QuantizedKVCache:
        raise NotImplementedError("RotatingKVCache Quantization NYI")

    def make_mask(
        self, N: int, window_size: Optional[int] = None, return_array: bool = False
    ):
        if N > 1:
            window_size = window_size or self.max_size
            offset = min(self.max_size - 1, self.offset)
            if offset + N > window_size or return_array:
                return create_causal_mask(N, offset, window_size=window_size)
            else:
                return "causal"
        else:
            if window_size is None:
                return None
            # May need a mask for when window_size < max_size
            if self.offset >= window_size and self.max_size > window_size:
                idx = self._idx
                if idx >= self.max_size:
                    idx = 0
                if self.offset < self.max_size:
                    mask_size = self.offset + 1
                else:
                    mask_size = self.max_size
                mask = mx.arange(mask_size) >= (mask_size - window_size)
                mask = mx.roll(mask, shift=idx + 1)
                return mask


class ArraysCache(_BaseCache):
    def __init__(self, size, left_padding: Optional[List[int]] = None):
        self.cache = [None] * size
        self.left_padding = mx.array(left_padding) if left_padding else None

    def __setitem__(self, idx, value):
        self.cache[idx] = value

    def __getitem__(self, idx):
        return self.cache[idx]

    @property
    def state(self):
        return self.cache

    @state.setter
    def state(self, v):
        self.cache = v

    def filter(self, batch_indices):
        """
        In-place filter to keep just the given indices in the cache.
        """
        self.cache = [c[batch_indices] for c in self.cache]
        self.left_padding = None

    def extend(self, other):
        """
        In-place extend this cache with the other cache.
        """
        self.cache = [mx.concatenate([c, o]) for c, o in zip(self.cache, other.cache)]
        self.left_padding = None

    def make_mask(self, N: int):
        if self.cache[0] is None and self.left_padding is not None:
            return mx.arange(N) >= self.left_padding[:, None]
        else:
            return None


class MambaCache(ArraysCache):
    def __init__(self, left_padding: Optional[List[int]] = None):
        super().__init__(size=2, left_padding=left_padding)


class ChunkedKVCache(KVCache):
    def __init__(self, chunk_size):
        super().__init__()
        self.chunk_size = chunk_size
        self.start_position = 0

    def maybe_trim_front(self):
        # Maintain the cache below the chunk size
        if self.keys is not None and self.keys.shape[2] >= self.chunk_size:
            self.start_position += self.keys.shape[2] - self.chunk_size
            self.keys = self.keys[..., -self.chunk_size :, :]
            self.values = self.values[..., -self.chunk_size :, :]

    def update_and_fetch(self, keys, values):
        prev = self.offset - self.start_position
        if self.keys is None or (prev + keys.shape[2]) > self.keys.shape[2]:
            B, n_kv_heads, _, k_head_dim = keys.shape
            v_head_dim = values.shape[3]
            n_steps = (self.step + keys.shape[2] - 1) // self.step
            k_shape = (B, n_kv_heads, n_steps * self.step, k_head_dim)
            v_shape = (B, n_kv_heads, n_steps * self.step, v_head_dim)
            new_k = mx.zeros(k_shape, keys.dtype)
            new_v = mx.zeros(v_shape, values.dtype)
            if self.keys is not None:
                if prev % self.step != 0:
                    self.keys = self.keys[..., :prev, :]
                    self.values = self.values[..., :prev, :]
                self.keys = mx.concatenate([self.keys, new_k], axis=2)
                self.values = mx.concatenate([self.values, new_v], axis=2)
            else:
                self.keys, self.values = new_k, new_v

        self.offset += keys.shape[2]
        end = self.offset - self.start_position
        self.keys[..., prev:end, :] = keys
        self.values[..., prev:end, :] = values
        return self.keys[..., :end, :], self.values[..., :end, :]

    def trim(self, n):
        n = min(self.offset - self.start_position, n)
        self.offset -= n
        return n

    @property
    def meta_state(self):
        return tuple(map(str, (self.chunk_size, self.start_position)))

    @meta_state.setter
    def meta_state(self, v):
        self.chunk_size, self.start_position = map(int, v)


class CacheList(_BaseCache):
    def __init__(self, *caches):
        self.caches = caches

    def __getitem__(self, idx):
        return self.caches[idx]

    def is_trimmable(self):
        return all(c.is_trimmable() for c in self.caches)

    def trim(self, n):
        for c in self.caches:
            m = c.trim(n)
        return m

    @property
    def state(self):
        return [s for c in self.caches for s in c.state]

    @state.setter
    def state(self, v):
        state_lens = [len(c.state) for c in self.caches]
        start = 0
        for c in self.caches:
            l = len(c.state)
            c.state = v[start : start + l]
            start += l

    def filter(self, batch_indices):
        """
        In-place filter to keep just the given indices in the cache.
        """
        for c in self.caches:
            c.filter(batch_indices)

    def extend(self, other):
        """
        In-place extend this cache with the other cache.
        """
        for c, o in zip(self.caches, other.caches):
            c.extend(o)


class BatchKVCache(_BaseCache):
    step = 256

    def __init__(self, left_padding: List[int]):
        """
        The BatchKV cache expects inputs to be left-padded.

        E.g. the following prompts:

            [1, 3, 5]
            [7]
            [2, 6, 8, 9]

        Should be padded like so:

            [0, 1, 3, 5]
            [0, 0, 0, 7]
            [2, 6, 8, 9]

        And ``left_padding`` specifies the amount of padding for each.
        In this case, ``left_padding = [1, 3, 0]``.
        """
        self.keys = None
        self.values = None
        self.left_padding = mx.array(left_padding)
        self.offset = mx.array([-l for l in left_padding])
        self._idx = 0

    def update_and_fetch(self, keys, values):
        prev = self._idx
        if self.keys is None or (prev + keys.shape[2]) > self.keys.shape[2]:
            B, n_kv_heads, _, k_head_dim = keys.shape
            v_head_dim = values.shape[3]
            n_steps = (self.step + keys.shape[2] - 1) // self.step
            k_shape = (B, n_kv_heads, n_steps * self.step, k_head_dim)
            v_shape = (B, n_kv_heads, n_steps * self.step, v_head_dim)
            new_k = mx.zeros(k_shape, keys.dtype)
            new_v = mx.zeros(v_shape, values.dtype)
            if self.keys is not None:
                if prev % self.step != 0:
                    self.keys = self.keys[..., :prev, :]
                    self.values = self.values[..., :prev, :]
                self.keys = mx.concatenate([self.keys, new_k], axis=2)
                self.values = mx.concatenate([self.values, new_v], axis=2)
            else:
                self.keys, self.values = new_k, new_v

        self.offset += keys.shape[2]
        self._idx += keys.shape[2]
        self.keys[..., prev : self._idx, :] = keys
        self.values[..., prev : self._idx, :] = values
        return self.keys[..., : self._idx, :], self.values[..., : self._idx, :]

    @property
    def state(self):
        k, v = self.keys, self.values
        if self._idx < k.shape[2]:
            k = k[..., : self._idx, :]
            v = v[..., : self._idx, :]
        return k, v, self.offset, self.left_padding

    @state.setter
    def state(self, v):
        self.keys, self.values, self.offset, self.left_padding = v
        self._idx = self.keys.shape[2]

    def is_trimmable(self):
        return True

    def trim(self, n):
        n = min(self._idx, n)
        self._idx -= n
        self.offset -= n
        return n

    def make_mask(self, N: int, return_array: bool = False, **kwargs):
        return create_causal_mask(
            N, offset=self._idx, left_padding=self.left_padding, **kwargs
        )

    def filter(self, batch_indices):
        """
        In-place filter to keep just the given indices in the cache.
        """
        self.keys = self.keys[batch_indices]
        self.values = self.values[batch_indices]
        self.offset = self.offset[batch_indices]
        self.left_padding = self.left_padding[batch_indices]

        # Shift left to reduce padding
        min_left_pad = self.left_padding.min().item()
        if min_left_pad > 0:
            self.keys = self.keys[..., min_left_pad:, :]
            self.values = self.values[..., min_left_pad:, :]
            self._idx -= min_left_pad
            self.left_padding -= min_left_pad

    def extend(self, other):
        """
        In-place extend this cache with the other cache.
        """
        max_idx = max(self._idx, other._idx)
        max_size = max(self.keys.shape[2], other.keys.shape[2])

        # Pad the keys and values so they are right-justified
        # with the index and the same size
        def pad(c):
            left = max_idx - c._idx
            right = max_size - c.keys.shape[2] - left
            k, v = c.keys, c.values
            if right < 0:
                k = k[..., :right, :]
                v = v[..., :right, :]
                right = 0
            if left != 0 or right != 0:
                pad = [(0, 0), (0, 0), (left, right), (0, 0)]
                k = mx.pad(k, pad)
                v = mx.pad(v, pad)
            left_padding = c.left_padding + left
            return k, v, c.offset, left_padding

        self.keys, self.values, self.offset, self.left_padding = map(
            mx.concatenate, zip(*(pad(self), pad(other)))
        )
        self._idx = max_idx


class BatchRotatingKVCache(_BaseCache):
    step = 256

    def __init__(self, max_size, left_padding: List[int]):
        self.keys = None
        self.values = None

        self.left_padding = mx.array(left_padding)
        self.offset = mx.array([-l for l in left_padding])

        self.max_size = max_size
        self._idx = 0
        self._offset = 0
        self.rotated = False

    def _trim(self, trim_size, v, append=None):
        if trim_size > 0:
            v = v[..., trim_size:, :]
        if append is not None:
            return mx.concatenate([v, append], axis=2)
        return v

    def _temporal_order(self):
        """
        Rearrange the cache into temporal order.
        """
        if self.rotated:
            self.keys = mx.roll(self.keys, -self._idx, axis=2)
            self.values = mx.roll(self.values, -self._idx, axis=2)
            self._idx = self.keys.shape[2]
            self.rotated = False

    def _update_concat(self, keys, values):
        if self.keys is None:
            self.keys = keys
            self.values = values
        else:
            # Put the keys/values in temporal order to
            # preserve context
            self._temporal_order()

            # Slice off the end if needed
            if self.keys.shape[2] > self._idx:
                self.keys = self.keys[..., : self._idx, :]
                self.values = self.values[..., : self._idx, :]

            # The largest size is self.max_size + S - 1 to ensure
            # every token gets at least self.max_size context
            trim_size = self._idx - self.max_size + 1
            if trim_size > 0:
                self.left_padding -= trim_size
            self.keys = self._trim(trim_size, self.keys, keys)
            self.values = self._trim(trim_size, self.values, values)
        self.offset += keys.shape[2]
        self._offset += keys.shape[2]
        self._idx = self.keys.shape[2]
        return self.keys, self.values

    def _update_in_place(self, keys, values):
        # May not have hit the max size yet, so potentially
        # keep growing the cache
        B, n_kv_heads, S, k_head_dim = keys.shape
        prev = self._offset
        if self.keys is None or (
            prev >= self.keys.shape[2] and self.keys.shape[2] < self.max_size
        ):
            v_head_dim = values.shape[3]
            new_size = min(self.step, self.max_size - prev)
            k_shape = (B, n_kv_heads, new_size, k_head_dim)
            v_shape = (B, n_kv_heads, new_size, v_head_dim)
            new_k = mx.zeros(k_shape, keys.dtype)
            new_v = mx.zeros(v_shape, values.dtype)
            if self.keys is not None:
                self.keys = mx.concatenate([self.keys, new_k], axis=2)
                self.values = mx.concatenate([self.values, new_v], axis=2)
            else:
                self.keys, self.values = new_k, new_v
            self._idx = prev

        # Trim if needed
        trim_size = self.keys.shape[2] - self.max_size
        if trim_size > 0:
            self.keys = self._trim(trim_size, self.keys)
            self.values = self._trim(trim_size, self.values)
            self._idx = self.max_size
            self.left_padding -= trim_size

        # Rotate
        if self._idx == self.max_size:
            self.rotated = True
            self._idx = 0
        if self.rotated:
            self.left_padding -= S

        # Assign
        self.keys[..., self._idx : self._idx + S, :] = keys
        self.values[..., self._idx : self._idx + S, :] = values
        self._offset += S
        self.offset += S
        self._idx += S

        # If the buffer is not full, slice off the end
        if self._offset < self.max_size:
            return (
                self.keys[..., : self._offset, :],
                self.values[..., : self._offset, :],
            )
        return self.keys, self.values

    def update_and_fetch(self, keys, values):
        if keys.shape[2] == 1:
            return self._update_in_place(keys, values)
        return self._update_concat(keys, values)

    @property
    def state(self):
        k, v = self.keys, self.values
        if self._offset < k.shape[2]:
            k, v = k[..., : self._offset, :], v[..., : self._offset, :]
        return k, v, self.offset, self.left_padding

    @state.setter
    def state(self, v):
        self.keys, self.values, self.offset, self.left_padding = v

    @property
    def meta_state(self):
        return tuple(map(str, (self.max_size, self._offset, self._idx, self.rotated)))

    @meta_state.setter
    def meta_state(self, v):
        self.max_size, self._offset, self._idx = map(
            int,
            v[:3],
        )
        self.rotated = bool(v[3])

    def is_trimmable(self):
        return self._offset < self.max_size

    def trim(self, n):
        n = min(self._offset, n)
        self._offset -= n
        self._idx -= n
        self.offset -= n
        return n

    def to_quantized(self, group_size: int = 64, bits: int = 4) -> QuantizedKVCache:
        raise NotImplementedError("BatchRotatingKVCache Quantization NYI")

    def make_mask(
        self, N: int, window_size: Optional[int] = None, return_array: bool = False
    ):
        left_padding = self.left_padding
        window_size = window_size or self.max_size
        offset = min(self.max_size - 1, self._offset)
        rinds = mx.arange(offset + N)
        linds = mx.arange(offset, offset + N) if offset else rinds
        linds = linds[:, None]
        rinds = rinds[None]
        mask = linds >= rinds
        mask &= linds < rinds + window_size
        if (trim_size := self._idx - self.max_size + int(N > 1)) > 0:
            left_padding = left_padding - trim_size

        rotated = N == 1 and (self.rotated or self._idx >= self.max_size)
        if rotated:
            left_padding = left_padding - 1

        mask = mask & (rinds >= mx.expand_dims(left_padding, (1, 2, 3)))

        if rotated:
            idx = self._idx
            if idx >= self.max_size:
                idx = 0
            mask = mx.roll(mask, shift=idx + 1, axis=-1)

        return mask

    def filter(self, batch_indices):
        """
        In-place filter to keep just the given indices in the cache.
        """
        self.keys = self.keys[batch_indices]
        self.values = self.values[batch_indices]
        self.offset = self.offset[batch_indices]
        self.left_padding = self.left_padding[batch_indices]

    def extend(self, other):
        """
        In-place extend this cache with the other cache.
        """
        if (self.rotated != other.rotated) or self._idx != other._idx:
            self._temporal_order()
            other._temporal_order()

        max_idx = max(self._idx, other._idx)
        max_size = max(self.keys.shape[2], other.keys.shape[2])

        def pad(c):
            left = max_idx - c._idx
            right = max_size - c.keys.shape[2] - left
            k, v = c.keys, c.values
            if right < 0:
                k = k[..., :right, :]
                v = v[..., :right, :]
                right = 0
            if left != 0 or right != 0:
                pad = [(0, 0), (0, 0), (left, right), (0, 0)]
                k = mx.pad(k, pad)
                v = mx.pad(v, pad)
            left_padding = c.left_padding + left
            return k, v, c.offset, left_padding

        self.keys, self.values, self.offset, self.left_padding = map(
            mx.concatenate, zip(*(pad(self), pad(other)))
        )
        self._idx = max_idx
        self._offset = max(self._offset, other._offset)
