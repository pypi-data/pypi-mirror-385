from dataclasses import field
from typing import List, Optional, Union

from pydantic import Field
from pydantic.dataclasses import dataclass
from typing_extensions import Literal

from kumoapi.common import StrEnum
from kumoapi.data_source import DataSourceType
from kumoapi.typing import Dtype, Stype, compatible_field_validator

TableName = str

# Source Table ================================================================


class FileType(StrEnum):
    r"""Supported file types for file-based source tables."""
    CSV = "CSV"
    PARQUET = "PARQUET"


class LLMType(StrEnum):
    r"""Supported LLM types."""
    # Use LLM embeddings as features
    FEATURE = "feature"


@dataclass(frozen=True)
class UnavailableSourceTable:
    r"""A source table not available during processing, e.g. because it is
    processed by client-side."""
    table: TableName
    data_source_type: Literal[
        DataSourceType.UNAVAILABLE] = DataSourceType.UNAVAILABLE


@dataclass(frozen=True)
class S3SourceTable:
    r"""A source table located on the Amazon S3 object store."""
    # We support two types of table file path:
    # 1. s3_path specifies the whole directory (prefix), ending with "/"
    # 2. s3_path specifies the full path of a single file, ending with file
    #    name suffix that must be one of ".csv" or ".parquet"
    s3_path: str

    # Internal: S3 connector ID, if we are working with a Kumo-owned named S3
    # connector:
    connector_id: Optional[str] = None
    source_table_name: Optional[TableName] = None

    # If not provided, then the file_path must either end in `.csv` or
    # `.parquet`, and we will parse the file type from there. Please use the
    # `validated_file_type` proper to access the parsed & validated file type.
    file_type: Optional[FileType] = None

    data_source_type: Literal[DataSourceType.S3] = DataSourceType.S3

    @property
    def table(self) -> TableName:
        if self.s3_path == "":
            assert self.source_table_name is not None
            return self.source_table_name
        if self.s3_path.endswith('/'):
            return TableName(
                self.s3_path.rstrip('/').rsplit('/', maxsplit=1)[1])
        filename = self.s3_path.rsplit('/', maxsplit=1)[1]
        return TableName(filename.rsplit('.', maxsplit=1)[0])  # strip suffix


@dataclass(frozen=True)
class SnowflakeSourceTable:
    r"""A source table located in the Snowflake data warehouse."""
    snowflake_connector_id: str
    database: str
    schema_name: str
    table: TableName
    data_source_type: Literal[
        DataSourceType.SNOWFLAKE] = DataSourceType.SNOWFLAKE


@dataclass(frozen=True)
class DatabricksSourceTable:
    r"""A source table located in the Databricks data warehouse."""
    databricks_connector_id: str
    table: TableName
    data_source_type: Literal[
        DataSourceType.DATABRICKS] = DataSourceType.DATABRICKS


@dataclass(frozen=True)
class GlueSourceTable:
    r"""A source table located in the AWS Glue data warehouse."""
    glue_connector_id: str
    table: TableName
    account: str
    region: str
    database: str
    data_source_type: Literal[DataSourceType.GLUE] = DataSourceType.GLUE


@dataclass(frozen=True)
class BigQuerySourceTable:
    r"""A source table loated in the BigQuery data warehouse."""
    bigquery_connector_id: str
    table_name: TableName
    project_id: str
    dataset_id: str
    data_source_type: Literal[
        DataSourceType.BIGQUERY] = DataSourceType.BIGQUERY


SourceTableType = Union[S3SourceTable, SnowflakeSourceTable,
                        DatabricksSourceTable, BigQuerySourceTable,
                        GlueSourceTable, UnavailableSourceTable]

# Method: Configuration =======================================================


@dataclass
class SourceTableConfigRequest:
    connector_id: Optional[str]
    table_name: str
    source_type: DataSourceType

    root_dir: Optional[str] = None
    file_type: Optional[FileType] = None


@dataclass
class SourceTableConfigResponse:
    source_table: SourceTableType = Field(discriminator='data_source_type')


# Method: Validate ============================================================


@dataclass
class SourceTableValidateRequest:
    table_name: str
    connector_id: Optional[str]
    source_type: DataSourceType
    root_dir: Optional[str] = None


@dataclass
class SourceTableValidateResponse:
    is_valid: bool
    # In case there's a suggestion, a warning, or an error:
    msg: str


# Method: List ================================================================


