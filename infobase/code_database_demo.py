#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
=================================================
@Project -> File   ：infobase -> code_database_demo
@IDE    ：PyCharm
@Author ：Desmond.zhan
@Date   ：2023/10/24 10:33
@Desc   ：代码数据 demo分析
==================================================
"""
import fnmatch
import os
import traceback
import uuid
import re
from enum import Enum
from typing import List, Any

import ujson
from langchain.chains import LLMChain
from langchain.chat_models import AzureChatOpenAI
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.prompts import PromptTemplate
from langchain.retrievers import MultiVectorRetriever
from langchain.schema import Document
from langchain.storage import InMemoryStore
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores.chroma import Chroma
from pydantic import BaseModel, Field
from tree_sitter import Language, Parser

from infobase.configs import IGNORE_PATH, logger, CODE_TYPE_FILE_SUFFIX_MAPPING, SUPPORT_LANGUAGE_DEFINITION_TYPE
from infobase.prompt_template import LLM_WHOLE_FILE_SUMMARY_PROMPT_TEMPLATE, \
    LLM_DIR_SUMMARY_PROMPT_TEMPLATE, LLM_QUERY_PROMPT_TEMPLATE, LLM_LANGUAGE_TRANSLATOR_PROMPT_TEMPLATE, \
    LLM_FUNCTION_SUMMARY_PROMPT_TEMPLATE, LLM_FUNCTION_SUMMARY_OUTPUT, \
    DIR_SUMMARY_OUTPUT, MULTI_QUERY_PROMPT_TEMPLATE, LLM_MULTI_QUERY_PROMPT_TEMPLATE, \
    HYPOTHETICAL_QUESTIONS_PROMPT_TEMPLATE, NEED_ORIGIN_CODE_PROMPT_TEMPLATE


class PathType(Enum):
    FILE = "file",
    DIR = "dir",
    FUNCTION = "function",
    CLASS = "class",


class SupportLanguageParser:
    def __init__(self, type_str: str):
        self.file_suffix: str = CODE_TYPE_FILE_SUFFIX_MAPPING.get(type_str)
        self.language_tree_sitter: Language = Language(
            '/Users/zhanbei/PycharmProjects/infobase/build/local-support-languages.so', type_str)
        self.parser = Parser()
        self.parser.set_language(self.language_tree_sitter)
        self.tree_sitter_type_list: list = SUPPORT_LANGUAGE_DEFINITION_TYPE.get(type_str).get("definition_list", [])
        self.mini_analysis_type: str = SUPPORT_LANGUAGE_DEFINITION_TYPE.get(type_str).get("mini_analysis_type", None)
        self.ignore_save_type: list[str] = SUPPORT_LANGUAGE_DEFINITION_TYPE.get(type_str).get("ignore_save_type", [])


# LANGCHAIN_TRACING_V2=true
# LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
# LANGCHAIN_API_KEY="ls__500d00851450424e9410eff8edf5cdda"
# LANGCHAIN_PROJECT="desmond_test"
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = "ls__500d00851450424e9410eff8edf5cdda"
os.environ["LANGCHAIN_PROJECT"] = "desmond_test"


# 支持的语言和文件识别的后缀
class CodeLanguageEnum(Enum):
    JAVA = SupportLanguageParser("java"),
    PYTHON = SupportLanguageParser("python")


class Description(BaseModel):
    type: str = Field(default=None, description="类型，file,module,class,function等", required=False)
    path: str = Field(default=None, description=" 路径，这里只记录文件路径", required=False)
    description: str = Field(default=None, description="LLM大模型总结的描述", required=False)
    code_byte_range: list[int] = Field(default=None, description="代码的范围，某些场景下，可能需要寻找源码", required=False)
    # 如果是代码，包含这些，如果不是，可以为空
    name: str = Field(default=None, description="函数名或者类名", required=False)
    input_parameter: str = Field(default=None, description="入参", required=False)
    return_obj: str = Field(default=None, description="出参", required=False)
    possible_exception: list[str] = Field(default=None, description="可能发生的异常列表", required=False)
    children_desc_list: list = Field(default=None, description="子节点总结内容，类型也是Description", required=False)


# 构建项目 代码description 树
class ProjectCodeDescTree:
    def __init__(self, project_path: str = None, collection_name: str = None):
        self.project_path = project_path
        self.llm35 = AzureChatOpenAI(openai_api_key='1bfd2fc2b23c4539b4eeb9834a66fd8e',
                                     openai_api_base="https://codedog.openai.azure.com",
                                     model="gpt-3.5-turbo",
                                     deployment_name="gpt-35-turbo",
                                     openai_api_version="2023-05-15",
                                     temperature=0,
                                     )
        self.embedding_model = HuggingFaceEmbeddings(
            model_name="/Users/zhanbei/PycharmProjects/infobase/models/moka-ai/m3e-small",
            model_kwargs={'device': 'cpu'})

        self.chroma_db = Chroma(collection_name="infobase" if collection_name is None else collection_name,
                                embedding_function=self.embedding_model,
                                persist_directory="/Users/zhanbei/PycharmProjects/infobase/data/chroma_db")
        self.common_text_splitter = CharacterTextSplitter.from_tiktoken_encoder(chunk_size=500, chunk_overlap=10)

    # 构造目录描述文件树
    def constructDescriptionTree(self, path: str) -> Description | None:
        print(f"正在解析：{path} =================== < < < < < < < < < < < ")
        for pattern in IGNORE_PATH:
            if fnmatch.fnmatch(path.split("/")[-1], pattern):
                logger.info(f"忽略文件夹：{path}")
                return None

        if os.path.isdir(path):
            desc_list: list[Description] = []
            # 文件和文件夹计数
            for path_name in os.listdir(path=path):
                current_path: str = os.path.join(path, path_name)
                path_desc = self.constructDescriptionTree(current_path)
                if path_desc is not None:
                    desc_list.append(path_desc)
            # 根据desc_list 总结本目录主要功能
            if desc_list is None:
                return None
            # 尽量排除过多空的文件夹，只保留一个文件夹即可
            if len(desc_list) > 1 or (len(desc_list) == 1 and desc_list[0].type == PathType.FILE.value[0]):
                desc: Description = self.llm_dir_summary_description(desc_list=desc_list, path_type="module")
                desc.type = PathType.DIR.value[0]
                desc.path = path.replace(self.project_path, "")
                # desc.children_desc_list = desc_list
                self.insert_to_vector_db(desc)
                return desc
            elif len(desc_list) == 1 and desc_list[0].type == PathType.DIR.value[0]:
                return desc_list[0]

        elif os.path.isfile(path):
            try:
                # 如果是代码，进行切分
                if path.endswith(".py"):
                    file_desc = self.split_code_file_summary_desc(path, CodeLanguageEnum.PYTHON)
                    parser: SupportLanguageParser = CodeLanguageEnum.PYTHON.value[0]
                    self.insert_to_vector_db(file_desc, parser.ignore_save_type)
                    return file_desc
                elif path.endswith(".java"):
                    file_desc = self.split_code_file_summary_desc(path, CodeLanguageEnum.JAVA)
                    parser: SupportLanguageParser = CodeLanguageEnum.JAVA.value[0]
                    self.insert_to_vector_db(file_desc, parser.ignore_save_type)
                    return file_desc
                else:
                    with open(path) as f:
                        # 如果认为是普通文本，直接文本切分，写入向量数据库
                        texts: List[str] = self.common_text_splitter.split_text(f.read())
                        for text in texts:
                            desc = Description(type=PathType.FILE.value[0], path=path.replace(self.project_path, ""),
                                               description=text)
                            self.insert_to_vector_db(desc)
                        return None
            except Exception as e:
                print(f"{path} open error , error info is : {e}")
                raise e
        print(f"{path} 内的文件已经解析完成 =================== > > > > > > > > > > >  ")

    # 根据文件类型切分文件内容
    # .py、.java 其他的都按照正常的文本文件切割
    def split_code_file_summary_desc(self, file_path: str, code_type: CodeLanguageEnum) -> Description:
        # 如果文本不长，
        with open(file_path) as f:
            context = f.read()
            if len(context) < 7000:
                file_desc: Description = self.llm_summary_file_description(file_path)
                file_desc.code_byte_range = [0, len(context)]
            else:
                file_desc = self._code_splitter_summary(file_path, code_type)
            file_desc.type = PathType.FILE.value[0]
            return file_desc

    def _code_splitter_summary(self, file_path: str, code_type: CodeLanguageEnum) -> Description:
        with open(file_path) as f:
            text = f.read()
            language_parser: SupportLanguageParser = code_type.value[0]
            tree = language_parser.parser.parse(bytes(text, encoding="utf-8"))
            if (
                    not tree.root_node.children
                    or tree.root_node.children[0].type != "ERROR"
            ):
                return self._chunk_node(tree.root_node, file_path, language_parser)

    def _chunk_node(self, node: Any, file_path: str, code_parser: SupportLanguageParser) -> Description | None:
        """
        对具体实现代码树进行遍历总结，并返回这个节点的总结和其他信息
        :node: 需要处理的节点
        :file_path: 文件路径，给类，函数添加文件路径，方便后续源代码查找
        :code_parser: 不同代码类型的分析对象
        :return: 返回这个节点的Description 信息
        """
        new_chunks_desc = []
        # 类型定义，没有超长，直接大语言模型分析
        # 直接洗这几个模块，至于其他参数啥的，不处理
        if node.type in code_parser.tree_sitter_type_list:
            if node.end_byte - node.start_byte < 7000:
                if node.type == code_parser.mini_analysis_type:
                    desc: Description = self.llm_function_summary_description(node.text)
                else:
                    desc: Description = self.llm_code_summary_description(node.text, file_path)
            else:
                # 还有子节点
                if node.children is not None:
                    for children in node.children:
                        desc_chunks = self._chunk_node(children, file_path, code_parser)
                        if desc_chunks is not None:
                            new_chunks_desc.append(desc_chunks)
                    if new_chunks_desc is not None:
                        desc: Description = self.llm_dir_summary_description(new_chunks_desc, node.type)
                        desc.children_desc_list = new_chunks_desc
            desc.code_byte_range = [node.start_byte, node.end_byte]
            desc.type = node.type
            desc.path = file_path.replace(self.project_path, "")
            return desc

    def llm_code_summary_description(self, class_code_text: str, file_path: str = None) -> Description:
        """
        LLM 对整个代码文件的类和函数进行摘要
        :param class_code_text:
        :return:
        """
        prompt_template = PromptTemplate(template=LLM_WHOLE_FILE_SUMMARY_PROMPT_TEMPLATE, input_variables=["Input"])
        chain = LLMChain(llm=self.llm35, prompt=prompt_template)
        response = chain.predict(Input=class_code_text)
        children_desc_list: list[Description] = []
        try:
            response = re.sub(r',\s*\n*}', '}', response)
            # result_dict: dict = ujson.loads(response)
            file_name = file_path.replace(self.project_path, "")
            # if result_dict.get("content_description"):
            #     content_description: list = result_dict.get("content_description")
            #     for content_desc in content_description:
            #         des: Description = Description.parse_obj(content_desc)
            #         des.path = file_name
            #         children_desc_list.append(des)
            # desc: Description = Description.parse_obj(result_dict)
            desc: Description = Description(description=response)
            desc.path = file_name
            # desc.children_desc_list = children_desc_list
        except Exception as e:
            print(e)
            desc = Description(description=response)
        return desc

    def llm_function_summary_description(self, class_code_text: str) -> Description:
        """
        LLM 对整个代码文件的类和函数进行摘要
        :param class_code_text:
        :return: Description
        """
        prompt_template = PromptTemplate(template=LLM_FUNCTION_SUMMARY_PROMPT_TEMPLATE,
                                         input_variables=["output_template", "Input"])
        chain = LLMChain(llm=self.llm35,
                         prompt=prompt_template)
        response = chain.predict(Input=class_code_text, output_template=LLM_FUNCTION_SUMMARY_OUTPUT)
        children_desc_list: list[Description] = []
        try:
            result_dict: dict = ujson.loads(response)
            if result_dict.get("content_description"):
                content_description: list = result_dict.get("content_description")
                for content_desc in content_description:
                    des = Description.parse_obj(content_desc)
                    children_desc_list.append(des)
            desc: Description = Description.parse_obj(result_dict)
            desc.children_desc_list = children_desc_list
        except Exception as e:
            print(e)
            desc = Description(description=response)
        return desc

    def llm_dir_summary_description(self, desc_list: list[Description], path_type: str = None) -> Description:
        """
        对具有一群子节点的文件，文件夹或者类进行总结
        :param desc_list:子节点描述列表
        :param path_type:路径类型，文件夹还是文件
        :return:Description，总结的结果
        """
        if desc_list and len(desc_list) > 0:
            prompt_template = PromptTemplate(template=LLM_DIR_SUMMARY_PROMPT_TEMPLATE,
                                             input_variables=["desc_list", "path_type", "dir_summary_output"])
            response = None
            try:
                chain = LLMChain(llm=self.llm35, prompt=prompt_template)
                response = chain.predict(desc_list=[description.description for description in desc_list],
                                         path_type=path_type, dir_summary_output=DIR_SUMMARY_OUTPUT)
                desc = Description.parse_obj(ujson.loads(response))
                return desc
            except Exception as e:
                print(f"引起异常的desc_list ： {desc_list}, \n response:{response} \n 异常信息为：{e}")
                return Description(description=response)

    # 对代码文件进行总结, 是代码就输出json，也可能输出总结的字符串
    def llm_summary_file_description(self, file_path: str) -> Description:
        """
        对整个文件进行总结
        :file_path:文件路径
        :return:返回结果，Description类型
        """
        try:
            with open(file_path) as f:
                return self.llm_code_summary_description(f.read(), file_path)
        except Exception as e:
            print(e)

    def llm_split_multi_query(self, query_text: str) -> list[dict]:
        prompt = PromptTemplate.from_template(MULTI_QUERY_PROMPT_TEMPLATE)

        try:
            llm_chain = LLMChain(llm=self.llm35, prompt=prompt)
            llm_response = llm_chain.predict(question=query_text)
            question_list: list[str] = llm_response.split("\n")
            split_question_list = []
            if question_list is not None and len(question_list) > 0:
                for question in question_list:
                    question = re.sub(r"^\d\.", "", question)
                    split_question_list.append({
                        "question": question,
                        "need_code": self.llm_check_need_code(question)
                    })
            return split_question_list
        except Exception as e:
            traceback.print_exc()
            return []

    def llm_check_need_code(self, query_text) -> bool:
        """
        check if the query need code
        :param query_text: 问题
        :return:
        """
        need_code_prompt = PromptTemplate.from_template(NEED_ORIGIN_CODE_PROMPT_TEMPLATE)
        llm_chain = LLMChain(llm=self.llm35, prompt=need_code_prompt)
        llm_response = llm_chain.predict(question=query_text)
        return True if llm_response.lower() == "yes" else False

    # TODO： 不需要了
    def llm_hypothetical_questions(self, desc: Description) -> str:
        prompt = PromptTemplate.from_template(HYPOTHETICAL_QUESTIONS_PROMPT_TEMPLATE)

        try:
            description = f"""
            name:{desc.name}
            type:{desc.type}
            description:{desc.description}
            """
            llm_chain = LLMChain(llm=self.llm35, prompt=prompt)
            llm_response = llm_chain.predict(description=description)
            return llm_response
        except Exception as e:
            traceback.print_exc()
            raise e

    # 保存到向量数据库中
    def insert_to_vector_db(self, desc: Description, ignore_save_list: list[str] = []):
        """
        遍历保存整个总结树，并且忽略某个规定类型（tree-sitter结果树有些层级是不必要的，不用保存）
        desc: 总结的对象
        ignore_save_list: 忽略保存的类型
        return:None
        """
        # 如果类型为忽略保存的类,或是不需要保存的类型，直接就跳过
        if desc is None or desc.type in ignore_save_list:
            return
        if desc.children_desc_list is not None:
            for d in desc.children_desc_list:
                self.insert_to_vector_db(d)
            # 子类写完之后，清空
            desc.children_desc_list = None
        docs_list = []
        id_key = "doc_id"
        id = str(uuid.uuid4())

        metadata = {id_key: id, "metadata": {"type": desc.type, "path": desc.path}}
        if desc.code_byte_range:
            metadata["metadata"]["code_byte_range"] = desc.code_byte_range
        metadata["metadata"] = ujson.dumps(metadata["metadata"])
        page_content = ujson.dumps({
            "name": desc.name,
            "description": desc.description,
        })
        # 假设性问题回答
        # hypothetical_questions = self.llm_hypothetical_questions(desc=desc)
        # docs_list.append(Document(page_content=hypothetical_questions, metadata={id_key: id}))
        if page_content is None:
            return

        docs_list.append(Document(page_content=page_content, metadata=metadata))
        try:
            self.chroma_db.add_documents(docs_list)
        except Exception as e:
            logger.error(f"vector db add documents error , error info : {e}")

    def query_similarity(self, query_text: str) -> str:
        query_english = self.translator_text_language(query_text, 'english')
        split_query_list: list[dict] = self.llm_split_multi_query(query_english)
        # split_query_list = []
        answer_list = []
        split_query_list.append({
            "question": query_english,
            "need_code": self.llm_check_need_code(query_english)
        })
        retriever = MultiVectorRetriever(
            vectorstore=self.chroma_db,
            docstore=InMemoryStore(),
            id_key="doc_id",
        )
        for query in split_query_list:
            similar_list: list[Document] = retriever.vectorstore.similarity_search(query=query.get("question"), k=8)
            # similar_content_list = self.chroma_db.similarity_search(query=query, k=10)
            prompt_template = PromptTemplate(template=LLM_QUERY_PROMPT_TEMPLATE,
                                             input_variables=["context", "query"])
            # 如果问题需要代码，则根据路径查找代码
            similar_content_obj = []
            if query.get("need_code", False):
                for similar_doc in similar_list:
                    metadata = ujson.loads(similar_doc.metadata.get("metadata", '{}'))
                    code_byte_range = metadata.get("code_byte_range", [])
                    file_path = metadata.get("path", "")
                    try:
                        with open(os.path.join(self.project_path, file_path)) as f:
                            f.seek(code_byte_range[0])
                            code_content = f.read(code_byte_range[1] - code_byte_range[0] + 1)
                            similar_content_obj.append({
                                "origin_code": code_content,
                                "page_content": similar_doc.page_content
                            })
                    except Exception as e:
                        logger.error(f"读取源代码异常，异常信息为：{e}")
            else:
                similar_content_obj = [similar_content.page_content for similar_content in similar_list]

            chain = LLMChain(llm=self.llm35, prompt=prompt_template)
            response = chain.predict(context=similar_content_obj, query=query.get("question"))
            answer_list.append({
                "Question": query.get("question"),
                "Answer": response
            })

        prompt_template = PromptTemplate(template=LLM_MULTI_QUERY_PROMPT_TEMPLATE,
                                         input_variables=["multi_query_answer", "question"])
        chain = LLMChain(llm=self.llm35, prompt=prompt_template)
        response = chain.predict(multi_query_answer=answer_list, question=query_english)
        return response

    def translator_text_language(self, context: str, language: str):
        prompt_template = PromptTemplate(template=LLM_LANGUAGE_TRANSLATOR_PROMPT_TEMPLATE,
                                         input_variables=["language", "content"])
        chain = LLMChain(llm=self.llm35,
                         prompt=prompt_template)
        response = chain.predict(language=language, content=context)
        return response


if __name__ == '__main__':
    # infobase_with_docs: 带有docs 进行embedding的
    # infobase_with_docs_without_params : 不带有任何出入参数询问llm ，直接进行总结即可
    codeDesc = ProjectCodeDescTree(project_path="/Users/zhanbei/IdeaProjects/EvalEx/",
                                   collection_name="infobase_with_docs")
    try:
        # desc = codeDesc.constructDescriptionTree("/Users/zhanbei/IdeaProjects/EvalEx")
        # print(desc.dict())
        # pass
        # result = codeDesc.query_similarity("EvalEx 的主要功能有哪些，按照功能点列出。我可以用EvalEx 做什么？")
        # translator_text = codeDesc.translator_text_language(result, "Chinese")
        # print(translator_text)
        # print("=" * 20)
        #
        # result = codeDesc.query_similarity("EvalEx使用的语言是什么？打包工具是什么？EvalEx 的版本号是多少？")
        # translator_text = codeDesc.translator_text_language(result, "Chinese")
        # print(translator_text)
        # print("=" * 20)
        #
        # result = codeDesc.query_similarity("EvalEx中主要的功能有哪些，都具有什么功能，按照模块分别列出来")
        # translator_text = codeDesc.translator_text_language(result, "Chinese")
        # print(translator_text)
        # print("=" * 20)
        #
        # result = codeDesc.query_similarity("判断一个条件是否成立的功能 在EvalEx中有没有，如果有，哪些类下可以实现")
        # translator_text = codeDesc.translator_text_language(result, "Chinese")
        # print(translator_text)
        # print("=" * 20)
        #
        # result = codeDesc.query_similarity("使用EvalEx 实现一个判断条件是否成立的函数代码")
        # translator_text = codeDesc.translator_text_language(result, "Chinese")
        # print(translator_text)
        # print("=" * 20)
        #
        # result = codeDesc.query_similarity("InfixNotEqualsOperator这个类，主要功能有哪些？")
        # translator_text = codeDesc.translator_text_language(result, "Chinese")
        # print(translator_text)
        # print("=" * 20)

        # ISSUES
        issues = [
            """
            How to restrict list of operators used in formula evaluation? 
            Thank you for your library. How to restrict the list of operators before evaluating the formula? I only use the +, -, *, / how to disable for example the unary operators?
           """,
            """
            Structure access with arbitrary key format
            Hello, really loving this little library.
            I'm facing the issue where my context is as follows
            
            {
                "element": {
                    "a prop": 1
                }
            }
            and I wish I could write an expression such as element['a prop'] or element.'a prop'. Is there a way to achieve this?
            """,

            """
            Fraction calculation, is that possible?
            Hi,
            I successfully implemented basic features of a calculator.
            Thank you a lot for the useful library!
            I plan to see if I can enhance my calculator with the feature like at https://www.mathpapa.com/fraction-calculator.html
            Basically, the calculator should allow to switch between decimal and fraction mode.
            In fraction mode, every part, which is not an integer will be kept as original or in an optimal result.
            Examples:
            2 / 6 should be 1 / 3
            sqrt(4 / 2) should be sqrt(2)
            2 / 6 + sqrt(4 / 2) should be 1 / 3 + sqrt(2)
            Do you see any possibility for fraction calculation with this library?
            """,

            """
            Detect whether an Expression is a simple number
            Question: I was wondering whether there is an easy way to detect with EvalEx whether an expression is a simple number?
            Let me describe in more details my use-case. I have two input values for expressions which get multiplied in the end.
            For example:
            expression1: 12+3
            expression2: 5-3
            
            Hence what I do is to is to concatenate the strings (if valid): (expression1) * (expression2)
            Note: To be on the safe side I need to add brackets around it. I also show the "resulting" expression to the user. In this case (12+3) * (5-3)
            This bring me to the actual question. In most of the cases people insert simple numbers like
            expression1: 8
            expression2: 9
            and the results looks like this: (8) * (9)
            People wonder why these brackets are added since it would be nicer looking to have in this case 8 * 9
            I noticed there is a isNumber(...) function. Unfortunately it is protected.
            Is there another way to achieve what I am looking for?
            Thanks for any advice and your library in the first place!
            """
        ]
        for issue in issues:
            result = codeDesc.query_similarity(issue)
            translator_text = codeDesc.translator_text_language(result, "Chinese")
            logger.info(translator_text)
            logger.info("=" * 20)

        # desc = codeDesc.constructDescriptionTree("/Users/zhanbei/IdeaProjects/EvalEx/src/main/java/com/ezylang/evalex/operators/booleans")
        # print(desc.dict())

        # embedding_model = HuggingFaceEmbeddings(
        #     model_name="/Users/zhanbei/PycharmProjects/infobase/models/moka-ai/m3e-small",
        #     model_kwargs={'device': 'cpu'})
        # chroma_db = Chroma(collection_name="infobase_embedding_with_multi_vector",
        #                    embedding_function=embedding_model,
        #                    persist_directory="/Users/zhanbei/PycharmProjects/infobase/data/chroma_db")
        # result: list[Document] = chroma_db.similarity_search("InfixNotEqualsOperator.java", k=20)
        # print([r.dict() for r in result])
        #
        # result_score: list[tuple[Document, float]] = chroma_db.similarity_search_with_score("Evaluation of asin(1.5) will throw NumberFormatException which is a bit misleading", k=10)
        #
        # print([r.dict() for r in result])
    except Exception as e:
        traceback.print_exc()
