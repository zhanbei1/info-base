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
from langchain.chat_models import ChatOpenAI
from langchain.schema.runnable import Runnable, RunnableLambda, RunnablePassthrough
from langchain.schema.runnable.utils import Output

from infobase.chain import get_translator_chain, get_chain
from infobase.llm_chat.llm_model import LLMModel


def test_get_translator_chain():
    chain = get_translator_chain()
    output: Output = chain.invoke({"language": "English", "content": "测试语言翻译功能"})
    print(output)


# coding=utf-8
from unittest import mock
from pytest import mark, fixture


@mark.parametrize("request_body,expected_result", [
    ({"query": "hi"}, "None or blank query， please input a query"),
    ({"query": "hi", "output_language": "English"}, "None or blank query， please input a query"),
    ({"query": "hi", "collection_name": ""}, "None or blank query， please input a query"),
    ({"query": "hi", "collection_name": "test"}, "None or blank query， please input a query"),
    ({"query": "hi", "collection_name": "test", "output_language": "English"},
     "None or blank query， please input a query"),
    ({"query": "hi", "collection_name": "test", "output_language": "English", "input": "hi"}, "hi"),
    ({"query": "hi", "collection_name": "test", "output_language": "English", "input": ""},
     "None or blank query， please input a query"),
])
def test_get_chain(request_body, expected_result):
    with mock.patch('infobase.chain.get_chain.get_translator_chain',
                    return_value=mock.MagicMock()) as translator_chain_mock:
        with mock.patch('infobase.chain.get_chain.common_ai_chat_chain',
                        return_value=mock.MagicMock()) as common_chat_chain_mock:
            with mock.patch('infobase.chain.get_chain.get_chat_chain',
                            return_value=mock.MagicMock()) as get_chat_chain_mock:
                with mock.patch('infobase.chain.get_chain.RunnableLambda',
                                return_value=mock.MagicMock()) as RunnableLambda_mock:
                    with mock.patch('infobase.chain.get_chain.RunnablePassthrough',
                                    return_value=mock.MagicMock()) as RunnablePassthrough_mock:
                        result = get_chain(request_body)  # 执行函数，根据参数生成对应的返回结果
                        assert result == expected_result  # 断言返回结果与预期结果一致
                        # 验证各个mock函数是否被正确调用
                        translator_chain_mock.assert_called()
                        common_chat_chain_mock.assert_called()
                        get_chat_chain_mock.assert_called()
                        RunnableLambda_mock.assert_called()
                        RunnablePassthrough_mock.assert_called()


def test_chain() -> Runnable:
    """
    自动生成单元测试chain
    """
    llm_model: ChatOpenAI = LLMModel.get_model()
    result = llm_model.predict("""
    Understand the following code content and generate detailed unit testing content for functions based on the main dimensions of unit testing (black box testing, logic branch testing, boundary condition testing, equivalence testing, exception testing, etc.).
    The path where this function is located is: infobase.chain.get_chain
    Input code:
    ```python
    def get_chain(request_body: dict) -> str:
        if request_body.get("query") is None or request_body.get("query") == "":
            return "None or blank query， please input a query"
        translator_chain = (
                {"language": RunnableLambda(lambda x: request_body.get("output_language")),
                 "content": RunnablePassthrough()}
                | get_translator_chain()
        )
        translator_english_chain = (
                {"language": RunnableLambda(lambda x: "English"), "content": RunnablePassthrough()}
                | get_translator_chain()
        )
        if request_body.get("collection_name") is None or request_body.get("collection_name") == "":
            common_chat_chain = (translator_english_chain | common_ai_chat_chain() | translator_chain)
            return common_chat_chain.invoke({"input": request_body.get("query")})
        else:
            chain = get_chat_chain(request_body.get("collection_name"))
            executor_chain = (chain | translator_chain)
            return executor_chain.invoke({"input": request_body.get("query")})
    ```
    Directly output unit test code, and other content and explanations can be in the form of code comments.
    For non essential third-party functions or classes, mock and reasonably mock the return values so that the test method can execute
    """)

    print(result)


def testFDF():
    from rdflib import Graph
    g = Graph()
    with open("/Users/zhanbei/PycharmProjects/infobase/sources/index.scip", "r", encoding="utf-8") as f:
        g.parse(f)
        for s, p, o in g:
            print(s, p, o)
