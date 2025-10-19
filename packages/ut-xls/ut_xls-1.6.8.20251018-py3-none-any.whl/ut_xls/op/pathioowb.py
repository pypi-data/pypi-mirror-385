from openpyxl import Workbook

from ut_xls.op.wb import DoAoD

from typing import Any, TypeAlias

TyWb: TypeAlias = Workbook

TyArr = list[Any]
TyDic = dict[Any, Any]
TyAoA = list[TyArr]
TyAoD = list[TyDic]
TyDoAoA = dict[Any, TyAoA]
TyDoAoD = dict[Any, TyAoD]
TyPath = str
TyPathnm = str
TySheet = int | str

TnPath = None | TyPath
TnWb = None | TyWb


class PathIooWb:

    @staticmethod
    def write(path: TnPath, wb: TnWb) -> None:
        if wb is None or not path:
            return
        wb.save(path)

    @classmethod
    def write_wb_from_doaod(cls, path: TnPath, doaod: TyDoAoD) -> None:
        if not doaod or not path:
            return
        _wb: TyWb = DoAoD.create_wb(doaod)
        cls.write(path, _wb)
