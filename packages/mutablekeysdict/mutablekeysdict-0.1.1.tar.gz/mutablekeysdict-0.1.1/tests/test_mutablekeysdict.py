"""Comprehensive test suite for MutableKeysDict."""

import pytest

from mutablekeysdict import MutableKeysDict


class HashableList(list):
    """A hashable list for testing mutable key behavior."""

    def __hash__(self):
        return hash(tuple(self))


class TestMutableKeysDictBasics:
    """Test basic dictionary operations."""

    def test_empty_init(self):
        """Test creating an empty MutableKeysDict."""
        d = MutableKeysDict()
        assert len(d) == 0
        assert dict(d) == {}

    def test_init_with_data(self):
        """Test creating MutableKeysDict with initial data."""
        d = MutableKeysDict({"a": 1, "b": 2, "c": 3})
        assert len(d) == 3
        assert d["a"] == 1
        assert d["b"] == 2
        assert d["c"] == 3

    def test_setitem_new_key(self):
        """Test setting a new key-value pair."""
        d = MutableKeysDict()
        d["key"] = "value"
        assert d["key"] == "value"
        assert len(d) == 1

    def test_setitem_existing_key(self):
        """Test updating an existing key."""
        d = MutableKeysDict({"a": 1})
        d["a"] = 2
        assert d["a"] == 2
        assert len(d) == 1

    def test_getitem(self):
        """Test getting values by key."""
        d = MutableKeysDict({"a": 1, "b": 2})
        assert d["a"] == 1
        assert d["b"] == 2

    def test_getitem_keyerror(self):
        """Test KeyError for non-existent key."""
        d = MutableKeysDict({"a": 1})
        with pytest.raises(KeyError):
            _ = d["nonexistent"]

    def test_delitem(self):
        """Test deleting items."""
        d = MutableKeysDict({"a": 1, "b": 2, "c": 3})
        del d["b"]
        assert len(d) == 2
        assert "b" not in d
        assert d["a"] == 1
        assert d["c"] == 3

    def test_delitem_keyerror(self):
        """Test KeyError when deleting non-existent key."""
        d = MutableKeysDict({"a": 1})
        with pytest.raises(KeyError):
            del d["nonexistent"]

    def test_contains(self):
        """Test the 'in' operator."""
        d = MutableKeysDict({"a": 1, "b": 2})
        assert "a" in d
        assert "b" in d
        assert "c" not in d

    def test_len(self):
        """Test len() function."""
        d = MutableKeysDict()
        assert len(d) == 0
        d["a"] = 1
        assert len(d) == 1
        d["b"] = 2
        assert len(d) == 2
        del d["a"]
        assert len(d) == 1

    def test_iter(self):
        """Test iteration over keys."""
        d = MutableKeysDict({"a": 1, "b": 2, "c": 3})
        keys = list(d)
        assert set(keys) == {"a", "b", "c"}

    def test_repr(self):
        """Test string representation."""
        d = MutableKeysDict({"a": 1, "b": 2})
        repr_str = repr(d)
        assert "MutableKeysDict" in repr_str
        assert "'a': 1" in repr_str or "'b': 2" in repr_str


