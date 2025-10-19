from typing import Any, TypeAlias

import pyexcelerate as pe

from ut_xls.pe.iocwb import IocWb

TyWb: TypeAlias = pe.Workbook

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


class DoAoA:

    @staticmethod
    def create_wb(doaoa: TyDoAoA) -> TyWb:
        wb: TyWb = IocWb.get()
        if not doaoa:
            return wb
        for sheet, aoa in doaoa.items():
            if not aoa:
                continue
            wb.new_sheet(sheet, data=aoa)
        return wb


class DoAoD:

    @staticmethod
    def create_wb(doaod: TyDoAoD) -> TyWb:
        # if not doaod:
        #    raise Exception('doaod is empty')
        wb: TyWb = IocWb.get()
        if not doaod:
            return wb
        for sheet, aod in doaod.items():
            if not aod:
                continue
            a_header = [list(aod[0].keys())]
            a_data = [list(d.values()) for d in aod]
            a_row = a_header + a_data
            wb.new_sheet(sheet, data=a_row)
        return wb


class PathIooWb:

    @staticmethod
    def write(path: TnPath, wb: TnWb) -> None:
        if not path:
            return
        if wb is not None:
            wb.save(path)

    @staticmethod
    def write_wb_from_doaoa(path: TnPath, kwargs: TyDic, doaoa: TyDoAoA) -> None:
        # def write_xls_wb_from_doaoa(doaoa: TyDoAoA, path: str) -> None:
        if not path:
            return
        if not doaoa:
            return
        wb: TyWb = DoAoA.create_wb(doaoa)
        wb.save(path)

    @staticmethod
    def write_wb_from_doaod(path: TnPath, kwargs: TyDic, doaod: TyDoAoD) -> None:
        if not path:
            return
        if not doaod:
            return
        wb: TyWb = DoAoD.create_wb(doaod)
        wb.save(path)

    @staticmethod
    def write_wb_from_aod(
            path: TnPath, aod: TyAoD, sheet: TySheet) -> None:
        if not path:
            return
        if not aod:
            return
        wb: TyWb = IocWb.get()
        a_header: TyArr = [list(aod[0].keys())]
        a_data: TyArr = [list(d.values()) for d in aod]
        a_row: TyArr = a_header + a_data
        wb.new_sheet(sheet, data=a_row)
        wb.save(path)
