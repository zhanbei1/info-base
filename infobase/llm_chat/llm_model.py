#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
=================================================
@Project -> File   ：infobase -> llm_model
@IDE    ：PyCharm
@Author ：Desmond.zhan
@Date   ：2023/11/13 15:29
@Desc   ：
==================================================
"""
from langchain.chains import LLMChain
from langchain.chat_models import AzureChatOpenAI, ChatOpenAI
from langchain.prompts import PromptTemplate

from infobase.configs import LLM_MODEL_DICT, LLM_MODEL


def azure_chat_open_ai(**kwargs) -> ChatOpenAI:
    return AzureChatOpenAI(**kwargs)


class LLMModel:
    _model: ChatOpenAI = None
    # 所支持的模型和对应的构造函数
    _support_model_function = {
        "AzureChatOpenAI": azure_chat_open_ai
    }

    @classmethod
    def get_model(cls) -> ChatOpenAI:
        if cls._model is None:
            model_config = LLM_MODEL_DICT.get(LLM_MODEL, None)
            if model_config is None:
                raise ValueError("LLM_MODEL_DICT中未找到对应的模型配置")
            constructor_function = cls._support_model_function.get(LLM_MODEL)
            cls._model = constructor_function(**model_config)
        return cls._model


if __name__ == '__main__':
    config = {
        "openai_api_key": '1bfd2fc2b23c4539b4eeb9834a66fd8e',
        "openai_api_base": "https://codedog.openai.azure.com",
        "model": "gpt-3.5-turbo",
        "deployment_name": "gpt-35-turbo",
        "openai_api_version": "2023-05-15",
        "temperature": 0
    }
    llm35 = AzureChatOpenAI(**config)
    prompt_template = PromptTemplate(template="My name is {name}, this is a test.", input_variables=["name"])
    chain = LLMChain(llm=llm35, prompt=prompt_template)
    print(chain.predict(name="infobase"))
