from typing import Optional, List, Dict, Any

from pydantic import BaseModel

from ..database import SearchContext, TableName, ColumnDefinition
from ..semantic_context import SemanticStatement
from ..waii_http_client import WaiiHttpClient

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
TRANSCODE_ENDPOINT = 'transcode-query'
PLOT_ENDPOINT = 'python-plot'


class Tweak(BaseModel):
    sql: Optional[str] = None
    ask: Optional[str] = None


class TranscodeQueryRequest(BaseModel):
    search_context: Optional[List[SearchContext]] = None
    ask: Optional[str] = ""
    source_dialect: Optional[str] = None
    source_query: Optional[str] = None
    target_dialect: Optional[str] = None


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

    def run(self):
        return Query.run(RunQueryRequest(query=self.query))


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

    def to_pandas_df(self):
        import pandas as pd
        return pd.DataFrame(self.rows, columns=[col.name for col in self.column_definitions])

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

class PythonPlotRequest(BaseModel):
    ask: Optional[str]
    dataframe_rows: Optional[List[Dict[str, Any]]]
    dataframe_cols: Optional[List[ColumnDefinition]]

class PythonPlotResponse(BaseModel):
    # based on the request, return N plot script
    plots: Optional[List[str]]


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

    @staticmethod
    def transcode(params: TranscodeQueryRequest) -> GeneratedQuery:
        return WaiiHttpClient.get_instance().common_fetch(TRANSCODE_ENDPOINT, params.__dict__, GeneratedQuery)

    @staticmethod
    def plot(df, ask=None, automatically_exec=True, return_plot_script=False):
        # create ColumnDefinition from df.columns, use first row to get type
        cols = []
        for col in df.columns:
            cols.append(ColumnDefinition(name=col, type=str(type(df[col][0]))))

        params = PythonPlotRequest(dataframe_cols=cols, ask=ask)
        plot_response = WaiiHttpClient.get_instance().common_fetch(PLOT_ENDPOINT, params.__dict__, PythonPlotResponse)
        p = plot_response.plots[0]

        # if the p include ``` ... ```, only include lines between them, handle the case like
        # ```python
        # ...
        # ```
        # or
        # ```
        # <python code>
        # ```

        if p.startswith("```"):
            p = p[3:]
            if p.startswith("python"):
                p = p[6:]
            p = p.strip()
            p = p[:-3]
            p = p.strip()

        if automatically_exec:
            exec(p)

        if return_plot_script:
            return p