@dataclass
class SourceTableListRequest:
    # TODO(manan): enforce one-of connector ID or root_dir
    connector_id: Optional[str]
    source_type: DataSourceType

    # Only for object store-based connectors:
    root_dir: Optional[str] = None

    def __post_init__(self):
        if self.connector_id is None and self.source_type != DataSourceType.S3:
            raise ValueError(
                "A 'None' connector ID is only supported for S3-backed "
                "tables. Please specify a connector ID to proceed.")


@dataclass
class SourceTableListResponse:
    table_names: List[str]


# Method: Get Data ============================================================


@dataclass
class SourceColumn:
    r"""The metadata of a column in a source table. Note that a source column
    simply provides a view into the metadata of a source table. To modify
    metadata, please create a Kumo Table and adjust the table's data and
    semantic types.

    .. note::
        Semantic types are inferred based on data types only, and thus may not
        be accurate.

    Args:
        name (str): The name of the column.
        stype (Stype, optional): The semantic type of the column.
        dtype (Dtype): The data type of the column
        is_primary (bool): Whether the column refers to a primary key.
    """
    name: str
    stype: Optional[Stype]  # Kumo-inferred.
    dtype: Dtype
    is_primary: bool


@dataclass
class S3SourceTableRequest:
    r"""A request to fetch a source table located on Amazon S3. This table
    can be located at either
        root_dir/table_name/*.(csv|parquet)
        root_dir/table_name.(csv|parquet)
    """
    s3_root_dir: str  # TODO(manan): rename to `root_dir`
    connector_id: Optional[str] = None
    table_names: Optional[List[str]] = None
    file_type: Optional[FileType] = None
    source_type: Literal[DataSourceType.S3] = DataSourceType.S3


@dataclass
class SnowflakeSourceTableRequest:
    connector_id: str
    table_names: Optional[List[str]] = None
    source_type: Literal[DataSourceType.SNOWFLAKE] = DataSourceType.SNOWFLAKE

    # TODO(siyang): We should move database and schema out of SF connector.
    # database: Optional[str] = None
    # schema: Optional[str] = None


@dataclass
class BigQuerySourceTableRequest:
    connector_id: str
    table_names: Optional[List[str]] = None

    # Discriminator:
    source_type: Literal[DataSourceType.BIGQUERY] = DataSourceType.BIGQUERY


@dataclass
class DatabricksSourceTableRequest:
    connector_id: str
    table_names: Optional[List[str]] = None

    # Discriminator:
    source_type: Literal[DataSourceType.DATABRICKS] = DataSourceType.DATABRICKS


@dataclass
class GlueSourceTableRequest:
    connector_id: str
    table_names: Optional[List[str]] = None
    source_type: Literal[DataSourceType.GLUE] = DataSourceType.GLUE


@dataclass
class SourceTableDataRequest:
    # Table request (metadata needed to fetch a table from the connector):
    source_table_request: Union[
        S3SourceTableRequest,
        BigQuerySourceTableRequest,
        DatabricksSourceTableRequest,
        SnowflakeSourceTableRequest,
        GlueSourceTableRequest,
    ] = Field(discriminator='source_type')

    # Whether to fetch and include sample rows in the response:
    sample_rows: int = 0

    @compatible_field_validator('sample_rows')
    def _validate_sample_rows(cls, v: int):
        if v > 1000:
            return ValueError('sample_rows cannot be greater than 1000.')
        if v < 0:
            return ValueError('sample_rows cannot be negative.')
        return v


@dataclass
class SourceTableDataResponse:
    table_name: TableName
    cols: List[SourceColumn] = field(default_factory=list)

    # Serialized (json) data of sample rows dataframe, if requested:
    # TODO(siyang,manan): figure out the ser/de protocol for pandas dataframe
    sample_rows: Optional[str] = None


# Other =======================================================================


@dataclass
class TableStats:
    r"""Minimal statistics of a :class:`SourceTable`.

    Args:
        size_bytes (int): The size of the table in bytes.
        num_rows (int): The number of rows in the table.
    """
    size_bytes: int
    num_rows: int
    # TODO(siyang): add a flag to indicate if stats are exact or approx?


@dataclass
class LLMRequest:
    source_table_type: SourceTableType
    template: str
    model: str
    model_api_key: str
    output_dir: str
    output_column_name: str
    output_table_name: str
    dimensions: Optional[int] = None
    llm_type: LLMType = LLMType.FEATURE


@dataclass
class LLMResponse:
    job_id: str
