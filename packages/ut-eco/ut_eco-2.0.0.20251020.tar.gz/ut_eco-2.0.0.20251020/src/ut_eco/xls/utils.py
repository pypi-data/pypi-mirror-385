"""
This module provides utilities classes for the management of Sustainability Risk Rating (SRR) processing.
"""
from __future__ import annotations
from typing import Any, TypeAlias, TextIO, BinaryIO

import pandas as pd
from pathlib import Path

from ut_xls.pd.pathkioiwb import PathKIoiWb as PdPathKIoiWb
from ut_eco.cfg import Cfg

TyPdDf: TypeAlias = pd.DataFrame
TyXls: TypeAlias = pd.ExcelFile

TyArr = list[Any]
TyBool = bool
TyDic = dict[Any, Any]
TyAoD = list[TyDic]
TyPdFileSrc = str | bytes | TyXls | Path | TextIO | BinaryIO
TySheet = int | str

TnDic = None | TyDic
TnAoD = None | TyAoD
TnPdDf = None | TyPdDf
TnSheet = None | TySheet


class EvexIoc:
    """
    EcoVadis Export class
    """
    @classmethod
    def read_wb_exp_to_df(cls, kwargs: TyDic) -> TnPdDf:
        _pddf: TnPdDf = PdPathKIoiWb.read_wb_to_df(Cfg.InPathK.evex, kwargs, Cfg.sheet_exp)
        return _pddf

    @classmethod
    def read_wb_exp_to_aod(cls, kwargs: TyDic) -> TnAoD:
        _aod: TnAoD = PdPathKIoiWb.read_wb_to_aod(Cfg.InPathK.evex, kwargs, Cfg.sheet_exp)
        return _aod
