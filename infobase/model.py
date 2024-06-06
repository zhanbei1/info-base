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
from urllib.parse import quote
from pydantic import BaseModel, Field
from tree_sitter import Parser, Language

from infobase.configs import IGNORE_PATH, CODE_TYPE_FILE_SUFFIX_MAPPING, SUPPORT_LANGUAGE_DEFINITION_TYPE


class ChatRequestInput(BaseModel):
    collection_name: str = Field(description="collection name")
    output_language: str = Field(default="Chinese")
    query: str = Field(description="query", default=None)


class BaseConfig(BaseModel):
    extension_to_language = {
        # "js": "tsx",
        # "jsx": "tsx",
        # "ts": "tsx",
        # "tsx": "tsx",
        # "mjs": "tsx",
        "py": "python",
        # "rs": "rust",
        # "go": "go",
        "java": "java",
        # "cpp": "cpp",
        # "cc": "cpp",
        # "cxx": "cpp",
        # "c": "cpp",
        # "h": "cpp",
        # "hpp": "cpp",
        # "cs": "cpp",
        # "rb": "ruby",
        # "md": "markdown",
        # "rst": "markdown",
        # "txt": "markdown",
        # "erb": "embedded-template",
        # "ejs": "embedded-template",
        # "html": "embedded-template",
        # "erb": "html",
        # "ejs": "html",
        # "html": "html",
        # "vue": "html",
        # "php": "php",
    }
    include_dirs: list[str] = []
    exclude_dirs: list[str] = [
        ".git",
        "node_modules",
        "venv",
        "patch",
        "packages/blobs",
        ".classpath",
        ".eclipse",
        ".gradle",
        ".idea",
        ".mvn",
        ".project",
        ".settings",
        ".vscode",
        "bin",
        "build",
        "doc",
        "logs",
        "out",
        "target"
    ]
    include_exts: list[str] = [
        ".cs",
        ".csharp",
        ".py",
        ".md",
        ".txt",
        ".ts",
        ".tsx",
        ".js",
        ".jsx",
        ".mjs",
        ".java"
    ]
    exclude_exts: list[str] = IGNORE_PATH
    # Image formats
    max_file_limit: int = 60_000
    # 需要排除的开发语言的关键词
    exclude_words = {
        "java": ["abstract", "assert", "boolean", "break", "byte", "case", "catch", "char", "class", "const",
                 "continue", "default", "do", "double", "else", "enum", "extends", "final", "finally", "float", "for",
                 "if", "goto", "implements", "import", "instanceof", "int", "interface", "long", "native", "new",
                 "package", "private", "protected", "public", "return", "short", "static", "strictfp", "super",
                 "switch", "synchronized", "this", "throw", "throws", "transient", "try", "typeof", "var", "void",
                 "volatile", "while"],
        "python": ["and", "as", "assert", "break", "class", "continue", "def", "del", "elif", "else", "except",
                   "finally", "for", "from", "global", "if", "import", "in", "is", "lambda", "nonlocal", "pass",
                   "raise", "return", "try", "while", "with", "yield"],
        "go": ["break", "case", "chan", "const", "continue", "default", "defer", "else", "for", "func", "go", "goto",
               "if", "import", "interface", "map", "package", "range", "return", "select", "struct", "switch", "type",
               "var"],
        "c": ["auto", "void", "char", "const", "double", "float", "int", "long", "short", "signed", "unsigned",
              "struct", "union", "enum", "typedef", "sizeof", "const_cast", "dynamic_cast", "reinterpret_cast",
              "static_cast"],
        "c++": ["auto", "bool", "break", "case", "char", "class", "const", "const_cast", "continue", "default",
                "delete", "do", "double", "dynamic_cast", "else", "enum", "explicit", "extern", "float", "for",
                "friend", "goto", "if", "inline", "int", "long", "mutable", "namespace", "new", "private", "protected",
                "public", "register", "reinterpret_cast", "return", "short", "signed", "sizeof", "static",
                "static_cast", "struct", "switch", "template", "this", "throw", "try", "typedef", "typeid", "typename",
                "union", "unsigned", "using", "virtual", "void", "volatile", "wchar_t"],
        "shell": ["alias", "break", "continue", "declare", "echo", "else", "elif", "export", "false", "for", "function",
                  "if", "local", "readonly", "return", "select", "shift", "then", "time", "trap", "true", "while"],
    }

    exclude_words["all_set"] = set([item for sublist in exclude_words.values() for item in sublist])


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


