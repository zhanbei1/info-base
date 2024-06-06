#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
=================================================
@Project -> File   ：infobase -> dir_tree_util
@IDE    ：PyCharm
@Author ：Desmond.zhan
@Date   ：2024/1/17 19:47
@Desc   ：
==================================================
"""
import fnmatch

from infobase.configs import IGNORE_PATH, logger

max_n = 12


def generate_tree(pathname, n=0):
    global tree_str

    if n >= max_n:
        return

    for pattern in IGNORE_PATH:
        if fnmatch.fnmatch(pathname.name.split("/")[-1], pattern):
            logger.info(f"忽略文件夹：{pathname.name}")
            return None

    if pathname.is_file():
        tree_str += '    |' * n + '-' * 4 + pathname.name + '\n'
    elif pathname.is_dir():
        tree_str += '    |' * n + '-' * 4 + \
                    str(pathname.relative_to(pathname.parent)) + '\\' + '\n'
        for cp in pathname.iterdir():
            generate_tree(cp, n + 1)


if __name__ == '__main__':
    import pathlib

    tree_str = ""
    pathname = pathlib.Path('/Users/zhanbei/IdeaProjects/doop-server/doop-starter/src')
    generate_tree(pathname)
    print(tree_str)
