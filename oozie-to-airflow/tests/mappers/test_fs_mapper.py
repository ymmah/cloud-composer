# -*- coding: utf-8 -*-
# Copyright 2019 Google LLC
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
"""Tests fs mapper"""

import ast
import unittest
from xml.etree import ElementTree as ET

from parameterized import parameterized
from airflow.utils.trigger_rule import TriggerRule

from mappers import fs_mapper

TEST_PARAMS = {"user.name": "pig", "nameNode": "hdfs://localhost:8020"}


# pylint: disable=invalid-name
class prepare_mkdir_commandTest(unittest.TestCase):
    @parameterized.expand(
        [
            (
                "<mkdir path='hdfs://localhost:8020/home/pig/test-fs/test-mkdir-1'/>",
                "fs -mkdir -p /home/pig/test-fs/test-mkdir-1",
            ),
            (
                "<mkdir path='${nameNode}/home/pig/test-fs/DDD-mkdir-1'/>",
                "fs -mkdir -p /home/pig/test-fs/DDD-mkdir-1",
            ),
        ]
    )
    def test_result(self, xml, command):
        node = ET.fromstring(xml)
        self.assertEqual(fs_mapper.prepare_mkdir_command(node, TEST_PARAMS), command)


class prepare_delete_commandTest(unittest.TestCase):
    @parameterized.expand(
        [
            (
                "<delete path='hdfs://localhost:8020/home/pig/test-fsXXX/test-delete-3'/>",
                "fs -rm -r /home/pig/test-fsXXX/test-delete-3",
            ),
            (
                "<delete path='hdfs://localhost:8020/home/pig/test-fs/test-delete-3'/>",
                "fs -rm -r /home/pig/test-fs/test-delete-3",
            ),
        ]
    )
    def test_result(self, xml, command):
        node = ET.fromstring(xml)
        self.assertEqual(fs_mapper.prepare_delete_command(node, TEST_PARAMS), command)


class prepare_move_commanddTest(unittest.TestCase):
    @parameterized.expand(
        [
            (
                "<move source='hdfs://localhost:8020/home/pig/test-fs/test-move-1' "
                "target='/home/pig/test-fs/test-move-2' />",
                "fs -mv /home/pig/test-fs/test-move-1 /home/pig/test-fs/test-move-2",
            ),
            (
                "<move source='${nameNode}/home/pig/test-fs/test-move-1' "
                "target='/home/pig/test-DDD/test-move-2' />",
                "fs -mv /home/pig/test-fs/test-move-1 /home/pig/test-DDD/test-move-2",
            ),
            (
                "<move source='${nameNode}/home/pig/test-fs/test-move-1' "
                "target='/home/pig/test-DDD/test-move-2' />",
                "fs -mv /home/pig/test-fs/test-move-1 /home/pig/test-DDD/test-move-2",
            ),
        ]
    )
    def test_result(self, xml, command):
        node = ET.fromstring(xml)
        self.assertEqual(fs_mapper.prepare_move_command(node, TEST_PARAMS), command)


class prepare_chmod_commandTest(unittest.TestCase):
    @parameterized.expand(
        [
            (
                "<chmod path='hdfs://localhost:8020/home/pig/test-fs/test-chmod-1' "
                "permissions='777' dir-files='false' />",
                "fs -chmod  777 /home/pig/test-fs/test-chmod-1",
            ),
            (
                "<chmod path='hdfs://localhost:8020/home/pig/test-fs/test-chmod-2' "
                "permissions='777' dir-files='true' />",
                "fs -chmod  777 /home/pig/test-fs/test-chmod-2",
            ),
            (
                "<chmod path='${nameNode}/home/pig/test-fs/test-chmod-3' permissions='777' />",
                "fs -chmod  777 /home/pig/test-fs/test-chmod-3",
            ),
            (
                """<chmod path='hdfs://localhost:8020/home/pig/test-fs/test-chmod-4'
                permissions='777' dir-files='false' >
         <recursive/>
         </chmod>""",
                "fs -chmod -R 777 /home/pig/test-fs/test-chmod-4",
            ),
        ]
    )
    def test_result(self, xml, command):
        node = ET.fromstring(xml)
        self.assertEqual(fs_mapper.prepare_chmod_command(node, TEST_PARAMS), command)


class prepare_touchz_commandTest(unittest.TestCase):
    @parameterized.expand(
        [
            (
                "<touchz path='hdfs://localhost:8020/home/pig/test-fs/test-touchz-1' />",
                "fs -touchz /home/pig/test-fs/test-touchz-1",
            ),
            (
                "<touchz path='${nameNode}/home/pig/test-fs/DDDD-touchz-1' />",
                "fs -touchz /home/pig/test-fs/DDDD-touchz-1",
            ),
        ]
    )
    def test_result(self, xml, command):
        node = ET.fromstring(xml)
        self.assertEqual(fs_mapper.prepare_touchz_command(node, TEST_PARAMS), command)


class prepare_chgrp_commandTest(unittest.TestCase):
    @parameterized.expand(
        [
            (
                "<chgrp path='hdfs://localhost:8020/home/pig/test-fs/test-chgrp-1' group='hadoop' />",
                "fs -chgrp  hadoop /home/pig/test-fs/test-chgrp-1",
            ),
            (
                "<chgrp path='${nameNode}0/home/pig/test-fs/DDD-chgrp-1' group='hadoop' />",
                "fs -chgrp  hadoop /home/pig/test-fs/DDD-chgrp-1",
            ),
        ]
    )
    def test_result(self, xml, command):
        node = ET.fromstring(xml)
        self.assertEqual(fs_mapper.prepare_chgrp_command(node, TEST_PARAMS), command)


