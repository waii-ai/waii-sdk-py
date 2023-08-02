from typing import List, Optional
from dataclasses import dataclass
from WaiiHttpClient import WaiiHttpClient  # Assuming WaiiHttpClient is properly imported
from Database import SearchContext, TableName, Column  # Assuming these are the correct imports
from SemanticContext import SemanticStatement  # Assuming this is the correct import

GENERATE_ENDPOINT = 'generate-query'
RUN_ENDPOINT = 'run-query'
SUBMIT_ENDPOINT = 'submit-query'
FAVORITE_ENDPOINT = 'like-query'
DESCRIBE_ENDPOINT = 'describe-query'
RESULTS_ENDPOINT = 'get-query-result'
CANCEL_ENDPOINT = 'cancel-query'


@dataclass
class Tweak:
    sql: Optional[str] = None
    ask: Optional[str] = None


@dataclass
class QueryGenerationRequest:
    search_context: Optional[List[SearchContext]] = None
    tweak_history: Optional[List[Tweak]] = None
    ask: Optional[str] = None
    uuid: Optional[str] = None
    dialect: Optional[str] = None
    parent_uuid: Optional[str] = None


@dataclass
class DescribeQueryRequest:
    search_context: Optional[List[SearchContext]] = None
    current_schema: Optional[str] = None
    query: Optional[str] = None


@dataclass
class DescribeQueryResponse:
    summary: Optional[str] = None
    detailed_steps: Optional[List[str]] = None
    tables: Optional[List[TableName]] = None


@dataclass
class CompilationError:
    message: str
    line: Optional[List[int]] = None


@dataclass
class GeneratedQuery:
    uuid: Optional[str] = None
    liked: Optional[bool] = None
    tables: Optional[List[TableName]] = None
    semantic_context: Optional[List[SemanticStatement]] = None
    query: Optional[str] = None
    detailed_steps: Optional[List[str]] = None
    what_changed: Optional[str] = None
    compilation_errors: Optional[List[CompilationError]] = None
    is_new: Optional[bool] = None
    timestamp_ms: Optional[int] = None


@dataclass
class SyncRunQueryRequest:
    query: str
    timeout_ms: Optional[int] = None
    max_returned_rows: Optional[int] = None


@dataclass
class RunQueryRequest:
    query: str
    session_id: Optional[str] = None


@dataclass
class RunQueryResponse:
    query_id: Optional[str] = None


@dataclass
class GetQueryResultRequest:
    query_id: str


@dataclass
class CancelQueryRequest:
    query_id: str


@dataclass
class CancelQueryResponse:
    pass


@dataclass
class GetQueryResultResponse:
    rows: Optional[List[object]] = None
    more_rows: Optional[int] = None
    column_definitions: Optional[List[Column]] = None
    query_uuid: Optional[str] = None


@dataclass
class LikeQueryRequest:
    query_uuid: str
    liked: bool


@dataclass
class LikeQueryResponse:
    pass


class Query:
    @staticmethod
    def generate(params: QueryGenerationRequest) -> GeneratedQuery:
        return WaiiHttpClient.getInstance().commonFetch(GENERATE_ENDPOINT, params.__dict__)

    @staticmethod
    def run(params: RunQueryRequest) -> GetQueryResultResponse:
        return WaiiHttpClient.getInstance().commonFetch(RUN_ENDPOINT, params.__dict__)

    @staticmethod
    def like(params: LikeQueryRequest) -> LikeQueryResponse:
        return WaiiHttpClient.getInstance().commonFetch(FAVORITE_ENDPOINT, params.__dict__)

    @staticmethod
    def submit(params: RunQueryRequest) -> RunQueryResponse:
        return WaiiHttpClient.getInstance().commonFetch(SUBMIT_ENDPOINT, params.__dict__)

    @staticmethod
    def getResults(params: GetQueryResultRequest) -> GetQueryResultResponse:
        return WaiiHttpClient.getInstance().commonFetch(RESULTS_ENDPOINT, params.__dict__)

    @staticmethod
    def cancel(params: CancelQueryRequest) -> CancelQueryResponse:
        return WaiiHttpClient.getInstance().commonFetch(CANCEL_ENDPOINT, params.__dict__)

    @staticmethod
    def describe(params: DescribeQueryRequest) -> DescribeQueryResponse:
        return WaiiHttpClient.getInstance().commonFetch(DESCRIBE_ENDPOINT, params.__dict__)
