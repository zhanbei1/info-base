#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
=================================================
@Project -> File   ：infobase -> enums
@IDE    ：PyCharm
@Author ：Desmond.zhan
@Date   ：2023/11/22 17:51
@Desc   ：
==================================================
"""
from enum import Enum

from infobase.model import SupportLanguageParser


class PathType(Enum):
    FILE = "file"
    DIR = "dir"
    FUNCTION = "function"
    CLASS = "class"


# 支持的语言和文件识别的后缀
class CodeLanguageEnum(Enum):
    JAVA = SupportLanguageParser("java")
    PYTHON = SupportLanguageParser("python")
