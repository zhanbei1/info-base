#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
=================================================
@Project -> File   ：infobase -> vector_retriever_test
@IDE    ：PyCharm
@Author ：Desmond.zhan
@Date   ：2023/11/16 17:59
@Desc   ：
==================================================
"""
from langchain.embeddings import HuggingFaceEmbeddings
import pytest
from langchain.schema import Document
from langchain.vectorstores.chroma import Chroma


def test_vector_retriever():
    embedding_model = HuggingFaceEmbeddings(
        model_name="/Users/zhanbei/PycharmProjects/infobase/models/moka-ai/m3e-small",
        model_kwargs={'device': 'cpu'})
    chroma_db = Chroma(collection_name="doop-server",
                       embedding_function=embedding_model,
                       persist_directory="/Users/zhanbei/PycharmProjects/infobase/data/chroma_db")

    result_score: list[tuple[Document, float]] = chroma_db.similarity_search_with_score(
        "How does the 'server common' module provide common functionalities across the system?", k=10)
    for result in result_score:
        print(f"page_content:{result[0].page_content}")
        print(f"page_content:{result[1]}")
        print("=" * 30)
