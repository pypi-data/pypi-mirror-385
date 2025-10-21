import io
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union

from pydantic.dataclasses import dataclass
from typing_extensions import Self

from kumoapi.task import TaskType
from kumoapi.typing import StrEnum, Stype

if TYPE_CHECKING:
    from numpy import ndarray
else:
    try:
        from numpy import ndarray
    except ImportError:
        ndarray = Any

if TYPE_CHECKING:
    from pandas import DataFrame, Series
else:
    try:
        from pandas import DataFrame, Series
    except ImportError:
        DataFrame = Any
        Series = Any

REV_REL = '__###REV###__'
EDGE_TYPE_SEP = '__###__'
NUMPY_NAME = '__###NP###__'
SERIES_NAME = '__###SER###__'


class EdgeLayout(StrEnum):
    COO = 'COO'
    CSC = 'CSC'
    REV = 'REV'


@dataclass(config={'arbitrary_types_allowed': True})
class Table:
    df: DataFrame
    row: Optional[ndarray]
    batch: ndarray
    num_sampled_nodes: List[int]
    stype_dict: Dict[str, Stype]
    primary_key: Optional[str]

    @property
    def num_rows(self) -> int:
        return sum(self.num_sampled_nodes)


@dataclass(config={'arbitrary_types_allowed': True})
class Link:
    layout: EdgeLayout
    row: Optional[ndarray]
    col: Optional[ndarray]
    num_sampled_edges: List[int]

    def __post_init__(self) -> None:
        if self.layout == EdgeLayout.REV:  # Look up edges from reverse link:
            assert self.row is None and self.col is None

    @property
    def num_edges(self) -> int:
        return sum(self.num_sampled_edges)


@dataclass(config={'arbitrary_types_allowed': True})
class Subgraph:
    anchor_time: ndarray
    table_dict: Dict[str, Table]
    link_dict: Dict[Tuple[str, str, str], Link]

    @property
    def batch_size(self) -> int:
        return len(self.anchor_time)

    @property
    def num_hops(self) -> int:
        return max(
            [len(link.num_sampled_edges)
             for link in self.link_dict.values()] + [0])

    @staticmethod
    def rev_edge_type(edge_type: Tuple[str, str, str]) -> Tuple[str, str, str]:
        src, rel, dst = edge_type
        if rel.startswith(REV_REL):
            return (dst, rel[len(REV_REL):], src)
        return (dst, f'{REV_REL}{rel}', src)


