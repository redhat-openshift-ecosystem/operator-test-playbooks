#!/usr/bin/env python3
import os
import sys
import json
import unittest
import subprocess
from os import path

class RunMidstreamCVPTests(unittest.TestCase):

    def setUp(self):
        self.operator_dir = os.getenv('OPERATOR_DIR',
                                      "/project/operator_dir/")
        self.operator_work_dir = os.getenv('OPERATOR_WORK_DIR',
                                           "/project/test_operator_work_dir/")
        self.work_dir = os.getenv('WORK_DIR',
                                  "/project/output/")
        self.playbooks_dir = os.getenv('PLAYBOOKS_DIR',
                                       "/project/operator-test-playbooks/")
        self.image_to_test = os.getenv('IMAGE_TO_TEST',
                                       'quay.io/cvpops/test-operator:v1.0-16')
        self.umoci_bin_path = os.getenv('UMOCI_BIN_PATH',
                                        '/usr/local/bin/umoci')

    def run_extract_operator_bundle(self):
        exec_cmd = "ansible-playbook -i localhost, -c local -v operator-test-playbooks/extract-operator-bundle.yml \
                    -e 'bundle_image={bundle_image}' \
                    -e 'operator_work_dir={operator_work_dir}' \
                    -e 'umoci_bin_path={umoci_bin_path}'".format(
                                                    operator_dir=self.operator_dir,
                                                    operator_work_dir=self.operator_work_dir,
                                                    bundle_image=self.image_to_test,
                                                    umoci_bin_path=self.umoci_bin_path)
        result = subprocess.run(exec_cmd, shell=True)
        return result

    def run_validate_operator_bundle(self):
        exec_cmd = "ansible-playbook -vvv -i localhost, --connection local \
                    operator-test-playbooks/validate-operator-bundle.yml \
                    -e 'operator_dir={operator_dir}' \
                    -e 'operator_work_dir={operator_work_dir}' \
                    -e 'work_dir={work_dir}'".format(operator_dir=self.operator_dir,
                                                    operator_work_dir=self.operator_work_dir,
                                                    work_dir=self.work_dir)
        result = subprocess.run(exec_cmd, shell=True)
        return result

    def test_for_extract_and_validate_bundle_image(self):
        result = self.run_extract_operator_bundle()
        self.assertEqual(0,
                         result.returncode,
                         "extract-operator-bundle.yml failed")
        result = self.run_validate_operator_bundle()
        self.assertEqual(0,
                         result.returncode,
                         "validate-operator-bundle.yml failed")
        self.assertTrue(path.exists("/project/output/validation-rc.txt"))
        self.assertTrue(path.exists("/project/output/validation-output.txt"))
        self.assertTrue(path.exists("/project/output/validation-version.txt"))
        with open('/project/output/validation-rc.txt', 'r') as reader:
            rc = reader.read()
            self.assertEqual(0, int(rc), "validation of bundle image failed")

if __name__ == '__main__':
    unittest.main()
