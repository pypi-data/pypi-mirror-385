# coding=utf-8
import datetime
import glob
import os
import pathlib
import pandas as pd
import re
from string import Template

from ut_aod.aod import AoD
from ut_dic.dic import Dic
from ut_pac.pac import Pac
from ut_path.aopath import AoPath
from ut_log.log import Log, LogEq
from ut_obj.str import Str

from collections.abc import Callable, Iterator
from typing import Any, TypedDict


class TyDoDataType(TypedDict):
    start: int
    add: int


class TyDoRunDatetime(TypedDict):
    start: int


class TyDoInPathIx(TypedDict):
    data_type: TyDoDataType
    rundatetime: TyDoRunDatetime


class TyDoOutPathEdit(TypedDict):
    from_: str
    to_: str


TyAny = Any
TyObj = Any
TyAoS = list[str]
TyArr = list[Any]
TyAoA = list[TyArr]
TyBasename = str
TyCallable = Callable[..., Any]
TyDic = dict[Any, Any]
TyAoD = list[TyDic]
TyDoA = dict[Any, TyArr]
TyDoAoA = dict[Any, TyAoA]
TyDoD = dict[Any, TyDic]
TyDoS = dict[Any, str]
TyDoInt = dict[str, int]
TyDoDoInt = dict[str, TyDoInt]
TyFnc = Callable[..., Any]
TyIntStr = int | str
TyIoS = Iterator[str]
TyPath = str
TyPathLike = os.PathLike
TyAoPath = list[str]
TyTup = tuple[Any, ...]
TyIterAny = Iterator[Any]
TyIterPath = Iterator[TyPath]
TyIterTup = Iterator[TyTup]
TyStr = str
TyToS = tuple[str, ...]

TnAny = None | TyAny
TnArr = None | TyArr
TnAoA = None | TyAoA
TnAoPath = None | TyAoPath
TnBool = None | bool
TnDic = None | TyDic
TnFnc = None | TyFnc
TnInt = None | int
TnPath = None | TyPath
TnStr = None | str
TnTup = None | TyTup

TnDoDataType = None | TyDoDataType
TnDoRunDatetime = None | TyDoRunDatetime
TnDoInPathIx = None | TyDoInPathIx


