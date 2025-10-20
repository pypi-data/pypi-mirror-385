import json
import typing as t
from collections.abc import MutableSequence
from typing import overload

import numpy as np
import zarr.dtype
from typing_extensions import deprecated


def _convert_numpy_types(obj):
    """Convert numpy scalar types to native Python types for JSON serialization.

    This function recursively converts numpy scalars (int64, float64, bool_, etc.)
    to their Python equivalents, making them JSON-serializable. Numpy arrays are
    left unchanged as they are handled separately by the storage system.
    """
    if isinstance(obj, np.generic):
        # Use .item() to convert any numpy scalar to native Python type
        return obj.item()
    elif isinstance(obj, dict):
        return {key: _convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [_convert_numpy_types(item) for item in obj]
    else:
        return obj


def encode_data(data: dict) -> dict:
    serialized = {}
    for key, value in data.items():
        if isinstance(value, np.ndarray):
            # Object dtype arrays (like hex color strings) cannot be serialized with tobytes()
            # so we serialize them as JSON instead
            if value.dtype == object:
                serialized[key] = {
                    "data": json.dumps(value.tolist()),
                    "shape": value.shape,
                    "dtype": str(value.dtype),
                }
            else:
                serialized[key] = {
                    "data": value.tobytes(),
                    "shape": value.shape,
                    "dtype": str(value.dtype),
                }
        elif isinstance(value, dict):
            serialized[key] = encode_data(value)
        else:
            serialized[key] = value
    return serialized


def decode_data(data: dict) -> dict:
    deserialized = {}
    for key, value in data.items():
        if (
            isinstance(value, dict)
            and "data" in value
            and "shape" in value
            and "dtype" in value
        ):
            # Object dtype arrays were serialized as JSON, not bytes
            if value["dtype"] == "object":
                deserialized[key] = np.array(
                    json.loads(value["data"]), dtype=object
                ).reshape(value["shape"])
            else:
                deserialized[key] = np.frombuffer(
                    value["data"], dtype=value["dtype"]
                ).reshape(value["shape"])
        elif isinstance(value, dict):
            deserialized[key] = decode_data(value)
        else:
            deserialized[key] = value
    return deserialized


@deprecated("Use extend_zarr() instead.")
def create_zarr(root: zarr.Group, data: dict):
    extend_zarr(root, [data])


def read_zarr(root: zarr.Group, index: int, keys: t.Optional[list[str]] = None) -> dict:
    """
    Reads a single frame (at `index`) from a Zarr group hierarchy.

    This function uses the `__valid_keys__` metadata, if present, to load only
    the data that is valid for the specified frame.

    - If `keys` is not provided, it loads all keys listed in `__valid_keys__[index]`.
    - If `keys` is provided, it first validates that all requested keys are
      present in `__valid_keys__[index]` before loading them.
    - For subgroups, which do not have their own `__valid_keys__`, it validates
      requested keys against the subgroup's members.
    """
    data = {}
    keys_to_load = []

    # At the top level, determine which keys to load based on __valid_keys__
    if "__valid_keys__" in root:
        try:
            valid_keys_for_frame = set(json.loads(root["__valid_keys__"][index].item()))
        except IndexError as e:
            raise IndexError(
                f"Index {index} is out of bounds for the Zarr store."
            ) from e

        if keys is not None:
            # Case 1: User requested specific keys.
            # Validate that the requested keys are a subset of the valid keys for THIS FRAME.
            requested_keys = set(keys)
            invalid_keys_for_frame = requested_keys - valid_keys_for_frame
            if invalid_keys_for_frame:
                raise KeyError(
                    f"Requested keys {sorted(list(invalid_keys_for_frame))} are not valid for index {index}."
                )
            keys_to_load = list(requested_keys)
        else:
            # Case 2: No keys specified. Load all valid keys for this frame.
            keys_to_load = list(valid_keys_for_frame)
    else:
        # This is a subgroup or a store without metadata. Fall back to the general check.
        if keys is not None:
            missing_keys = set(keys) - set(root.keys())
            if missing_keys:
                raise KeyError(
                    f"Requested keys {sorted(list(missing_keys))} not found in Zarr group '{root.name}'"
                )
        keys_to_load = keys if keys is not None else list(root.keys())

    # Process and load the data for the determined keys
    for key in keys_to_load:
        item = root[key]
        if isinstance(item, zarr.Array):
            if item.attrs.get("format") == "json":
                deserialized = json.loads(item[index].item())
                # Check if this was originally an object dtype array
                if item.attrs.get("original_dtype") == "object":
                    # The shape is naturally preserved through JSON serialization
                    # (tolist() -> json.dumps() -> json.loads() -> np.array preserves nested structure)
                    # No need to reshape!
                    data[key] = np.array(deserialized, dtype=object)
                else:
                    data[key] = deserialized
            else:
                if f"__mask__{key}__" in root:
                    mask = root[f"__mask__{key}__"][index]
                    data[key] = item[index, :mask]
                else:
                    data[key] = item[index]
        elif isinstance(item, zarr.Group):
            # For a subgroup, we read its entire contents for the given index.
            data[key] = read_zarr(item, index=index)

    return data


def extend_zarr(root: zarr.Group, data: list[dict]):
    """
    Extends or creates a Zarr hierarchy using an index-based approach.

    This function ensures that all datasets within the group (and subgroups)
    are synchronized to the same length. For each entry in the input data list,
    it performs the following:

    1.  Records the list of keys present in the entry into a special dataset
        `__valid_keys__`. The length of this dataset serves as the authoritative
        length for the entire store.
    2.  Writes the corresponding data to the correct index.
    3.  If a dataset for a given key does not exist, it is created with a
        length equal to the total number of entries, with all preceding
        indices left with the default fill value.
    4.  If a dataset already exists but is too short, it is resized.
    """
    # TODO: introduce `"__mask_{key}__"` to support variable shapes.

    try:
        start_index = root["__valid_keys__"].shape[0]
    except KeyError:
        start_index = 0
    total_entries = start_index + len(data)

    # Ensure the __valid_keys__ dataset exists and is the correct size
    if "__valid_keys__" not in root:
        valid_keys_ds = root.create_array(
            name="__valid_keys__",
            shape=(total_entries,),
            chunks=(1024,),
            dtype=zarr.dtype.VariableLengthUTF8(),
        )
        valid_keys_ds.attrs["format"] = "json"
    else:
        valid_keys_ds = root["__valid_keys__"]
        if valid_keys_ds.shape[0] < total_entries:
            valid_keys_ds.resize(total_entries)

    def _extend_recursive(group: zarr.Group, data_dict: dict, idx: int, total_len: int):
        for key, value in data_dict.items():
            is_new = key not in group
            attrs, item_type, prepared_value, shape_suffix, dtype = (
                {},
                None,
                None,
                None,
                None,
            )

            # Determine how to handle the value based on its type
            if isinstance(value, np.ndarray):
                # Object dtype arrays (like hex color strings) need to be stored as JSON
                # because Zarr doesn't support object dtype directly
                if value.dtype == object:
                    # tolist() preserves nested structure, json preserves it, and np.array reconstructs it
                    # so no need to store shape separately
                    prepared_value = json.dumps(value.tolist())
                    item_type, dtype, shape_suffix, attrs = (
                        "json_array",
                        zarr.dtype.VariableLengthUTF8(),
                        (),
                        {"format": "json", "original_dtype": "object"},
                    )
                else:
                    item_type, dtype, shape_suffix, prepared_value = (
                        "array",
                        value.dtype,
                        value.shape,
                        value,
                    )
            elif isinstance(value, dict):
                try:
                    # Convert numpy types to native Python types before JSON serialization
                    converted_value = _convert_numpy_types(value)
                    prepared_value = json.dumps(converted_value)
                    item_type, dtype, shape_suffix, attrs = (
                        "json_array",
                        zarr.dtype.VariableLengthUTF8(),
                        (),
                        {"format": "json"},
                    )
                except TypeError:
                    item_type = "group"
            else:
                # Convert numpy types to native Python types before JSON serialization
                converted_value = _convert_numpy_types(value)
                prepared_value = json.dumps(converted_value)
                item_type, dtype, shape_suffix, attrs = (
                    "json_array",
                    zarr.dtype.VariableLengthUTF8(),
                    (),
                    {"format": "json"},
                )

            # Create/resize and write to the Zarr item
            if item_type in ["array", "json_array"]:
                if is_new:
                    item = group.create_array(
                        name=key,
                        shape=(total_len,) + shape_suffix,
                        chunks=(1,) + shape_suffix,
                        dtype=dtype,
                    )
                    item.attrs.update(attrs)
                else:
                    item = group[key]
                    if not isinstance(item, zarr.Array):
                        raise TypeError(
                            f"Existing item '{key}' is a Group, expected Array."
                        )
                    if item.shape[0] < total_len:
                        item.resize((total_len,) + item.shape[1:])
                    if len(item.shape) - 1 != len(shape_suffix):
                        raise ValueError(
                            f"Shape mismatch for key '{key}': existing shape {item.shape}, new shape {shape_suffix}."
                        )
                    if item.shape[2:] != shape_suffix[1:]:
                        raise ValueError(
                            f"Shape mismatch for key '{key}': existing shape {item.shape}, new shape {shape_suffix}."
                        )

                    # Handle variable-sized arrays with masks
                    if item.shape[1:] != shape_suffix:
                        # Create or update mask array
                        if f"__mask__{key}__" not in group:
                            grp = group.require_array(
                                name=f"__mask__{key}__",
                                shape=(total_len,),
                                chunks="auto",
                                dtype="int32",
                            )
                            # Initialize all previous entries with the existing array shape
                            grp[:idx] = item.shape[1]
                        else:
                            grp = group[f"__mask__{key}__"]
                            if grp.shape[0] < total_len:
                                grp.resize((total_len,))

                        # Always set the mask value for current index
                        grp[idx] = shape_suffix[0]

                        # Resize array if needed to accommodate larger shapes
                        if item.shape[1:] < shape_suffix:
                            item.resize((item.shape[0],) + shape_suffix)
                    else:
                        # Even if shapes match, we might need to set mask if it exists
                        if f"__mask__{key}__" in group:
                            grp = group[f"__mask__{key}__"]
                            # Resize mask array if needed
                            if grp.shape[0] < total_len:
                                grp.resize((total_len,))
                            grp[idx] = shape_suffix[0]

                # If the array shape is smaller than the allocated space, pad it
                # (only for numpy arrays, not json_array strings)
                if item_type == "array" and item.shape[1:] != prepared_value.shape:
                    padded_value = np.zeros(item.shape[1:], dtype=prepared_value.dtype)
                    # Copy the actual data into the padded array
                    slices = tuple(slice(0, s) for s in prepared_value.shape)
                    padded_value[slices] = prepared_value
                    item[idx] = padded_value
                else:
                    item[idx] = prepared_value
            elif item_type == "group":
                subgroup = group.require_group(key)
                _extend_recursive(subgroup, value, idx, total_len)

    # Process each new data entry
    for i, entry in enumerate(data):
        current_index = start_index + i

        # 1. Store the list of valid keys for this entry
        valid_keys_ds[current_index] = json.dumps(list(entry.keys()))

        # 2. Process the actual data recursively
        _extend_recursive(root, entry, current_index, total_entries)


class ZarrStorageSequence(MutableSequence):
    def __init__(self, group: zarr.Group):
        self.group = group

    @overload
    def __getitem__(self, index: int) -> dict: ...
    @overload
    def __getitem__(self, index: slice) -> dict: ...
    @overload
    def __getitem__(self, index: list[int]) -> dict: ...
    @overload
    def __getitem__(self, index: np.ndarray) -> dict: ...

    def __getitem__(self, index: int | list[int] | slice | np.ndarray) -> dict:
        return self.get(index)

    @overload
    def get(self, index: int, keys: list[str] | None = None) -> dict: ...
    @overload
    def get(self, index: slice, keys: list[str] | None = None) -> dict: ...
    @overload
    def get(self, index: list[int], keys: list[str] | None = None) -> dict: ...
    @overload
    def get(self, index: np.ndarray, keys: list[str] | None = None) -> dict: ...

    def get(
        self, index: int | list[int] | slice | np.ndarray, keys: list[str] | None = None
    ) -> dict:
        # Handle numpy arrays and scalars
        if isinstance(index, np.ndarray):
            if index.ndim == 0:
                # 0-d array (scalar)
                index = int(index.item())
            else:
                # Multi-dimensional array
                index = index.tolist()

        if isinstance(index, slice):
            index = list(range(*index.indices(len(self))))
        is_single = False
        if isinstance(index, int):
            is_single = True
            index = [index]

        # Validate indices are within bounds
        length = len(self)
        for i in index:
            if i < -length or i >= length:
                raise IndexError(
                    f"Index {i} is out of bounds for storage of length {length}"
                )

        result = [read_zarr(self.group, i, keys=keys) for i in index]
        if is_single:
            return result[0]

        # For multiple indices, concatenate arrays for each key
        if not result:
            return {}

        concatenated = {}
        all_keys = set()
        for d in result:
            all_keys.update(d.keys())

        for key in all_keys:
            values = [d[key] for d in result if key in d]
            if values and isinstance(values[0], np.ndarray):
                concatenated[key] = np.array(values)
            else:
                # For non-array values, just return as list
                concatenated[key] = values

        return concatenated

    def __setitem__(self, index: int | list[int] | slice, value: dict | list[dict]):
        if isinstance(index, slice):
            index = list(range(*index.indices(len(self))))
        if isinstance(index, int):
            index = [index]

        raise NotImplementedError

    def __delitem__(self, index: int | list[int] | slice):
        if isinstance(index, slice):
            index = list(range(*index.indices(len(self))))
        if isinstance(index, int):
            index = [index]
        raise NotImplementedError

    def __len__(self):
        try:
            return self.group["__valid_keys__"].shape[0]
        except (IndexError, KeyError):
            return 0

    def insert(self, index: int, value: dict):
        raise NotImplementedError

    def append(self, value: dict) -> None:
        self.extend([value])

    def extend(self, values: list[dict]) -> None:
        extend_zarr(self.group, values)
