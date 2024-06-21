import functools
import threading
import time
import traceback
from typing import Optional, List, Dict, Any
from enum import Enum

from ..my_pydantic import BaseModel, Field

from ..common import CommonRequest, LLMBasedRequest
from ..database import SearchContext, TableName, ColumnDefinition, SchemaName
from ..semantic_context import SemanticStatement
from ..waii_http_client import WaiiHttpClient

GENERATE_ENDPOINT = "generate-query"
RUN_ENDPOINT = "run-query"
SUBMIT_ENDPOINT = "submit-query"
FAVORITE_ENDPOINT = "like-query"
DESCRIBE_ENDPOINT = "describe-query"
DIFF_ENDPOINT = "diff-query"
RESULTS_ENDPOINT = "get-query-result"
CANCEL_ENDPOINT = "cancel-query"
AUTOCOMPLETE_ENDPOINT = "auto-complete"
PERF_ENDPOINT = "get-query-performance"
TRANSCODE_ENDPOINT = "transcode-query"
PLOT_ENDPOINT = "python-plot"
GENERATE_QUESTION_ENDPOINT = "generate-questions"
GET_SIMILAR_QUERY_ENDPOINT = "get-similar-query"

class Tweak(BaseModel):
    sql: Optional[str] = None
    ask: Optional[str] = None


class TranscodeQueryRequest(LLMBasedRequest):
    search_context: Optional[List[SearchContext]] = None
    ask: Optional[str] = ""
    source_dialect: Optional[str] = None
    source_query: Optional[str] = None
    target_dialect: Optional[str] = None


class QueryGenerationRequest(LLMBasedRequest):
    search_context: Optional[List[SearchContext]] = None
    tweak_history: Optional[List[Tweak]] = None
    ask: Optional[str] = None
    uuid: Optional[str] = None
    dialect: Optional[str] = None
    parent_uuid: Optional[str] = None


class DescribeQueryRequest(CommonRequest):
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


class LLMUsageStatistics(BaseModel):
    # total tokens consumed by the LLM model
    token_total: Optional[int]


class Query(BaseModel):
    uuid: str
    ask: str
    query: str
    detailed_steps: Optional[List[str]]


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
    llm_usage_stats: Optional[LLMUsageStatistics] = None
    debug_info: Optional[Dict[str, Any]] = {}
    http_client: Optional[Any] = Field(default=None, exclude=True)

    def run(self):
        return QueryImpl(self.http_client).run(RunQueryRequest(query=self.query))


class RunQueryRequest(CommonRequest):
    query: str
    session_id: Optional[str] = None
    current_schema: Optional[SchemaName] = None
    session_parameters: Optional[Dict[str, Any]] = None


class RunQueryResponse(BaseModel):
    query_id: Optional[str] = None


class GetQueryResultRequest(CommonRequest):
    query_id: str


class CancelQueryRequest(CommonRequest):
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

        return pd.DataFrame(
            self.rows, columns=[col.name for col in self.column_definitions]
        )


class LikeQueryRequest(CommonRequest):
    # you need to specify either query_uuid or ask/query
    query_uuid: Optional[str]
    ask: Optional[str]
    query: Optional[str]

    liked: bool

    # do we want to rewrite the question before storing it? by default, it is True. If it is False, then we will store
    # the ask as-is
    rewrite_question: Optional[bool] = True


class LikeQueryResponse(BaseModel):
    pass


class AutoCompleteRequest(CommonRequest):
    text: str
    cursor_offset: Optional[int] = None
    dialect: Optional[str] = None
    search_context: Optional[List[SearchContext]] = None
    max_output_tokens: Optional[int] = None


class AutoCompleteResponse(BaseModel):
    text: Optional[str] = None


class QueryPerformanceRequest(CommonRequest):
    query_id: str


class QueryPerformanceResponse(BaseModel):
    summary: List[str]
    recommendations: List[str]
    query_text: str
    execution_time_ms: Optional[int]
    compilation_time_ms: Optional[int]


class PythonPlotRequest(CommonRequest):
    ask: Optional[str]
    dataframe_rows: Optional[List[Dict[str, Any]]]
    dataframe_cols: Optional[List[ColumnDefinition]]


class PythonPlotResponse(BaseModel):
    # based on the request, return N plot script
    plots: Optional[List[str]]


