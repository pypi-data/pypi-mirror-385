# coding=utf-8

from ut_dic.dic import Dic

from collections.abc import Callable
from typing import Any

TyAny = Any
TyArr = list[Any]
TyCallable = Callable[..., Any]
TyDic = dict[Any, Any]
TyDoA = dict[Any, TyArr]
TyKey = Any
TyTup = tuple[Any, ...]
TyKeys = Any | TyArr | TyTup

TnAny = None | Any
TnArr = None | TyArr
TnDoA = None | TyDoA
TnCallable = None | TyCallable
TnDic = None | TyDic
TnKey = None | TyKey
TnKeys = None | TyKeys


class Item:
    """
    Manage Dictionary of Arrays
    """
    @staticmethod
    def sh(item: TnAny) -> TyArr:
        if item is None:
            return []
        if isinstance(item, list):
            return item
        else:
            return [item]


class DoA:
    """
    Manage Dictionary of Arrays
    """
    @staticmethod
    def append_by_key_value(
            doa: TyDoA, key: TyKey, value: TnAny, item: TnAny = None) -> None:
        """
        append the item to the value of the dictionary of Arrays
        for the given key if the item is not contained in the value.
        """
        if doa is None:
            return
        if not key:
            return
        if key not in doa:
            doa[key] = Item.sh(item)
        doa[key].append(value)

    @classmethod
    def append_by_keys_value(
            cls, doa: TyDoA, keys: TyKeys, value: Any, item: TnAny = None
    ) -> None:
        """
        Apply the function "append with key" to the last key of the key
        list amd the dictionary localized by that key.
        """
        if isinstance(keys, (list, tuple)):
            _doa = Dic.locate_secondlast(doa, keys)
            cls.append_by_key_value(_doa, keys[-1], value, item)
        else:
            cls.append_by_key_value(doa, keys, value, item)

    @staticmethod
    def append_by_key_unique_value(
            doa: TyDoA, key: TyKey, value: TnAny, item: TnAny = None) -> None:
        """assign item to dictionary defined as value
           for the given keys.
        """
        if doa is None:
            return
        if not key:
            return
        if key not in doa:
            doa[key] = Item.sh(item)
        if value not in doa[key]:
            doa[key].append(value)

    @classmethod
    def append_by_keys_unique_value(
            cls, doa: TyDoA, keys: TyKeys, value: Any, item: TnAny = None
    ) -> None:
        """
        assign item to dictionary defined as value
        for the given keys.
        """
        if isinstance(keys, (list, tuple)):
            _doa = Dic.locate_secondlast(doa, keys)
            cls.append_by_key_unique_value(_doa, keys[-1], value, item)
        else:
            cls.append_by_key_unique_value(doa, keys, value, item)

    # @classmethod
    # def apply_by_keys(
    #         cls, doa: TyDoA, keys: TyKeys, fnc: TyCallable, value: TyAny, item: TnAny
    # ) -> None:
    #     """
    #     assign item to dictionary defined as value
    #     for the given keys.
    #     """
    #     # def apply(
    #     #        fnc: TyCallable, doa: TyDic, keys: TyArr, item: TyAny, item0: TnAny
    #     if item is None:
    #         item = []
    #     if keys is None:
    #         return
    #     if not isinstance(keys, (list, tuple)):
    #         keys = [keys]
    #     _doa = Dic.locate(doa, keys[:-1])
    #     cls.append_by_key(_doa, keys[-1], value, item)
    #     fnc(doa[keys[:-1]], item)

    @staticmethod
    def extend_by_key_value(
            doa: TnDoA, key: TnKey, value: TyAny, item: TnAny = None
    ) -> None:
        """
        Add the item with the key as element to the dictionary if the key
        is undefined in the dictionary. Extend the element value with the
        value if it supports the extend function.
        """
        # def extend_value(
        if not doa:
            return
        if key not in doa:
            doa[key] = Item.sh(item)
        if isinstance(value, (list, tuple)):
            doa[key].extend(value)
        else:
            doa[key].extend([value])

    @classmethod
    def extend_by_keys_value(
            cls, doa: TyDic, keys: TnKeys, value: TyAny, item: TnAny = None
    ) -> None:
        """
        assign item to dictionary defined as value
        for the given keys.
        """
        if isinstance(keys, (list, tuple)):
            _doa = Dic.locate_secondlast(doa, keys)
            cls.extend_by_key_value(_doa, keys[-1], value, item)
        else:
            cls.extend_by_key_value(doa, keys, value, item)

    @staticmethod
    def union_distinct_by_keys(doa: TyDoA, keys: TnKeys) -> TyArr:
        _values: TyArr = []
        for _arr in Dic.sh_values_by_keys(doa, keys):
            _values = _values + [item for item in _arr if item not in _values]
        return _values

    @staticmethod
    def union_distinct(doa: TyDoA) -> TyArr:
        _values: TyArr = []
        for _arr in doa.values():
            _values = _values + [item for item in _arr if item not in _values]
        return _values

    @staticmethod
    def union(doa: TyDoA) -> TyArr:
        _values: TyArr = []
        for _arr in doa.values():
            _values = _values + _arr
        return _values
