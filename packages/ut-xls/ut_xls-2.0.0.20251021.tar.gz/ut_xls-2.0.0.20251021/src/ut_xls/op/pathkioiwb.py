import openpyxl as op

from ut_xls import dec
from ut_xls.op.pathioiwb import PathIoiWb

from typing import Any

TyWb = op.workbook.workbook.Workbook
TyWs = op.worksheet.worksheet.Worksheet

TyArr = list[Any]
TyDic = dict[Any, Any]
TyAoA = list[TyArr]
TyAoD = list[TyDic]
TyDoAoD = dict[Any, TyAoD]
TyDoWs = dict[Any, TyWs]
TyAoD_DoAoD = TyAoD | TyDoAoD
TyPath = str
TyPathK = str
TyStr = str
TyTo2AoA = tuple[TyAoA, TyAoA]

TySheet = int | str
TySheets = TySheet | list[int | str]

TnAoD = None | TyAoD
TnAoD_DoAoD = None | TyAoD_DoAoD
TnDoAoD = None | TyDoAoD
TnSheet = None | TySheet
TnSheets = None | TySheets
TnWb = None | TyWb
TnWs = None | TyWs
TnPath = None | TyPath


class PathKIoiWb:

    @staticmethod
    @dec.sh_static_path
    def load(pathk: TyPathK, kwargs: TyDic) -> TyWb:
        """
        Read Excel workbooks
        """
        _wb: TyWb = PathIoiWb.load(pathk, kwargs)
        return _wb

    @classmethod
    @dec.sh_class_path
    def read_wb_to_aod(
            cls, pathk: TyPathK, kwargs: TyDic, sheet: TnSheet) -> TyAoD:
        """
        Read Excel workbooks into Array of Dictionaries
        """
        _obj: TyAoD = PathIoiWb.read_wb_to_aod(pathk, kwargs, sheet)
        return _obj

    @classmethod
    @dec.sh_class_path
    def read_wb_to_doaod(
            cls, pathk: TyPathK, kwargs: TyDic, sheets: TnSheets) -> TyDoAoD:
        """
        Read Excel workbooks into Dictionary of Array of Dictionaries
        """
        _obj: TyDoAoD = PathIoiWb.read_wb_to_doaod(pathk, kwargs, sheets)
        return _obj

    @classmethod
    @dec.sh_class_path
    def read_wb_to_aod_or_doaod(
            cls, pathk: TyPathK, kwargs: TyDic, sheets: TnSheets
    ) -> TnAoD_DoAoD:
        """
        Read Excel workbooks into Array od Dictionaries or
        Dictionary of Array of Dictionaries
        """
        _obj: TnAoD_DoAoD = PathIoiWb.read_wb_to_aod_or_doaod(pathk, kwargs, sheets)
        return _obj

    @classmethod
    @dec.sh_class_path
    def read_wb_to_aoa(
            cls, pathk: TyPathK, kwargs: TyDic) -> TyTo2AoA:
        """
        Read Excel workbooks into Array of Arrays
        """
        _to2aoa: TyTo2AoA = PathIoiWb.read_wb_to_aoa(pathk, kwargs)
        return _to2aoa

    @classmethod
    @dec.sh_class_path
    def sh_wb_adm(
            cls, pathk: TyPathK, kwargs: TyDic, aod: TnAoD, sheet: TySheet
    ) -> TnWb:
        """
        Administration processsing for Excel workbooks
        """
        _wb: TnWb = PathIoiWb.sh_wb_adm(pathk, kwargs, aod, sheet)
        return _wb

    @classmethod
    @dec.sh_class_path
    def sh_wb_del(
            cls, pathk: TyPathK, kwargs: TyDic, aod: TnAoD, sheet: TySheet
    ) -> TnWb:
        """
        Delete processsing for Excel workbooks
        """
        _wb: TnWb = PathIoiWb.sh_wb_del(pathk, kwargs, aod, sheet)
        return _wb

    @classmethod
    @dec.sh_class_path
    def sh_wb_reg(
            cls, pathk: TyPathK, kwargs: TyDic,
            aod_adm: TnAoD, aod_del: TnAoD,
            sheet_adm: TySheet, sheet_del: TySheet
    ) -> TnWb:
        """
        Regular processsing for Excel workbooks
        """
        _wb: TnWb = PathIoiWb.sh_wb_reg(
                pathk, kwargs, aod_adm, aod_del, sheet_adm, sheet_del)
        return _wb
