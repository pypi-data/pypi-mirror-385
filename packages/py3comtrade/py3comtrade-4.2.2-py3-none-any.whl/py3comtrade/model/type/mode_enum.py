#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  Copyright (c) [2019] [name of copyright holder]
#  [py3comtrade] is licensed under Mulan PSL v2.
#  You can use this software according to the terms and conditions of the Mulan
#  PSL v2.
#  You may obtain a copy of Mulan PSL v2 at:
#           http://license.coscl.org.cn/MulanPSL2
#  THIS SOFTWARE IS PROVIDED ON CFGAN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY
#  KIND, EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
#  NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
#  See the Mulan PSL v2 for more details.
from enum import Enum

from py3comtrade.model.type.base_enum import BaseEnum


class ReadMode(Enum):
    FULL = (0, "comtrade所有文件")
    CFG = (1, "仅读取cfg文件")
    DAT = (2, "读取cfg和dat文件")
    DMF = (3, "读取cfg和dmf文件")


class SampleMode(BaseEnum):
    CENTERED = ("CENTERED", "以当前点为中心，前后各取数据。")  # 表示以当前点为中心，前后各取数据。
    FORWARD = ("FORWARD", "表示从起点向后取数据。")
    BACKWARD = ("BACKWARD", "表示从终点向前取数据。")