class FsMapperSingleTestCase(unittest.TestCase):
    def setUp(self):
        # language=XML
        node_str = """
            <fs>
                <mkdir path='hdfs://localhost:9200/home/pig/test-delete-1'/>
            </fs>"""
        self.node = ET.fromstring(node_str)

        self.mapper = fs_mapper.FsMapper(oozie_node=self.node, name="test_id", trigger_rule=TriggerRule.DUMMY)
        self.mapper.on_parse_node()

    def test_convert_to_text(self):
        # Throws a syntax error if doesn't parse correctly
        self.assertIsNotNone(ast.parse(self.mapper.convert_to_text()))

    def test_required_imports(self):
        imps = fs_mapper.FsMapper.required_imports()
        imp_str = "\n".join(imps)
        self.assertIsNotNone(ast.parse(imp_str))

    def test_get_first_task_id(self):
        self.assertEqual(self.mapper.first_task_id, "test_id")

    def test_get_last_task_id(self):
        self.assertEqual(self.mapper.last_task_id, "test_id")


class FsMapperEmptyTestCase(unittest.TestCase):
    def setUp(self):
        self.node = ET.Element("fs")
        self.mapper = fs_mapper.FsMapper(oozie_node=self.node, name="test_id", trigger_rule=TriggerRule.DUMMY)
        self.mapper.on_parse_node()

    def test_convert_to_text(self):
        # Throws a syntax error if doesn't parse correctly
        self.assertIsNotNone(ast.parse(self.mapper.convert_to_text()))

    def test_required_imports(self):
        imps = fs_mapper.FsMapper.required_imports()
        imp_str = "\n".join(imps)
        self.assertIsNotNone(ast.parse(imp_str))

    def test_get_first_task_id(self):
        self.assertEqual(self.mapper.first_task_id, "test_id")

    def test_get_last_task_id(self):
        self.assertEqual(self.mapper.last_task_id, "test_id")


class FsMapperComplexTestCase(unittest.TestCase):
    def setUp(self):
        # language=XML
        node_str = """
            <fs>
                <!-- mkdir -->
                <mkdir path='hdfs://localhost:9200/home/pig/test-delete-1'/>
                <mkdir path='hdfs:///home/pig/test-delete-2'/>
                <!-- delete -->
                <mkdir path='hdfs://localhost:9200/home/pig/test-delete-1'/>
                <mkdir path='hdfs://localhost:9200/home/pig/test-delete-2'/>
                <mkdir path='hdfs://localhost:9200/home/pig/test-delete-3'/>
                <delete path='hdfs://localhost:9200/home/pig/test-delete-1'/>

                <!-- move -->
                <mkdir path='hdfs://localhost:9200/home/pig/test-delete-1'/>
                <move source='hdfs://localhost:9200/home/pig/test-chmod-1' target='/home/pig/test-chmod-2' />

                <!-- chmod -->
                <mkdir path='hdfs://localhost:9200/home/pig/test-chmod-1'/>
                <mkdir path='hdfs://localhost:9200/home/pig/test-chmod-2'/>
                <mkdir path='hdfs://localhost:9200/home/pig/test-chmod-3'/>
                <mkdir path='hdfs://localhost:9200/home/pig/test-chmod-4'/>
                <chmod path='hdfs://localhost:9200/home/pig/test-chmod-1'
                    permissions='-rwxrw-rw-' dir-files='false' />
                <chmod path='hdfs://localhost:9200/home/pig/test-chmod-2'
                    permissions='-rwxrw-rw-' dir-files='true' />
                <chmod path='hdfs://localhost:9200/home/pig/test-chmod-3'
                    permissions='-rwxrw-rw-' />
                <chmod path='hdfs://localhost:9200/home/pig/test-chmod-4'
                    permissions='-rwxrw-rw-' dir-files='false' >
                    <recursive/>
                </chmod>

                <!-- touchz -->
                <touchz path='hdfs://localhost:9200/home/pig/test-touchz-1' />

                <!-- chgrp -->
                <chgrp path='hdfs://localhost:9200/home/pig/test-touchz-1' group='pig' />
            </fs>"""
        self.node = ET.fromstring(node_str)

        self.mapper = fs_mapper.FsMapper(oozie_node=self.node, name="test_id", trigger_rule=TriggerRule.DUMMY)
        self.mapper.on_parse_node()

    def test_convert_to_text(self):
        # Throws a syntax error if doesn't parse correctly
        self.assertIsNotNone(ast.parse(self.mapper.convert_to_text()))

    def test_required_imports(self):
        imps = fs_mapper.FsMapper.required_imports()
        imp_str = "\n".join(imps)
        self.assertIsNotNone(ast.parse(imp_str))

    def test_get_first_task_id(self):
        self.assertEqual(self.mapper.first_task_id, "test_id_fs_0_mkdir")

    def test_get_last_task_id(self):
        self.assertEqual(self.mapper.last_task_id, "test_id_fs_17_chgrp")