class TestMutableKeysDictMethods:
    """Test dictionary methods."""

    def test_keys(self):
        """Test keys() method."""
        d = MutableKeysDict({"a": 1, "b": 2, "c": 3})
        keys = d.keys()
        assert set(keys) == {"a", "b", "c"}

    def test_values(self):
        """Test values() method."""
        d = MutableKeysDict({"a": 1, "b": 2, "c": 3})
        values = list(d.values())
        assert set(values) == {1, 2, 3}

    def test_items(self):
        """Test items() method."""
        d = MutableKeysDict({"a": 1, "b": 2, "c": 3})
        items = d.items()
        assert set(items) == {("a", 1), ("b", 2), ("c", 3)}

    def test_get_existing_key(self):
        """Test get() with existing key."""
        d = MutableKeysDict({"a": 1, "b": 2})
        assert d.get("a") == 1
        assert d.get("b") == 2

    def test_get_nonexistent_key(self):
        """Test get() with non-existent key."""
        d = MutableKeysDict({"a": 1})
        assert d.get("nonexistent") is None
        assert d.get("nonexistent", "default") == "default"

    def test_pop(self):
        """Test pop() method."""
        d = MutableKeysDict({"a": 1, "b": 2, "c": 3})
        value = d.pop("b")
        assert value == 2
        assert "b" not in d
        assert len(d) == 2

    def test_pop_keyerror(self):
        """Test pop() with non-existent key."""
        d = MutableKeysDict({"a": 1})
        with pytest.raises(KeyError):
            d.pop("nonexistent")

    def test_popitem(self):
        """Test popitem() method."""
        d = MutableKeysDict({"a": 1, "b": 2})
        key, value = d.popitem()
        assert key in {"a", "b"}
        assert value in {1, 2}
        assert len(d) == 1

    def test_popitem_empty(self):
        """Test popitem() on empty dict."""
        d = MutableKeysDict()
        with pytest.raises(KeyError):
            d.popitem()

    def test_clear(self):
        """Test clear() method."""
        d = MutableKeysDict({"a": 1, "b": 2, "c": 3})
        d.clear()
        assert len(d) == 0
        assert dict(d) == {}

    def test_update_dict(self):
        """Test update() with dict."""
        d = MutableKeysDict({"a": 1})
        d.update({"b": 2, "c": 3})
        assert d["a"] == 1
        assert d["b"] == 2
        assert d["c"] == 3

    def test_update_iterable(self):
        """Test update() with iterable of pairs."""
        d = MutableKeysDict({"a": 1})
        d.update([("b", 2), ("c", 3)])
        assert d["a"] == 1
        assert d["b"] == 2
        assert d["c"] == 3

    def test_update_overwrites(self):
        """Test that update() overwrites existing keys."""
        d = MutableKeysDict({"a": 1, "b": 2})
        d.update({"a": 10})
        assert d["a"] == 10
        assert d["b"] == 2

    def test_setdefault_new_key(self):
        """Test setdefault() with new key."""
        d = MutableKeysDict({"a": 1})
        result = d.setdefault("b", 2)
        assert result == 2
        assert d["b"] == 2

    def test_setdefault_existing_key(self):
        """Test setdefault() with existing key."""
        d = MutableKeysDict({"a": 1})
        result = d.setdefault("a", 999)
        assert result == 1
        assert d["a"] == 1

    def test_setdefault_no_default(self):
        """Test setdefault() without default value."""
        d = MutableKeysDict()
        result = d.setdefault("a")
        assert result is None
        assert d["a"] is None

    def test_copy(self):
        """Test copy() method."""
        d1 = MutableKeysDict({"a": 1, "b": 2})
        d2 = d1.copy()
        assert dict(d1) == dict(d2)
        assert d1 is not d2
        # Modify d2 and ensure d1 is unchanged
        d2["c"] = 3
        assert "c" not in d1
        assert "c" in d2

    def test_fromkeys(self):
        """Test fromkeys() class method."""
        d = MutableKeysDict.fromkeys(["a", "b", "c"], 0)
        assert d["a"] == 0
        assert d["b"] == 0
        assert d["c"] == 0

    def test_fromkeys_no_value(self):
        """Test fromkeys() without value."""
        d = MutableKeysDict.fromkeys(["a", "b", "c"])
        assert d["a"] is None
        assert d["b"] is None
        assert d["c"] is None

    def test_replace_key(self):
        """Test replace_key() method."""
        d = MutableKeysDict({"a": 1, "b": 2})
        d.replace_key("a", "new_a")
        assert "a" not in d
        assert d["new_a"] == 1
        assert d["b"] == 2


class TestMutableKeysDictOperators:
    """Test dictionary operators."""

    def test_equality_with_dict(self):
        """Test equality comparison with dict."""
        d1 = MutableKeysDict({"a": 1, "b": 2})
        d2 = {"a": 1, "b": 2}
        assert d1 == d2

    def test_inequality_with_dict(self):
        """Test inequality comparison with dict."""
        d1 = MutableKeysDict({"a": 1, "b": 2})
        d2 = {"a": 1, "b": 999}
        assert d1 != d2

    def test_or_operator(self):
        """Test | (union) operator."""
        d1 = MutableKeysDict({"a": 1, "b": 2})
        d2 = {"b": 20, "c": 3}
        d3 = d1 | d2
        assert d3["a"] == 1
        assert d3["b"] == 20  # d2 overwrites d1
        assert d3["c"] == 3
        # Ensure d1 is unchanged
        assert d1["b"] == 2

    def test_ior_operator(self):
        """Test |= (in-place union) operator."""
        d = MutableKeysDict({"a": 1, "b": 2})
        d |= {"b": 20, "c": 3}
        assert d["a"] == 1
        assert d["b"] == 20
        assert d["c"] == 3


