# coding=utf-8

from ut_dic.dic import Dic
from ut_obj.str import Str
from ut_obj.strdate import StrDate

from typing import Any

TyArr = list[Any]
TyDic = dict[Any, Any]
TyTup = tuple[Any, Any]
TyStr = str

TnDic = None | TyDic
TnStr = None | TyStr


class DoEq:
    """ Manage Commandline Arguments
    """

    @classmethod
    def verify_value(cls, key, value, value_type) -> None:
        match value_type[0]:
            case '{', '[':
                _range = Str.sh_dic(value_type)
                if value not in _range:
                    _msg = (f"Value={value} of Parameter={key} "
                            f"is invalid; valid values are={_range}")
                    raise Exception(_msg)

    @classmethod
    def verify_key_value(cls, key, value, d_parms: TyDic) -> TyTup:
        _value_type: TnStr = d_parms.get(key)
        if _value_type is None:
            msg = f"Wrong parameter: {key}; valid parameters are: {d_parms}"
            raise Exception(msg)
        match _value_type:
            case 'str':
                _value = value
            case 'int':
                _value = int(value)
            case 'bool':
                _value = Str.sh_boolean(value)
            case 'dict':
                value = Str.sh_dic(value)
            case 'list':
                _value = Str.sh_arr(value)
            case '%Y-%m-%d':
                _value = StrDate.sh(value, _value_type)
            case '_':
                _value = value
                cls.verify_value(key, _value, _value_type)
        return key, _value

    @classmethod
    def verify(cls, d_eq: TyDic, d_parms: TnDic) -> TyDic:
        if not d_parms:
            return d_eq
        _cmd = d_eq.get('cmd', [])
        _d_parms = Dic.locate(d_parms, _cmd)
        _d_eq_new = {}
        for _k, _v in d_eq.items():
            _k, _v = cls.verify_key_value(_k, _v, _d_parms)
            _d_eq_new[_k] = _v
        return _d_eq_new
