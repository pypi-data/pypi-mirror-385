from typing import Any

from ut_log.log import LogEq
from ut_path.path import Path

TyDic = dict[Any, Any]
TyPath = str
TyPathK = str

TnDic = None | TyDic
TnPath = None | TyPath


class PathK:

    @staticmethod
    def sh_path(pathk: TyPathK, kwargs: TyDic) -> TyPath:
        _path: TnPath = kwargs.get(pathk)
        LogEq.debug("_path", _path)
        _path_new: TnPath = Path.sh_path_by_var_and_d_pathk2type(
                _path, pathk, kwargs)
        if not _path_new:
            msg = (f"Path for _path={_path}, pathk={pathk} "
                   f"and kwargs={kwargs} is undefined")
            raise Exception(msg)
        LogEq.debug("_path_new", _path_new)
        return _path_new
