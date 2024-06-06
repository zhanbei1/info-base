#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
=================================================
@Project -> File   ：infobase -> inverted_index_util
@IDE    ：PyCharm
@Author ：Desmond.zhan
@Date   ：2023/11/22 09:32
@Desc   ：构建倒排索引和
==================================================
"""
import glob
import os

from tqdm import tqdm

from infobase.configs import logger, FILE_THRESHOLD
from infobase.lexical_search import snippets_to_docs, CustomIndex
from infobase.model import Snippet, BaseConfig
from infobase.utils.file_utils import read_file, file_chunk_node


def filter_file(directory, file, config: BaseConfig):
    """
    Check if a file should be filtered based on its size and other criteria.

    Args:
        file (str): The path to the file.
        config (SweepConfig): The configuration object.

    Returns:
        bool: True if the file should be included, False otherwise.
    """
    for ext in config.exclude_exts:
        if file.endswith(ext):
            return False
    for dir_name in config.exclude_dirs:
        if file[len(directory) + 1:].startswith(dir_name):
            return False
    if not os.path.isfile(file):
        return False
    with open(file, "rb") as f:
        is_binary = False
        for block in iter(lambda: f.read(1024), b""):
            if b"\0" in block:
                is_binary = True
                break
        if is_binary:
            return False

    with open(file, "rb") as f:
        if os.stat(file).st_size > 240000:
            return False
    return True


def repo_to_chunks(
        directory: str, config: BaseConfig
) -> tuple[list[Snippet], list[str]]:
    dir_file_count = {}

    def is_dir_too_big(file_name):
        dir_name = os.path.dirname(file_name)
        only_file_name = file_name[: len(directory)]
        if (
                only_file_name == "node_modules"
                or only_file_name == "venv"
                or only_file_name == "patch"
        ):
            return True
        if dir_name not in dir_file_count:
            dir_file_count[dir_name] = len(os.listdir(dir_name))
        return dir_file_count[dir_name] > FILE_THRESHOLD

    logger.info(f"Reading files from {directory}")

    file_list = glob.iglob(f"{directory}/**", recursive=True)
    file_list = [
        file_name
        for file_name in file_list
        if filter_file(directory, file_name, config) and not is_dir_too_big(file_name)
    ]
    logger.info(f"Found {len(file_list)} files")
    all_chunks = []
    for file_path in tqdm(file_list, desc="Reading files"):
        file_contents = read_file(file_path)
        chunks = file_chunk_node(file_contents, path=file_path, base_config=config)
        all_chunks = all_chunks + chunks
    return all_chunks, file_list


def prepare_index_from_snippets(snippets, len_repo_cache_dir=0):
    '''
    从片段准备索引。

    :param snippets: 片段对象列表。
    :param len_repo_cache_dir: 仓库缓存目录的长度。
    :return: 索引。
    '''
    # Convert the snippets to documents
    all_docs = snippets_to_docs(snippets, len_repo_cache_dir)
    # If there are no documents, return None
    if len(all_docs) == 0:
        return None
    # Create the index based on the schema
    index = CustomIndex()
    try:
        # Iterate through the documents and add them to the index
        for doc in tqdm(all_docs, total=len(all_docs)):
            index.add_document(
                title=f"{doc.title}:{doc.start}:{doc.end}", content=doc.content
            )
    # If a FileNotFoundError is thrown, log it
    except FileNotFoundError as e:
        logger.error(e)

    # Return the index
    return index


def prepare_lexical_search_index(repo_path, config, repo_full_name):
    """
   准备词法搜索索引

   Args:
       repo_path (str): 克隆的存储库对象
       config (BaseConfig): 清理配置对象
       repo_full_name (str): 存储库的完整名称

   Returns:
       file_list (list): 文件列表
       snippets (list): 拆分后的代码片段列表
       index (object): 词法搜索索引对象
   """
    snippets, file_list = repo_to_chunks(repo_path, config)
    logger.info(f"Found {len(snippets)} snippets in repository {repo_full_name}")
    # prepare lexical search
    index = prepare_index_from_snippets(
        snippets, len_repo_cache_dir=len(repo_path) + 1
    )
    logger.info("Prepared index from snippets")
    return file_list, snippets, index
