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

import pytest
from pytz import UTC
from requests import Response

from faculty.clients.experiment import (
    ExperimentRunStatus as FacultyExperimentRunStatus,
)
from faculty.clients.base import HTTPError
from mlflow.exceptions import MlflowException
from mlflow.entities import LifecycleStage, RunStatus

from mlflow_faculty.mlflow_converters import (
    faculty_http_error_to_mlflow_exception,
    faculty_experiment_to_mlflow_experiment,
    faculty_run_to_mlflow_run,
    mlflow_timestamp_to_datetime_milliseconds,
    mlflow_timestamp_to_datetime_seconds,
    faculty_tag_to_mlflow_tag,
    mlflow_metric_to_faculty_metric,
    mlflow_param_to_faculty_param,
    mlflow_tag_to_faculty_tag,
)
from mlflow_faculty.py23 import to_timestamp
from tests.fixtures import (
    FACULTY_EXPERIMENT,
    FACULTY_METRIC,
    FACULTY_PARAM,
    FACULTY_RUN,
    FACULTY_TAG,
    MLFLOW_METRIC,
    MLFLOW_PARAM,
    MLFLOW_TAG,
    mlflow_experiment,
    mlflow_run,
)


DATETIME = datetime(2018, 3, 10, 11, 45, 32, 110000, tzinfo=UTC)
DATETIME_MILLISECONDS = to_timestamp(DATETIME) * 1000


def experiment_equals(first, other):
    return (
        first.experiment_id == other.experiment_id
        and first.name == other.name
        and first.artifact_location == other.artifact_location
        and first.lifecycle_stage == other.lifecycle_stage
    )


def run_data_equals(first, other):
    return (
        first.metrics == other.metrics
        and first.params == other.params
        and first.tags == other.tags
    )


def run_equals(first, other):
    return run_data_equals(first.data, other.data) and first.info == other.info


def test_faculty_http_error_to_mlflow_exception():
    dummy_response = Response()
    dummy_response.status_code = 418
    faculty_http_error = HTTPError(dummy_response, "error", "error_code")

    assert isinstance(
        faculty_http_error_to_mlflow_exception(faculty_http_error),
        MlflowException,
    )


@pytest.mark.parametrize(
    "deleted_at, lifecycle_stage",
    [
        (None, LifecycleStage.ACTIVE),
        (datetime.now(tz=UTC), LifecycleStage.DELETED),
    ],
)
def test_faculty_experiment_to_mlflow_experiment(deleted_at, lifecycle_stage):
    faculty_experiment = FACULTY_EXPERIMENT._replace(deleted_at=deleted_at)
    expected_mlflow_experiment = mlflow_experiment(lifecycle_stage)

    assert experiment_equals(
        faculty_experiment_to_mlflow_experiment(faculty_experiment),
        expected_mlflow_experiment,
    )


@pytest.mark.parametrize(
    "faculty_run_status, mlflow_run_status",
    [
        (FacultyExperimentRunStatus.RUNNING, RunStatus.RUNNING),
        (FacultyExperimentRunStatus.FINISHED, RunStatus.FINISHED),
        (FacultyExperimentRunStatus.FAILED, RunStatus.FAILED),
        (FacultyExperimentRunStatus.SCHEDULED, RunStatus.SCHEDULED),
    ],
    ids=["running", "finishes", "failed", "scheduled"],
)
@pytest.mark.parametrize(
    "deleted_at, lifecycle_stage",
    [
        (None, LifecycleStage.ACTIVE),
        (datetime.now(tz=UTC), LifecycleStage.DELETED),
    ],
    ids=["active", "deleted"],
)
@pytest.mark.parametrize(
    "faculty_ended_at, mlflow_end_time",
    [(None, None), (DATETIME, DATETIME_MILLISECONDS)],
    ids=["not ended", "ended"],
)
def test_faculty_run_to_mlflow_run(
    faculty_run_status,
    mlflow_run_status,
    deleted_at,
    lifecycle_stage,
    faculty_ended_at,
    mlflow_end_time,
):
    faculty_run = FACULTY_RUN._replace(
        status=faculty_run_status,
        deleted_at=deleted_at,
        ended_at=faculty_ended_at,
    )

    expected_mlflow_run = mlflow_run(
        status=mlflow_run_status,
        end_time=mlflow_end_time,
        lifecycle_stage=lifecycle_stage,
    )

    assert run_equals(
        faculty_run_to_mlflow_run(faculty_run), expected_mlflow_run
    )


@pytest.mark.parametrize(
    "timestamp, expected_datetime",
    [
        (0, datetime(1970, 1, 1, tzinfo=UTC)),
        (1551884271987, datetime(2019, 3, 6, 14, 57, 51, 987000, tzinfo=UTC)),
    ],
)
def test_mlflow_timestamp_to_datetime_milliseconds(
    timestamp, expected_datetime
):
    assert (
        mlflow_timestamp_to_datetime_milliseconds(timestamp)
        == expected_datetime
    )


@pytest.mark.parametrize(
    "timestamp, expected_datetime",
    [
        (0, datetime(1970, 1, 1, tzinfo=UTC)),
        (1552484641, datetime(2019, 3, 13, 13, 44, 1, tzinfo=UTC)),
    ],
)
def test_mlflow_timestamp_to_datetime_seconds(timestamp, expected_datetime):
    assert mlflow_timestamp_to_datetime_seconds(timestamp) == expected_datetime


def test_faculty_tag_to_mlflow_tag():
    assert faculty_tag_to_mlflow_tag(FACULTY_TAG) == MLFLOW_TAG


def test_mlflow_metric_to_faculty_metric():
    assert mlflow_metric_to_faculty_metric(MLFLOW_METRIC) == FACULTY_METRIC


def test_mlflow_param_to_faculty_param():
    assert mlflow_param_to_faculty_param(MLFLOW_PARAM) == FACULTY_PARAM


def test_mlflow_tag_to_faculty_tag():
    assert mlflow_tag_to_faculty_tag(MLFLOW_TAG) == FACULTY_TAG
