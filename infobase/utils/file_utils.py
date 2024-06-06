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
from typing import Any
from infobase.enums import CodeLanguageEnum
from infobase.model import BaseConfig, Snippet, SupportLanguageParser


class FileUtils:
    @staticmethod
    def get_file_content(file_path: str, start_byte: int, end_byte: int) -> str:
        with open(file_path) as f:
            f.seek(start_byte)
            return f.read(end_byte - start_byte + 1)


def read_file(file_name):
    try:
        with open(file_name, "r") as f:
            return f.read()
    except SystemExit:
        raise SystemExit
    except:
        return ""


def naive_chunker(code: str, line_count: int = 30, overlap: int = 5):
    """
    按行分割代码字符串。

    参数：
    code (str): 待分割的代码字符串。
    line_count (int): 每个分割块的行数，默认为30。
    overlap (int): 分割块之间的重叠行数，默认为15。

    返回值：
    chunks (list): 分割后的代码块列表。

    异常：
    ValueError: 如果重叠行数大于等于分割块的行数。

    """
    if overlap >= line_count:
        raise ValueError("Overlap should be smaller than line_count.")
    lines = code.split("\n")
    total_lines = len(lines)
    chunks = []

    start = 0
    while start < total_lines:
        end = min(start + line_count, total_lines)
        chunk = "\n".join(lines[start:end])
        chunks.append(chunk)
        start += line_count - overlap

    return chunks


def _chunk_node(node: Any, file_path: str, code_parser: SupportLanguageParser) -> list[Snippet]:
    snippet_list = []
    # 类型定义，没有超长，直接大语言模型分析
    # 直接洗这几个模块，至于其他参数啥的，不处理
    if node.type in code_parser.tree_sitter_type_list:
        if node.end_byte - node.start_byte < 7000:
            snippet_list.append(
                Snippet(content=node.text, start=node.start_byte, end=node.end_byte, file_path=file_path)
            )
        else:
            # 还有子节点
            if node.children is not None:
                for children in node.children:
                    children_snippets = _chunk_node(children, file_path, code_parser)
                    if children_snippets is not None and len(children_snippets) > 0:
                        snippet_list = snippet_list + children_snippets
        return snippet_list


def parser_code_chunk(code: str, language: str, file_path: str, base_config: BaseConfig) -> list[Snippet]:
    if language is None:
        language = base_config.extension_to_language[file_path.split(".")[-1]]
    language_parser: SupportLanguageParser = CodeLanguageEnum[language.upper()].value
    tree = language_parser.parser.parse(bytes(code, encoding="utf-8"))
    if (
            not tree.root_node.children
            or tree.root_node.children[0].type != "ERROR"
    ):
        return _chunk_node(tree.root_node, file_path, language_parser)


def file_chunk_node(file_content: str, path: str, base_config: BaseConfig) -> list[Snippet]:
    # 1、如果是可以识别的语言，使用语言进行分词
    ext = path.split(".")[-1]
    if ext in base_config.extension_to_language:
        language = base_config.extension_to_language[ext]
        return parser_code_chunk(file_content, language, path, base_config)
    else:
        # 如果认为是普通文本，直接文本切分，写入向量数据库
        line_count = 50
        overlap = 10
        chunks = naive_chunker(file_content, line_count, overlap)
        snippets = []
        for idx, chunk in enumerate(chunks):
            new_snippet = Snippet(
                content=chunk,
                start=idx * (line_count - overlap),
                end=(idx + 1) * (line_count - overlap),
                file_path=path,
            )
            snippets.append(new_snippet)
        return snippets
