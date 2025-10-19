# coding=utf-8
import inspect

from typing import Any
TyArr = list[Any]
TyMod = str
TyPac = str
TyPointPath = str
TyStr = str

TnPointPath = None | TyPointPath


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
        _fnc_name: TyPointPath = fnc.__name__
        if _module:
            _mod_name: TyPointPath = _module.__name__
            # Get the package name (if available)
            _pac_name: TnPointPath = _module.__package__
            if _pac_name:
                return '.'.join([_pac_name, _mod_name, _fnc_name])
            return '.'.join([_mod_name, _fnc_name])
        return f"{_fnc_name}"

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
        _arr = [_mod_name]
        if _qualname:
            _arr.append(_qualname)
        _fnc_name: TyPointPath = '.'.join(_arr)
        print("***************************")
        print(f"_mod_name = {_mod_name}")
        print(f"_qualname = {_qualname}")
        print(f"_fnc_name = {_fnc_name}")
        print("***************************")
        return _fnc_name
