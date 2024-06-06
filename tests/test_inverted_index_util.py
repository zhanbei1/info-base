#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
=================================================
@Project -> File   ：infobase -> test_inverted_index_util
@IDE    ：PyCharm
@Author ：Desmond.zhan
@Date   ：2023/11/22 14:19
@Desc   ：
==================================================
"""
import os.path
import pickle

from infobase.lexical_search import search_index
from infobase.model import BaseConfig
from infobase.utils.inverted_index_util import prepare_lexical_search_index


def test_prepare_lexical_search_index():
    index = None
    try:
        if os.path.exists("../data/lexical_inverted_index.pickle"):
            with open("../data/lexical_inverted_index.pickle", "rb") as f:
                index = pickle.load(f)
        else:
            file_list, snippets, index = prepare_lexical_search_index("/Users/zhanbei/IdeaProjects/EvalEx", BaseConfig(),
                                                                      "EvalEx")
        query = """
        I have an expression and I need to calculate results for a lot of cases of variables.

        For example,
        val expression = Expression("a + b")
        
        // thread 1
        thread {
          expression.with("a", 1)
          expression.with("b", 1)
        }
        
        // thread 2
        thread {
          expression.with("a", 2)
          expression.with("b", 2)
        }
        
        // ...
        
        // thread n
        thread {
          // ...
        }
        
        If I understand the implementation correctly, it will not work because Expression object is not safe to be used in multi threads.
        Could we make it thread-safe? Maybe Expression should allow to build immutable snapshots with a list of variables. The snapshots should reuse the expensive computation from Expression to evaluate the result.
        """
        result_snippets = search_index(query=query, index=index)
        for snippet in result_snippets:
            print(snippet)
    finally:
        with open("../data/lexical_inverted_index.pickle", "wb") as f:
            pickle.dump(index, f)