class Snippet(BaseModel):
    """
    Start and end refer to line numbers
    """

    content: str
    start: int
    end: int
    file_path: str

    def __eq__(self, other):
        if isinstance(other, Snippet):
            return (
                    self.file_path == other.file_path
                    and self.start == other.start
                    and self.end == other.end
            )
        return False

    def __hash__(self):
        return hash((self.file_path, self.start, self.end))

    def get_snippet(self, add_ellipsis: bool = True, add_lines: bool = True):
        lines = self.content.splitlines()
        snippet = "\n".join(
            (f"{i + self.start}: {line}" if add_lines else line)
            for i, line in enumerate(lines[max(self.start - 1, 0): self.end])
        )
        if add_ellipsis:
            if self.start > 1:
                snippet = "...\n" + snippet
            if self.end < self.content.count("\n") + 1:
                snippet = snippet + "\n..."
        return snippet

    def __add__(self, other):
        assert self.content == other.content
        assert self.file_path == other.file_path
        return Snippet(
            content=self.content,
            start=self.start,
            end=other.end,
            file_path=self.file_path,
        )

    def __xor__(self, other: "Snippet") -> bool:
        """
        Returns True if there is an overlap between two snippets.
        """
        if self.file_path != other.file_path:
            return False
        return self.file_path == other.file_path and (
                (self.start <= other.start <= self.end)
                or (other.start <= self.start <= other.end)
        )

    def __or__(self, other: "Snippet") -> "Snippet":
        assert self.file_path == other.file_path
        return Snippet(
            content=self.content,
            start=min(self.start, other.start),
            end=max(self.end, other.end),
            file_path=self.file_path,
        )

    @property
    def xml(self):
        return f"""<snippet source="{self.file_path}:{self.start}-{self.end}">\n{self.get_snippet()}\n</snippet>"""

    def get_url(self, repo_name: str, commit_id: str = "main"):
        num_lines = self.content.count("\n") + 1
        encoded_file_path = quote(self.file_path, safe="/")
        return f"https://github.com/{repo_name}/blob/{commit_id}/{encoded_file_path}#L{max(self.start, 1)}-L{min(self.end, num_lines)}"

    def get_markdown_link(self, repo_name: str, commit_id: str = "main"):
        num_lines = self.content.count("\n") + 1
        base = commit_id + "/" if commit_id != "main" else ""
        return f"[{base}{self.file_path}#L{max(self.start, 1)}-L{min(self.end, num_lines)}]({self.get_url(repo_name, commit_id)})"

    def get_slack_link(self, repo_name: str, commit_id: str = "main"):
        num_lines = self.content.count("\n") + 1
        base = commit_id + "/" if commit_id != "main" else ""
        return f"<{self.get_url(repo_name, commit_id)}|{base}{self.file_path}#L{max(self.start, 1)}-L{min(self.end, num_lines)}>"

    def get_preview(self, max_lines: int = 5):
        snippet = "\n".join(
            self.content.splitlines()[
            self.start: min(self.start + max_lines, self.end)
            ]
        )
        if self.start > 1:
            snippet = "\n" + snippet
        if self.content.count("\n") + 1 > self.end > max_lines:
            snippet = snippet + "\n"
        return snippet

    def expand(self, num_lines: int = 25):
        return Snippet(
            content=self.content,
            start=max(self.start - num_lines, 1),
            end=min(self.end + num_lines, self.content.count("\n") + 1),
            file_path=self.file_path,
        )

    @property
    def denotation(self):
        return f"{self.file_path}:{self.start}-{self.end}"
