"""Public typed expression API built from modular components."""

# pylint: disable=too-few-public-methods,invalid-name,import-outside-toplevel,cyclic-import,protected-access

from __future__ import annotations

from .expressions.base import (
    AliasedExpression,
    BooleanExpression,
    GenericExpression,
    TypedExpression,
)
from .expressions.case import CaseExpressionBuilder
from .expressions.binary import BlobExpression, BlobFactory
from .expressions.boolean import BooleanFactory
from .expressions.generic import GenericFactory
from .expressions.numeric import (
    NumericAggregateFactory,
    NumericExpression,
    NumericFactory,
    NumericOperand,
)
from .expressions.text import VarcharExpression, VarcharFactory
from .expressions.utils import format_numeric as _format_numeric
from .expressions.utils import quote_identifier as _quote_identifier
from .expressions.utils import quote_string as _quote_string
from .select import SelectStatementBuilder


class DuckTypeNamespace:
    """Container exposing typed expression factories."""

    def __init__(self) -> None:
        self.Numeric = NumericFactory()
        self.Varchar = VarcharFactory()
        self.Boolean = BooleanFactory()
        self.Blob = BlobFactory()
        self.Generic = GenericFactory()

    def select(self) -> SelectStatementBuilder:
        return SelectStatementBuilder()

    def row_number(self) -> NumericExpression:
        """Return a typed expression invoking ``ROW_NUMBER()``."""

        return NumericExpression._raw("row_number()")


ducktype = DuckTypeNamespace()

__all__ = [
    "AliasedExpression",
    "BlobExpression",
    "BlobFactory",
    "BooleanExpression",
    "CaseExpressionBuilder",
    "BooleanFactory",
    "DuckTypeNamespace",
    "GenericExpression",
    "GenericFactory",
    "NumericAggregateFactory",
    "NumericExpression",
    "NumericFactory",
    "NumericOperand",
    "SelectStatementBuilder",
    "TypedExpression",
    "VarcharExpression",
    "VarcharFactory",
    "_format_numeric",
    "_quote_identifier",
    "_quote_string",
    "ducktype",
]
