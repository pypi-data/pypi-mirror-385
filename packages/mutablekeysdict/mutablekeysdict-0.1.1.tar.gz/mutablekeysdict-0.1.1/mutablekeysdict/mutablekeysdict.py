from collections.abc import MutableMapping
from itertools import count
from typing import (
    Any,
    ItemsView,
    Iterable,
    Iterator,
    KeysView,
    Mapping,
    Optional,
    Tuple,
    TypeVar,
    ValuesView,
    overload,
)

_T = TypeVar("_T")
_MISSING = object()


class MutableKeysDict(MutableMapping):
    def __init__(self, data: Optional[Mapping] = None) -> None:
        self.i = count()
        self._keys = {}  # {key: index}
        self.data: dict = {}  # {index: value}
        if data is not None:
            for key, value in data.items():
                self._keys[key] = next(self.i)
                self.data[self._keys[key]] = value

    def need_keys_reset(self) -> bool:
        for key in self.keys():
            try:
                self._keys[key]
            except KeyError:
                return True
        return False

    def reset_keys(self) -> None:
        if self.need_keys_reset():
            # Rebuild _keys mapping with new indices
            old_keys = list(self._keys.keys())
            old_data = list(self.data.values())
            self._keys.clear()
            self.data.clear()
            for key, value in zip(old_keys, old_data):
                self._keys[key] = next(self.i)
                self.data[self._keys[key]] = value

    def replace_key(self, old_key, new_key) -> None:
        value = self[old_key]
        self[new_key] = value
        del self[old_key]

    def __repr__(self) -> str:
        self.reset_keys()
        return f"MutableKeysDict({dict(self)})"

    def __getitem__(self, key) -> Any:
        self.reset_keys()
        return self.data[self._keys[key]]

    def __setitem__(self, key, value) -> None:
        self.reset_keys()
        if key not in self.keys():
            self._keys[key] = next(self.i)
        self.data[self._keys[key]] = value

    def __delitem__(self, key) -> None:
        self.reset_keys()
        del self.data[self._keys[key]]
        del self._keys[key]

    def __iter__(self) -> Iterator:
        return iter(self.keys())

    def __len__(self) -> int:
        return len(self.keys())

    def __contains__(self, value: Any) -> bool:
        return value in self.keys()

    def __eq__(self, other: object) -> bool:
        if isinstance(other, dict):
            return dict(self) == other
        if isinstance(other, MutableKeysDict):
            return dict(self) == dict(other)
        return False

    def __ne__(self, other: object) -> bool:
        return not self.__eq__(other)

    def keys(self) -> KeysView:
        return self._keys.keys()

    def items(self) -> ItemsView:
        return dict(self).items()

    def values(self) -> ValuesView:
        return self.data.values()

    def get(self, key, default=None) -> Any:
        self.reset_keys()
        try:
            return self.data[self._keys[key]]
        except KeyError:
            return default

    def pop(self, key: Any, default: Any = _MISSING) -> Any:
        self.reset_keys()
        try:
            value = self.data.pop(self._keys[key])
            del self._keys[key]
            return value
        except KeyError:
            if default is _MISSING:
                raise
            return default

    def popitem(self) -> tuple:
        self.reset_keys()
        if not self._keys:
            raise KeyError("dictionary is empty")
        key = next(iter(self._keys))
        index = self._keys[key]
        value = self.data[index]
        del self._keys[key]
        del self.data[index]
        return (key, value)

    def clear(self) -> None:
        self._keys.clear()
        self.data.clear()

    @overload  # type: ignore[override]
    def update(self, __m: Mapping[Any, Any], **kwargs: Any) -> None: ...

    @overload
    def update(self, __m: Iterable[Tuple[Any, Any]], **kwargs: Any) -> None: ...

    @overload
    def update(self, **kwargs: Any) -> None: ...

    def update(self, __m: Any = None, **kwargs: Any) -> None:
        if __m is not None:
            if isinstance(__m, Mapping):
                for key, value in __m.items():
                    self[key] = value
            else:
                for key, value in __m:
                    self[key] = value
        for key, value in kwargs.items():
            self[key] = value

    def setdefault(self, key, default=None) -> Any:
        self.reset_keys()
        if key not in self._keys:
            self[key] = default
        return self[key]

    def copy(self) -> "MutableKeysDict":
        """Return a shallow copy of the dictionary."""
        return MutableKeysDict(dict(self))

    @classmethod
    def fromkeys(cls, keys, value=None) -> "MutableKeysDict":
        """Create a new dictionary with keys from iterable and values set to value."""
        return cls(dict.fromkeys(keys, value))

    def __or__(self, other) -> "MutableKeysDict":
        """Return self|other (dict union operator)."""
        if not isinstance(other, Mapping):
            return NotImplemented
        new_dict = self.copy()
        new_dict.update(other)
        return new_dict

    def __ior__(self, other) -> "MutableKeysDict":
        """Implement self|=other (in-place dict union operator)."""
        self.update(other)
        return self
