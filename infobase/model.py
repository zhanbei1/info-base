#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
=================================================
@Project -> File   ：infobase -> model
@IDE    ：PyCharm
@Author ：Desmond.zhan
@Date   ：2023/11/15 18:00
@Desc   ：
==================================================
"""
from pydantic import BaseModel, Field


class ChatRequestInput(BaseModel):
    collection_name: str = Field(description="collection name")
    output_language: str = Field(default="Chinese")
    query: str = Field(description="query", default=None)
