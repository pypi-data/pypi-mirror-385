import openpyxl as op
import pandas as pd

from ut_path.path import Path

from ut_xls.op.pathioiwb import PathIoiWb
from ut_xls.op.wb import Wb

from typing import Any, TypeAlias

TyWb: TypeAlias = op.workbook.workbook.Workbook
TyPdDf: TypeAlias = pd.DataFrame

TyDic = dict[Any, Any]
TyDoPdDf = dict[Any, TyPdDf]
TyPath = str
TnWb = None | TyWb


class PathIouWb:

    @staticmethod
    def update_wb_with_dodf(
            path: TyPath, kwargs: TyDic, dodf: TyDoPdDf) -> None:
        _wb: TyWb = PathIoiWb.load(path, kwargs)
        _wb_new: TnWb = Wb.update_wb_with_dodf(_wb, dodf, **kwargs)
        if _wb_new is None:
            return
        Path.mkdir_from_path(path)
        _wb_new.save(path)
