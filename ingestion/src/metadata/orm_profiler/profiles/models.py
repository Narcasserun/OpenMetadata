#  Copyright 2021 Collate
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#  http://www.apache.org/licenses/LICENSE-2.0
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

"""
Models to map profiles definitions
JSON workflows to the profiler
"""
from typing import List

from pydantic import BaseModel, validator

from metadata.orm_profiler.metrics.registry import Metrics


class TimeMetricDef(BaseModel):
    """
    Model representing the input of a time metric
    """

    name: str  # metric name
    window: int  # time delta in days to apply


class CustomMetricDef(BaseModel):
    """
    Model representing the input of a time metric
    """

    name: str  # metric name
    sql: str  # custom SQL query to run


class ProfilerDef(BaseModel):
    """
    Incoming profiler definition from the
    JSON workflow
    """

    name: str  # Profiler name
    table_metrics: List[str]  # names of supported table metrics
    metrics: List[str]  # names of currently supported Static and Composed metrics
    time_metrics: List[TimeMetricDef] = None
    custom_metrics: List[CustomMetricDef] = None
    # rule_metrics: ...

    @validator("metrics", "table_metrics", each_item=True)
    def valid_metric(cls, value):  # cls as per pydantic docs
        """
        Validate that the input metrics are correctly named
        and can be found in the Registry
        """
        if not Metrics.get(value.upper()):
            raise ValueError(
                f"Metric name {value} is not a proper metric name from the Registry"
            )

        return value.upper()
