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

from enum import Enum
from typing import Optional, Literal, List, Union, Dict, Any

from ..database import ColumnDefinition
from ..my_pydantic import WaiiBaseModel

from ..common import LLMBasedRequest
from waii_sdk_py.utils import wrap_methods_with_async
from ..waii_http_client import WaiiHttpClient

GENERATE_CHART_ENDPOINT = "generate-chart"


class ChartType(str, Enum):
    METABASE = "metabase"
    SUPERSET = "superset"
    PLOTLY = "plotly"
    VEGALITE = "vegalite"


class SuperSetChartSpec(WaiiBaseModel):
    spec_type: Literal['superset']
    plot_type: Optional[str]
    metrics: Optional[List[str]]
    dimensions: Optional[List[str]]
    chart_name: Optional[str]
    color_hex: Optional[str]
    x_axis: Optional[str]
    y_axis: Optional[str]
    grid_style: Optional[str]
    stacked: Optional[bool]
    width: Optional[int]
    height: Optional[int]


class MetabaseChartSpec(WaiiBaseModel):
    spec_type: Literal['metabase']
    plot_type: Optional[str]
    metric: Optional[str]
    dimension: Optional[str]
    name: Optional[str]
    color_hex: Optional[str]


class PlotlyChartSpec(WaiiBaseModel):
    spec_type: Literal['plotly'] = 'plotly'
    plot: Optional[str]


class VegaliteChartSpec(WaiiBaseModel):
    spec_type: Literal['vegalite'] = 'vegalite'
    chart: Optional[str]
    number_of_data_points: Optional[int] = None
    generation_message: Optional[str] = None


class ChartTweak(WaiiBaseModel):
    ask: Optional[str]
    chart_spec: Optional[Union[SuperSetChartSpec, MetabaseChartSpec, PlotlyChartSpec, VegaliteChartSpec]]

    def __str__(self):
        return f"previous ask={self.ask}, previous chart_spec={self.chart_spec})\n"


class ChartGenerationRequest(LLMBasedRequest):
    sql: Optional[str]
    ask: Optional[str]
    dataframe_rows: Optional[List[Dict[str, Any]]]
    dataframe_cols: Optional[List[ColumnDefinition]]
    chart_type: Optional[ChartType]
    parent_uuid: Optional[str]
    tweak_history: Optional[List[ChartTweak]]


class ChartGenerationResponse(WaiiBaseModel):
    uuid: str
    timestamp_ms: Optional[int]
    chart_spec: Optional[Union[SuperSetChartSpec, MetabaseChartSpec, PlotlyChartSpec, VegaliteChartSpec]]


class ChartImpl:

    def __init__(self, http_client: WaiiHttpClient):
        self.http_client = http_client

    def generate_chart(
        self, df, ask=None, sql=None, chart_type=None, parent_uuid=None, tweak_history=None,
    ) -> ChartGenerationResponse:

        #Remove duplicate columns
        df = df.loc[:, ~df.columns.duplicated()]

        cols = []
        for col in df.columns:
            cols.append(ColumnDefinition(name=col, type=df[col][0].__class__.__name__))

        params = ChartGenerationRequest(dataframe_cols=cols,
                                        dataframe_rows=df.to_dict(orient='records'),
                                        ask=ask,
                                        chart_type=chart_type,
                                        parent_uuid=parent_uuid,
                                        tweak_history=tweak_history)
        params.check_extra_fields()
        params_dict = {k: v.value if isinstance(v, Enum) else v for k, v in params.dict().items() if v is not None}

        return self.http_client.common_fetch(
            GENERATE_CHART_ENDPOINT, params_dict, ChartGenerationResponse
        )


class AsyncChartImpl:
    def __init__(self, http_client: WaiiHttpClient):
        self._chart_impl = ChartImpl(http_client)
        wrap_methods_with_async(self._chart_impl, self)


Chart = ChartImpl(WaiiHttpClient.get_instance())
