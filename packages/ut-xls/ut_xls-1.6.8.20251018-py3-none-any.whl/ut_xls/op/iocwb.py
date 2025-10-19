import openpyxl as op

from typing import Any

TyWb = op.workbook.workbook.Workbook


class IocWb:

    @staticmethod
    def get(**kwargs: Any) -> TyWb:
        wb: TyWb = op.Workbook(**kwargs)
        return wb
