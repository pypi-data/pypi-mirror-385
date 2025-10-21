"""SQL statement splitter with caching and dialect support.

This module provides SQL script statement splitting functionality
with support for multiple SQL dialects and caching for performance.

Components:
    StatementSplitter: Main SQL script splitter with caching
    DialectConfig: Base class for dialect-specific configurations
    Token/TokenType: Token representation and classification
    Caching: Pattern and result caching for performance

Supported dialects include Oracle PL/SQL, T-SQL, PostgreSQL,
MySQL, SQLite, DuckDB, and BigQuery.
"""

import re
import threading
from abc import ABC, abstractmethod
from collections.abc import Callable, Generator
from enum import Enum
from re import Pattern
from typing import Any, Final, TypeAlias, cast

from mypy_extensions import mypyc_attr

from sqlspec.core.cache import CacheKey, UnifiedCache
from sqlspec.utils.logging import get_logger

__all__ = (
    "DialectConfig",
    "OracleDialectConfig",
    "PostgreSQLDialectConfig",
    "StatementSplitter",
    "TSQLDialectConfig",
    "Token",
    "TokenType",
    "split_sql_script",
)

logger = get_logger("sqlspec.core.splitter")

DEFAULT_PATTERN_CACHE_SIZE: Final = 1000
DEFAULT_RESULT_CACHE_SIZE: Final = 5000
DEFAULT_CACHE_TTL: Final = 3600

DIALECT_CONFIG_SLOTS: Final = (
    "_block_starters",
    "_block_enders",
    "_statement_terminators",
    "_batch_separators",
    "_special_terminators",
    "_max_nesting_depth",
    "_name",
)

TOKEN_SLOTS: Final = ("type", "value", "line", "column", "position")

SPLITTER_SLOTS: Final = (
    "_dialect",
    "_strip_trailing_semicolon",
    "_token_patterns",
    "_compiled_patterns",
    "_pattern_cache_key",
    "_result_cache",
    "_pattern_cache",
)


class TokenType(Enum):
    """Types of tokens recognized by the SQL lexer."""

    COMMENT_LINE = "COMMENT_LINE"
    COMMENT_BLOCK = "COMMENT_BLOCK"
    STRING_LITERAL = "STRING_LITERAL"
    QUOTED_IDENTIFIER = "QUOTED_IDENTIFIER"
    KEYWORD = "KEYWORD"
    TERMINATOR = "TERMINATOR"
    BATCH_SEPARATOR = "BATCH_SEPARATOR"
    WHITESPACE = "WHITESPACE"
    OTHER = "OTHER"


@mypyc_attr(allow_interpreted_subclasses=False)
class Token:
    """SQL token with metadata."""

    __slots__ = TOKEN_SLOTS

    def __init__(self, type: TokenType, value: str, line: int, column: int, position: int) -> None:
        self.type = type
        self.value = value
        self.line = line
        self.column = column
        self.position = position

    def __repr__(self) -> str:
        return f"Token({self.type.value}, {self.value!r}, {self.line}:{self.column})"


TokenHandler: TypeAlias = Callable[[str, int, int, int], Token | None]
TokenPattern: TypeAlias = str | TokenHandler
CompiledTokenPattern: TypeAlias = Pattern[str] | TokenHandler


