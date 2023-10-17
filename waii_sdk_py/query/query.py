from dataclasses import dataclass
from ..waii_http_client import WaiiHttpClient
from ..database import SearchContext, TableName, ColumnDefinition
from ..semantic_context import SemanticStatement
from pydantic import BaseModel
import re
from typing import Optional, List, Dict, Any, Union
from urllib.parse import urlparse, parse_qs

GENERATE_ENDPOINT = 'generate-query'
RUN_ENDPOINT = 'run-query'
SUBMIT_ENDPOINT = 'submit-query'
FAVORITE_ENDPOINT = 'like-query'
DESCRIBE_ENDPOINT = 'describe-query'
DIFF_ENDPOINT = "diff-query"
RESULTS_ENDPOINT = 'get-query-result'
CANCEL_ENDPOINT = 'cancel-query'
AUTOCOMPLETE_ENDPOINT = 'auto-complete'
PERF_ENDPOINT = 'get-query-performance'


class Tweak(BaseModel):
    sql: Optional[str] = None
    ask: Optional[str] = None


class QueryGenerationRequest(BaseModel):
    search_context: Optional[List[SearchContext]] = None
    tweak_history: Optional[List[Tweak]] = None
    ask: Optional[str] = None
    uuid: Optional[str] = None
    dialect: Optional[str] = None
    parent_uuid: Optional[str] = None


class DescribeQueryRequest(BaseModel):
    search_context: Optional[List[SearchContext]] = None
    current_schema: Optional[str] = None
    query: Optional[str] = None


class DescribeQueryResponse(BaseModel):
    summary: Optional[str] = None
    detailed_steps: Optional[List[str]] = None
    tables: Optional[List[TableName]] = None


class DiffQueryRequest(DescribeQueryRequest):
    search_context: Optional[List[SearchContext]] = None
    current_schema: Optional[str] = None
    query: Optional[str] = None
    previous_query: Optional[str] = None


class DiffQueryResponse(DescribeQueryResponse):
    summary: Optional[str] = None
    tables: Optional[List[TableName]] = None
    detailed_steps: Optional[List[str]] = None
    what_changed: Optional[str] = None


class CompilationError(BaseModel):
    message: str
    line: Optional[int] = None


class GeneratedQuery(BaseModel):
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


class SyncRunQueryRequest(BaseModel):
    query: str
    timeout_ms: Optional[int] = None
    max_returned_rows: Optional[int] = None
    current_schema: Optional[str] = None


class RunQueryRequest(BaseModel):
    query: str
    session_id: Optional[str] = None
    current_schema: Optional[str] = None
    session_parameters: Optional[Dict[str, Any]] = None


class RunQueryResponse(BaseModel):
    query_id: Optional[str] = None


class GetQueryResultRequest(BaseModel):
    query_id: str


class CancelQueryRequest(BaseModel):
    query_id: str


class CancelQueryResponse(BaseModel):
    pass


class GetQueryResultResponse(BaseModel):
    rows: Optional[List[object]] = None
    more_rows: Optional[int] = None
    column_definitions: Optional[List[ColumnDefinition]] = None
    query_uuid: Optional[str] = None


class LikeQueryRequest(BaseModel):
    query_uuid: str
    liked: bool


class LikeQueryResponse(BaseModel):
    pass


class AutoCompleteRequest(BaseModel):
    text: str
    cursor_offset: Optional[int] = None
    dialect: Optional[str] = None
    search_context: Optional[List[SearchContext]] = None
    max_output_tokens: Optional[int] = None


class AutoCompleteResponse(BaseModel):
    text: Optional[str] = None


class QueryPerformanceRequest(BaseModel):
    query_id: str


class QueryPerformanceResponse(BaseModel):
    summary: List[str]
    recommendations: List[str]
    query_text: str
    execution_time_ms: Optional[int]
    compilation_time_ms: Optional[int]


class Query:
    @staticmethod
    def generate(params: QueryGenerationRequest) -> GeneratedQuery:
        return WaiiHttpClient[GeneratedQuery].get_instance().common_fetch(GENERATE_ENDPOINT, params.__dict__, GeneratedQuery)

    @staticmethod
    def run(params: RunQueryRequest) -> GetQueryResultResponse:
        return WaiiHttpClient.get_instance().common_fetch(RUN_ENDPOINT, params.__dict__, GetQueryResultResponse)

    @staticmethod
    def like(params: LikeQueryRequest) -> LikeQueryResponse:
        return WaiiHttpClient.get_instance().common_fetch(FAVORITE_ENDPOINT, params.__dict__, LikeQueryResponse)

    @staticmethod
    def submit(params: RunQueryRequest) -> RunQueryResponse:
        return WaiiHttpClient.get_instance().common_fetch(SUBMIT_ENDPOINT, params.__dict__, RunQueryResponse)

    @staticmethod
    def get_results(params: GetQueryResultRequest) -> GetQueryResultResponse:
        return WaiiHttpClient.get_instance().common_fetch(RESULTS_ENDPOINT, params.__dict__, GetQueryResultResponse)

    @staticmethod
    def cancel(params: CancelQueryRequest) -> CancelQueryResponse:
        return WaiiHttpClient.get_instance().common_fetch(CANCEL_ENDPOINT, params.__dict__, CancelQueryResponse)

    @staticmethod
    def describe(params: DescribeQueryRequest) -> DescribeQueryResponse:
        return WaiiHttpClient.get_instance().common_fetch(DESCRIBE_ENDPOINT, params.__dict__, DescribeQueryResponse)

    @staticmethod
    def auto_complete(params: AutoCompleteRequest) -> AutoCompleteResponse:
        return WaiiHttpClient.get_instance().common_fetch(AUTOCOMPLETE_ENDPOINT, params.__dict__, AutoCompleteResponse)

    @staticmethod
    def diff(params: DiffQueryRequest) -> DiffQueryResponse:
        return WaiiHttpClient.get_instance().common_fetch(DIFF_ENDPOINT, params.__dict__, DiffQueryResponse)

    @staticmethod
    def analyze_performance(params: QueryPerformanceRequest) -> QueryPerformanceResponse:
        return WaiiHttpClient.get_instance().common_fetch(PERF_ENDPOINT, params.__dict__, QueryPerformanceResponse)
