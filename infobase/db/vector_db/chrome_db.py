#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
=================================================
@Project -> File   ：infobase -> chrome_db
@IDE    ：PyCharm
@Author ：Desmond.zhan
@Date   ：2023/11/13 10:33
@Desc   ：chrome 向量数据库
==================================================
"""

from langchain.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
from langchain.vectorstores.chroma import Chroma

from infobase.configs import EMBEDDING_MODEL_DICT, EMBEDDING_MODEL, EMBEDDING_DEVICE, PERSIST_DIRECTORY, logger, \
    SIMILARITY_SEARCH_TOP_K


class ChromaDb:
    chroma_db_dict = {}
    embedding_model = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_DICT.get(EMBEDDING_MODEL),
                                            model_kwargs={'device': EMBEDDING_DEVICE})

    @classmethod
    def similarity_search(cls, context: str, collection_name: str) -> list[Document]:
        try:
            chroma_db: Chroma = cls.chroma_db_dict.get(collection_name)
            return chroma_db.similarity_search(context, k=SIMILARITY_SEARCH_TOP_K)
        except Exception as e:
            logger.error(f"ChromaDb similarity_search error info : {e}")
            return []

    @classmethod
    def add_documents(cls, docs_list: list[Document], collection_name: str) -> bool:
        try:
            chroma_db: Chroma = cls.chroma_db_dict.get(collection_name)
            chroma_db.add_documents(documents=docs_list)
            return True
        except Exception as e:
            logger.error(f"ChromaDb add_documents error, error info :{e}")
            return False

    @classmethod
    def get_db_client(cls, collection_name: str) -> Chroma:
        return cls._check_db_collection(collection_name)

    @classmethod
    def _check_db_collection(cls, collection_name: str) -> Chroma:
        if cls.chroma_db_dict.get(collection_name, None) is None:
            cls.chroma_db_dict[collection_name] = Chroma(collection_name=collection_name,
                                                         embedding_function=cls.embedding_model,
                                                         persist_directory=PERSIST_DIRECTORY)
        return cls.chroma_db_dict.get(collection_name)
