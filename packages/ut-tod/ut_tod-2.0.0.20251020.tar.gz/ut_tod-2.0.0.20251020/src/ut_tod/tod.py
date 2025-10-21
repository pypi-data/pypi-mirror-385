# import builtins
from collections.abc import Iterator
from typing import Any

from ut_log.log import Log

TyAny = Any
TyArr = list[Any]
TyDic = dict[Any, Any]
TyAoD = list[TyDic]
TyDoA = dict[Any, TyArr]
TyDoAoD = dict[Any, TyAoD]
TyIterAny = Iterator[Any]
TyKey = Any
TyKeys = Any | TyArr
TyStr = str
TyToD = tuple[TyDic, ...]
TyToDD = tuple[TyDic, TyDic]

TnAny = None | Any
TnAoD = None | TyAoD
TnArr = None | TyArr
TnDic = None | TyDic
TnDoA = None | TyDoA
TnKey = None | TyKey
TnKeys = None | TyKeys


class ToD:
    """
    Management of Tuple of dictionaries
    """
    @staticmethod
    def copy(
            dic_target: TnDic, dic_source: TnDic, keys: TnKeys = None) -> None:
        """
        copy values for keys from source to target dictionary
        """
        # Dictionary is None or empty
        if not dic_target:
            return
        if not dic_source:
            return
        if keys is None:
            keys = list(dic_source.keys())
        for key in keys:
            dic_target[key] = dic_source[key]

    @staticmethod
    def change_filter_keys_by_dic(
            dic: TyDic, keydic: TyDic) -> TyDic:
        # def change_keys_with_keyfilter(
        """
        Change the keys of the dictionary by the values of the keyfilter
        Dictionary with the same keys.
        """
        _dic: TyDic = {}
        for _key, _value in dic.items():
            _key_new = keydic.get(_key)
            if _key_new is not None:
                _dic[_key_new] = _value
        return _dic

    @staticmethod
    def change_keys_by_dic(
            dic: TyDic, keydic: TyDic) -> TyDic:
        # def change_keys_with_keyfilter(
        """
        Change the keys of the dictionary by the values of the keyfilter
        Dictionary with the same keys.
        """
        _dic: TyDic = {}
        for _key, _value in dic.items():
            _key_new = keydic.get(_key)
            if _key_new is None:
                _dic[_key] = _value
            else:
                _dic[_key_new] = _value
        return _dic

    @staticmethod
    def new_d_index_d_values(dic: TyDic, d_pivot: TyDic) -> TyToDD:
        # def sh_d_index_d_values(dic: TyDic, d_pivot: TyDic) -> TyToDD:
        """
        Create index and value dictionary from dictionary and pivot dictionary.
        """
        a_index: TyArr = d_pivot.get('index', [])
        a_values: TyArr = d_pivot.get('values', [])
        d_index: TyDic = {}
        d_values: TyDic = {}
        if len(a_values) == 1:
            for key, value in dic.items():
                Log.debug(f"len(a_values) == 1 key = {key}")
                Log.debug(f"len(a_values) == 1 value = {value}")
                if key in a_index:
                    d_index[key] = value
                else:
                    key0 = key
                    key1 = a_values[0]
                    Log.debug(f"len(a_values) == 1 key not in a_index key0 = {key0}")
                    Log.debug(f"len(a_values) == 1 key not in a_index key1 = {key1}")
                    if key0 not in d_values:
                        d_values[key0] = {}
                    d_values[key0][key1] = value
        else:
            for key, value in dic.items():
                if key in a_index:
                    d_index[key] = value
                else:
                    a_key = key.split("_")
                    key1 = a_key[0]
                    key0 = a_key[1]
                    if key0 in a_values:
                        if key0 not in d_values:
                            d_values[key0] = {}
                        d_values[key0][key1] = value
                    else:
                        Log.error(f"ERROR key0 = {key0} no in a_values = {a_values}")
            Log.debug(f"len(a_values) != 1 d_values = {d_values}")
        return d_index, d_values

    @classmethod
    def set_first_tgt_with_src_by_d_src2tgt(
            cls, dic_tgt: TyDic, dic_src: TyDic, d_src2tgt: TyDic):
        """
        Replace value of first dictionary target key found in the source to
        target dictionary by the source value found in the dictionary.
        """
        for key_src, key_tgt in d_src2tgt.items():
            value_src = dic_src.get(key_src)
            if value_src:
                dic_tgt[key_tgt] = value_src
                break

    @classmethod
    def set_first_tgt_with_src_by_d_tgt2src(
            cls, dic_tgt: TyDic, dic_src: TyDic, d_tgt2src: TyDic):
        """
        Replace value of first dictionary target key found in the target to
        source dictionary by the source value found in the dictionary.
        """
        for key_tgt, key_src in d_tgt2src.items():
            value_src = dic_src.get(key_src)
            if value_src:
                dic_tgt[key_tgt] = value_src
                break

    @classmethod
    def set_tgt_with_src(
            cls, dic_tgt: TyDic, dic_src: TyDic) -> None:
        """
        Replace source dictionary values by target dictionary values.
        """
        for key_src in dic_src.keys():
            dic_tgt[key_src] = dic_src.get(key_src)

    @classmethod
    def set_tgt_with_src_by_doaod_tgt2src(
            cls, dic_tgt: TyDic, dic_src: TyDic, d_aotgt2src: TyDoAoD):
        """
        Loop through the target to source dictionaries of the values of the
        dictionary of the arrays of target to source dictionaries until the
        return value of the function "set_nonempty_tgt_with_src_by_d_tgt2src"
        is defined.
        """
        for aotgt2src in d_aotgt2src.values():
            for tgt2src in aotgt2src:
                sw_none = cls.set_nonempty_tgt_with_src_by_d_tgt2src(
                       dic_tgt, dic_src, tgt2src)
                if not sw_none:
                    return

    @classmethod
    def set_nonempty_tgt_with_src_by_d_tgt2src(
            cls, dic_tgt: TyDic, dic_src: TyDic, d_tgt2src: TyDoAoD) -> bool:
        """
        Execute the function "set_tgt_with_src_by_d_tgt2src" if all
        dictionary values for the keys provided by the values of the
        target to source dictionary are defined.
        """
        if any(dic_src.get(_key_src) is None for _key_src in d_tgt2src.values()):
            return True
        cls.set_tgt_with_src_by_d_tgt2src(dic_tgt, dic_src, d_tgt2src)
        return False

    @staticmethod
    def set_tgt_with_src_by_d_src2tgt(
            dic_tgt: TyDic, dic_src: TyDic, d_src2tgt: TyDic):
        for key_src, key_tgt in d_src2tgt.items():
            dic_tgt[key_tgt] = dic_src.get(key_src)

    @staticmethod
    def set_tgt_with_src_by_d_tgt2src(
            dic_tgt: TyDic, dic_src: TyDic, d_tgt2src: TyDic):
        for key_tgt, key_src in d_tgt2src.items():
            dic_tgt[key_tgt] = dic_src.get(key_src)

    @staticmethod
    def yield_values_with_keyfilter(dic: TyDic, keyfilter: TyDic) -> TyIterAny:
        for key, value in dic.items():
            if key in keyfilter:
                yield value

    @staticmethod
    def union(dic0: TnDic, dic1: TnDic) -> TnDic:
        if dic0 is None:
            return dic1
        if dic1 is None:
            return dic0
        return dic0 | dic1

    merge = union

    @classmethod
    def merge_nested(cls, dic1: TyDic, dic2: TyDic) -> TyDic:
        _dic: TyDic = {
                _key: (
                    cls.merge_nested(dic1[_key], dic2[_key])
                    if isinstance(dic1.get(_key), dict) and isinstance(dic2.get(_key), dict)
                    else dic2.get(_key, dic1.get(_key))
                )
                for _key in dic1.keys() | dic2.keys()
        }
        return _dic
