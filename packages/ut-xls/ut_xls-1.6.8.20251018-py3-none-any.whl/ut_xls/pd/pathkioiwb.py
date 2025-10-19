import pandas as pd

from ut_path.pathk import PathK
from ut_xls.pd.pathioiwb import PathIoiWb

from typing import Any, TypeAlias

TyPdDf: TypeAlias = pd.DataFrame

TyArr = list[Any]
TyDic = dict[Any, Any]
TyAoA = list[TyArr]
TyAoD = list[TyDic]
TyDoAoD = dict[Any, TyAoD]
TyDoPdDf = dict[str, TyPdDf] | dict[Any, TyPdDf]
TyAoD_DoAoD = TyAoD | TyDoAoD
TyPdDf_DoPdDf = TyPdDf | dict[str, TyPdDf] | dict[Any, TyPdDf]
TyPath = str
TyPathK = str

TySheet = int | str
TySheets = int | str | list[int | str]
TySheetname = str
TySheetnames = list[TySheetname]

TnAoD = None | TyAoD
TnAoD_DoAoD = None | TyAoD_DoAoD
TnDoAoD = None | TyDoAoD
TnPdDf = None | TyPdDf
TnPdDf_DoPdDf = None | TyPdDf_DoPdDf
TnDoPdDf = None | TyDoPdDf
TnSheet = None | TySheet
TnSheets = None | TySheets
TnSheetname = None | TySheetname
TnSheetnames = None | TySheetnames


class PathKIoiWb:

    @staticmethod
    def read_wb_to_aod(
            pathk: TyPathK, kwargs: TyDic, sheet: TnSheet) -> TnAoD:
        _path: TyPath = PathK.sh_path(pathk, kwargs)
        _aod: TnAoD = PathIoiWb.read_wb_to_aod(_path, kwargs, sheet)
        return _aod

    @staticmethod
    def read_wb_to_doaod(
            pathk: TyPathK, kwargs: TyDic, sheet: TnSheet) -> TnDoAoD:
        _path: TyPath = PathK.sh_path(pathk, kwargs)
        _doaod: TnDoAoD = PathIoiWb.read_wb_to_doaod(_path, kwargs, sheet)
        return _doaod

    @staticmethod
    def read_wb_to_aod_or_doaod(
            pathk: TyPathK, kwargs: TyDic, sheet: TnSheet) -> TnAoD_DoAoD:
        _path: TyPath = PathK.sh_path(pathk, kwargs)
        _obj: TnAoD_DoAoD = PathIoiWb.read_wb_to_aod_or_doaod(
                _path, kwargs, sheet)
        return _obj

    @staticmethod
    def read_wb_to_df(
            pathk: TyPathK, kwargs: TyDic, sheet: TnSheet) -> TnPdDf:
        _path: TyPath = PathK.sh_path(pathk, kwargs)
        _pddf: TnPdDf = PathIoiWb.read_wb_to_df(_path, kwargs, sheet)
        return _pddf

    @staticmethod
    def read_wb_to_dodf(
            pathk: TyPathK, kwargs: TyDic, sheet: TnSheet) -> TnDoPdDf:
        _path: TyPath = PathK.sh_path(pathk, kwargs)
        _dopddf: TnDoPdDf = PathIoiWb.read_wb_to_dodf(_path, kwargs, sheet)
        return _dopddf

    @staticmethod
    def read_wb_to_df_or_dodf(
            pathk: TyPathK, kwargs: TyDic, sheet: TnSheet) -> TnPdDf_DoPdDf:
        _path: TyPath = PathK.sh_path(pathk, kwargs)
        _obj: TnPdDf_DoPdDf = PathIoiWb.read_wb_to_df_or_dodf(_path, kwargs, sheet)
        return _obj