@mypyc_attr(allow_interpreted_subclasses=False)
class DialectConfig(ABC):
    """Abstract base class for SQL dialect configurations."""

    __slots__ = DIALECT_CONFIG_SLOTS

    def __init__(self) -> None:
        """Initialize dialect configuration."""
        self._name: str | None = None
        self._block_starters: set[str] | None = None
        self._block_enders: set[str] | None = None
        self._statement_terminators: set[str] | None = None
        self._batch_separators: set[str] | None = None
        self._special_terminators: dict[str, Callable[[list[Token], int], bool]] | None = None
        self._max_nesting_depth: int | None = None

    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the dialect (e.g., 'oracle', 'tsql')."""

    @property
    @abstractmethod
    def block_starters(self) -> set[str]:
        """Keywords that start a block (e.g., BEGIN, DECLARE)."""

    @property
    @abstractmethod
    def block_enders(self) -> set[str]:
        """Keywords that end a block (e.g., END)."""

    @property
    @abstractmethod
    def statement_terminators(self) -> set[str]:
        """Characters that terminate statements (e.g., ;)."""

    @property
    def batch_separators(self) -> set[str]:
        """Keywords that separate batches (e.g., GO for T-SQL)."""
        if self._batch_separators is None:
            self._batch_separators = set()
        return self._batch_separators

    @property
    def special_terminators(self) -> dict[str, Callable[[list[Token], int], bool]]:
        """Special terminators that need custom handling."""
        if self._special_terminators is None:
            self._special_terminators = {}
        return self._special_terminators

    @property
    def max_nesting_depth(self) -> int:
        """Maximum allowed nesting depth for blocks."""
        if self._max_nesting_depth is None:
            self._max_nesting_depth = 256
        return self._max_nesting_depth

    def get_all_token_patterns(self) -> list[tuple[TokenType, TokenPattern]]:
        """Get the complete ordered list of token patterns for this dialect.

        Returns:
            List of tuples containing token types and their regex patterns
        """
        patterns: list[tuple[TokenType, TokenPattern]] = [
            (TokenType.COMMENT_LINE, r"--[^\n]*"),
            (TokenType.COMMENT_BLOCK, r"/\*[\s\S]*?\*/"),
            (TokenType.STRING_LITERAL, r"'(?:[^']|'')*'"),
            (TokenType.QUOTED_IDENTIFIER, r'"[^"]*"|\[[^\]]*\]'),
        ]

        patterns.extend(self._get_dialect_specific_patterns())

        all_keywords = self.block_starters | self.block_enders | self.batch_separators
        if all_keywords:
            sorted_keywords = sorted(all_keywords, key=len, reverse=True)
            patterns.append((TokenType.KEYWORD, r"\b(" + "|".join(re.escape(kw) for kw in sorted_keywords) + r")\b"))

        all_terminators = self.statement_terminators | set(self.special_terminators.keys())
        if all_terminators:
            patterns.append((TokenType.TERMINATOR, "|".join(re.escape(t) for t in all_terminators)))

        patterns.extend([(TokenType.WHITESPACE, r"\s+"), (TokenType.OTHER, r".")])

        return patterns

    def _get_dialect_specific_patterns(self) -> list[tuple[TokenType, TokenPattern]]:
        """Get dialect-specific token patterns.

        Returns:
            List of dialect-specific token patterns
        """
        return []

    @staticmethod
    def is_real_block_ender(tokens: list[Token], current_pos: int) -> bool:  # noqa: ARG004
        """Check if END keyword represents an actual block terminator.

        Args:
            tokens: List of all tokens
            current_pos: Position of END token

        Returns:
            True if END represents a block terminator, False otherwise
        """
        return True

    def should_delay_semicolon_termination(self, tokens: list[Token], current_pos: int) -> bool:
        """Check if semicolon termination should be delayed.

        Args:
            tokens: List of all tokens
            current_pos: Current position in token list

        Returns:
            True if termination should be delayed, False otherwise
        """
        return False


class OracleDialectConfig(DialectConfig):
    """Configuration for Oracle PL/SQL dialect."""

    @property
    def name(self) -> str:
        if self._name is None:
            self._name = "oracle"
        return self._name

    @property
    def block_starters(self) -> set[str]:
        if self._block_starters is None:
            self._block_starters = {"BEGIN", "DECLARE", "CASE"}
        return self._block_starters

    @property
    def block_enders(self) -> set[str]:
        if self._block_enders is None:
            self._block_enders = {"END"}
        return self._block_enders

    @property
    def statement_terminators(self) -> set[str]:
        if self._statement_terminators is None:
            self._statement_terminators = {";"}
        return self._statement_terminators

    @property
    def special_terminators(self) -> dict[str, Callable[[list[Token], int], bool]]:
        if self._special_terminators is None:
            self._special_terminators = {"/": self._handle_slash_terminator}
        return self._special_terminators

    def should_delay_semicolon_termination(self, tokens: list[Token], current_pos: int) -> bool:
        """Check if semicolon termination should be delayed for Oracle slash terminators.

        Args:
            tokens: List of all tokens
            current_pos: Current position in token list

        Returns:
            True if termination should be delayed, False otherwise
        """
        pos = current_pos - 1
        while pos >= 0:
            token = tokens[pos]
            if token.type == TokenType.WHITESPACE:
                pos -= 1
                continue
            if token.type == TokenType.KEYWORD and token.value.upper() == "END":
                return self._has_upcoming_slash(tokens, current_pos)
            break

        return False

    def _has_upcoming_slash(self, tokens: list[Token], current_pos: int) -> bool:
        """Check if there's a slash terminator on its own line ahead.

        Args:
            tokens: List of all tokens
            current_pos: Current position in token list

        Returns:
            True if slash terminator found on its own line, False otherwise
        """
        pos = current_pos + 1
        found_newline = False

        while pos < len(tokens):
            token = tokens[pos]
            if token.type == TokenType.WHITESPACE:
                if "\n" in token.value:
                    found_newline = True
                pos += 1
                continue
            if token.type == TokenType.TERMINATOR and token.value == "/":
                return found_newline and self._handle_slash_terminator(tokens, pos)
            if token.type in {TokenType.COMMENT_LINE, TokenType.COMMENT_BLOCK}:
                pos += 1
                continue
            break

        return False

    @staticmethod
    def is_real_block_ender(tokens: list[Token], current_pos: int) -> bool:
        """Check if END keyword represents a block terminator in Oracle PL/SQL.

        Args:
            tokens: List of all tokens
            current_pos: Position of END token

        Returns:
            True if END represents a block terminator, False otherwise
        """
        pos = current_pos + 1
        while pos < len(tokens):
            next_token = tokens[pos]

            if next_token.type == TokenType.WHITESPACE:
                pos += 1
                continue
            if next_token.type == TokenType.OTHER:
                word_chars = []
                word_pos = pos
                while word_pos < len(tokens) and tokens[word_pos].type == TokenType.OTHER:
                    word_chars.append(tokens[word_pos].value)
                    word_pos += 1

                word = "".join(word_chars).upper()
                if word in {"IF", "LOOP", "CASE", "WHILE"}:
                    return False
            break
        return True

    @staticmethod
    def _handle_slash_terminator(tokens: list[Token], current_pos: int) -> bool:
        """Check if Oracle slash terminator is properly positioned.

        Oracle slash terminators must be on their own line with only
        whitespace or comments preceding them on the same line.

        Args:
            tokens: List of all tokens
            current_pos: Position of slash token

        Returns:
            True if slash is properly positioned, False otherwise
        """
        if current_pos == 0:
            return True

        pos = current_pos - 1
        while pos >= 0:
            token = tokens[pos]
            if "\n" in token.value:
                break
            if token.type not in {TokenType.WHITESPACE, TokenType.COMMENT_LINE}:
                return False
            pos -= 1

        return True


class TSQLDialectConfig(DialectConfig):
    """Configuration for T-SQL (SQL Server) dialect."""

    @property
    def name(self) -> str:
        if self._name is None:
            self._name = "tsql"
        return self._name

    @property
    def block_starters(self) -> set[str]:
        if self._block_starters is None:
            self._block_starters = {"BEGIN", "TRY"}
        return self._block_starters

    @property
    def block_enders(self) -> set[str]:
        if self._block_enders is None:
            self._block_enders = {"END", "CATCH"}
        return self._block_enders

    @property
    def statement_terminators(self) -> set[str]:
        if self._statement_terminators is None:
            self._statement_terminators = {";"}
        return self._statement_terminators

    @property
    def batch_separators(self) -> set[str]:
        if self._batch_separators is None:
            self._batch_separators = {"GO"}
        return self._batch_separators


class PostgreSQLDialectConfig(DialectConfig):
    """Configuration for PostgreSQL dialect with dollar-quoted strings."""

    @property
    def name(self) -> str:
        if self._name is None:
            self._name = "postgresql"
        return self._name

    @property
    def block_starters(self) -> set[str]:
        if self._block_starters is None:
            self._block_starters = {"BEGIN", "DECLARE", "CASE", "DO"}
        return self._block_starters

    @property
    def block_enders(self) -> set[str]:
        if self._block_enders is None:
            self._block_enders = {"END"}
        return self._block_enders

    @property
    def statement_terminators(self) -> set[str]:
        if self._statement_terminators is None:
            self._statement_terminators = {";"}
        return self._statement_terminators

    def _get_dialect_specific_patterns(self) -> list[tuple[TokenType, TokenPattern]]:
        """Get PostgreSQL-specific token patterns.

        Returns:
        List of dialect-specific token patterns
        """
        return [(TokenType.STRING_LITERAL, self._handle_dollar_quoted_string)]

    @staticmethod
    def _handle_dollar_quoted_string(text: str, position: int, line: int, column: int) -> Token | None:
        """Handle PostgreSQL dollar-quoted string literals.

        Parses dollar-quoted strings in the format $tag$content$tag$
        where tag is optional.

        Args:
            text: The full SQL text being tokenized
            position: Current position in the text
            line: Current line number
            column: Current column number

        Returns:
            Token representing the dollar-quoted string, or None if no match
        """
        start_match = re.match(r"\$([a-zA-Z_][a-zA-Z0-9_]*)?\$", text[position:])
        if not start_match:
            return None

        tag = start_match.group(0)
        content_start = position + len(tag)

        try:
            content_end = text.index(tag, content_start)
            full_value = text[position : content_end + len(tag)]

            return Token(type=TokenType.STRING_LITERAL, value=full_value, line=line, column=column, position=position)
        except ValueError:
            return None


class GenericDialectConfig(DialectConfig):
    """Generic SQL dialect configuration for standard SQL."""

    @property
    def name(self) -> str:
        if self._name is None:
            self._name = "generic"
        return self._name

    @property
    def block_starters(self) -> set[str]:
        if self._block_starters is None:
            self._block_starters = {"BEGIN", "DECLARE", "CASE"}
        return self._block_starters

    @property
    def block_enders(self) -> set[str]:
        if self._block_enders is None:
            self._block_enders = {"END"}
        return self._block_enders

    @property
    def statement_terminators(self) -> set[str]:
        if self._statement_terminators is None:
            self._statement_terminators = {";"}
        return self._statement_terminators


class MySQLDialectConfig(DialectConfig):
    """Configuration for MySQL dialect."""

    @property
    def name(self) -> str:
        if self._name is None:
            self._name = "mysql"
        return self._name

    @property
    def block_starters(self) -> set[str]:
        if self._block_starters is None:
            self._block_starters = {"BEGIN", "DECLARE", "CASE"}
        return self._block_starters

    @property
    def block_enders(self) -> set[str]:
        if self._block_enders is None:
            self._block_enders = {"END"}
        return self._block_enders

    @property
    def statement_terminators(self) -> set[str]:
        if self._statement_terminators is None:
            self._statement_terminators = {";"}
        return self._statement_terminators

    @property
    def special_terminators(self) -> dict[str, Callable[[list[Token], int], bool]]:
        if self._special_terminators is None:
            self._special_terminators = {"\\g": lambda _tokens, _pos: True, "\\G": lambda _tokens, _pos: True}
        return self._special_terminators


class SQLiteDialectConfig(DialectConfig):
    """Configuration for SQLite dialect."""

    @property
    def name(self) -> str:
        if self._name is None:
            self._name = "sqlite"
        return self._name

    @property
    def block_starters(self) -> set[str]:
        if self._block_starters is None:
            self._block_starters = {"BEGIN", "CASE"}
        return self._block_starters

    @property
    def block_enders(self) -> set[str]:
        if self._block_enders is None:
            self._block_enders = {"END"}
        return self._block_enders

    @property
    def statement_terminators(self) -> set[str]:
        if self._statement_terminators is None:
            self._statement_terminators = {";"}
        return self._statement_terminators


class DuckDBDialectConfig(DialectConfig):
    """Configuration for DuckDB dialect."""

    @property
    def name(self) -> str:
        if self._name is None:
            self._name = "duckdb"
        return self._name

    @property
    def block_starters(self) -> set[str]:
        if self._block_starters is None:
            self._block_starters = {"BEGIN", "CASE"}
        return self._block_starters

    @property
    def block_enders(self) -> set[str]:
        if self._block_enders is None:
            self._block_enders = {"END"}
        return self._block_enders

    @property
    def statement_terminators(self) -> set[str]:
        if self._statement_terminators is None:
            self._statement_terminators = {";"}
        return self._statement_terminators


class BigQueryDialectConfig(DialectConfig):
    """Configuration for BigQuery dialect."""

    @property
    def name(self) -> str:
        if self._name is None:
            self._name = "bigquery"
        return self._name

    @property
    def block_starters(self) -> set[str]:
        if self._block_starters is None:
            self._block_starters = {"BEGIN", "CASE"}
        return self._block_starters

    @property
    def block_enders(self) -> set[str]:
        if self._block_enders is None:
            self._block_enders = {"END"}
        return self._block_enders

    @property
    def statement_terminators(self) -> set[str]:
        if self._statement_terminators is None:
            self._statement_terminators = {";"}
        return self._statement_terminators


_pattern_cache: UnifiedCache | None = None
_result_cache: UnifiedCache | None = None
_cache_lock = threading.Lock()


def _get_pattern_cache() -> UnifiedCache:
    """Get or create the global pattern compilation cache.

    Returns:
        The pattern cache instance
    """
    global _pattern_cache
    if _pattern_cache is None:
        with _cache_lock:
            if _pattern_cache is None:
                _pattern_cache = UnifiedCache(max_size=DEFAULT_PATTERN_CACHE_SIZE, ttl_seconds=DEFAULT_CACHE_TTL)
    return _pattern_cache


def _get_result_cache() -> UnifiedCache:
    """Get or create the global result cache.

    Returns:
        The result cache instance
    """
    global _result_cache
    if _result_cache is None:
        with _cache_lock:
            if _result_cache is None:
                _result_cache = UnifiedCache(max_size=DEFAULT_RESULT_CACHE_SIZE, ttl_seconds=DEFAULT_CACHE_TTL)
    return _result_cache


@mypyc_attr(allow_interpreted_subclasses=False)
class StatementSplitter:
    """SQL script splitter with caching and dialect support."""

    __slots__ = SPLITTER_SLOTS

    def __init__(self, dialect: DialectConfig, strip_trailing_semicolon: bool = False) -> None:
        """Initialize the statement splitter.

        Args:
            dialect: The SQL dialect configuration to use
            strip_trailing_semicolon: Whether to remove trailing semicolons from statements
        """
        self._dialect = dialect
        self._strip_trailing_semicolon = strip_trailing_semicolon
        self._token_patterns = dialect.get_all_token_patterns()

        self._pattern_cache_key = f"{dialect.name}:{hash(tuple(str(p) for _, p in self._token_patterns))}"

        self._pattern_cache = _get_pattern_cache()
        self._result_cache = _get_result_cache()

        self._compiled_patterns = self._get_or_compile_patterns()

    def _get_or_compile_patterns(self) -> list[tuple[TokenType, CompiledTokenPattern]]:
        """Get compiled regex patterns from cache or compile and cache them.

        Returns:
            List of compiled token patterns with their types
        """
        cache_key = CacheKey(("pattern", self._pattern_cache_key))

        cached_patterns = self._pattern_cache.get(cache_key)
        if cached_patterns is not None:
            return cast("list[tuple[TokenType, CompiledTokenPattern]]", cached_patterns)

        compiled: list[tuple[TokenType, CompiledTokenPattern]] = []
        for token_type, pattern in self._token_patterns:
            if isinstance(pattern, str):
                compiled.append((token_type, re.compile(pattern, re.IGNORECASE | re.DOTALL)))
            else:
                compiled.append((token_type, pattern))

        self._pattern_cache.put(cache_key, compiled)
        return compiled

    def _tokenize(self, sql: str) -> Generator[Token, None, None]:
        """Tokenize SQL string into Token objects.

        Args:
            sql: The SQL string to tokenize

        Yields:
            Token objects representing the lexical elements
        """
        pos = 0
        line = 1
        line_start = 0

        while pos < len(sql):
            matched = False

            for token_type, pattern in self._compiled_patterns:
                if callable(pattern):
                    column = pos - line_start + 1
                    token = pattern(sql, pos, line, column)
                    if token:
                        newlines = token.value.count("\n")
                        if newlines > 0:
                            line += newlines
                            last_newline = token.value.rfind("\n")
                            line_start = pos + last_newline + 1

                        yield token
                        pos += len(token.value)
                        matched = True
                        break
                else:
                    match = pattern.match(sql, pos)
                    if match:
                        value = match.group(0)
                        column = pos - line_start + 1

                        newlines = value.count("\n")
                        if newlines > 0:
                            line += newlines
                            last_newline = value.rfind("\n")
                            line_start = pos + last_newline + 1

                        yield Token(type=token_type, value=value, line=line, column=column, position=pos)
                        pos = match.end()
                        matched = True
                        break

            if not matched:
                logger.error("Failed to tokenize at position %d: %s", pos, sql[pos : pos + 20])
                pos += 1

    def split(self, sql: str) -> list[str]:
        """Split SQL script into individual statements.

        Args:
            sql: The SQL script to split

        Returns:
            List of individual SQL statements
        """
        script_hash = hash(sql)
        cache_key = CacheKey(("split", self._dialect.name, script_hash, self._strip_trailing_semicolon))

        cached_result = self._result_cache.get(cache_key)
        if cached_result is not None:
            return cast("list[str]", cached_result)

        statements = self._do_split(sql)

        self._result_cache.put(cache_key, statements)
        return statements

    def _do_split(self, sql: str) -> list[str]:
        """Perform the actual SQL script splitting logic.

        Args:
            sql: The SQL script to split

        Returns:
            List of individual SQL statements
        """
        statements = []
        current_statement_tokens = []
        current_statement_chars = []
        block_stack = []

        all_tokens = list(self._tokenize(sql))

        for token_idx, token in enumerate(all_tokens):
            current_statement_chars.append(token.value)

            if token.type in {TokenType.WHITESPACE, TokenType.COMMENT_LINE, TokenType.COMMENT_BLOCK}:
                current_statement_tokens.append(token)
                continue

            current_statement_tokens.append(token)
            token_upper = token.value.upper()

            if token.type == TokenType.KEYWORD:
                if token_upper in self._dialect.block_starters:
                    block_stack.append(token_upper)
                    if len(block_stack) > self._dialect.max_nesting_depth:
                        msg = f"Maximum nesting depth ({self._dialect.max_nesting_depth}) exceeded"
                        raise ValueError(msg)
                elif token_upper in self._dialect.block_enders:
                    if block_stack and self._dialect.is_real_block_ender(all_tokens, token_idx):
                        block_stack.pop()

            is_terminator = False
            if not block_stack:
                if token.type == TokenType.TERMINATOR:
                    if token.value in self._dialect.statement_terminators:
                        should_delay = self._dialect.should_delay_semicolon_termination(all_tokens, token_idx)

                        if not should_delay and token.value == ";" and self._dialect.batch_separators:
                            should_delay = True

                        if not should_delay:
                            is_terminator = True
                    elif token.value in self._dialect.special_terminators:
                        handler = self._dialect.special_terminators[token.value]
                        if handler(all_tokens, token_idx):
                            is_terminator = True

                elif token.type == TokenType.KEYWORD and token_upper in self._dialect.batch_separators:
                    is_terminator = True

            if is_terminator:
                statement = "".join(current_statement_chars).strip()

                is_plsql_block = self._is_plsql_block(current_statement_tokens)

                if (
                    self._strip_trailing_semicolon
                    and token.type == TokenType.TERMINATOR
                    and statement.endswith(token.value)
                    and not is_plsql_block
                ):
                    statement = statement[: -len(token.value)].rstrip()

                if statement and self._contains_executable_content(statement):
                    statements.append(statement)
                current_statement_tokens = []
                current_statement_chars = []

        if current_statement_chars:
            statement = "".join(current_statement_chars).strip()
            if statement and self._contains_executable_content(statement):
                statements.append(statement)

        return statements

    @staticmethod
    def _is_plsql_block(tokens: list[Token]) -> bool:
        """Check if the token list represents a PL/SQL block.

        Args:
            tokens: List of tokens to examine

        Returns:
            True if tokens represent a PL/SQL block, False otherwise
        """
        for token in tokens:
            if token.type == TokenType.KEYWORD:
                return token.value.upper() in {"BEGIN", "DECLARE"}
        return False

    def _contains_executable_content(self, statement: str) -> bool:
        """Check if a statement contains executable content.

        Args:
            statement: The SQL statement to check

        Returns:
            True if statement contains non-whitespace/non-comment content
        """
        tokens = list(self._tokenize(statement))

        for token in tokens:
            if token.type not in {TokenType.WHITESPACE, TokenType.COMMENT_LINE, TokenType.COMMENT_BLOCK}:
                return True

        return False


def split_sql_script(script: str, dialect: str | None = None, strip_trailing_terminator: bool = False) -> list[str]:
    """Split SQL script into individual statements.

    Args:
        script: The SQL script to split
        dialect: The SQL dialect name
        strip_trailing_terminator: If True, remove trailing terminators from statements

    Returns:
        List of individual SQL statements
    """
    if dialect is None:
        dialect = "generic"

    dialect_configs = {
        "generic": GenericDialectConfig(),
        "oracle": OracleDialectConfig(),
        "tsql": TSQLDialectConfig(),
        "mssql": TSQLDialectConfig(),
        "sqlserver": TSQLDialectConfig(),
        "postgresql": PostgreSQLDialectConfig(),
        "postgres": PostgreSQLDialectConfig(),
        "mysql": MySQLDialectConfig(),
        "sqlite": SQLiteDialectConfig(),
        "duckdb": DuckDBDialectConfig(),
        "bigquery": BigQueryDialectConfig(),
    }

    config = dialect_configs.get(dialect.lower())
    if not config:
        logger.warning("Unknown dialect '%s', using generic SQL splitter", dialect)
        config = GenericDialectConfig()

    splitter = StatementSplitter(config, strip_trailing_semicolon=strip_trailing_terminator)
    return splitter.split(script)


def clear_splitter_caches() -> None:
    """Clear all splitter caches.

    Clears both pattern and result caches to free memory.
    """
    pattern_cache = _get_pattern_cache()
    result_cache = _get_result_cache()
    pattern_cache.clear()
    result_cache.clear()


def get_splitter_cache_stats() -> dict[str, Any]:
    """Get statistics from splitter caches.

    Returns:
        Dictionary containing cache statistics
    """
    pattern_cache = _get_pattern_cache()
    result_cache = _get_result_cache()

    return {
        "pattern_cache": {"size": pattern_cache.size(), "stats": pattern_cache.get_stats()},
        "result_cache": {"size": result_cache.size(), "stats": result_cache.get_stats()},
    }