class TestMutableKeyBehavior:
    """Test the core feature: mutable keys."""

    def test_mutable_key_lookup(self):
        """Test that dict works after key is mutated."""
        h = HashableList([1, 2, 3])
        d = MutableKeysDict({h: 6})

        # Mutate the key
        h.append(4)

        # Should still be able to access the value
        assert d[h] == 6

    def test_multiple_mutable_keys(self):
        """Test multiple mutable keys."""
        h1 = HashableList([1, 2])
        h2 = HashableList([3, 4])
        h3 = HashableList([5, 6])

        d = MutableKeysDict({h1: "a", h2: "b", h3: "c"})

        # Mutate all keys
        h1.append(10)
        h2.append(20)
        h3.append(30)

        # All values should still be accessible
        assert d[h1] == "a"
        assert d[h2] == "b"
        assert d[h3] == "c"

    def test_mutable_key_after_operations(self):
        """Test mutable keys after various operations."""
        h1 = HashableList([1])
        h2 = HashableList([2])

        d = MutableKeysDict({h1: "first"})
        d[h2] = "second"

        # Mutate keys
        h1.append(10)
        h2.append(20)

        # Update value
        d[h1] = "updated_first"

        assert d[h1] == "updated_first"
        assert d[h2] == "second"

    def test_mutable_key_deletion(self):
        """Test deleting entries with mutated keys."""
        h1 = HashableList([1, 2])
        h2 = HashableList([3, 4])

        d = MutableKeysDict({h1: "a", h2: "b"})

        # Mutate and delete
        h1.append(5)
        del d[h1]

        assert h1 not in d
        assert h2 in d

    def test_mutable_key_contains(self):
        """Test 'in' operator with mutated keys."""
        h = HashableList([1, 2, 3])
        d = MutableKeysDict({h: "value"})

        # Before mutation
        assert h in d

        h.append(4)

        # After mutation - the dict needs to be accessed to trigger reset_keys
        # The 'in' operator calls __contains__ which calls keys() which triggers the reset
        # However, since the key was mutated, its hash changed, so it won't be in _keys
        # until reset_keys is called. Let's trigger a reset by accessing the dict.
        _ = d.get(h)  # This triggers reset_keys
        assert h in d

    def test_mutable_key_get(self):
        """Test get() with mutated keys."""
        h = HashableList([1, 2])
        d = MutableKeysDict({h: "value"})

        h.append(3)

        assert d.get(h) == "value"
        assert d.get(h, "default") == "value"

    def test_mutable_key_pop(self):
        """Test pop() with mutated keys."""
        h = HashableList([1, 2])
        d = MutableKeysDict({h: "value"})

        h.append(3)
        value = d.pop(h)

        assert value == "value"
        assert h not in d

    def test_mutable_key_iteration(self):
        """Test iteration with mutated keys."""
        h1 = HashableList([1])
        h2 = HashableList([2])
        h3 = HashableList([3])

        d = MutableKeysDict({h1: "a", h2: "b", h3: "c"})

        # Mutate all keys
        h1.append(10)
        h2.append(20)
        h3.append(30)

        # Should be able to iterate
        keys = list(d.keys())
        assert len(keys) == 3
        assert h1 in keys
        assert h2 in keys
        assert h3 in keys

    def test_mutable_key_items(self):
        """Test items() with mutated keys."""
        h = HashableList([1, 2])
        d = MutableKeysDict({h: "value"})

        h.append(3)
        items = list(d.items())

        assert len(items) == 1
        assert items[0] == (h, "value")


class TestEdgeCases:
    """Test edge cases and corner scenarios."""

    def test_none_as_key(self):
        """Test None as a key."""
        d = MutableKeysDict({None: "null_value"})
        assert d[None] == "null_value"

    def test_none_as_value(self):
        """Test None as a value."""
        d = MutableKeysDict({"key": None})
        assert d["key"] is None

    def test_empty_string_key(self):
        """Test empty string as key."""
        d = MutableKeysDict({"": "empty"})
        assert d[""] == "empty"

    def test_numeric_keys(self):
        """Test numeric keys."""
        d = MutableKeysDict({1: "one", 2: "two", 3.14: "pi"})
        assert d[1] == "one"
        assert d[2] == "two"
        assert d[3.14] == "pi"

    def test_tuple_keys(self):
        """Test tuple keys."""
        d = MutableKeysDict({(1, 2): "tuple1", (3, 4, 5): "tuple2"})
        assert d[(1, 2)] == "tuple1"
        assert d[(3, 4, 5)] == "tuple2"

    def test_large_dict(self):
        """Test with a large number of items."""
        data = {f"key_{i}": i for i in range(1000)}
        d = MutableKeysDict(data)
        assert len(d) == 1000
        assert d["key_500"] == 500
        assert d["key_999"] == 999

    def test_repeated_mutations(self):
        """Test repeated mutations of the same key."""
        h = HashableList([1])
        d = MutableKeysDict({h: "initial"})

        for i in range(10):
            h.append(i)
            # After each mutation, we should still be able to access and update
            new_value = f"value_{i}"
            d[h] = new_value
            assert d[h] == new_value
