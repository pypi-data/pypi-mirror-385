"""Loppers: Extract source file skeletons using tree-sitter queries.

Remove function implementations while preserving structure using AST queries.
Compatible with tree-sitter >= 0.25
"""

from __future__ import annotations

from loppers.extensions import EXTENSION_TO_LANGUAGE, get_language
from loppers.source_utils import (
    concatenate_files,
    extract_skeleton,
    find_files,
    get_skeleton,
    get_tree,
)

__all__ = [
    "EXTENSION_TO_LANGUAGE",
    "concatenate_files",
    "extract_skeleton",
    "find_files",
    "get_language",
    "get_skeleton",
    "get_tree",
]