class Path:

    @staticmethod
    def count(path_pattern: TnPath) -> None | int:
        """
        count number of paths that match path pattern
        """
        if not path_pattern:
            return None
        return len(list(glob.iglob(path_pattern)))

    @staticmethod
    def ex_get_aod_by_fnc(
            path: TnPath, fnc: TyFnc, kwargs: TyDic) -> TyAoD:
        _aod: TyAoD = []
        if not path:
            return _aod
        _mode = kwargs.get('mode', 'r')
        with open(path, _mode) as _fd:
            for _line in _fd:
                _dic = Str.sh_dic(_line)
                _obj = fnc(_dic, kwargs)
                AoD.add(_aod, _obj)
        return _aod

    @staticmethod
    def ex_get_aod(path: TnPath, kwargs: TyDic) -> TyAoD:
        _aod: TyAoD = []
        if not path:
            return _aod
        _mode = kwargs.get('mode', 'r')
        with open(path, _mode) as _fd:
            for _line in _fd:
                _dic = Str.sh_dic(_line)
                AoD.add(_aod, _dic)
        return _aod

    @staticmethod
    def ex_get_dod_by_fnc(
            path: TnPath, fnc: TyFnc, key: str, kwargs: TyDic) -> TyDoD:
        """
        Create a dictionary of dictionaries by executing the following steps:
        1. read every line of the json file <path> into a dictionary
        2. If the function <obj_fnc> is not None:
             transform the dictionary by the function <obj_fnc>
             get value of the transformed dictionary for the key <key>
           else
             get value of the dictionary for the key <key>
        2. if the value is not None:
             insert the transformed dictionary into the new dictionary
             of dictionaries with the value as key.
        """
        _dod: TyDoD = {}
        if not path:
            return _dod
        _mode = kwargs.get('mode', 'r')
        with open(path, _mode) as _fd:
            for _line in _fd:
                _obj = Str.sh_dic(_line)
                _obj = fnc(_obj, kwargs)
                if _obj is not None:
                    _key = _obj.get(key)
                    if _key is not None:
                        _dod[_key] = _obj
        return _dod

    @staticmethod
    def ex_get_dod(
            path: TnPath, key: str, kwargs: TyDic) -> TyDoD:
        """
        Create a dictionary of dictionaries by executing the following steps:
        1. read every line of the json file <path> into a dictionary
        2. If the function <obj_fnc> is not None:
             transform the dictionary by the function <obj_fnc>
             get value of the transformed dictionary for the key <key>
           else
             get value of the dictionary for the key <key>
        2. if the value is not None:
             insert the transformed dictionary into the new dictionary
             of dictionaries with the value as key.
        """
        _dod: TyDoD = {}
        if not path:
            return _dod
        _mode = kwargs.get('mode', 'r')
        with open(path, _mode) as _fd:
            for _line in _fd:
                _obj = Str.sh_dic(_line)
                if _obj is not None:
                    _key = _obj.get(key)
                    _key = _obj[key]
                    if _key is not None:
                        _dod[_key] = _obj
        return _dod

    @classmethod
    def get_aod(cls, path: TnPath, fnc: TnFnc, kwargs: TyDic) -> TyAoD:
        # Timer.start(cls.get_aod, f"{path}")
        if fnc is not None:
            _aod = cls.ex_get_aod_by_fnc(path, fnc, kwargs)
        else:
            _aod = cls.ex_get_aod(path, kwargs)
        # Timer.end(cls.get_aod, f"{path}")
        return _aod

    @classmethod
    def get_first_dic(cls, path: TnPath, fnc: TnFnc, kwargs: TyDic) -> TyDic:
        # def get_dic(cls, path: TyPath, fnc: TnFnc, kwargs: TyDic) -> TyDic:
        aod = cls.get_aod(path, fnc, kwargs)
        if len(aod) > 1:
            msg = (f"File {path} contains {len(aod)} records; "
                   "it should contain only one record")
            raise Exception(msg)
        return aod[0]

    @classmethod
    def get_dod(
            cls, path: TnPath, fnc: TnFnc, key: str, kwargs: TyDic) -> TyDoD:
        """
        Create a dictionary of dictionaries by executing the following steps:
        1. read every line of the json file <path> into a dictionary
        2. If the function <obj_fnc> is not None:
             transform the dictionary by the function <obj_fnc>
             get value of the transformed dictionary for the key <key>
           else
             get value of the dictionary for the key <key>
        2. if the value is not None:
             insert the transformed dictionary into the new dictionary
             of dictionaries with the value as key.
        """
        if fnc is not None:
            _dod = cls.ex_get_dod_by_fnc(path, fnc, key, kwargs)
        else:
            _dod = cls.ex_get_dod(path, key, kwargs)
        return _dod

    @staticmethod
    def get_latest(path_pattern: TnPath) -> TnPath:
        """
        get latest path that match path pattern
        """
        if not path_pattern:
            return None
        _iter_path = glob.iglob(path_pattern)
        _a_path = list(_iter_path)
        if len(_a_path) <= 0:
            msg = f"No path exist for pattern: {path_pattern}"
            Log.error(msg)
            return None
        return max(_a_path, key=os.path.getmtime)

    @staticmethod
    def get_paths(
            path_pattern: TnPath, sw_recursive: TnBool = None) -> TyIoS:
        """
        get all paths that match path_pattern
        """
        if not path_pattern:
            return
        if sw_recursive is None:
            sw_recursive = False
        _paths: Iterator[str] = glob.iglob(path_pattern, recursive=sw_recursive)
        LogEq.debug("path_pattern", path_pattern)
        LogEq.debug("_paths", _paths)
        for _path in _paths:
            if os.path.isfile(_path):
                LogEq.debug("_path", _path)
                yield _path

    @staticmethod
    def io(obj: TyObj, path: TnPath, fnc: TyFnc) -> None:
        """
        execute io function
        """
        fnc(obj, path)

    @staticmethod
    def verify(path: TnPath) -> None:
        if path is None:
            raise Exception("path is None")
        elif path == '':
            raise Exception("path is empty")

    @classmethod
    def edit_path(cls, path: TnPath, kwargs: TyDic) -> TnPath:
        if not path:
            return path
        _d_edit: TyDoOutPathEdit = kwargs.get('d_out_path_edit', {})
        _prefix = kwargs.get('dl_out_file_prefix', '')
        _suffix = kwargs.get('dl_out_file_suffix', '.csv')
        _edit_from = _d_edit.get('from_')
        _edit_to = _d_edit.get('to_')
        if _edit_from is not None and _edit_to is not None:
            _path_out = path.replace(_edit_from, _edit_to)
        else:
            _path_out = path
        _dir_out = os.path.dirname(_path_out)
        cls.mkdir_from_path(_dir_out)
        _basename_out = os.path.basename(_path_out)
        if _prefix:
            _basename_out = str(f"{_prefix}{_basename_out}")
        if _suffix:
            _basename_out = os.path.splitext(_basename_out)[0]
            _basename_out = str(f"{_basename_out}{_suffix}")
        _path_out = os.path.join(_dir_out, _basename_out)
        return _path_out

    @staticmethod
    def mkdir(path: TnPath) -> None:
        if not path:
            return
        if not os.path.exists(path):
            # Create the directory
            os.makedirs(path)

    @staticmethod
    def mkdir_from_path(path: TnPath) -> None:
        if not path:
            return
        _dir = os.path.dirname(path)
        if not os.path.exists(_dir):
            # Create the directory
            os.makedirs(_dir)

    @staticmethod
    def sh_aopath(path: TnPath) -> TyAoPath:
        if not path:
            raise Exception("Argument 'path' is empty")
        return glob.glob(path)

    @classmethod
    def sh_aopath_mtime_gt_threshold(
            cls, path: TyPath, mtime_threshhold: float) -> TnAoPath:
        _aopath: TyAoPath = cls.sh_aopath(path)
        _aopath = AoPath.sh_aopath_mtime_gt_threshold(
                _aopath, mtime_threshhold)
        return _aopath

    @staticmethod
    def sh_basename(path: TnPath) -> None | TyBasename:
        """
        Extracts basename of a given path.
        Should Work with any OS Path on any OS
        """
        if not path:
            return path
        raw_string = r'[^\\/]+(?=[\\/]?$)'
        basename = re.search(raw_string, path)
        if basename:
            return basename.group(0)
        return path

    @classmethod
    def sh_components(
            cls, path: TnPath, d_ix: TyDoDataType, separator: str = "-") -> TnPath:
        if not path:
            return path
        ix_start = d_ix.get("start")
        ix_add = d_ix.get("add", 0)
        if not ix_start:
            return None
        _a_dir: TyArr = cls.split_to_array(path)
        _ix_end = ix_start + ix_add + 1
        _component = separator.join(_a_dir[ix_start:_ix_end])
        _a_component = os.path.splitext(_component)
        return _a_component[0]

    @classmethod
    def sh_component_by_rundatetime(
        # def sh_component_at_start(
            cls, path: TnPath, d_in_path_ix: TyDoInPathIx) -> TnPath:
        if not path:
            return path
        # _d_ix: TyDoInt = d_path_ix.get(field_name, {})
        _d_ix: TnDoRunDatetime = d_in_path_ix.get('rundatetime')
        if not _d_ix:
            msg = (f"field_name: 'rundatetime' is not defined "
                   f"in dictionary: {d_in_path_ix}")
            raise Exception(msg)
        _start = _d_ix.get('start')
        if not _start:
            msg = f"'start' is not defined in dictionary: {_d_ix}"
            raise Exception(msg)
        _a_dir: TyAoS = cls.split_to_array(path)
        if _start < len(_a_dir):
            return _a_dir[_start]
        msg = f"index: {_start} is out of range of list: {_a_dir}"
        raise Exception(msg)

    @classmethod
    def sh_data_type(cls, path: TnPath, kwargs: TyDic) -> TnPath:
        if not path:
            return path
        _d_in_path_ix: TnDoInPathIx = kwargs.get("d_in_path_ix", {})
        if _d_in_path_ix is None:
            return None
        _d_data_type_ix: TnDoDataType = _d_in_path_ix.get("data_type")
        if _d_data_type_ix is None:
            return None
        return cls.sh_components(path, _d_data_type_ix)

    @classmethod
    def sh_rundatetime_ms(cls, dl_in_dir: TnPath, kwargs: TyDic) -> None | pd.Timestamp:
        if not dl_in_dir:
            return None
        _d_in_path_ix: TyDoInPathIx = kwargs.get("d_in_path_ix", {})
        _rundatetime_iso8601: TnPath = cls.sh_component_by_rundatetime(
                dl_in_dir, _d_in_path_ix)
        if not _rundatetime_iso8601:
            return None
        _rundatetime_iso8601 = _rundatetime_iso8601.replace("_", ".")
        _rundatetime_ms: pd.Timestamp = pd.to_datetime(
                _rundatetime_iso8601, utc=True, format='ISO8601')
        LogEq.debug("_rundatetime_ms", _rundatetime_ms)
        return _rundatetime_ms

    @staticmethod
    def sh_fnc_name_by_pathlib(path: TnPath) -> TnPath:
        if not path:
            return path
        # def sh_fnc_name(path: TyPath) -> str:
        _purepath = pathlib.PurePath(path)
        dir_: str = _purepath.parent.name
        stem_: str = _purepath.stem
        return f"{dir_}-{stem_}"

    @staticmethod
    def sh_fnc_name_by_os_path(path: TnPath) -> TnPath:
        if not path:
            return path
        # def sh_os_fnc_name(path: TyPath) -> str:
        split_ = os.path.split(path)
        dir_ = os.path.basename(split_[0])
        stem_ = os.path.splitext(split_[1])[0]
        return f"{dir_}-{stem_}"

    @classmethod
    def sh_last_part(cls, path: TnPath) -> TnPath:
        if not path:
            return path
        # def sh_last_component(cls, path: TyPath) -> TyPath:
        a_dir: TyArr = cls.split_to_array(path)
        _path: TyPath = a_dir[-1]
        return _path

    @staticmethod
    def sh_path_by_d_path(path: TnPath, kwargs: TyDic) -> TnPath:
        if not path:
            return path
        _d_path = kwargs.get('d_path', {})
        if not _d_path:
            return path
        return Template(path).safe_substitute(_d_path)

    @staticmethod
    def sh_path_by_pac(path: TyPath) -> TyPath:
        # Define the regex pattern
        _pattern = r"pac_fpath\(\'([a-zA-Z0-9_]+)\'\)"
        # Use re.search to find the first match
        match = re.search(_pattern, path)
        if match:
            Log.debug(f"match with _pattern = {_pattern} succesfull")
            # Extract the full matched string
            _group0: TnStr = match.group(0)
            if not _group0:
                _msg = (f"Group 0 of matched path={path} with "
                        f"pattern={_pattern} is undefined or empty")
                raise Exception(_msg)
            # Extract the package name (first match group)
            _pac: TnStr = match.group(1)
            if not _pac:
                _msg = (f"Group 1 of matched path={path} with "
                        f"pattern={_pattern} is undefined or empty")
                raise Exception(_msg)
            LogEq.debug("_pac", _pac)
            _path: TnPath = Pac.sh_path((_pac))
            if not _path:
                _msg = f"Package={_pac} is unknown"
                raise Exception(_msg)
            _path = path.replace(_group0, path)
            LogEq.debug("_path", _path)
            return _path
        return path

    @classmethod
    def sh_path_by_var_pac(
            cls, path: TnPath, kwargs: TyDic) -> TyPath:
        _path: TyPath = cls.sh_path_by_var(path, kwargs)
        _path = cls.sh_path_by_pac(_path)
        return _path

    @staticmethod
    def sh_path_by_var(path: TnPath, kwargs: TyDic) -> TyPath:
        """
        Apply template function to replace variables in path and show result
        """
        if not path:
            raise Exception("The parameter 'path' is udefined or empty")
        # Extract variables starting with '$'
        _a_key = re.findall(r'\$(\w+)', path)
        if not _a_key:
            return path
        LogEq.debug("_a_key", _a_key)
        _dic = {}
        for _key in _a_key:
            _val = Dic.locate_key(kwargs, _key)
            _dic[_key] = _val
        LogEq.debug("_dic", _dic)
        if not _dic:
            return path
        LogEq.debug("path", path)
        _template = Template(path)
        return _template.safe_substitute(**_dic)

    @classmethod
    def sh_path_by_var_pac_sep(
            cls, path: TnPath, kwargs: TyDic, sep: str = "|") -> TyPath:
        _path: TyPath = cls.sh_path_by_var_pac(path, kwargs)
        _aopath: TyAoPath = _path.split(sep)
        _path = AoPath.sh_path_by_first_exists(_aopath)
        return _path

    @classmethod
    def sh_path_by_var_sep(
            cls, path: TnPath, kwargs: TyDic, sep: str = "|") -> TyPath:
        _path: TyPath = cls.sh_path_by_var(path, kwargs)
        _aopath: TyAoPath = _path.split(sep)
        _path = AoPath.sh_path_by_first_exists(_aopath)
        return _path

    @classmethod
    def sh_path_by_var_and_d_pathk2type(
           cls,  path: TnPath, pathk: str, kwargs: TyDic) -> TnPath:
        LogEq.debug("path", path)
        _path: TnPath = cls.sh_path_by_var(path, kwargs)
        LogEq.debug("_path", _path)
        return cls.sh_path_by_d_pathk2type(_path, pathk, kwargs)

    @classmethod
    def sh_path_by_d_pathk2type(
            cls, path: TnPath, pathk: str, kwargs: TyDic) -> TnPath:
        LogEq.debug("pathk", pathk)
        _d_pathk2type: TyDoS = kwargs.get('d_pathk2type', {})
        LogEq.debug("_d_pathk2type", _d_pathk2type)
        if not _d_pathk2type:
            return path
        _type: TnStr = _d_pathk2type.get(pathk)
        if _type is None:
            return path
        return cls.sh_path_by_type(path, _type, kwargs)

    @classmethod
    def sh_path_by_type(
            cls, path: TnPath, _type: TyStr, kwargs: TyDic) -> TnPath:
        if not path:
            return path
        LogEq.debug("path", path)
        LogEq.debug("_type", _type)
        match _type:
            case 'last':
                path_new: TnPath = cls.sh_path_last(path)
            case 'first':
                path_new = cls.sh_path_first(path)
            case 'now':
                path_new = cls.sh_path_now(path, **kwargs)
            case _:
                path_new = cls.sh_path_first(path)
        LogEq.debug("path_new", path_new)
        return path_new

    @classmethod
    def sh_path(cls, path: TnPath) -> TyPath:
        return cls.sh_path_first(path)

    @classmethod
    def sh_path_first(cls, path: TnPath) -> TyPath:
        _a_path: TyAoPath = cls.sh_aopath(path)
        if not _a_path:
            msg = f"glob.glob find no paths for template: {path}"
            raise Exception(msg)
        _path: TyPath = sorted(_a_path)[0]
        return _path

    @classmethod
    def sh_path_last(cls, path: TnPath) -> TyPath:
        _a_path: TyAoPath = cls.sh_aopath(path)
        if not _a_path:
            msg = f"glob.glob find no paths for template: {path}"
            raise Exception(msg)
        _path: TyPath = sorted(_a_path)[-1]
        return _path

    @staticmethod
    def sh_path_now(path: TnPath, **kwargs) -> TyPath:
        if not path:
            raise Exception("Argument 'path' is empty")
        now_var = kwargs.get('now_var', 'now')
        now_fmt = kwargs.get('now_fmt', '%Y%m%d')
        _current_date: str = datetime.datetime.now().strftime(now_fmt)
        _dic = {now_var: _current_date}
        return Template(path).safe_substitute(_dic)

    @staticmethod
    def split_to_array(path: TyPath) -> TyArr:
        """
        Convert path to normalized pyth
        Should Work with any OS Path on any OS
        """
        _normalized_path = os.path.normpath(path)
        return _normalized_path.split(os.sep)
