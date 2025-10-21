from typing import Any, TypeAlias, IO, TYPE_CHECKING

import openpyxl as op

from ut_log.log import LogEq
from ut_obj.io import Io

from ut_xls.op.wb import Wb
from ut_xls.op.ws import Ws

if TYPE_CHECKING:
    from os import PathLike
    from _typeshed import SupportsRead
    TyOpPath = str | PathLike[str] | IO[bytes] | SupportsRead[bytes]
else:
    from os import PathLike
    TyOpPath = str | PathLike[str] | IO[bytes]

TyWb: TypeAlias = op.workbook.workbook.Workbook
TyWs: TypeAlias = op.worksheet.worksheet.Worksheet
TyOpWb: TypeAlias = op.Workbook

TyArr = list[Any]
TyDic = dict[Any, Any]
TyAoA = list[TyArr]
TyAoD = list[TyDic]
TyDoAoA = dict[Any, TyAoA]
TyDoAoD = dict[Any, TyAoD]
TyDoWs = dict[Any, TyWs]
TyAoD_DoAoD = TyAoD | TyDoAoD
TyPath = str
TyPathnm = str
TyStr = str

TySheet = int | str
TySheets = int | str | list[int | str]
TySheetname = str
TySheetnames = list[TySheetname]

TnArr = None | TyArr
TnAoA = None | TyAoA
TnAoD = None | TyAoD
TnAoD_DoAoD = None | TyAoD_DoAoD
TnDic = None | TyDic
TnDoAoA = None | TyDoAoA
TnDoAoD = None | TyDoAoD
TnDoWs = None | TyDoWs
TnPath = None | TyPath
TnSheet = None | TySheet
TnSheets = None | TySheets
TnSheetname = None | TySheetname
TnSheetnames = None | TySheetnames
TnWs = None | TyWs
# TnDf_DoDf = TnPdDf_DoPdDf | TnPlDf_DoPlDf
TnWb = None | TyWb
# TnOpWb = None | TyOpWb


class PathIoiWb:

    op_ioi = {'read_only': False}

    @classmethod
    def load(cls, io: TyOpPath, kwargs: Any) -> TyWb:
        if io == '':
            raise Exception('io is empty String')
        if io is None:
            raise Exception('io is None')
        try:
            op_ioi = kwargs.get('op_ioi', cls.op_ioi)
            wb: TyWb = op.load_workbook(io, **op_ioi)
        except Exception as e:
            msg = f"openpyxl.load_workbook for io = {io!r} throw exception {e}"
            raise Exception(msg)
        return wb

    @classmethod
    def read_wb_to_aod(
            cls, io: TyOpPath, kwargs: TyDic, sheet: TnSheet) -> TyAoD:
        Io.verify(io)
        _wb: TyWb = cls.load(io, kwargs)
        _aod: TyAoD = Wb.to_aod(_wb, sheet)
        return _aod

    @classmethod
    def read_wb_to_doaod(
            cls, io: TyOpPath, kwargs: TyDic, sheet: TnSheets) -> TyDoAoD:
        Io.verify(io)
        _wb: TyWb = cls.load(io, kwargs)
        _doaod: TyDoAoD = Wb.to_doaod(_wb, sheet)
        return _doaod

    @classmethod
    def read_wb_to_aod_or_doaod(
            cls, io: TyOpPath, kwargs: TyDic, sheet: TnSheets) -> TnAoD_DoAoD:
        Io.verify(io)
        _wb: TyWb = cls.load(io, kwargs)
        _aod_doaod: TnAoD_DoAoD = Wb.to_aod_or_doaod(_wb, sheet)
        return _aod_doaod

    @classmethod
    def read_wb_to_aoa(
            cls, io: TyOpPath, kwargs: TyDic, **kwargs_wb: Any) -> tuple[TyAoA, TyAoA]:
        Io.verify(io)
        wb: TyWb = cls.load(io, kwargs)
        heads_sheet_name = kwargs_wb.get('headers_sheet_name')
        ws_names: TySheetnames = Wb.sh_sheetnms(wb, **kwargs_wb)
        _aoa: TyAoA = []
        if heads_sheet_name is not None:
            ws = wb[heads_sheet_name]
            _heads: TyAoA = Ws.sh_headers(ws, **kwargs_wb)
        else:
            _heads = []
        for ws_name in ws_names:
            LogEq.debug("ws_name", ws_name)
            ws = wb[ws_name]
            _aoa_ws = Ws.sh_aoa(ws, sheet_name=ws_name, **kwargs_wb)
            _aoa.extend(_aoa_ws)
            LogEq.debug("_aoa_ws", _aoa_ws)
        return _heads, _aoa

    @classmethod
    def read_wb_to_aoa_by_prefix(cls, kwargs: TyDic) -> TyAoA:
        prefix = kwargs.get('prefix')
        if prefix is not None:
            prefix = f"_{prefix}"
        in_io: TyOpPath = kwargs.get(f'in_path{prefix}', '')
        row_start = kwargs.get(f'row_start{prefix}')
        cols_count = kwargs.get(f'cols_count{prefix}')
        sw_add_sheet_name = kwargs.get(f'sw_add_sheet_name{prefix}')
        sheet_names = kwargs.get(f'sheet_names{prefix}')
        headers_sheet_name = kwargs.get(f'headers_sheet_name{prefix}')
        headers_start = kwargs.get(f'headers_start{prefix}')

        Io.verify(in_io)

        heads, aoa = cls.read_wb_to_aoa(
                in_io,
                kwargs,
                row_start=row_start,
                cols_count=cols_count,
                sw_add_sheet_name=sw_add_sheet_name,
                sheet_names=sheet_names,
                headers_sheet_name=headers_sheet_name,
                headers_start=headers_start)
        return aoa

    @classmethod
    def sh_wb_adm(
            cls, path: TnPath, kwargs: TyDic, aod: TnAoD, sheet: TySheet
    ) -> TnWb:
        """
        Administration processsing for evup xlsx workbooks
        """
        if not path:
            return None
        _wb: TnWb = cls.load(path, kwargs)
        Wb.update_wb_with_aod(_wb, aod, sheet)
        return _wb

    @classmethod
    def sh_wb_del(
            cls, path: TnPath, kwargs: TyDic, aod: TnAoD, sheet: TySheet
    ) -> TnWb:
        """
        Delete processsing for evup xlsx workbooks
        """
        if not path:
            return None
        _wb: TnWb = cls.load(path, kwargs)
        Wb.update_wb_with_aod(_wb, aod, sheet)
        return _wb

    @classmethod
    def sh_wb_reg(
            cls, path: TnPath, kwargs: TyDic,
            aod_adm: TnAoD, aod_del: TnAoD,
            sheet_adm: TySheet, sheet_del: TySheet
    ) -> TnWb:
        """
        Delete processsing for evup xlsx workbooks
        """
        if not path:
            return None
        _wb: TnWb = cls.load(path, kwargs)
        Wb.update_wb_with_aod(_wb, aod_adm, sheet_adm)
        Wb.update_wb_with_aod(_wb, aod_del, sheet_del)
        return _wb
