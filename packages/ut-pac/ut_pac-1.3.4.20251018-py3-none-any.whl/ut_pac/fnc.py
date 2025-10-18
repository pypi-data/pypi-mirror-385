# coding=utf-8
import inspect

from typing import Any
TyArr = list[Any]
TyMod = str
TyPac = str
TyPointPath = str
TyPacName = str
TyModName = str
TyClsName = str
TyFncName = str
TyStr = str

TnClsName = None | TyClsName
TnPacName = None | TyPacName


class Fnc:

    @staticmethod
    def xsh_full_name(fnc) -> TyPointPath:
        """
        show full qualified name of object
        """
        # _class = fnc.__class__
        # _module: TyPointPath = _class.__module__
        # _qualname: TyPointPath = _class.__qualname__
        #  Avoid prefixing built-in types
        # if _module == "builtins":
        #     return _qualname
        # return f"{_module}.{_qualname}"

        # Get the module where the function is defined
        _module = inspect.getmodule(fnc)
        # Get the function name
        _fnc_name: TyFncName = fnc.__name__
        if _module:
            _mod_name: TyModName = _module.__name__
            # Get the package name (if available)
            _pac_name: TnPacName = _module.__package__
            return f"{_pac_name}.{_mod_name}.{_fnc_name}"
        return f"{_fnc_name}"

    @staticmethod
    def sh_cls_name(fnc) -> TnClsName:
        """
        show class name of function
        """
        if hasattr(fnc, '__qualname__'):
            _a_pac = fnc.__qualname__.split('.')
            _cls_name: TnClsName = '.'.join(_a_pac[-1])
        else:
            _cls_name = None
        return _cls_name

    @classmethod
    def sh_full_name(cls, fnc) -> TyFncName:
        """
        show class name of function
        """
        _mod_name = fnc.__module
        _cls_name = cls.sh_cls_name(fnc)
        _fnc_name = f"{_mod_name}.{_cls_name}"
        return _fnc_name
