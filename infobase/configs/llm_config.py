#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# 大语言模型相关配置
# --------------------- 大模型基础配置 ---------------------
CHAIN_VERBOSE = True

# --------------------- embedding 配置 ---------------------
# 选用的 Embedding 名称
EMBEDDING_MODEL = "m3e-small"
# Embedding 模型运行设备。设为"auto"会自动检测，也可手动设定为"cuda","mps","cpu"其中之一。
EMBEDDING_DEVICE = "cpu"
EMBEDDING_MODEL_DICT = {
    "m3e-small": "../models/moka-ai/m3e-small",
}

# --------------------- 对话大模型 配置 ---------------------
# 对话大模型
LLM_MODEL_DICT = {
    # 线上模型。当前支持智谱AI。
    # 如果没有设置有效的local_model_path，则认为是在线模型API。
    # 请在server_config中为每个在线API设置不同的端口
    # 具体注册及api key获取请前往 http://open.bigmodel.cn
    "AzureChatOpenAI": {
        "openai_api_base": "https://codedog.openai.azure.com",
        "openai_api_key": "1bfd2fc2b23c4539b4eeb9834a66fd8e",
        "model": "gpt-3.5-turbo",
        "deployment_name": "gpt-35-turbo",
        "openai_api_version": "2023-05-15",
        "temperature": 0
        # 可选包括 "chatglm_lite", "chatglm_std", "chatglm_pro"
    }
}

# LLM 名称
LLM_MODEL = "AzureChatOpenAI"
