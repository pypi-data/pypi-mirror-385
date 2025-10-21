from os import PathLike
import openpyxl as op

from ut_obj.io import Io

from ut_xls.op.pathioiwb import PathIoiWb
from ut_xls.op.wb import Wb
from ut_xls.op.ws import Ws

from typing import Any, TypeAlias, IO, TYPE_CHECKING

if TYPE_CHECKING:
    from _typeshed import SupportsRead
    TyOpFileSrc = str | PathLike[str] | IO[bytes] | SupportsRead[bytes]
else:
    TyOpFileSrc = str | PathLike[str] | IO[bytes]

TyWb: TypeAlias = op.workbook.workbook.Workbook
TyWs: TypeAlias = op.worksheet.worksheet.Worksheet

TyArr = list[Any]
TyDic = dict[Any, Any]
TyAoA = list[TyArr]
TyAoD = list[TyDic]
TyDoAoA = dict[Any, TyAoA]
TyDoAoD = dict[Any, TyAoD]
TyDoWs = dict[Any, TyWs]
TyAoD_DoAoD = TyAoD | TyDoAoD
# TyOpFileSrc = str | bytes | Path | TextIO | BinaryIO
TyPath = str
TyPathnm = str

TySheet = int | str
TySheets = int | str | list[int | str]
TySheetnm = str
TySheetnms = list[TySheetnm]

TnArr = None | TyArr
TnAoA = None | TyAoA
TnAoD = None | TyAoD
TnAoD_DoAoD = None | TyAoD_DoAoD
TnDic = None | TyDic
TnDoAoA = None | TyDoAoA
TnDoAoD = None | TyDoAoD
TnDoWs = None | TyDoWs
TnSheet = None | TySheet
TnSheets = None | TySheets
TnSheetnm = None | TySheetnm
TnSheetnms = None | TySheetnms
TnWs = None | TyWs


class PathIoiWs:

    @staticmethod
    def read_ws_to_dic(
            io: TyOpFileSrc, kwargs: TyDic, sheet: TySheet) -> TnDic:
        _wb: TyWb = PathIoiWb.load(io, kwargs)
        _ws: TnWs = Wb.sh_sheet(_wb, sheet)
        _dic: TyDic = Ws.to_dic(_ws)
        return _dic

    @staticmethod
    def read_ws_to_aod(
            io: TyOpFileSrc, kwargs: TyDic, sheet: TySheet) -> TnAoD:
        _wb: TyWb = PathIoiWb.load(io, kwargs)
        _ws: TnWs = Wb.sh_sheet(_wb, sheet)
        _aod: TyAoD = Ws.to_aod(_ws)
        return _aod

    @staticmethod
    def read_ws_filter_rows(io: TyOpFileSrc, kwargs: TyDic, sheet: TySheet) -> TnArr:
        Io.verify(io)
        _wb: TyWb = PathIoiWb.load(io, kwargs)
        _arr: TnArr = Ws.filter_rows(Wb.sh_sheet(_wb, sheet))
        return _arr

    @staticmethod
    def read_ws_to_aoa(
            io: TyOpFileSrc, kwargs: TyDic, sheet: TnSheets
    ) -> tuple[TnAoA, TnSheetnms]:
        Io.verify(io)
        _wb: TyWb = PathIoiWb.load(io, kwargs)
        aoa: TyAoA = []
        if not sheet:
            return aoa, None
        _sheetnms: TnSheetnms = Wb.sh_sheetnms(_wb, sheet)
        if not _sheetnms:
            return aoa, _sheetnms
        for _sheetnm in _sheetnms:
            _ws: TnWs = Wb.sh_worksheet(_wb, _sheetnm)
            if _ws is not None:
                values: TyArr = Ws.to_row_values(_ws)
                aoa.append(values)
        return aoa, _sheetnms

    @staticmethod
    def read_sheetnames(io: TyOpFileSrc, kwargs: TyDic) -> TyArr:
        Io.verify(io)
        wb: TyWb = PathIoiWb.load(io, kwargs)
        sheetnms: TySheetnms = wb.sheetnames
        return sheetnms

    @staticmethod
    def read_ws_to_doaoa(
            io: TyOpFileSrc, kwargs: TyDic, sheet: TnSheets
    ) -> tuple[TnDoAoA, TnSheetnms]:
        Io.verify(io)
        _wb: TyWb = PathIoiWb.load(io, kwargs)
        doaoa: TyDoAoA = {}
        if _wb is None:
            return doaoa, None
        sheetnms: TnSheetnms = Wb.sh_sheetnms(_wb, sheet)
        if not sheetnms:
            return doaoa, sheetnms
        for _sheetnm in sheetnms:
            _ws: TnWs = Wb.sh_worksheet(_wb, _sheetnm)
            if _ws is not None:
                values: TyArr = Ws.to_row_values(_ws)
                doaoa[sheet] = values
        return doaoa, sheetnms

    @staticmethod
    def read_ws_to_dowsop(
            io: TyOpFileSrc, kwargs: TyDic, sheet: TnSheets
    ) -> tuple[TnDoWs, TnSheetnms]:
        Io.verify(io)
        _wb: TyWb = PathIoiWb.load(io, kwargs)
        dows: TyDoWs = {}
        if _wb is None:
            return dows, None
        sheetnms: TnSheetnms = Wb.sh_sheetnms(_wb, sheet)
        if not sheetnms:
            return dows, sheetnms
        for _sheetnm in sheetnms:
            _ws: TnWs = Wb.sh_worksheet(_wb, _sheetnm)
            if _ws is not None:
                dows[_sheetnm] = _ws
        return dows, sheetnms
