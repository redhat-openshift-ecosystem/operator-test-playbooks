#!/usr/bin/env python3

import os
import sys
import json
import unittest
import subprocess
from os import path

class RunOperatorTestPlaybookTests(unittest.TestCase):

    def setUp(self):
        self.operator_dir = os.getenv('OPERATOR_DIR',
                                      "/project/operator_dir/")
        self.operator_work_dir = os.getenv('OPERATOR_WORK_DIR',
                                           "/project/test_operator_work_dir/")
        self.work_dir = os.getenv('WORK_DIR',
                                  "/project/output/")
        self.playbooks_dir = os.getenv('PLAYBOOKS_DIR',
                                       "/project/operator-test-playbooks/")

    def test_for_report_success_empty_alm_examples(self):
        exec_cmd = "ansible-playbook -vvv -i localhost, --connection local \
                    operator-test-playbooks/prepare-operator-metadata.yml \
                    -e 'operator_dir={operator_dir}' \
                    -e 'operator_work_dir={operator_work_dir}' \
                    -e'work_dir={work_dir}'".format(operator_dir=self.operator_dir,
                                                    operator_work_dir=self.operator_work_dir,
                                                    work_dir=self.work_dir)
        subprocess.run(exec_cmd, shell=True)
        self.assertTrue(path.exists("{}/parsed_operator_data.yml".format(self.work_dir)))
        self.assertTrue(path.exists("{}/parse_operator_metadata_results.json".format(self.playbooks_dir)))
        with open("{}/parse_operator_metadata_results.json".format(self.playbooks_dir), "r") as fd:
            result_output = json.load(fd)
            print(result_output)
            self.assertEqual(result_output["result"], "pass")

if __name__ == '__main__':
    unittest.main()
