from typing import Any, TypeAlias

import pyexcelerate as pe

from ut_path.pathk import PathK
from ut_xls.pe.pathioowb import PathIooWb

TyWb: TypeAlias = pe.Workbook

TyArr = list[Any]
TyDic = dict[Any, Any]
TyAoA = list[TyArr]
TyAoD = list[TyDic]
TyDoAoA = dict[Any, TyAoA]
TyDoAoD = dict[Any, TyAoD]
TyPath = str
TyPathK = str
TySheet = int | str

TnPath = None | TyPath
TnWb = None | TyWb


class PathKIooWb:

    @staticmethod
    def write(
            pathk: TyPathK, kwargs: TyDic, wb: TnWb) -> None:
        if wb is None:
            return
        _path: TnPath = PathK.sh_path(pathk, kwargs)
        if not _path:
            return
        wb.save(_path)

    @staticmethod
    def write_wb_from_doaoa(
            pathk: TyPathK, kwargs: TyDic, doaoa: TyDoAoA) -> None:
        if not doaoa:
            return
        _path: TnPath = PathK.sh_path(pathk, kwargs)
        PathIooWb.write_wb_from_doaoa(_path, kwargs, doaoa)

    @staticmethod
    def write_wb_from_doaod(
            pathk: TyPathK, kwargs: TyDic, doaod: TyDoAoD) -> None:
        if not doaod:
            return
        _path: TnPath = PathK.sh_path(pathk, kwargs)
        PathIooWb.write_wb_from_doaod(_path, kwargs, doaod)

    @staticmethod
    def write_wb_from_aod(
            pathk: TyPathK, kwargs: TyDic, aod: TyAoD, sheet: TySheet
    ) -> None:
        if not aod:
            return
        _path: TnPath = PathK.sh_path(pathk, kwargs)
        PathIooWb.write_wb_from_aod(_path, aod, sheet)
