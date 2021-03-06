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
"""Tests for the MapReduce mapper"""
import ast
import unittest
from xml.etree import ElementTree as ET

from airflow.utils.trigger_rule import TriggerRule

from mappers import mapreduce_mapper


class TestMapReduceMapper(unittest.TestCase):
    def setUp(self):
        # language=XML
        mapreduce_node_str = """
<map-reduce>
    <name-node>hdfs://</name-node>
    <prepare>
        <delete path="${nameNode}/examples/mapreduce/output" />
    </prepare>
    <configuration>
        <property>
            <name>mapred.mapper.new-api</name>
            <value>true</value>
        </property>
        <property>
            <name>mapred.reducer.new-api</name>
            <value>true</value>
        </property>
        <property>
            <name>mapred.job.queue.name</name>
            <value>${queueName}</value>
        </property>
        <property>
            <name>mapreduce.job.map.class</name>
            <value>WordCount$Map</value>
        </property>
        <property>
            <name>mapreduce.job.reduce.class</name>
            <value>WordCount$Reduce</value>
        </property>
        <property>
            <name>mapreduce.job.output.key.class</name>
            <value>org.apache.hadoop.io.Text</value>
        </property>
        <property>
            <name>mapreduce.job.output.value.class</name>
            <value>org.apache.hadoop.io.IntWritable</value>
        </property>
        <property>
            <name>mapreduce.input.fileinputformat.inputdir</name>
            <value>/user/mapred/${examplesRoot}/mapreduce/input</value>
        </property>
        <property>
            <name>mapreduce.output.fileoutputformat.outputdir</name>
            <value>/user/mapred/${examplesRoot}/mapreduce/output</value>
        </property>
    </configuration>
</map-reduce>
"""
        self.mapreduce_node = ET.fromstring(mapreduce_node_str)

    def test_create_mapper_no_jinja(self):
        mapper = mapreduce_mapper.MapReduceMapper(
            oozie_node=self.mapreduce_node, name="test_id", trigger_rule=TriggerRule.DUMMY
        )
        # make sure everything is getting initialized correctly
        self.assertEqual("test_id", mapper.name)
        self.assertEqual(TriggerRule.DUMMY, mapper.trigger_rule)
        self.assertEqual(self.mapreduce_node, mapper.oozie_node)
        self.assertEqual("hdfs://", mapper.name_node)
        self.assertEqual("${queueName}", mapper.properties["mapred.job.queue.name"])
        self.assertEqual("WordCount$Map", mapper.properties["mapreduce.job.map.class"])
        self.assertEqual("WordCount$Reduce", mapper.properties["mapreduce.job.reduce.class"])
        self.assertEqual("org.apache.hadoop.io.Text", mapper.properties["mapreduce.job.output.key.class"])
        self.assertEqual(
            "org.apache.hadoop.io.IntWritable", mapper.properties["mapreduce.job.output.value.class"]
        )
        self.assertEqual(
            "/user/mapred/${examplesRoot}/mapreduce/input",
            mapper.properties["mapreduce.input.fileinputformat.inputdir"],
        )
        self.assertEqual(
            "/user/mapred/${examplesRoot}/mapreduce/output",
            mapper.properties["mapreduce.output.fileoutputformat.outputdir"],
        )

    def test_create_mapper_jinja(self):
        # test jinja templating
        params = {"nameNode": "hdfs://", "queueName": "myQueue", "examplesRoot": "examples"}

        mapper = mapreduce_mapper.MapReduceMapper(
            oozie_node=self.mapreduce_node, name="test_id", trigger_rule=TriggerRule.DUMMY, params=params
        )

        # make sure everything is getting initialized correctly
        self.assertEqual("test_id", mapper.name)
        self.assertEqual(TriggerRule.DUMMY, mapper.trigger_rule)
        self.assertEqual(self.mapreduce_node, mapper.oozie_node)
        self.assertEqual("hdfs://", mapper.name_node)
        self.assertEqual("myQueue", mapper.properties["mapred.job.queue.name"])
        self.assertEqual("WordCount$Map", mapper.properties["mapreduce.job.map.class"])
        self.assertEqual("WordCount$Reduce", mapper.properties["mapreduce.job.reduce.class"])
        self.assertEqual("org.apache.hadoop.io.Text", mapper.properties["mapreduce.job.output.key.class"])
        self.assertEqual(
            "org.apache.hadoop.io.IntWritable", mapper.properties["mapreduce.job.output.value.class"]
        )
        self.assertEqual(
            "/user/mapred/examples/mapreduce/input",
            mapper.properties["mapreduce.input.fileinputformat.inputdir"],
        )
        self.assertEqual(
            "/user/mapred/examples/mapreduce/output",
            mapper.properties["mapreduce.output.fileoutputformat.outputdir"],
        )
        # )

    def test_convert_to_text(self):
        mapper = mapreduce_mapper.MapReduceMapper(
            oozie_node=self.mapreduce_node,
            name="test_id",
            trigger_rule=TriggerRule.DUMMY,
            params={
                "nameNode": "hdfs://",
                "dataproc_cluster": "my-cluster",
                "gcp_region": "europe-west3",
                "hadoop_jars": "hdfs:///user/mapred/examples/mapreduce/lib/wordcount.jar",
                "hadoop_main_class": "WordCount",
            },
        )
        # Throws a syntax error if doesn't parse correctly
        ast.parse(mapper.convert_to_text())

    # pylint: disable=no-self-use
    def test_required_imports(self):
        imps = mapreduce_mapper.MapReduceMapper.required_imports()
        imp_str = "\n".join(imps)
        ast.parse(imp_str)
