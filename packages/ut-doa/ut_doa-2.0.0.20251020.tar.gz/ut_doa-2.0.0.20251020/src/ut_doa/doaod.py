# coding=utf-8
import pandas as pd

from ut_dic.dic import Dic

from typing import Any, TypeAlias

TyArr = list[Any]
TyAoA = list[TyArr]
TyBool = bool
TyDic = dict[Any, Any]
TyAoD = list[TyDic]
TyAoAoD = list[TyAoD]
TyPdDf: TypeAlias = pd.DataFrame
TyDoAoD = dict[Any, TyAoD]
TyDoPdDf = dict[Any, TyPdDf]
TyKeys = str | TyArr
TyStr = str

TnAoA = None | TyAoA


class DoAoD:

    @staticmethod
    def is_dic_value_empty(
            doaod: TyDoAoD, key: TyStr, sw_raise: TyBool = False) -> TyBool:
        """
        Check if all keys of the given Dictionary of Arrays of
        Dictionaries are found in any Dictionary of the Array
        of Dictionaries and the value for the key is not empty.
        """
        # def dic_value_is_empty(doaod: TyDoAoD, key: str) -> bool:
        for _key, _aod in doaod.items():
            for _dic in _aod:
                if not _dic:
                    pass
                elif not _dic.get(key):
                    if not sw_raise:
                        return True
                    msg = f"Value for key={key} in dictionary of aod={_dic} is empty"
                    raise Exception(msg)
        return False

    @staticmethod
    def sh_d_pddf(doaod: TyDoAoD) -> TyDoPdDf:
        """
        Convert Dictionary of Array of Dictionaries to
        Dictionary of Pandas dataframes.
        """
        d_df: TyDoPdDf = {}
        for key, aod in doaod.items():
            df: TyPdDf = pd.DataFrame(aod)
            d_df[key] = df
        return d_df

    @staticmethod
    def sh_unique(doaod: TyDoAoD) -> TyDoAoD:
        """
        Convert Dictionary of Array of Dictionaries to
        Dictionary of array of unique dicionaries.
        """
        doaod_new: TyDoAoD = {}
        for key, aod in doaod.items():
            # doaod_new[key] = AoD.sh_unique(aod)
            doaod_new[key] = list(set(aod))
        return doaod_new

    @staticmethod
    def union_distinct_by_keys(doaod: TyDoAoD, keys: TyKeys) -> TyAoD:
        """
        Convert filtered Dictionary of Arrays of Dictionaries
        by keys to an Array of distinct Dictionaries
        """
        _aod_new: TyAoD = []
        for _aod in Dic.sh_values_by_keys(doaod, keys):
            _aod_new = _aod_new + [item for item in _aod if item not in _aod_new]
        return _aod_new

    @staticmethod
    def union_distinct(doaod: TyDoAoD) -> TyAoD:
        """
        Convert Dictionary of Arrays of Dictionaries to an
        Array of distinct Dictionaries
        """
        _aod_new: TyAoD = []
        for _aod in doaod.values():
            _aod_new = _aod_new + [item for item in _aod if item not in _aod_new]
        return _aod_new

    @staticmethod
    def union(doaod: TyDoAoD) -> TyAoD:
        """
        Convert Dictionary of Arrays of Dictionaries to an
        Array of Dictionaries
        """
        _aod_new: TyAoD = []
        for _aod in doaod.values():
            _aod_new = _aod_new + _aod
        return _aod_new
