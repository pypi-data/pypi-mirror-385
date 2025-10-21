from typing import List, Optional, Union

import pydantic
from pydantic.dataclasses import dataclass

from kumoapi.pquery.AST.ast_node import ASTNode
from kumoapi.pquery.AST.column import Column


@dataclass(repr=False)
class Filter(ASTNode):
    r"""Creates an atomic description of a filter on :obj:`target`
    corresponding to statement "target WHERE condition".
    Args:
        target: :class:`Column` defining the column to filter.
        condition: :class:`ASTNode` used to
            determine which rows to filter out.
    """
    target: Optional[Column] = None
    condition: Union['Condition', 'LogicalOperation', None] = None

    def __post_init__(self) -> None:
        if self.target is None:
            raise ValueError(f"Class '{self.__class__.__name__}' is missing a "
                             f"target.")
        if self.condition is None:
            raise ValueError(f"Class '{self.__class__.__name__}' is missing a "
                             f"condition.")
        super().__post_init__()

    @property
    def children(self) -> List['ASTNode']:
        assert self.target is not None
        assert self.condition is not None
        return [self.target, self.condition]

    def to_string(self) -> str:
        r"""Creates a predictive query statement from the filter."""
        return f"{self.target} WHERE {self.condition}"


from kumoapi.pquery.AST.condition import Condition  # noqa: E402
from kumoapi.pquery.AST.logical_operation import LogicalOperation  # noqa: E402

if pydantic.__version__.startswith('1.'):
    Filter.__pydantic_model__.update_forward_refs()  # type: ignore
