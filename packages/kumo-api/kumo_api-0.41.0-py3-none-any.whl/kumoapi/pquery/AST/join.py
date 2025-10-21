from typing import List, Union

import pydantic
from pydantic.dataclasses import dataclass

from kumoapi.pquery.AST.ast_node import ASTNode
from kumoapi.pquery.AST.column import Column


@dataclass(repr=False)
class Join(ASTNode):
    r"""Creates an atomic description of a hop from `lhs_key` to
    `rhs_key`. Inferred automatically and used internally.
    Args:
        rhs_target: :class:`ASTNode` defining the rhs df to join.
        lhs_key: Join key of the left table in `table.col` format.
        rhs_key: Join key of the right table in `table.col` format.
    """
    rhs_target: Union['Aggregation', Column, None] = None
    lhs_key: str = ''
    rhs_key: str = ''

    def __post_init__(self) -> None:
        if self.rhs_target is None:
            raise ValueError(f"Class '{self.__class__.__name__}' is missing a "
                             f"rhs_target.")
        super().__post_init__()
        self.dtype_maybe = self.rhs_target.dtype_maybe
        self.stype_maybe = self.rhs_target.stype_maybe
        self.location = self.rhs_target.location

    @property
    def children(self) -> List['ASTNode']:
        assert self.rhs_target is not None
        return [self.rhs_target]

    def to_string(self) -> str:
        r"""Creates a predictive query statement from the filter."""
        return f"{self.rhs_target}"

    @property
    def all_join_columns(self) -> List[str]:
        r"""List of all columns that are needed for joins in the query, given
        with in a fully-qualified name format: `table.column`."""
        assert self.rhs_target is not None
        targets = self.rhs_target.all_join_columns
        targets.append(self.lhs_key)
        targets.append(self.rhs_key)
        return list(set(targets))


from kumoapi.pquery.AST.aggregation import Aggregation  # noqa: E402

if pydantic.__version__.startswith('1.'):
    Join.__pydantic_model__.update_forward_refs()  # type: ignore
