import polars as pl
from pathlib import Path

from ut_dic.dopldf import DoPlDf
from ut_dfr.pldf import PlDf
from ut_obj.io import Io

from collections.abc import Sequence, Iterator
from typing import Any, Literal, TypeGuard, IO

TyPlDf = pl.DataFrame

TyArr = list[Any]
TyDic = dict[Any, Any]
TyAoA = list[TyArr]
TyAoD = list[TyDic]
TyDoAoA = dict[Any, TyAoA]
TyDoAoD = dict[Any, TyAoD]
TyDoPlDf = dict[str, TyPlDf] | dict[Any, TyPlDf]
TyAoD_DoAoD = TyAoD | TyDoAoD
TyPath = str
TyPathnm = str

TyPlDf_DoPlDf = TyPlDf | TyDoPlDf
TyPlFileSrc = str | Path | IO[bytes] | bytes
TyPlFileArr = list[str] | list[Path] | list[IO[bytes]] | list[bytes]
TyPlFileSrcArr = TyPlFileSrc | TyPlFileArr
TyPlSheetsId = int | Sequence[int] | Literal[0]
TyPlSheetsNm = str | list[str] | tuple[str]
TyPlSheets = TyPlSheetsId | TyPlSheetsNm

TnArr = None | TyArr
TnAoA = None | TyAoA
TnAoD = None | TyAoD
TnAoD_DoAoD = None | TyAoD_DoAoD
TnDic = None | TyDic
TnDoAoA = None | TyDoAoA
TnDoAoD = None | TyDoAoD

TnDoPlDf = None | TyDoPlDf
TnPlDf = None | TyPlDf
TnPlDf_DoPlDf = None | TyPlDf_DoPlDf
TnPlSheetsId = None | TyPlSheetsId
TnPlSheetsNm = None | TyPlSheetsNm
TnPlSheets = None | TyPlSheets


class PathIoiWb:

    @staticmethod
    def is_str_list(val: Iterator) -> TypeGuard[list[str]]:
        '''Determines whether all objects in the list are strings'''
        return all(isinstance(x, str) for x in val)

    @staticmethod
    def is_int_list(val: Iterator) -> TypeGuard[list[int]]:
        '''Determines whether all objects in the list are integers'''
        return all(isinstance(x, int) for x in val)

    @classmethod
    def read_wb_to_aod(
            cls, io: TyPlFileSrcArr, kwargs: TyDic, sheet: TnPlSheets) -> TnAoD:
        _aod: TnAoD = PlDf.to_aod(cls.read_wb_to_df(io, kwargs, sheet))
        return _aod

    @classmethod
    def read_wb_to_aod_or_doaod(
            cls, io: TyPlFileSrcArr, kwargs: TyDic, sheet: TnPlSheets) -> TnAoD_DoAoD:
        _obj: TnPlDf_DoPlDf = cls.read_wb_to_df_or_dodf(io, kwargs, sheet)
        if isinstance(_obj, dict):
            _doaod: TnDoAoD = DoPlDf.to_doaod(_obj)
            return _doaod
        _aod: TnAoD = PlDf.to_aod(_obj)
        return _aod

    @classmethod
    def read_wb_to_doaod(
            cls, io: TyPlFileSrcArr, kwargs: TyDic, sheet: TnPlSheets) -> TnDoAoD:
        _obj: TnDoPlDf = cls.read_wb_to_dodf(io, kwargs, sheet)
        _doaod: TnDoAoD = DoPlDf.to_doaod(_obj)
        return _doaod

    @classmethod
    def read_wb_to_df(
            cls, io: TyPlFileSrcArr, kwargs: TyDic, sheet: TnPlSheets) -> TnPlDf:
        Io.verify(io)
        if isinstance(sheet, str):
            _obj: TnPlDf = pl.read_excel(
                    io, sheet_id=None, sheet_name=sheet, **kwargs)
        elif isinstance(sheet, int):
            if sheet == 0:
                raise Exception(f"sheet; {sheet} should not be 0")
            _obj = pl.read_excel(io, sheet_id=sheet, **kwargs)
        else:
            raise Exception(f"sheet; {sheet} is invalid")
        cls.verify_obj(io, _obj, sheet)
        return _obj

    @classmethod
    def read_wb_to_df_or_dodf(
            cls, io: TyPlFileSrcArr, kwargs: TyDic, sheet: TnPlSheets) -> TnPlDf_DoPlDf:
        Io.verify(io)
        if isinstance(sheet, str):
            _obj: TnPlDf_DoPlDf = pl.read_excel(
                    io, sheet_id=None, sheet_name=sheet, **kwargs)
        elif isinstance(sheet, int):
            _obj = pl.read_excel(io, sheet_id=sheet, **kwargs)
        elif isinstance(sheet, Iterator):
            _obj = cls.sh_obj_for_iterator(io, sheet, kwargs)
        else:
            raise Exception(f"sheet; {sheet} is invalid")
        cls.verify_obj(io, _obj, sheet)
        return _obj

    @classmethod
    def read_wb_to_dodf(
            cls, io: TyPlFileSrcArr, kwargs: TyDic, sheet: TnPlSheets) -> TnDoPlDf:
        Io.verify(io)
        if isinstance(sheet, str):
            _obj: TnPlDf_DoPlDf = pl.read_excel(
                    io, sheet_id=None, sheet_name=[sheet], **kwargs)
        elif isinstance(sheet, int):
            if sheet == 0:
                _obj = pl.read_excel(io, sheet_id=0, **kwargs)
            else:
                _obj = pl.read_excel(io, sheet_id=[sheet], **kwargs)
        elif isinstance(sheet, Iterator):
            _obj = cls.sh_obj_for_iterator(io, sheet, kwargs)
        else:
            raise Exception(f"sheet; {sheet} is invalid")
        cls.verify_obj(io, _obj, sheet)
        if not isinstance(_obj, dict):
            raise Exception(f"Object: {_obj} should be of type dict")
        return _obj

    @classmethod
    def sh_obj_for_iterator(
            cls, io: TyPlFileSrcArr, kwargs: TyDic, sheet: Iterator) -> TnPlDf_DoPlDf:
        if cls.is_int_list(sheet):
            return pl.read_excel(io, sheet_id=sheet, **kwargs)
        elif cls.is_str_list(sheet):
            return pl.read_excel(io, sheet_id=None, sheet_name=sheet, **kwargs)
        else:
            msg = f"sheet; {sheet} is is not of Type list[int] or list[str]"
            raise Exception(msg)

    @staticmethod
    def verify_obj(io: TyPlFileSrcArr, obj: TnPlDf_DoPlDf, sheet: TnPlSheets) -> None:
        if obj is not None:
            return
        if sheet is None:
            msg = f"Excel Workbook {io!r} contains no sheets"
        else:
            msg = f"Sheets {sheet} are not contained in Excel Workbook {io!r}"
        raise Exception(msg)
