from typing import Any, TypeAlias

import pandas as pd

from ut_dic.dic import Dic
from ut_path.path import Path

TyPdDf: TypeAlias = pd.DataFrame

TyArr = list[Any]
TyDic = dict[Any, Any]
TyAoA = list[TyArr]
TyAoD = list[TyDic]
TyDoAoA = dict[Any, TyAoA]
TyDoAoD = dict[Any, TyAoD]
TyDoPdDf = dict[Any, TyPdDf]


class PathIooPdDf:

    pd_ioo = dict(engine='openpyxl')

    @classmethod
    def write_pd_from_dopdf(cls, path: str, kwargs: TyDic, dodf: TyDoPdDf) -> None:
        _a_key: TyArr = Dic.show_sorted_keys(dodf)
        if not _a_key:
            return
        Path.mkdir_from_path(path)
        _pd_ioo = kwargs.get('pd_ioo', cls.pd_ioo)
        writer = pd.ExcelWriter(path, **_pd_ioo)
        for _key in _a_key:
            _df: TyPdDf = dodf[_key]
            _df.to_excel(writer, sheet_name=_key)
        writer.close()
