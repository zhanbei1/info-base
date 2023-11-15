#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
=================================================
@Project -> File   ：infobase -> boolean
@IDE    ：PyCharm
@Author ：Desmond.zhan
@Date   ：2023/11/13 16:24
@Desc   ：
==================================================
"""
import re

from langchain.schema import BaseOutputParser
from langchain.schema.output_parser import T


class BooleanOutputParser(BaseOutputParser[bool]):

    def parse(self, text: str) -> T:
        """
        Parse the text and return the boolean value.
        """
        affirmative_phrases = ["yes", "true", "ok"]
        affirmative_result = self._re_match(affirmative_phrases, text)
        if affirmative_result:
            return True
        return False

    def _re_match(self, patterns: list[str], text: str) -> bool:
        if patterns is not None and len(patterns) > 0:
            for pattern in patterns:
                # 大小写不敏感，全部为小些
                pattern = pattern.lower()
                text = text.lower()
                result = re.match(pattern, text)
                if result is not None:
                    return True
        return False

    def get_format_instructions(self) -> str:
        pass

    @property
    def _type(self) -> str:
        return "boolean_output_parser"
