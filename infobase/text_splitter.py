"""Text splitter implementations."""
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from langchain.callbacks.manager import CallbackManager
from langchain.text_splitter import TextSplitter
from tree_sitter import Language, Parser


@dataclass
class TextSplit:
    """Text split with overlap.

    Attributes:
        text_chunk: The text string.
        num_char_overlap: The number of overlapping characters with the previous chunk.
    """

    text_chunk: str
    num_char_overlap: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class CodeSplitter(TextSplitter):
    """Split code using a AST parser.

    Thank you to Kevin Lu / SweepAI for suggesting this elegant code splitting solution.
    https://docs.sweep.dev/blogs/chunking-2m-files
    """

    def __init__(
            self,
            language: str,
            chunk_lines: int = 200,
            chunk_lines_overlap: int = 15,
            max_chars: int = 1500,
            callback_manager: Optional[CallbackManager] = None,
            exclude_node_type: list[str] = None
    ):
        self.language = language
        self.chunk_lines = chunk_lines
        self.chunk_lines_overlap = chunk_lines_overlap
        self.max_chars = max_chars
        self.callback_manager = callback_manager or CallbackManager([])
        self.java_language = Language('/Users/zhanbei/PycharmProjects/infobase/build/local-support-languages.so',
                                      'java')
        self.py_language = Language('/Users/zhanbei/PycharmProjects/infobase/build/local-support-languages.so',
                                    'python')

    def _get_parser_by_language(self, language: str):
        if language == "java":
            parser = Parser()
            parser.set_language(self.java_language)
            return parser
        elif language == "python":
            parser = Parser()
            parser.set_language(self.py_language)
            return parser

    def _chunk_node(self, node: Any, text: str, last_end: int = 0) -> List[str]:
        new_chunks = []
        current_chunk = ""
        for child in node.children:
            if child.end_byte - child.start_byte > self.max_chars:
                # Child is too big, recursively chunk the child
                if len(current_chunk) > 0:
                    new_chunks.append(current_chunk)
                current_chunk = ""
                new_chunks.extend(self._chunk_node(child, text, last_end))
            elif (
                    len(current_chunk) + child.end_byte - child.start_byte > self.max_chars
            ):
                # Child would make the current chunk too big, so start a new chunk
                new_chunks.append(current_chunk)
                current_chunk = text[last_end: child.end_byte]
            else:
                current_chunk += text[last_end: child.end_byte]
            last_end = child.end_byte
        if len(current_chunk) > 0:
            new_chunks.append(current_chunk)
        return new_chunks


    def split_text(self, text: str) -> List[str]:
        """Split incoming code and return chunks using the AST."""

        try:
            parser = self._get_parser_by_language(self.language)
        except Exception as e:
            print(
                f"Could not get parser for language {self.language}. Check "
                "https://github.com/grantjenks/py-tree-sitter-languages#license "
                "for a list of valid languages."
            )
            raise e

        tree = parser.parse(bytes(text, "utf-8"))

        if (
                not tree.root_node.children
                or tree.root_node.children[0].type != "ERROR"
        ):
            chunks = [
                chunk.strip() for chunk in self._chunk_node(tree.root_node, text)
            ]

            return chunks
        else:
            raise ValueError(f"Could not parse code with language {self.language}.")

        # TODO: set up auto-language detection using something like https://github.com/yoeo/guesslang.


__all__ = ["TextSplitter", "CodeSplitter"]
