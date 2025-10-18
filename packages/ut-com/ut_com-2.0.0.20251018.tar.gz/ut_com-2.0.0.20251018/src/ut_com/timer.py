# coding=utf-8
from datetime import datetime

from ut_com.com import Com
from ut_log.log import Log
from ut_pac.fnc import Fnc

from typing import Any
TyAny = Any
TyArr = list[Any]
TyDic = dict[Any, Any]
TyStr = str
TnAny = None | TyAny
TnStr = None | TyStr


class Timestamp:

    @staticmethod
    def sh_elapse_time_sec(end: Any, start: TnAny) -> TnAny:
        if start is None:
            return None
        return end.timestamp()-start.timestamp()


class Timer:
    """ Timer Management
    """
    @staticmethod
    def sh_args_str(*args) -> TyStr:
        """
        Show class name, the item class_name is the class_id if its a string,
        otherwise the attribute __qualname__ is used.
        """
        if not args:
            return ""
        else:
            return f"{args}"

    @staticmethod
    def sh_kwargs_str(**kwargs) -> TyStr:
        """
        Show class name, the item class_name is the class_id if its a string,
        otherwise the attribute __qualname__ is used.
        """
        if not kwargs:
            return ""
        else:
            return f"{kwargs}"

    @classmethod
    def sh_task_id(cls, fnc, *args, **kwargs) -> TyStr:
        """
        Show task id, which is created by the concationation of the following items:
        package, module, class_name and parms if they are defined; the items package
        and module are get from the package-module directory; the item class_name is
        the class_id if its a string, otherwise the attribute __qualname__ is used.
        """
        _full_name = Fnc.sh_full_name(fnc)
        _args = cls.sh_args_str(*args)
        _kwargs = cls.sh_kwargs_str(**kwargs)
        _sep = kwargs.get('sep', '.')
        _task_id: TyStr = _sep.join([_full_name, _args, _kwargs])
        return _task_id

    @classmethod
    def start(cls, fnc: TyAny, *args, **kwargs) -> None:
        """
        Start Timer
        """
        task_id = cls.sh_task_id(fnc, *args, **kwargs)
        Com.d_timer[task_id] = datetime.now()

    @classmethod
    def end(cls, fnc: TyAny, *args, **kwargs) -> None:
        """
        End Timer
        """
        task_id = cls.sh_task_id(fnc, *args, **kwargs)
        start = Com.d_timer.get(task_id)
        end = datetime.now()
        elapse_time_sec = Timestamp.sh_elapse_time_sec(end, start)
        msg = f"{task_id} elapse time [sec] = {elapse_time_sec}"
        Log.info(msg, stacklevel=2)
