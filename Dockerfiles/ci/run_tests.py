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
        self.bundle_image = os.getenv('BUNDLE_IMAGE',
                                      "quay.io/cvpops/test-default-positive-v1")

    def test_validate_default_operator_bundle_success(self):
        exec_cmd = "ansible-playbook -vvv -i localhost, --connection local \
                operator-test-playbooks/validate-operator-bundle.yml \
                -e 'operator_dir={operator_dir}' \
                -e 'operator_work_dir={operator_work_dir}' \
                -e 'work_dir={work_dir}'".format(operator_dir=self.operator_dir,
                                                 operator_work_dir=self.operator_work_dir,
                                                 work_dir=self.work_dir)
        subprocess.run(exec_cmd, shell=True)
        self.assertTrue(path.exists("{}/validation-rc.txt".format(self.work_dir)))
        self.assertTrue(path.exists("{}/validation-output.txt".format(self.work_dir)))
        with open("{}/validation-rc.txt".format(self.work_dir), "r") as fd:
            validation_rc = fd.read()
            print(validation_rc)
            self.assertEqual(validation_rc, "0")

    def test_validate_default_operator_bundle_failure(self):
        exec_cmd = "ansible-playbook -vvv -i localhost, --connection local \
                operator-test-playbooks/validate-operator-bundle.yml \
                -e 'operator_dir={operator_dir}' \
                -e 'operator_work_dir={operator_work_dir}' \
                -e 'work_dir={work_dir}'".format(operator_dir=self.operator_dir,
                                                 operator_work_dir=self.operator_work_dir,
                                                 work_dir=self.work_dir)
        subprocess.run(exec_cmd, shell=True)
        self.assertTrue(path.exists("{}/validation-rc.txt".format(self.work_dir)))
        self.assertTrue(path.exists("{}/validation-output.txt".format(self.work_dir)))
        with open("{}/validation-rc.txt".format(self.work_dir), "r") as fd:
            validation_rc = fd.read()
            print(validation_rc)
            self.assertEqual(validation_rc, "1")


if __name__ == '__main__':
    test_name = os.getenv('TEST_NAME')
    if test_name:
        suite = unittest.TestSuite()
        suite.addTest(RunOperatorTestPlaybookTests(test_name))
        runner = unittest.TextTestRunner()
        return_code = not runner.run(suite).wasSuccessful()
        sys.exit(return_code)

