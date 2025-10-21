import openpyxl as op

from ut_xls import dec
from ut_xls.op.pathioowb import PathIooWb

from typing import Any, TypeAlias

TyWb: TypeAlias = op.workbook.workbook.Workbook

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
    @dec.sh_static_path
    def write(pathk: TyPathK, kwargs: TyDic, wb: TnWb) -> None:
        PathIooWb.write(pathk, wb)

    @staticmethod
    @dec.sh_static_path
    def write_wb_from_doaod(pathk: TyPathK, kwargs: TyDic, doaod: TyDoAoD) -> None:
        if not doaod:
            return
        PathIooWb.write_wb_from_doaod(pathk, doaod)
