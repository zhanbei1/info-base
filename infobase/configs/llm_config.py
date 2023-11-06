#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# 大语言模型相关配置

# --------------------- embedding 配置 ---------------------
# 选用的 Embedding 名称
EMBEDDING_MODEL = "m3e-small"
# Embedding 模型运行设备。设为"auto"会自动检测，也可手动设定为"cuda","mps","cpu"其中之一。
EMBEDDING_DEVICE = "cpu"
EMBEDDING_MODEL_DICT = {
    "m3e-small": "/root/desmond_zhan/hugginface/m3e-small",
}