@dataclass(config={'arbitrary_types_allowed': True})
class Context:
    task_type: TaskType
    entity_table_names: Tuple[str, ...]
    subgraph: Subgraph
    y_train: Series
    y_test: Optional[Series]
    top_k: Optional[int] = None
    step_size: Optional[int] = None

    def __post_init__(self) -> None:
        if len(self.entity_table_names) == 0:
            raise ValueError("'entity_table_names' needs to at least contain "
                             "one entity table name")

    @property
    def num_train(self) -> int:
        return len(self.y_train)

    @property
    def num_forecasts(self) -> int:
        if self.task_type.is_link_pred:
            return 1
        if not isinstance(self.y_train[0], list):
            return 1
        return len(self.y_train[0])

    @property
    def num_test(self) -> int:
        return self.subgraph.batch_size - self.num_train

    def fill_protobuf_(self, msg: Any) -> Any:
        import kumoapi.rfm.protos.context_pb2 as _context_pb2

        context_pb2: Any = _context_pb2

        msg.task_type = getattr(context_pb2.TaskType, self.task_type.upper())
        msg.entity_table_names.extend(list(self.entity_table_names))

        msg.subgraph.anchor_time = _to_bytes(self.subgraph.anchor_time)

        for table_name, table in self.subgraph.table_dict.items():
            table_msg = msg.subgraph.table_dict[table_name]
            table_msg.df = _to_bytes(table.df)
            if table.row is not None:
                table_msg.row = _to_bytes(table.row)
            table_msg.batch = _to_bytes(table.batch)
            table_msg.num_sampled_nodes.extend(table.num_sampled_nodes)
            for column_name, stype in table.stype_dict.items():
                table_msg.stype_dict[column_name] = getattr(
                    context_pb2.Stype, stype.upper())
            if table.primary_key is not None:
                table_msg.primary_key = table.primary_key

        for edge_type, link in self.subgraph.link_dict.items():
            link_msg = msg.subgraph.link_dict[EDGE_TYPE_SEP.join(edge_type)]
            link_msg.layout = getattr(context_pb2.EdgeLayout, link.layout)
            if link.row is not None:
                link_msg.row = _to_bytes(link.row)
            if link.col is not None:
                link_msg.col = _to_bytes(link.col)
            link_msg.num_sampled_edges.extend(link.num_sampled_edges)

        msg.y_train = _to_bytes(self.y_train)
        if self.y_test is not None:
            msg.y_test = _to_bytes(self.y_test)

        if self.top_k is not None:
            msg.top_k = self.top_k

        if self.step_size is not None:
            msg.step_size = self.step_size

        return msg

    def to_protobuf(self) -> Any:
        import kumoapi.rfm.protos.context_pb2 as _context_pb2

        context_pb2: Any = _context_pb2
        msg = context_pb2.Context()
        self.fill_protobuf_(msg)

        return msg

    def serialize(self) -> bytes:
        return self.to_protobuf().SerializeToString()

    @classmethod
    def from_protobuf(cls, msg: Any) -> Self:
        import pandas as pd

        import kumoapi.rfm.protos.context_pb2 as _context_pb2

        context_pb2: Any = _context_pb2

        table_dict: Dict[str, Table] = {}

        for table_name, table_msg in msg.subgraph.table_dict.items():
            table = Table(
                df=_to_data(table_msg.df),
                row=_to_data(table_msg.row)
                if table_msg.HasField('row') else None,
                batch=_to_data(table_msg.batch),
                num_sampled_nodes=list(table_msg.num_sampled_nodes),
                stype_dict={
                    col_name:
                    Stype(context_pb2.Stype.Name(stype_msg).lower())
                    if context_pb2.Stype.Name(stype_msg) != 'ID' else Stype.ID
                    for col_name, stype_msg in table_msg.stype_dict.items()
                },
                primary_key=table_msg.primary_key or None,
            )
            if len(table.df.columns) == 0:
                table.df = pd.DataFrame(index=range(len(table.batch)))
            table_dict[table_name] = table

        link_dict: Dict[Tuple[str, str, str], Link] = {}
        for edge_type, link_msg in msg.subgraph.link_dict.items():
            link_dict[tuple(edge_type.split(EDGE_TYPE_SEP))] = Link(
                layout=EdgeLayout(context_pb2.EdgeLayout.Name(
                    link_msg.layout)),
                row=_to_data(link_msg.row)
                if link_msg.HasField('row') else None,
                col=_to_data(link_msg.col)
                if link_msg.HasField('col') else None,
                num_sampled_edges=list(link_msg.num_sampled_edges),
            )

        return Context(
            task_type=TaskType(
                context_pb2.TaskType.Name(msg.task_type).lower()),
            entity_table_names=tuple(msg.entity_table_names),
            subgraph=Subgraph(
                anchor_time=_to_data(msg.subgraph.anchor_time),
                table_dict=table_dict,
                link_dict=link_dict,
            ),
            y_train=_to_data(msg.y_train),
            y_test=_to_data(msg.y_test) if msg.HasField('y_test') else None,
            top_k=msg.top_k or None,
            step_size=msg.step_size or None,
        )

    @classmethod
    def from_bytes(cls, data: bytes) -> Self:
        import kumoapi.rfm.protos.context_pb2 as _context_pb2

        context_pb2: Any = _context_pb2

        msg = context_pb2.Context()
        msg.ParseFromString(data)

        return cls.from_protobuf(msg)

    @staticmethod
    def get_memory_stats(msg: Any, top_k: int = 5) -> str:
        import pandas as pd

        num_tables = len(msg.subgraph.table_dict)
        num_nodes = sum([
            sum(table.num_sampled_nodes)
            for table in msg.subgraph.table_dict.values()
        ])
        num_edges = sum([
            sum(link.num_sampled_edges)
            for link in msg.subgraph.link_dict.values()
        ])

        df = pd.DataFrame({
            'name':
            pd.Series(
                [name for name in msg.subgraph.table_dict.keys()],
                dtype=str,
            ),
            '#nodes':
            pd.Series(
                [
                    f'{sum(table.num_sampled_nodes):,}'
                    for table in msg.subgraph.table_dict.values()
                ],
                dtype=str,
            ),
            'MB':
            pd.Series(
                [len(table.df) for table in msg.subgraph.table_dict.values()],
                dtype=int,
            ),
        })
        df = df.sort_values('MB', ascending=False).iloc[:top_k]
        df['MB'] = df['MB'].map(lambda x: f'{x / (1024*1024):.2f}')

        return (f"Current context contains {num_nodes:,} nodes and "
                f"{num_edges:,} edges across {num_tables} tables. "
                f"Top-{len(df)} tables contributing most to the context size:"
                f"\n{df.to_string(index=False)}")


def _to_bytes(data: Union[DataFrame, Series, ndarray]) -> bytes:
    import numpy as np
    import pandas as pd

    if isinstance(data, np.ndarray):
        data = pd.DataFrame({NUMPY_NAME: data})

    if isinstance(data, pd.Series):
        data = pd.DataFrame({SERIES_NAME: data})

    buffer = io.BytesIO()
    assert isinstance(data, pd.DataFrame)
    data.to_parquet(buffer, compression='zstd', index=False)  # type: ignore
    return buffer.getvalue()


def _to_data(data: bytes) -> Union[DataFrame, Series, ndarray]:
    import pandas as pd

    df = pd.read_parquet(io.BytesIO(data))

    if len(df.columns) == 1 and df.columns == NUMPY_NAME:
        return df[NUMPY_NAME].to_numpy()

    if len(df.columns) == 1 and df.columns == SERIES_NAME:
        ser = df[SERIES_NAME]
        ser.name = None
        return ser

    return df
