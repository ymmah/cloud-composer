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
import unittest

from mappers import base_mapper
from airflow.utils.trigger_rule import TriggerRule
from xml.etree import ElementTree as ET


class TestDecisionMapper(unittest.TestCase):
    def setUp(self):
        doc = ET.Element("decision", attrib={"name": "decision"})

        # default does not have text

        self.et = ET.ElementTree(doc)
        self.mapper = base_mapper.BaseMapper(
            oozie_node=self.et.getroot(), name="test_id", trigger_rule=TriggerRule.DUMMY
        )

    def test_dummy_method(self):
        self.assertEqual(self.mapper.get_name(), "test_id")
        self.assertEqual(self.mapper.get_first_task_id(), "test_id")
        self.assertEqual(self.mapper.get_last_task_id(), "test_id")