class GeneratedQuestionComplexity(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class GenerateQuestionRequest(CommonRequest):
    schema_name: str
    n_questions: Optional[int] = 10  # number of questions to generate
    complexity: Optional[GeneratedQuestionComplexity] = GeneratedQuestionComplexity.hard


class GeneratedQuestion(BaseModel):
    question: str
    complexity: GeneratedQuestionComplexity
    tables: Optional[List[TableName]]  # tables used in the question


class GenerateQuestionResponse(BaseModel):
    questions: Optional[List[GeneratedQuestion]]


class SimilarQueryResponse(BaseModel):
    qid: Optional[int]
    equivalent: Optional[bool]
    query: Optional[Query]


def show_progress(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        verbose = kwargs.get("verbose", False)

        if verbose:
            stop_event = threading.Event()
            dot_thread = threading.Thread(target=_print_dot, args=(stop_event,))
            dot_thread.start()

        try:
            return func(*args, **kwargs)
        except Exception as e:
            print("\nFailed:", e)
            raise
        finally:
            if verbose:
                stop_event.set()
                dot_thread.join()

    return wrapper


def _print_dot(stop_event):
    while not stop_event.is_set():
        print(".", end="", flush=True)
        time.sleep(1)


class QueryImpl:

    def __init__(self, http_client: WaiiHttpClient):
        self.http_client = http_client

    @show_progress
    def generate(self, params: QueryGenerationRequest, verbose=True) -> GeneratedQuery:
        generated = self.http_client.common_fetch(
            GENERATE_ENDPOINT, params.__dict__, GeneratedQuery
        )
        generated.http_client = self.http_client
        return generated

    @show_progress
    def run(self, params: RunQueryRequest, verbose=True) -> GetQueryResultResponse:
        return self.http_client.common_fetch(
            RUN_ENDPOINT, params.__dict__, GetQueryResultResponse
        )

    def like(self, params: LikeQueryRequest) -> LikeQueryResponse:
        return self.http_client.common_fetch(
            FAVORITE_ENDPOINT, params.__dict__, LikeQueryResponse
        )

    def submit(self, params: RunQueryRequest) -> RunQueryResponse:
        return self.http_client.common_fetch(
            SUBMIT_ENDPOINT, params.__dict__, RunQueryResponse
        )

    def get_results(self, params: GetQueryResultRequest) -> GetQueryResultResponse:
        return self.http_client.common_fetch(
            RESULTS_ENDPOINT, params.__dict__, GetQueryResultResponse
        )

    def cancel(self, params: CancelQueryRequest) -> CancelQueryResponse:
        return self.http_client.common_fetch(
            CANCEL_ENDPOINT, params.__dict__, CancelQueryResponse
        )

    def describe(self, params: DescribeQueryRequest) -> DescribeQueryResponse:
        return self.http_client.common_fetch(
            DESCRIBE_ENDPOINT, params.__dict__, DescribeQueryResponse
        )

    def auto_complete(self, params: AutoCompleteRequest) -> AutoCompleteResponse:
        return self.http_client.common_fetch(
            AUTOCOMPLETE_ENDPOINT, params.__dict__, AutoCompleteResponse
        )

    def diff(self, params: DiffQueryRequest) -> DiffQueryResponse:
        return self.http_client.common_fetch(
            DIFF_ENDPOINT, params.__dict__, DiffQueryResponse
        )

    def analyze_performance(
        self, params: QueryPerformanceRequest
    ) -> QueryPerformanceResponse:
        return self.http_client.common_fetch(
            PERF_ENDPOINT, params.__dict__, QueryPerformanceResponse
        )

    def transcode(self, params: TranscodeQueryRequest) -> GeneratedQuery:
        generated = self.http_client.common_fetch(
            TRANSCODE_ENDPOINT, params.__dict__, GeneratedQuery
        )
        generated.http_client = self.http_client
        return generated

    @show_progress
    def plot(
        self, df, ask=None, automatically_exec=True, verbose=True, max_retry=2
    ) -> str:
        if df is None or df.empty:
            raise ValueError("(Plot) Input dataframe is empty")

        # create ColumnDefinition from df.columns, use first row to get type
        cols = []
        for col in df.columns:
            cols.append(ColumnDefinition(name=col, type=df[col][0].__class__.__name__))

        params = PythonPlotRequest(dataframe_cols=cols, ask=ask)
        plot_response = self.http_client.common_fetch(
            PLOT_ENDPOINT, params.__dict__, PythonPlotResponse
        )
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

        retried = False
        if automatically_exec:
            try:
                exec(p)
            except Exception as e:
                if max_retry > 0:
                    retried = True
                    print(
                        f"Trying to fix error={str(e)}, Retry with max_retry={max_retry}"
                    )
                    fix_msg = "Fix the error and generate plot, find the following code and exception:"
                    if not ask:
                        ask = ""
                    return self.plot(
                        df,
                        ask=fix_msg
                        + f'"{ask}"'
                        + f"\ncode:```{p}```\nException:{str(e)}",
                        automatically_exec=automatically_exec,
                        verbose=verbose,
                        max_retry=max_retry - 1,
                    )
                else:
                    # print the code when not verbose (because finally will print the code if it is verbose)
                    if not verbose:
                        print("=== generated code ===")
                        print(p)
                    traceback.print_exc()
                    raise e

        if not retried and verbose:
            print("=== generated code ===")
            print(p)
        return p

    def generate_question(
        self, params: GenerateQuestionRequest
    ) -> GenerateQuestionResponse:
        return self.http_client.common_fetch(
            GENERATE_QUESTION_ENDPOINT, params.__dict__, GenerateQuestionResponse
        )

    def get_similar_query(
        self, params: QueryGenerationRequest
    ) -> SimilarQueryResponse:
        return self.http_client.common_fetch(
            GET_SIMILAR_QUERY_ENDPOINT, params.__dict__, SimilarQueryResponse
        )

Query = QueryImpl(WaiiHttpClient.get_instance())