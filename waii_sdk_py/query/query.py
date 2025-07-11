"""
Copyright 2023–2025 Waii, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import functools
import inspect
import math
import threading
import time
import traceback
from typing import Optional, List, Dict, Any, Union, Literal
from enum import Enum, IntEnum

from ..my_pydantic import WaiiBaseModel, Field

from ..common import CommonRequest, LLMBasedRequest, GetObjectRequest, AsyncObjectResponse, CommonResponse
from ..database import SearchContext, TableName, ColumnDefinition, SchemaName
from ..semantic_context import SemanticStatement
from ..waii_http_client import WaiiHttpClient
from waii_sdk_py.utils import wrap_methods_with_async

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
RUN_QUERY_COMPILER_ENDPOINT = "run-query-compiler"
SEMANTIC_CONTEXT_CHECKER_ENDPOINT = "semantic-context-checker"
APPLY_TABLE_ACCESS_RULES_ENDPOINT = "apply-table-access-rules"
SUBMIT_GENERATE_QUERY_ENDPOINT = "submit-generate-query"
GET_GENERATED_QUERY_ENDPOINT = "get-generated-query"
GET_LIKED_QUERY_ENDPOINT = "get-liked-query"


class DebugInfoType(str, Enum):
    learned_template = "learned_template"
    retry_info = "retry_info"
    equivalent = "equivalent"
    fixit_info = "fixit_info"
    query_gen_source = "query_gen_source"
    query_gen_model = "query_gen_model"
    empty_table_selection = "empty_table_selection"
    after_tweak_history = "after_considering_tweak_history"
    after_info_schema_check = "after_info_schema_check"
    after_embedding_match = "after_embedding_match"
    after_initial_table_selection = "after_initial_table_selection"
    after_iterative_table_selection = "after_iterative_table_selection"


class Tweak(WaiiBaseModel):
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
    flags: Optional[Dict[str, Any]] = {}
    # do we want to use example queries during query generation
    use_example_queries: Optional[bool] = True
    additional_context: Optional[List[SemanticStatement]] = None


class DescribeQueryResponse(WaiiBaseModel):
    summary: Optional[str] = None
    detailed_steps: Optional[List[str]] = None
    tables: Optional[List[TableName]] = None


class DiffQueryResponse(DescribeQueryResponse):
    summary: Optional[str] = None
    tables: Optional[List[TableName]] = None
    detailed_steps: Optional[List[str]] = None
    what_changed: Optional[str] = None


class CompilationError(WaiiBaseModel):
    message: str
    line: Optional[int] = None


class LLMUsageStatistics(WaiiBaseModel):
    # total tokens consumed by the LLM model
    token_total: Optional[int]


class Query(WaiiBaseModel):
    uuid: str
    ask: str
    query: str
    detailed_steps: Optional[List[str]]


class ConfidenceScore(WaiiBaseModel):
    log_prob_sum: Optional[float]
    token_count: Optional[int]
    confidence_value: Optional[float]

    def get_linear_probability(self):
        if self.token_count:
            avg_log_prob = self.log_prob_sum / self.token_count

            return math.exp(avg_log_prob)
        else:
            return 0.0


class AccessRuleProtectionState(str, Enum):
    protected = "protected"  # Query is completely protected regarding access rules
    unprotected = "unprotected"  # Query is not guaranteed to be protected, see error msg for details
    uncompilable = "uncompilable"
    unexplainable = "unexplainable"


class AccessRuleProtectionStatus(WaiiBaseModel):
    state: AccessRuleProtectionState
    msg: Optional[str]


class ApplyTableAccessRulesResponse(WaiiBaseModel):
    query: str
    status: AccessRuleProtectionStatus


class QueryGenerationStep(str, Enum):
    selecting_tables_and_rules = "Selecting Tables and Rules"
    generating_query = "Generating Query"
    validating_query = "Validating Query"
    completed = "Completed"


class GeneratedQuery(WaiiBaseModel):
    current_step: Optional[QueryGenerationStep] = None
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
    confidence_score: Optional[ConfidenceScore]
    debug_info: Optional[Dict[str, Any]] = {}
    elapsed_time_ms: Optional[int] = None  # elapsed time in milliseconds
    assumptions: Optional[List[str]] = None

    http_client: Optional[Any] = Field(default=None, exclude=True)

    def run(self):
        return QueryImpl(self.http_client).run(RunQueryRequest(query=self.query))

    def apply_table_access_rules(self) -> ApplyTableAccessRulesResponse:
        return QueryImpl(self.http_client).apply_table_access_rules(ApplyTableAccessRulesRequest(query=self.query))


class TargetPersona(str, Enum):
    sql_expert = "sql_expert"
    domain_expert = "domain_expert"


class DescribeQueryRequest(CommonRequest):
    search_context: Optional[List[SearchContext]]
    current_schema: Optional[str]
    query: Optional[str]
    asks: Optional[List[str]]
    semantic_context: Optional[List[SemanticStatement]] = None
    persona: Optional[TargetPersona] = TargetPersona.sql_expert


class DiffQueryRequest(DescribeQueryRequest):
    previous_query: Optional[str] = None


class RunQueryRequest(CommonRequest):
    query: str
    session_id: Optional[str] = None
    current_schema: Optional[SchemaName] = None
    session_parameters: Optional[Dict[str, Any]] = None


class RunQueryCompilerRequest(CommonRequest):
    query: str
    search_context: Optional[List[SearchContext]]
    additional_context: Optional[List[SemanticStatement]] = None


class RunQueryResponse(WaiiBaseModel):
    query_id: Optional[str] = None


class GetQueryResultRequest(CommonRequest):
    query_id: str
    max_returned_rows: Optional[int] = 10000


class CancelQueryRequest(CommonRequest):
    query_id: str


class CancelQueryResponse(WaiiBaseModel):
    pass


class GetQueryResultResponse(WaiiBaseModel):
    rows: Optional[List[object]] = None
    more_rows: Optional[int] = None
    column_definitions: Optional[List[ColumnDefinition]] = None
    query_uuid: Optional[str] = None

    def to_pandas_df(self):
        import pandas as pd

        return pd.DataFrame(
            self.rows, columns=[col.name for col in self.column_definitions]
        )


class LikedQuery(WaiiBaseModel):
    # you need to specify either query_uuid or ask/query
    query_uuid: Optional[str]
    ask: Optional[str]
    query: Optional[str]

    liked: bool

    # do we want to rewrite the question before storing it? by default, it is True. If it is False, then we will store
    # the ask as-is
    rewrite_question: Optional[bool] = False
    detailed_steps: Optional[List[str]] = []

    # by default, like query request applies to the current user only, there's an option to apply to other users
    target_user_id: Optional[str] = None
    target_tenant_id: Optional[str] = None
    target_org_id: Optional[str] = None


class GetLikedQueryRequest(CommonRequest):
    query_uuid: Optional[str] = None


class GetLikedQueryResponse(CommonResponse):
    queries: Optional[List[LikedQuery]] = None


class LikeQueryRequest(CommonRequest, LikedQuery):
    pass


class LikeQueryResponse(WaiiBaseModel):
    queries: Optional[List[LikedQuery]]


class AutoCompleteRequest(CommonRequest):
    text: str
    cursor_offset: Optional[int] = None
    dialect: Optional[str] = None
    search_context: Optional[List[SearchContext]] = None
    max_output_tokens: Optional[int] = None


class AutoCompleteResponse(WaiiBaseModel):
    text: Optional[str] = None


class QueryPerformanceRequest(CommonRequest):
    query_id: str


class QueryPerformanceResponse(WaiiBaseModel):
    summary: List[str]
    recommendations: List[str]
    query_text: str
    execution_time_ms: Optional[int]
    compilation_time_ms: Optional[int]


class PythonPlotRequest(LLMBasedRequest):
    ask: Optional[str]
    dataframe_rows: Optional[List[Dict[str, Any]]]
    dataframe_cols: Optional[List[ColumnDefinition]]


class PythonPlotResponse(WaiiBaseModel):
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


class GeneratedQuestion(WaiiBaseModel):
    question: str
    complexity: GeneratedQuestionComplexity
    tables: Optional[List[TableName]]  # tables used in the question


class GenerateQuestionResponse(WaiiBaseModel):
    questions: Optional[List[GeneratedQuestion]]


class SimilarQueryResponse(WaiiBaseModel):
    qid: Optional[int]
    equivalent: Optional[bool]
    query: Optional[Query]


class CompilationStateFromDBEngine(IntEnum):
    UNKNOWN = 0,  # this happens when explain query itself failed (because of permission, etc.)
    COMPILABLE = 1,
    UNCOMPILABLE = 2


class CompilationErrorMsgFromDBEngine(WaiiBaseModel):
    state: CompilationStateFromDBEngine
    msg: Optional[str]


class RunQueryCompilerResponse(WaiiBaseModel):
    query: str
    errors: str
    should_compile: bool
    tables: Optional[List[TableName]]
    explain_error_msg: CompilationErrorMsgFromDBEngine
    enforce_table_access_rules_response: Optional[ApplyTableAccessRulesResponse]


class SemanticContextCheckerRequest(LLMBasedRequest):
    ask: Optional[str]
    query: Optional[str]
    dialect: Optional[str]
    search_context: Optional[List[SearchContext]]
    flags: Optional[Dict[str, Any]]


class ApplyTableAccessRulesRequest(CommonRequest):
    query: str


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
            GENERATE_ENDPOINT, params, GeneratedQuery
        )
        generated.http_client = self.http_client
        return generated

    @show_progress
    def run(self, params: RunQueryRequest, verbose=True) -> GetQueryResultResponse:
        return self.http_client.common_fetch(
            RUN_ENDPOINT, params, GetQueryResultResponse
        )

    def like(self, params: LikeQueryRequest) -> LikeQueryResponse:
        return self.http_client.common_fetch(
            FAVORITE_ENDPOINT, params, LikeQueryResponse
        )

    def submit(self, params: RunQueryRequest) -> RunQueryResponse:
        return self.http_client.common_fetch(
            SUBMIT_ENDPOINT, params, RunQueryResponse
        )

    def get_results(self, params: GetQueryResultRequest) -> GetQueryResultResponse:
        return self.http_client.common_fetch(
            RESULTS_ENDPOINT, params, GetQueryResultResponse
        )

    def cancel(self, params: CancelQueryRequest) -> CancelQueryResponse:
        return self.http_client.common_fetch(
            CANCEL_ENDPOINT, params, CancelQueryResponse
        )

    def describe(self, params: DescribeQueryRequest) -> DescribeQueryResponse:
        return self.http_client.common_fetch(
            DESCRIBE_ENDPOINT, params, DescribeQueryResponse
        )

    def auto_complete(self, params: AutoCompleteRequest) -> AutoCompleteResponse:
        return self.http_client.common_fetch(
            AUTOCOMPLETE_ENDPOINT, params, AutoCompleteResponse
        )

    def diff(self, params: DiffQueryRequest) -> DiffQueryResponse:
        return self.http_client.common_fetch(
            DIFF_ENDPOINT, params, DiffQueryResponse
        )

    def analyze_performance(
        self, params: QueryPerformanceRequest
    ) -> QueryPerformanceResponse:
        return self.http_client.common_fetch(
            PERF_ENDPOINT, params, QueryPerformanceResponse
        )

    def transcode(self, params: TranscodeQueryRequest) -> GeneratedQuery:
        generated = self.http_client.common_fetch(
            TRANSCODE_ENDPOINT, params, GeneratedQuery
        )
        generated.http_client = self.http_client
        return generated

    @show_progress
    def plot(
        self, df, ask=None, automatically_exec=True, verbose=True, max_retry=2, model=None
    ) -> str:
        if df is None or df.empty:
            raise ValueError("(Plot) Input dataframe is empty")

        # create ColumnDefinition from df.columns, use first row to get type
        cols = []
        for col in df.columns:
            cols.append(ColumnDefinition(name=col, type=df[col][0].__class__.__name__))

        params = PythonPlotRequest(dataframe_cols=cols, ask=ask, model=model)
        plot_response = self.http_client.common_fetch(
            PLOT_ENDPOINT, params, PythonPlotResponse
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
            GENERATE_QUESTION_ENDPOINT, params, GenerateQuestionResponse
        )

    def get_similar_query(
        self, params: QueryGenerationRequest
    ) -> SimilarQueryResponse:
        return self.http_client.common_fetch(
            GET_SIMILAR_QUERY_ENDPOINT, params, SimilarQueryResponse
        )

    def run_query_compiler(
            self, params: RunQueryCompilerRequest
    ) -> RunQueryCompilerResponse:
        return self.http_client.common_fetch(
            RUN_QUERY_COMPILER_ENDPOINT, params, RunQueryCompilerResponse
        )

    def handle_semantic_context_checker(
            self, params: SemanticContextCheckerRequest
    ) -> GeneratedQuery:
        return self.http_client.common_fetch(
            SEMANTIC_CONTEXT_CHECKER_ENDPOINT, params, GeneratedQuery
        )

    def apply_table_access_rules(
            self, params: ApplyTableAccessRulesRequest
    ) -> ApplyTableAccessRulesResponse:
        return self.http_client.common_fetch(
            APPLY_TABLE_ACCESS_RULES_ENDPOINT, params, ApplyTableAccessRulesResponse
        )

    def submit_generate_query(
            self, params: QueryGenerationRequest
    ) -> AsyncObjectResponse:
        return self.http_client.common_fetch(
            SUBMIT_GENERATE_QUERY_ENDPOINT, params, AsyncObjectResponse,
        )

    def get_generated_query(
            self, params: GetObjectRequest
    ) -> GeneratedQuery:
        return self.http_client.common_fetch(
            GET_GENERATED_QUERY_ENDPOINT, params, GeneratedQuery
        )

    def get_liked_query(self, params: GetLikedQueryRequest) -> GetLikedQueryResponse:
        return self.http_client.common_fetch(
            GET_LIKED_QUERY_ENDPOINT, params, GetLikedQueryResponse
        )


class AsyncQueryImpl:
    """
    Asynchronous wrapper for QueryImpl that automatically converts all public methods to async.
    """

    def __init__(self, http_client: WaiiHttpClient):
        self._query_impl = QueryImpl(http_client)
        wrap_methods_with_async(self._query_impl, self)


Query = QueryImpl(WaiiHttpClient.get_instance())