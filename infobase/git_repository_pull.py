#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
=================================================
@Project -> File   ：infobase -> git_repository_pull
@IDE    ：PyCharm
@Author ：Desmond.zhan
@Date   ：2023/10/19 16:30
@Desc   ：git仓库下拉到本地
==================================================
"""
import os
import shutil

from infobase.configs import GIT_CLONE_PATH, logger
from git import Repo, Tree, GitCommandError


class GitRepositoryPull:
    def __init__(self, git_url: str, git_username=None, git_password=None, git_access_token=None):
        self.git_url = git_url
        self.git_username = git_username
        self.git_password = git_password
        self.git_access_token = git_access_token
        self.repo: Repo = self.git_clone_by_password() if git_username is not None and git_password is not None else self.git_clone_by_access_token()

    def git_clone_by_access_token(self) -> Repo:
        """
        仓库下拉到本地 指定目录下
        """
        try:
            # 仓库下拉到本地
            return Repo.clone_from(url=self.git_url, to_path=GIT_CLONE_PATH,
                                   env={'GIT_ASKPASS': 'echo', 'GIT_USERNAME': 'token',
                                        'GIT_PASSWORD': self.git_access_token})
        except BaseException as e:
            logger.error("git仓库下拉到本地失败, error info: %s", e.__str__())

    def git_clone_by_password(self) -> Repo | None:
        """
        git仓库下拉到本地
        """
        try:
            if self.git_url.startswith("http://"):
                request_url = self.git_url.replace("http://",
                                                   "http://" + self.git_username + ":" + self.git_password + "@")
            elif self.git_url.startswith("https://"):
                request_url = self.git_url.replace("https://",
                                                   "https://" + self.git_username + ":" + self.git_password + "@")
            else:
                logger.error("git仓库地址错误, 请检查")
                raise ConnectionError(f"Git仓库地址错误, 请检查")

            # 仓库下拉到本地
            repo_dir = self.git_url.split("/")[-1].replace(".git", "")
            if os.path.exists(GIT_CLONE_PATH + repo_dir):
                shutil.rmtree(GIT_CLONE_PATH + repo_dir)
            return Repo.clone_from(url=request_url, to_path=GIT_CLONE_PATH + repo_dir)
        except GitCommandError as error:
            logger.error("git仓库下拉到本地失败, error info: %s", error.stdout)
            raise error

    def git_commits_log(self, max_count: int = None) -> list[str]:
        """
        获取仓库的提交记录
        :param max_count: 获取的提交记录条数
        :return: 提交记录
        """
        # 获取commit提交记录
        if max_count is not None:
            prev_commits = list(self.repo.iter_commits(all=True, max_count=max_count))
        else:
            prev_commits = list(self.repo.iter_commits(all=True))

        # 返回commit提交记录的log文本
        return [commit.message for commit in prev_commits]

    def git_file_tree(self) -> str:
        """
        获取仓库的文件树
        :return: 文件树字符串
        """

        # 根据最后一次commit，构建这个仓库的文件树
        def print_files_from_git(root, level=0) -> str:
            """"
            :param root: 根节点
            :param level: 层级
            :return: 本层级的文件树字符串
            """
            tree_str = ""
            for entry in root:
                tree_str += f'{"-" * 4 * level}| {entry.path}, {entry.type} \n'
                if entry.type == "tree":
                    next_level_file_tree = print_files_from_git(entry, level + 1)
                    tree_str += next_level_file_tree
            return tree_str

        # 获取最后一次commit
        latest_commits = list(self.repo.iter_commits(all=True, max_count=1))
        latest_commit_tree: Tree = latest_commits[0].tree

        repo_file_tree = print_files_from_git(latest_commit_tree, 0)

        return repo_file_tree

    def get_branches(self) -> list:
        return list(self.repo.branches)

    def construct_markdown(self) -> str:
        """
        构建所有已知的git仓库信息，形成markdown
        :return: markdown格式的str
        """
        commit_log: list = self.git_commits_log()
        file_tree: str = self.git_file_tree()
        branches: list = self.get_branches()

        return GIT_INFO_MARKDOWN_TEMPLATE.format(commit_log="\n".join(commit_log), file_tree=file_tree,
                                                 branches=branches)


GIT_INFO_MARKDOWN_TEMPLATE = """
# Repository commit logs
{commit_log}

# Repository file tree 
{file_tree}

# Repository branches
{branches}

"""
