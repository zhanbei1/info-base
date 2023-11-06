#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
=================================================
@Project -> File   ：infobase -> function_test
@IDE    ：PyCharm
@Author ：Desmond.zhan
@Date   ：2023/10/26 10:03
@Desc   ：
==================================================
"""
import traceback

import ujson
from langchain.chains import LLMChain
from langchain.chat_models import AzureChatOpenAI
from langchain.document_loaders.generic import GenericLoader
from langchain.document_loaders.parsers import LanguageParser
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import StringPromptTemplate, PromptTemplate
from langchain.retrievers import MultiQueryRetriever, MultiVectorRetriever
from langchain.retrievers.multi_query import LineListOutputParser
from tree_sitter import Language, Parser, Tree, TreeCursor, Node

from infobase.text_splitter import CodeSplitter

# loader = GenericLoader.from_filesystem(
#     "/Users/zhanbei/PycharmProjects/sweep/sweepai/core/",
#     glob="*",
#     suffixes=[".py", ".js", ".java"],
#     parser=LanguageParser(),
# )
#
# docs = loader.load()
# print(docs)
#
# Language.build_library(
#     'build/local-support-languages.so',
#     [
#         'data/language_tree_sitter/tree-sitter-python',
#         'data/language_tree_sitter/tree-sitter-java'
#     ]
# )

# tree-sitter
JAVA_LANGUAGE = Language('/Users/zhanbei/PycharmProjects/infobase/build/local-support-languages.so', 'java')
PY_LANGUAGE = Language('/Users/zhanbei/PycharmProjects/infobase/build/local-support-languages.so', 'python')

parser = Parser()
parser.set_language(JAVA_LANGUAGE)
TreeCursor()
with open("/Users/zhanbei/IdeaProjects/EvalEx/src/main/java/com/ezylang/evalex/parser/ShuntingYardConverter.java") as f:
    tree: Tree = parser.parse(bytes(f.read(), "utf8"))
    for node in tree.root_node.children:
        node: Node
        print(node)

# sweep 底层代码切分 逻辑
# splitter = CodeSplitter(language='python', chunk_lines=500, chunk_lines_overlap=0)
# with open("/Users/zhanbei/IdeaProjects/EvalEx/src/main/java/com/ezylang/evalex/data") as f:
#     result_list = splitter.split_text(f.read())
#     for result in result_list:
#         print(result)
#         print("====" * 20)

# mutilQueryRetriever 测试
llm35 = AzureChatOpenAI(openai_api_key='1bfd2fc2b23c4539b4eeb9834a66fd8e',
                        openai_api_base="https://codedog.openai.azure.com",
                        model="gpt-3.5-turbo",
                        deployment_name="gpt-35-turbo",
                        openai_api_version="2023-05-15",
                        temperature=0,
                        )

prompt_str = """As a code management intelligent robot, your task is to analyze three different questions 
that can answer the user's questions, in order to search for relevant documents in the vector database.
In the vector database, there are only functional descriptions and hypothetical questions about code functions, 
classes, modules, and projects, and the original code is not saved. If the answer requires a question or code, 
please mark it out. Please strictly return the results in the form of a JSON array.
Example:
    Input:
        "How does the parsing and evaluating process work in EvalEx"
    Output:
        {Output}

 
Original question: {question}

Remember to strictly return the results in the form of JSON arrays, and do not fabricate or fabricate them when there are no results
 """
Output = """
[{
    "need_code": true,
    "question": "Here is a demo example of a problem that requires code, not a real problem"
  },
  {
    "need_code": false,
    "question": "This is an example of a problem that does not require code, not a real code example"
  }
]
"""

# prompt = PromptTemplate.from_template(prompt_str)
#
# try:
#     output_parser = LineListOutputParser()
#     llm_chain = LLMChain(llm=llm35, prompt=prompt)
#     result = llm_chain.predict(question="How does the parsing and evaluation process work in EvalEx", Output=Output)
#     question_list = ujson.loads(result)
#     print(question_list)
# except Exception as e:
#     traceback.print_exc()
