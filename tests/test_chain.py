#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
=================================================
@Project -> File   ：infobase -> test_chain
@IDE    ：PyCharm
@Author ：Desmond.zhan
@Date   ：2023/11/14 17:33
@Desc   ：
==================================================
"""
from langchain.schema.runnable.utils import Output

from infobase.chain import get_translator_chain


def test_get_translator_chain():
    chain = get_translator_chain()
    output: Output = chain.invoke({"language": "English", "content": "测试语言翻译功能"})
    print(output)
