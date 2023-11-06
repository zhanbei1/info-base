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

import ujson

from infobase.code_database_demo import ProjectCodeDescTree


def test_split_code_file():
    project = ProjectCodeDescTree(project_path="/Users/zhanbei/IdeaProjects/EvalEx")
    desc = project.constructDescriptionTree(
        "/Users/zhanbei/IdeaProjects/EvalEx/src/main/java/com/ezylang/evalex/functions/trigonometric/AsinFunction.java")
    print(desc.dict())



