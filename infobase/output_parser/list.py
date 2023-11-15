#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
=================================================
@Project -> File   ：infobase -> list
@IDE    ：PyCharm
@Author ：Desmond.zhan
@Date   ：2023/11/13 17:15
@Desc   ：
==================================================
"""
import re
from typing import List, Callable

from langchain.output_parsers import ListOutputParser


class CommonListOutputParser(ListOutputParser):

    def get_format_instructions(self) -> str:
        return (
            "Your response should be a list of comma separated values, "
            "eg: `foo\n bar\n baz`"
        )

    def parse(self, text: str) -> List[str]:
        split_patter = "\n"
        result_list: list = text.split(split_patter)
        result_list = [re.sub(r"^\d\.", "", result).strip() for result in result_list]
        return list(set(result_list))
