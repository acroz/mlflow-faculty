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

import os

import faculty

# from mlflow.tracking.context import RunContextProvider


FACULTY_ENV_TAGS = [
    ("FACULTY_PROJECT_ID", "mlflow.faculty.project.projectId"),
    ("FACULTY_SERVER_ID", "mlflow.faculty.server.serverId"),
    ("FACULTY_SERVER_NAME", "mlflow.faculty.server.name"),
    ("NUM_CPUS", "mlflow.faculty.server.cpus"),
    ("AVAILABLE_MEMORY_MB", "mlflow.faculty.server.memoryMb"),
    ("NUM_GPUS", "mlflow.faculty.server.gpus"),
    ("FACULTY_JOB_ID", "mlflow.faculty.job.jobId"),
    ("FACULTY_JOB_NAME", "mlflow.faculty.job.name"),
    ("FACULTY_RUN_ID", "mlflow.faculty.job.runId"),
    ("FACULTY_RUN_NUMBER", "mlflow.faculty.job.runNumber"),
    ("FACULTY_SUBRUN_ID", "mlflow.faculty.job.subrunId"),
    ("FACULTY_SUBRUN_NUMBER", "mlflow.faculty.job.subrunNumber"),
]

USER_ID_TAG = "mlflow.faculty.user.userId"
USERNAME_TAG = "mlflow.faculty.user.username"


def _tags_from_account(account):
    return {USER_ID_TAG: str(account.user_id), USERNAME_TAG: account.username}


class FacultyRunContext:  # TODO: This should inherit from RunContextProvider
    def __init__(self):
        self._account_cache = None

    def _get_account(self):
        if self._account_cache is None:
            client = faculty.client("account")
            self._account_cache = client.authenticated_account()
        return self._account_cache

    def in_context(self):
        return bool(os.environ.get("FACULTY_PROJECT_ID"))

    def tags(self):
        tags = {}

        for environment_variable, tag_name in FACULTY_ENV_TAGS:
            value = os.environ.get(environment_variable)
            if value:
                tags[tag_name] = value
        try:
            account = self._get_account()
        except Exception:
            pass
        else:
            tags.update(_tags_from_account(account))

        return tags
