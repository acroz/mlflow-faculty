# Copyright 2019 Faculty Science Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from datetime import datetime
from uuid import uuid4

from faculty.clients.experiment import (
    Experiment as FacultyExperiment,
    ExperimentRun,
    ExperimentRunStatus,
    Metric as FacultyMetric,
    Param as FacultyParam,
    Tag as FacultyTag,
)
from mlflow.entities import (
    Experiment,
    LifecycleStage,
    Metric,
    Param,
    Run,
    RunTag,
    RunData,
    RunInfo,
    RunStatus,
)
from pytz import UTC

from mlflow_faculty.py23 import to_timestamp


PROJECT_ID = uuid4()
EXPERIMENT_ID = 12

NAME = "experiment name"
ARTIFACT_LOCATION = "scheme://artifact-location"

METRIC_TIMESTAMP = datetime(2019, 3, 13, 17, 0, 15, tzinfo=UTC)
METRIC_TIMESTAMP_SECONDS = to_timestamp(METRIC_TIMESTAMP)
FACULTY_METRIC = FacultyMetric(
    key="metric-key", value="metric-value", timestamp=METRIC_TIMESTAMP
)
MLFLOW_METRIC = Metric("metric-key", "metric-value", METRIC_TIMESTAMP_SECONDS)

FACULTY_PARAM = FacultyParam(key="param-key", value="param-value")
MLFLOW_PARAM = Param("param-key", "param-value")

FACULTY_TAG = FacultyTag(key="tag-key", value="tag-value")
MLFLOW_TAG = RunTag("tag-key", "tag-value")

FACULTY_EXPERIMENT = FacultyExperiment(
    id=EXPERIMENT_ID,
    name=NAME,
    description="not used",
    artifact_location=ARTIFACT_LOCATION,
    created_at=datetime.now(tz=UTC),
    last_updated_at=datetime.now(tz=UTC),
    deleted_at=None,
)

RUN_UUID = uuid4()
RUN_UUID_HEX_STR = RUN_UUID.hex
RUN_NUMBER = 42

RUN_STARTED_AT = datetime(2018, 3, 10, 11, 39, 12, 110000, tzinfo=UTC)
RUN_STARTED_AT_MILLISECONDS = to_timestamp(RUN_STARTED_AT) * 1000
RUN_ENDED_AT = datetime(2018, 3, 11, 11, 39, 12, 110000, tzinfo=UTC)

FACULTY_RUN = ExperimentRun(
    id=RUN_UUID,
    run_number=RUN_NUMBER,
    experiment_id=FACULTY_EXPERIMENT.id,
    artifact_location=ARTIFACT_LOCATION,
    status=ExperimentRunStatus.RUNNING,
    started_at=RUN_STARTED_AT,
    ended_at=None,
    deleted_at=None,
    tags=[FACULTY_TAG],
    params=[],
    metrics=[],
)


def mlflow_experiment(lifecycle_stage=LifecycleStage.ACTIVE):
    return Experiment(EXPERIMENT_ID, NAME, ARTIFACT_LOCATION, lifecycle_stage)


def mlflow_run(
    status=RunStatus.RUNNING,
    end_time=None,
    lifecycle_stage=LifecycleStage.ACTIVE,
):
    data = RunData(tags=[MLFLOW_TAG])
    info = RunInfo(
        RUN_UUID_HEX_STR,
        EXPERIMENT_ID,
        "",  # name
        "",  # source_type
        "",  # source_name
        "",  # entry_point_name
        "",  # user_id
        status,
        RUN_STARTED_AT_MILLISECONDS,
        end_time,
        "",  # source_version
        lifecycle_stage,
        ARTIFACT_LOCATION,
    )
    return Run(info, data)
