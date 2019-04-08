# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from typing import Set

from airflow.operators import dummy_operator

from mappers.base_mapper import BaseMapper
from utils.template_utils import render_template


class DummyMapper(BaseMapper):
    def convert_to_text(self):
        return render_template(template_name="dummy.tpl", task_id=self.name, trigger_rule=self.trigger_rule)

    @staticmethod
    def required_imports() -> Set[str]:
        return {"from airflow.operators import dummy_operator"}

    # noinspection PyMethodMayBeStatic
    def has_prepare(self) -> bool:
        """ Required for Unknown Action Mapper """
        return False
