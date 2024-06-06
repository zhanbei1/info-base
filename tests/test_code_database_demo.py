#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
=================================================
@Project -> File   ：infobase -> test_code_database_demo
@IDE    ：PyCharm
@Author ：Desmond.zhan
@Date   ：2023/10/31 14:58
@Desc   ：
==================================================
"""
import traceback
from typing import List, Tuple

import ujson
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.schema import Document
from langchain.vectorstores.chroma import Chroma

from infobase.code_database_demo import ProjectCodeDescTree


def test_split_code_file():
    project = ProjectCodeDescTree(project_path="/Users/zhanbei/IdeaProjects/EvalEx")
    desc = project.constructDescriptionTree(
        "/Users/zhanbei/IdeaProjects/EvalEx/src/main/java/com/ezylang/evalex/functions/trigonometric/AsinFunction.java")
    print(desc.dict())


def test_insert_vector_to_db():
    embedding_model = HuggingFaceEmbeddings(
        model_name="/Users/zhanbei/PycharmProjects/infobase/models/moka-ai/m3e-small",
        model_kwargs={'device': 'cpu'})

    chroma_db = Chroma(collection_name="doop-server-with-inverted-index",
                       embedding_function=embedding_model,
                       persist_directory="/Users/zhanbei/PycharmProjects/infobase/data/chroma_db")
    page_content = {
        "name": "doop-server",
        "path": "doop-server",
        "description": "This doop-server module provides a range of functionalities for managing and processing various aspects of a distributed system, including managing services, interacting with the XxlJob system, managing tenants, clusters, and projects in a cloud-based environment, managing and displaying data in a dashboard application, managing pipelines and pipeline nodes, managing topology-related data in a database, managing and analyzing metric data, tracing and monitoring services, and managing and querying various clusters. The code uses various libraries and frameworks such as Spring, MyBatis-Plus, Lombok, and Swagger for implementation and documentation, and includes annotations for logging, validation, and defining behavior. It provides a standardized way of transferring data within an application and defines several data transfer object (DTO) classes with various properties and fields that represent different search criteria. Overall, this doop-server module provides a comprehensive set of tools for developers to use in their projects."
    }
    doc = Document(
        page_content=ujson.dumps(page_content),
        metadata={
            "doc_id": "doop-server",
            "metadata": ujson.dumps({
                "type": "module",
                "path": "doop-server"
            })
        })
    # chroma_db.add_documents([doc])
    result: List[Tuple[Document, float]] = chroma_db.similarity_search_with_relevance_scores(query="doop-server, functionalities", k=20)
    result_sorted = sorted(result, key=lambda x: x[1], reverse=True)
    for doc in result_sorted:
        print(f"page_content : {doc[0].page_content}, score: {doc[1]} \n\n")


def test_search_from_vector_db():
    embedding_model = HuggingFaceEmbeddings(
        model_name="/Users/zhanbei/PycharmProjects/infobase/models/moka-ai/m3e-small",
        model_kwargs={'device': 'cpu'})

    chroma_db = Chroma(collection_name="doop-server-with-inverted-index",
                       embedding_function=embedding_model,
                       persist_directory="/Users/zhanbei/PycharmProjects/infobase/data/chroma_db")
    # /doop-server-api/src/main/java/com/cloudwise/doop/server/api/pipeline/DoopPipelineManagementService.java
    result = chroma_db.get(where={"doc_id":"/doop-server-api/src/main/java/com/cloudwise/doop/server/api/pipeline/DoopPipelineNodeService.java"})
    print(f"page_content : {result}")
