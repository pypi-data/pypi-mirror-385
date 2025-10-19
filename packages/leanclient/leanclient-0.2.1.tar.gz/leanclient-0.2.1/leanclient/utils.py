# Varia to be sorted later...
from dataclasses import dataclass
from functools import wraps
from typing import Tuple

# Mapping SymbolKinds ints to string names:
# https://github.com/leanprover/lean4/blob/8422d936cff3b609bd2a1396e82356c82c383386/src/Lean/Data/Lsp/LanguageFeatures.lean#L202C1-L229C27
SYMBOL_KIND_MAP = {
    1: "file",
    2: "module",
    3: "namespace",
    4: "package",
    5: "class",
    6: "method",
    7: "property",
    8: "field",
    9: "constructor",
    10: "enum",
    11: "interface",
    12: "function",
    13: "variable",
    14: "constant",
    15: "string",
    16: "number",
    17: "boolean",
    18: "array",
    19: "object",
    20: "key",
    21: "null",
    22: "enumMember",
    23: "struct",
    24: "event",
    25: "operator",
    26: "typeParameter",
}


class SemanticTokenProcessor:
    """Converts semantic token response using a token legend.

    This function is a reverse translation of the LSP specification:
    `Semantic Tokens Full Request <https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/#semanticTokens_fullRequest>`_

    Token modifiers are ignored for speed gains, since they are not used. See: `LanguageFeatures.lean <https://github.com/leanprover/lean4/blob/10b2f6b27e79e2c38d4d613f18ead3323a58ba4b/src/Lean/Data/Lsp/LanguageFeatures.lean#L360>`_
    """

    def __init__(self, token_types: list[str]):
        self.token_types = token_types

    def __call__(self, raw_response: list[int]) -> list:
        return self._process_semantic_tokens(raw_response)

    def _process_semantic_tokens(self, raw_response: list[int]) -> list:
        tokens = []
        line = char = 0
        it = iter(raw_response)
        types = self.token_types
        for d_line, d_char, length, token, __ in zip(it, it, it, it, it):
            line += d_line
            char = char + d_char if d_line == 0 else d_char
            tokens.append([line, char, length, types[token]])
        return tokens


def normalize_newlines(text: str) -> str:
    """Convert CRLF sequences to LF for stable indexing."""
    return text.replace("\r\n", "\n")


def _index_from_line_character(text: str, line: int, character: int) -> int:
    if line < 0:
        return 0

    lines = text.split("\n")
    if line >= len(lines):
        return len(text)

    prefix = sum(len(lines[i]) + 1 for i in range(line))
    return prefix + max(character, 0)


@dataclass(frozen=True)
class DocumentContentChange:
    """Represents a change in a document."""

    text: str
    start: Tuple[int, int] | None = None
    end: Tuple[int, int] | None = None

    def __post_init__(self) -> None:
        normalized_text = normalize_newlines(self.text)
        object.__setattr__(self, "text", normalized_text)

        if (self.start is None) != (self.end is None):
            raise ValueError(
                "DocumentContentChange requires both start and end for ranged edits."
            )

        if self.start is not None:
            start = tuple(int(v) for v in self.start)
            if len(start) != 2:
                raise ValueError("start must be a (line, character) pair")
            object.__setattr__(self, "start", start)
        if self.end is not None:
            end = tuple(int(v) for v in self.end)
            if len(end) != 2:
                raise ValueError("end must be a (line, character) pair")
            object.__setattr__(self, "end", end)

    def is_full_change(self) -> bool:
        return self.start is None

    def get_dict(self) -> dict:
        if self.is_full_change():
            return {"text": self.text}

        assert self.start is not None and self.end is not None
        return {
            "text": self.text,
            "range": {
                "start": {"line": self.start[0], "character": self.start[1]},
                "end": {"line": self.end[0], "character": self.end[1]},
            },
        }


def apply_changes_to_text(text: str, changes: list[DocumentContentChange]) -> str:
    """Apply LSP-style incremental changes to ``text``."""

    text = normalize_newlines(text)
    if not changes:
        return text

    for change in changes:
        if change.is_full_change():
            text = change.text
            continue

        assert change.start is not None and change.end is not None
        start_idx = _index_from_line_character(text, change.start[0], change.start[1])
        end_idx = _index_from_line_character(text, change.end[0], change.end[1])
        text = text[:start_idx] + change.text + text[end_idx:]

    return text


def get_diagnostics_in_range(
    diagnostics: list,
    start_line: int,
    end_line: int,
) -> list:
    """Find overlapping diagnostics for a range of lines.

    Args:
        diagnostics (list): List of diagnostics.
        start_line (int): Start line.
        end_line (int): End line.

    Returns:
        list: Overlapping diagnostics.
    """
    return [
        diag
        for diag in diagnostics
        if diag["range"]["start"]["line"] <= end_line
        and diag["range"]["end"]["line"] >= start_line
    ]


def experimental(func):
    """Decorator to mark a method as experimental."""

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self.print_warnings:
            print(
                f"Warning: {func.__name__}() is experimental! Set print_warnings=False to mute."
            )
        return func(self, *args, **kwargs)

    # Change __doc__ to include a sphinx warning
    warning = "\n        .. admonition:: Experimental\n\n            This method is experimental. Use with caution.\n"
    doc_lines = wrapper.__doc__.split("\n")
    doc_lines.insert(1, warning)
    wrapper.__doc__ = "\n".join(doc_lines)
    return wrapper
