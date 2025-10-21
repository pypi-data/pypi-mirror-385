# coding=utf-8
import inspect

from typing import Any
TyArr = list[Any]
TyPointPath = str

TnPointPath = None | TyPointPath


class Fnc:

    @staticmethod
    def sh_qualname(fnc) -> TnPointPath:
        """
        show class name of function
        """
        if hasattr(fnc, '__qualname__'):
            _qualname: TnPointPath = fnc.__qualname__
        else:
            _qualname = None
        return _qualname

    @classmethod
    def sh_full_name(cls, fnc) -> TyPointPath:
        """
        show class name of function
        """
        _mod_name: TyPointPath = fnc.__module__
        _qualname: TnPointPath = cls.sh_qualname(fnc)
        _arr: TyArr = [_mod_name]
        if _qualname:
            _arr.append(_qualname)
        _fnc_name: TyPointPath = '.'.join(_arr)
        return _fnc_name
