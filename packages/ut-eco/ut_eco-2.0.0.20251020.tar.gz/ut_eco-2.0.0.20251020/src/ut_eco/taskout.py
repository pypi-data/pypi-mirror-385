"""
This module provides task scheduling classes for the management of OmniTracker
SRR (NHRR) processing for Department UMH.
    SRR: Sustainability Risk Rating
    NHRR: Nachhaltigkeits Risiko Rating
"""
import openpyxl as op

from ut_xls.op.pathkioowb import PathKIooWb as OpPathKIooWb
from ut_xls.pe.pathkioowb import PathKIooWb as PePathKIooWb

from ut_eco.cfg import Cfg
from ut_eco.taskin import TaskTmpIn

from typing import Any
TyOpWb = op.workbook.workbook.Workbook

TyArr = list[Any]
TyBool = bool
TyDic = dict[Any, Any]
TyAoA = list[TyArr]
TyAoD = list[TyDic]
TyDoAoA = dict[Any, TyAoA]
TyDoAoD = dict[Any, TyAoD]
TyCmd = str
TyPath = str
TyStr = str

TnAoD = None | TyAoD
TnDic = None | TyDic
TnOpWb = None | TyOpWb
TnPath = None | TyPath


class TaskOut:

    @classmethod
    def evupadm(cls, tup_adm: tuple[TnAoD, TyDoAoD], kwargs: TyDic) -> None:
        """
        Administration processsing for evup xlsx workbooks
        """
        _aod_evup_adm, _doaod_evin_adm_vfy = tup_adm
        _wb: TnOpWb = TaskTmpIn.evupadm(_aod_evup_adm, kwargs)
        OpPathKIooWb.write(Cfg.OutPathK.evup_adm, kwargs, _wb)
        PePathKIooWb.write_wb_from_doaod(
                Cfg.OutPathK.evin_adm_vfy, kwargs, _doaod_evin_adm_vfy)

    @classmethod
    def evupdel(cls, tup_del: tuple[TnAoD, TyDoAoD], kwargs: TyDic) -> None:
        """
        Delete processsing for evup xlsx workbooks
        """
        _aod_evup_del, _doaod_evin_del_vfy = tup_del
        _wb: TnOpWb = TaskTmpIn.evupdel(_aod_evup_del, kwargs)
        OpPathKIooWb.write(Cfg.OutPathK.evup_del, kwargs, _wb)
        PePathKIooWb.write_wb_from_doaod(
                Cfg.OutPathK.evin_del_vfy, kwargs, _doaod_evin_del_vfy)

    @classmethod
    def evupreg_reg_wb(
            cls, tup_adm_del: tuple[TnAoD, TyDoAoD, TnAoD, TyDoAoD], kwargs: TyDic
    ) -> None:
        """
        EcoVadus Upload Processing:
        Regular Processing (create, update, delete) of partners using
        one Xlsx Workbook with a populated admin- or delete-sheet
        """
        _aod_evup_adm: TnAoD
        _doaod_evin_adm_vfy: TyDoAoD
        _aod_evup_del: TnAoD
        _doaod_evin_del_vfy: TyDoAoD
        _aod_evup_adm, _doaod_evin_adm_vfy, _aod_evup_del, _doaod_evin_del_vfy = tup_adm_del
        _wb: TnOpWb = TaskTmpIn.evupreg(_aod_evup_adm, _aod_evup_del, kwargs)
        OpPathKIooWb.write(Cfg.OutPathK.evup_reg, kwargs, _wb)
        _doaod: TyDoAoD = _doaod_evin_adm_vfy | _doaod_evin_del_vfy
        PePathKIooWb.write_wb_from_doaod(Cfg.OutPathK.evin_reg_vfy, kwargs, _doaod)

    @classmethod
    def evupreg_adm_del_wb(
            cls, tup_adm_del: tuple[TnAoD, TyDoAoD, TnAoD, TyDoAoD], kwargs: TyDic
    ) -> None:
        """
        EcoVadus Upload Processing:
        Regular Processing (create, update, delete) of partners using
        two xlsx Workbooks:
          the first one contains a populated admin-sheet
          the second one contains a populated delete-sheet
        """
        _aod_evup_adm: TnAoD
        _doaod_evin_adm_vfy: TyDoAoD
        _aod_evup_del: TnAoD
        _doaod_evin_del_vfy: TyDoAoD
        _aod_evup_adm, _doaod_evin_adm_vfy, _aod_evup_del, _doaod_evin_del_vfy = tup_adm_del
        _wb: TnOpWb = TaskTmpIn.evupadm(_aod_evup_adm, kwargs)
        OpPathKIooWb.write(Cfg.OutPathK.evup_adm, kwargs, _wb)
        _wb = TaskTmpIn.evupdel(_aod_evup_del, kwargs)
        OpPathKIooWb.write(Cfg.OutPathK.evup_del, kwargs, _wb)
        _doaod: TyDoAoD = _doaod_evin_adm_vfy | _doaod_evin_del_vfy
        PePathKIooWb.write_wb_from_doaod(Cfg.OutPathK.evin_reg_vfy, kwargs, _doaod)

    @classmethod
    def evdomap(cls, aod_evex: TyAoD, kwargs: TyDic) -> None:
        """
        EcoVadus Download Processing: Mapping of EcoVadis export xlsx workbook
        """
        PePathKIooWb.write_wb_from_aod(
                Cfg.OutPathK.evex, kwargs, aod_evex, Cfg.sheet_exp)

    @classmethod
    def evdoexp(cls, tup_adm: tuple[TnAoD, TyDoAoD], kwargs: TyDic) -> None:
        """
        Administration processsing for evup xlsx workbooks
        """
        _aod_evup_adm, _doaod_evin_adm_vfy = tup_adm
        _wb: TnOpWb = TaskTmpIn.evupadm(_aod_evup_adm, kwargs)
        OpPathKIooWb.write(Cfg.OutPathK.evup_adm, kwargs, _wb)
        PePathKIooWb.write_wb_from_doaod(
                Cfg.OutPathK.evin_adm_vfy, kwargs, _doaod_evin_adm_vfy)
