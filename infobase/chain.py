"""This is a template for a custom chain.

Edit this file to implement your chain logic.
"""
import os
import pickle
from operator import itemgetter
from typing import List, Tuple

import ujson
from langchain.chat_models.openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.retrievers import MultiVectorRetriever
from langchain.schema import StrOutputParser, Document
from langchain.schema.runnable import Runnable, RunnablePassthrough, RunnableLambda
from langchain.storage import InMemoryStore
from traceloop.sdk.decorators import workflow

from infobase.configs import PROJECT_PATH, logger, INVERTED_INDEX_FILE_PATH
from infobase.db.vector_db.chrome_db import ChromaDb
from infobase.lexical_search import CustomIndex
from infobase.llm_chat.llm_model import LLMModel
from infobase.output_parser.boolean import BooleanOutputParser
from infobase.output_parser.list import CommonListOutputParser
from infobase.prompt_template import LLM_LANGUAGE_TRANSLATOR_PROMPT_TEMPLATE, MULTI_QUERY_PROMPT_TEMPLATE, \
    NEED_ORIGIN_CODE_PROMPT_TEMPLATE, LLM_QUERY_PROMPT_TEMPLATE, LLM_MULTI_QUERY_PROMPT_TEMPLATE, \
    COMMON_AI_CHAT_PROMPT_TEMPLATE, QUERY_KEY_WORD_PROMPT_TEMPLATE

template = """You are a helpful assistant who generates comma separated lists.
A user will pass in a category, and you should generate 5 objects in that category in a comma separated list.
ONLY return a comma separated list, and nothing more."""  # noqa: E501
human_template = "{text}"


@workflow(name="translator_chain")
def get_translator_chain() -> Runnable:
    llm_model: ChatOpenAI = LLMModel.get_model()

    translator_prompt_template = PromptTemplate(template=LLM_LANGUAGE_TRANSLATOR_PROMPT_TEMPLATE,
                                                input_variables=["language", "content"])

    return translator_prompt_template | llm_model | StrOutputParser()


@workflow(name="multi_query_chain")
def get_split_multi_query_chain() -> Runnable:
    llm_model: ChatOpenAI = LLMModel.get_model()
    prompt = PromptTemplate.from_template(MULTI_QUERY_PROMPT_TEMPLATE)
    list_parser = CommonListOutputParser()
    return {"question": RunnablePassthrough()} | prompt | llm_model | list_parser


@workflow(name="check_need_code_chain")
def get_check_need_code_chain() -> Runnable:
    need_code_prompt = PromptTemplate.from_template(NEED_ORIGIN_CODE_PROMPT_TEMPLATE)
    llm_model: ChatOpenAI = LLMModel.get_model()
    boolean_parser = BooleanOutputParser()
    need_code_chain = {"question": RunnablePassthrough()} | need_code_prompt | llm_model | boolean_parser
    return need_code_chain


@workflow(name="query_key_word_chain")
def get_query_key_word_chain() -> Runnable:
    llm_model: ChatOpenAI = LLMModel.get_model()
    prompt = PromptTemplate.from_template(QUERY_KEY_WORD_PROMPT_TEMPLATE)
    return {"query": RunnablePassthrough()} | prompt | llm_model | StrOutputParser()


@workflow(name="split_query_chain")
def get_split_query_chain() -> Runnable:
    def parallel_check() -> Runnable:
        return ({"question_list": RunnablePassthrough(),
                 "need_code_list": get_check_need_code_chain().batch,
                 "query_key_words": get_query_key_word_chain().batch
                 }
                | RunnableLambda(lambda check_result:
                                 [{"question": query, "need_code": need_code, "query_key_word": key_word}
                                  for query, need_code, key_word in
                                  zip(check_result.get("question_list"),
                                      check_result.get("need_code_list"),
                                      check_result.get("query_key_words"))
                                  ]
                                 )
                )

    return ({"origin_query": RunnablePassthrough(), "query_list": get_split_multi_query_chain()}
            | RunnableLambda(lambda query: list(set(query.get("query_list", []) + [str(query.get("origin_query"))])))
            | parallel_check()
            )


def construct_similar_doc_origin_code(question: dict):
    similar_list: list[Document] = question.get("similar_list")
    similar_content_obj = []
    for similar_doc in similar_list:
        metadata = ujson.loads(similar_doc.metadata.get("metadata", '{}'))
        code_byte_range = metadata.get("code_byte_range", [])
        file_path = metadata.get("path", "")
        try:
            with open(PROJECT_PATH + file_path) as f:
                f.seek(code_byte_range[0])
                if code_byte_range[1] - code_byte_range[0] + 1 > 7000:
                    code_content = f.read(7000 + 1)
                else:
                    code_content = f.read(code_byte_range[1] - code_byte_range[0] + 1)
                similar_content_obj.append({
                    "origin_code": code_content,
                    "page_content": similar_doc.page_content
                })
        except Exception as e:
            logger.error(f"读取源代码异常{PROJECT_PATH + file_path}，异常信息为：{e}")
            similar_content_obj.append({"page_content": similar_doc.page_content})
    return {"context": similar_content_obj, "query": question.get("question").get("question")}


