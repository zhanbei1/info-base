#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
=================================================
@Project -> File   ：infobase -> file_utils
@IDE    ：PyCharm
@Author ：Desmond.zhan
@Date   ：2023/11/13 18:54
@Desc   ：
==================================================
"""


# 文件操作类
class FileUtils:
    @staticmethod
    def get_file_content(file_path: str, start_byte: int, end_byte: int) -> str:
        with open(file_path) as f:
            f.seek(start_byte)
            return f.read(end_byte - start_byte + 1)
