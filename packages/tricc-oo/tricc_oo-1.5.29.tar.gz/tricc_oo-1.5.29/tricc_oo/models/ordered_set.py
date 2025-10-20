from collections import OrderedDict
from collections.abc import Iterable, Sequence
from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema


class OrderedSet(Sequence):
    def __init__(self, iterable=None):
        self._od = OrderedDict.fromkeys(iterable or [])

    def copy(self):
        return OrderedSet(list(self._od.keys()))

    def add(self, item):
        self.insert_at_bottom(item)

    def remove(self, item):
        del self._od[item]

    def pop(self):
        return self._od.popitem(last=False)[0]

    def insert_at_top(self, item):
        # Add item if not already present
        self.insert_at_bottom(item)
        # Move item to the top
        self._od.move_to_end(item, last=False)

    def insert_at_bottom(self, item):
        if item not in self._od:
            self._od[item] = None

    def __contains__(self, item):
        return item in self._od

    def __iter__(self):
        return iter(self._od)

    def __len__(self):
        return len(self._od)

    def __repr__(self):
        return f"{type(self).__name__}({list(self._od.keys())})"

    def _add_items(self, items):
        for item in items:
            if item not in self:
                self.insert_at_bottom(item)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        else:
            return self._od.keys() == other._od.keys()

    # Union method (| operator)
    def __or__(self, other):
        if not isinstance(other, Iterable):
            raise TypeError(f"Unsupported operand type(s) for |: 'OrderedSet' and '{type(other).__name__}'")
        new_set = self.copy()
        new_set._add_items(other)
        return new_set

    def union(self, other):
        return self.__or__(other)

    def __iadd__(self, other):
        if not isinstance(other, Iterable):
            raise TypeError("Unsupported operand type(s) for +=: 'OrderedSet' and '{}'".format(type(other)))
        self._add_items(other)
        return self

    def get(self, index):
        return self.__getitem__(index)

    def __getitem__(self, index):
        try:
            return list(self._od.keys())[index]
        except IndexError:
            raise IndexError("Index out of range") from None

    def sort(self, key=None, reverse=False):
        sorted_keys = sorted(self._od.keys(), key=key, reverse=reverse)
        self._od = OrderedDict.fromkeys(sorted_keys)

    def find_last(self, filter: callable):
        # Iterate over items in reverse order
        for item in reversed(list(self._od.keys())):
            if filter(item):
                return item
        return None  # Return None if no matching item is found

    def find_first(self, filter: callable):
        for item in list(self._od.keys()):
            if filter(item):
                return item
        return None  # Return None if no matching item is found

    def find_prev(self, obj, filter: callable):
        # Get the list of keys (items) in the OrderedSet
        keys = list(self._od.keys())

        # If the object is not in the OrderedSet, start from the end
        if obj not in self._od:
            start_index = len(keys)
        else:
            # Find the index of the given object
            start_index = keys.index(obj)

        # Iterate backward from the start_index
        for i in range(start_index - 1, -1, -1):
            item = keys[i]
            if filter(item):
                return item

        return None  # Return None if no matching item is found before the object

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: type, handler: GetCoreSchemaHandler) -> CoreSchema:
        # Define how Pydantic should handle this type
        return handler.generate_schema(list)  # Treat it as a list for validation purposes