def branch_router(question: dict):
    """
    :param question:
    :return:
    """
    if question.get("question", {}).get("need_code", False):
        return RunnableLambda(construct_similar_doc_origin_code)
    elif not question.get("question", {}).get("need_code", False):
        return RunnableLambda(
            lambda x: {"context": [similar_content.page_content for similar_content in x["similar_list"]],
                       "query": x.get("question").get("question")})

    else:
        raise ValueError(f"Unknown question type: {question.get('question_type', '')}")


def get_relevant_snippets(query: str, collection_name: str, top_k: int = 10):
    # 向量数据库中查询相关文档
    retriever = MultiVectorRetriever(vectorstore=ChromaDb.get_db_client(collection_name), docstore=InMemoryStore(),
                                     id_key="doc_id")
    vector_similarity_doc: List[Tuple[Document, float]] = retriever.vectorstore.similarity_search_with_score(
        query=query, k=50)

    # 倒排索引中查找相关文档
    if os.path.exists(INVERTED_INDEX_FILE_PATH):
        with open(INVERTED_INDEX_FILE_PATH, "rb") as f:
            index: CustomIndex = pickle.load(f)
            index_result = index.search_index(query)
            lexical_scores = []
            for doc in vector_similarity_doc:
                metadata = ujson.loads(doc[0].metadata.get("metadata", {}))
                code_byte_range = metadata.get("code_byte_range", ["", ""])
                key = f"{metadata['path']}:{str(code_byte_range[0])}:{str(code_byte_range[1])}"
                if key in index_result:
                    lexical_scores.append(index_result[key])
                else:
                    lexical_scores.append(0.3)

            combined_scores = [(100.0 - similarity_doc[1]) + lexical_score
                               for similarity_doc, lexical_score in zip(vector_similarity_doc, lexical_scores)]
            combined_list = list(zip(combined_scores, vector_similarity_doc))
            sorted_list = sorted(combined_list, key=lambda x: x[0], reverse=True)
            top_k_list = sorted_list[:top_k]
            return [doc[1][0] for doc in top_k_list]
    else:
        sorted_list = sorted(vector_similarity_doc, key=lambda x: x[1], reverse=True)
        return [doc[0] for doc in sorted_list[:top_k]]


@workflow(name="split_query_result_chain")
def get_split_query_result_chain(collection_name: str) -> Runnable:
    prompt_template = PromptTemplate(template=LLM_QUERY_PROMPT_TEMPLATE, input_variables=["context", "query"])
    llm_model: ChatOpenAI = LLMModel.get_model()

    llm_answer_chain = prompt_template | llm_model | StrOutputParser()

    return (RunnableLambda(
        lambda question: {
            "similar_list": get_relevant_snippets(question.get("query_key_word"), collection_name, top_k=10),
            "question": question})
            | RunnableLambda(branch_router)
            | {"Question": itemgetter("query"), "Answer": llm_answer_chain}
            )


@workflow(name="combine_query_result_chain")
def get_combine_result_chain() -> Runnable:
    prompt_template = PromptTemplate(template=LLM_MULTI_QUERY_PROMPT_TEMPLATE,
                                     input_variables=["multi_query_answer", "question"])
    llm_model: ChatOpenAI = LLMModel.get_model()
    return prompt_template | llm_model | StrOutputParser()


@workflow(name="chat_chain")
def get_chat_chain(collection_name: str) -> Runnable:
    # 翻译英文
    translator_chain = get_translator_chain()
    # 拆分问题
    split_query_chain = get_split_query_chain()
    # 拆分的问题进行搜索document和回答
    query_answer_chain = get_split_query_result_chain(collection_name=collection_name)
    # 合并结果，总结回答
    combine_result_chain = get_combine_result_chain()
    # 合并成一次回话的整个chain
    chain = ({"content": itemgetter("input"), "language": RunnableLambda(lambda x: "English")}
             | translator_chain
             | {"multi_query_answer": split_query_chain | query_answer_chain.batch | RunnableLambda(
                lambda x: [q if q["Answer"].lower() != "none" else None for q in x]),
                "question": RunnablePassthrough()}
             | combine_result_chain
             )
    # 添加memory，全局可以获取本次回话的上下文信息, [Legacy]
    # chat_chain = SequentialChain(
    #     memory=SimpleMemory(memories={"origin_query": query, "language": "English"}),
    #     chains=[chain],
    #     input_variables=["input", "output_language", ""],
    #     verbose=CHAIN_VERBOSE
    # )

    return chain


@workflow(name="common_ai_chat_chain")
def common_ai_chat_chain() -> Runnable:
    llm_model: ChatOpenAI = LLMModel.get_model()

    chat_prompt = PromptTemplate(template=COMMON_AI_CHAT_PROMPT_TEMPLATE, input_variables=["input"])

    return {"input": RunnablePassthrough()} | chat_prompt | llm_model | StrOutputParser()


def get_chain(request_body: dict) -> str:
    """Return a chain."""
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
        return common_chat_chain.invoke(request_body.get("query"))
    else:
        chain = get_chat_chain(request_body.get("collection_name"))
        executor_chain = (chain | translator_chain)
        return executor_chain.invoke({"input": request_body.get("query")})

# if __name__ == '__main__':
#     print(sys.getrecursionlimit())
#     chain = get_chain("doop-server")
#     output: Output = chain.invoke({"input": "doop-server主要有哪些模块"})
#     print(output)
