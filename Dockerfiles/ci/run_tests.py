#!/usr/bin/env python3

import os
import sys
import json
import unittest
import subprocess
from os import path


class RunOperatorTestPlaybookTests(unittest.TestCase):

    def setUp(self):
        self.test_dir = os.getenv('TEST_DIR', "/test_dir")
        self.playbooks_dir = os.getenv('PLAYBOOKS_DIR',
                                       "/project/operator-test-playbooks/")

    def test_prepare_metadata_without_alm_annotations_success(self):
        operator_work_dir = self.test_dir
        work_dir = self.test_dir
        operator_dir = "{}/example-metadata-without-alm-annotations".format(self.test_dir)
        exec_cmd = "ansible-playbook -vvv -i localhost, --connection local \
                    operator-test-playbooks/prepare-operator-metadata.yml \
                    -e 'operator_dir={operator_dir}' \
                    -e 'operator_work_dir={operator_work_dir}' \
                    -e 'work_dir={work_dir}'".format(operator_dir=operator_dir,
                                                     operator_work_dir=operator_work_dir,
                                                     work_dir=work_dir)
        playbook_command = subprocess.run(exec_cmd, shell=True)

        print(playbook_command.returncode)
        self.assertTrue(playbook_command.returncode == 0)
        self.assertTrue(path.exists("{}/parsed_operator_data.yml".format(work_dir)))
        self.assertTrue(path.exists("{}/parse_operator_metadata_results.json".format(self.playbooks_dir)))
        with open("{}/parse_operator_metadata_results.json".format(self.playbooks_dir), "r") as fd:
            result_output = json.load(fd)
            print(result_output)
            self.assertEqual(result_output["result"], "pass")

    def test_validate_default_operator_bundle_success(self):
        operator_work_dir = "{}/example-bundle-default-positive".format(self.test_dir)
        work_dir = "{}/example-workdir-v45-v49".format(self.test_dir)
        exec_cmd = "ansible-playbook -vvv -i localhost, --connection local \
                operator-test-playbooks/validate-operator-bundle.yml \
                -e 'operator_work_dir={operator_work_dir}' \
                -e 'work_dir={work_dir}'".format(operator_work_dir=operator_work_dir,
                                                 work_dir=work_dir)
        playbook_command = subprocess.run(exec_cmd, shell=True)

        print(playbook_command.returncode)
        self.assertTrue(playbook_command.returncode == 0)
        self.assertTrue(path.exists("{}/validation-rc.txt".format(work_dir)))
        self.assertTrue(path.exists("{}/validation-output.txt".format(work_dir)))
        with open("{}/validation-rc.txt".format(work_dir), "r") as fd:
            validation_rc = fd.read()
            print(validation_rc)
            self.assertEqual(validation_rc, "0")
        with open("{}/validation-output.txt".format(work_dir), "r") as fd:
            validation_output = fd.read()
            print(validation_output)
            self.assertIn("All validation tests have completed successfully", validation_output)

    def test_validate_deprecated_operator_bundle_failure(self):
        operator_work_dir = "{}/example-bundle-default-deprecated".format(self.test_dir)
        work_dir = "{}/example-workdir-v45-v49".format(self.test_dir)
        exec_cmd = "ansible-playbook -vvv -i localhost, --connection local \
                operator-test-playbooks/validate-operator-bundle.yml \
                -e 'operator_work_dir={operator_work_dir}' \
                -e 'work_dir={work_dir}'".format(operator_work_dir=operator_work_dir,
                                                 work_dir=work_dir)
        playbook_command = subprocess.run(exec_cmd, shell=True)

        print(playbook_command.returncode)
        self.assertTrue(playbook_command.returncode == 0)
        self.assertTrue(path.exists("{}/validation-rc.txt".format(work_dir)))
        self.assertTrue(path.exists("{}/validation-output.txt".format(work_dir)))
        with open("{}/validation-rc.txt".format(work_dir), "r") as fd:
            validation_rc = fd.read()
            print(validation_rc)
            self.assertEqual(validation_rc, "1")
        with open("{}/validation-output.txt".format(work_dir), "r") as fd:
            validation_output = fd.read()
            print(validation_output)
            self.assertIn("this bundle is using APIs which were deprecated and removed in v1.22", validation_output)

    def test_validate_v48_operator_bundle_success(self):
        operator_work_dir = "{}/example-bundle-default-deprecated".format(self.test_dir)
        work_dir = "{}/example-workdir-v45-v48".format(self.test_dir)
        exec_cmd = "ansible-playbook -vvv -i localhost, --connection local \
                operator-test-playbooks/validate-operator-bundle.yml \
                -e 'operator_work_dir={operator_work_dir}' \
                -e 'work_dir={work_dir}'".format(operator_work_dir=operator_work_dir,
                                                 work_dir=work_dir)
        playbook_command = subprocess.run(exec_cmd, shell=True)

        print(playbook_command.returncode)
        self.assertTrue(playbook_command.returncode == 0)
        self.assertTrue(path.exists("{}/validation-rc.txt".format(work_dir)))
        self.assertTrue(path.exists("{}/validation-output.txt".format(work_dir)))
        with open("{}/validation-rc.txt".format(work_dir), "r") as fd:
            validation_rc = fd.read()
            print(validation_rc)
            self.assertEqual(validation_rc, "0")
        with open("{}/validation-output.txt".format(work_dir), "r") as fd:
            validation_output = fd.read()
            print(validation_output)
            self.assertIn("All validation tests have completed successfully", validation_output)

    def test_validate_v43_operator_bundle_failure(self):
        operator_work_dir = "{}/example-bundle-default-positive".format(self.test_dir)
        work_dir = "{}/example-workdir-v43-v44".format(self.test_dir)
        exec_cmd = "ansible-playbook -vvv -i localhost, --connection local \
                operator-test-playbooks/validate-operator-bundle.yml \
                -e 'operator_work_dir={operator_work_dir}' \
                -e 'work_dir={work_dir}'".format(operator_work_dir=operator_work_dir,
                                                 work_dir=work_dir)
        playbook_command = subprocess.run(exec_cmd, shell=True, capture_output=True)
        print(playbook_command.returncode)
        self.assertTrue(playbook_command.returncode == 2)
        self.assertIn("No supported OCP versions found in Pyxis", playbook_command.stdout.decode("utf-8"))

    def test_validate_invalid_ocp_version_failure(self):
        operator_work_dir = "{}/example-bundle-default-positive".format(self.test_dir)
        work_dir = "{}/example-workdir-invalid-ocp-version".format(self.test_dir)
        exec_cmd = "ansible-playbook -vvv -i localhost, --connection local \
                operator-test-playbooks/validate-operator-bundle.yml \
                -e 'operator_work_dir={operator_work_dir}' \
                -e 'work_dir={work_dir}'".format(operator_work_dir=operator_work_dir,
                                                 work_dir=work_dir)
        playbook_command = subprocess.run(exec_cmd, shell=True, capture_output=True)
        print(playbook_command.returncode)
        self.assertTrue(playbook_command.returncode == 2)
        self.assertIn("Invalid semver in ocpfournine", playbook_command.stdout.decode("utf-8"))
        self.assertIn("Error collecting OCP version range from Pyxis", playbook_command.stdout.decode("utf-8"))


if __name__ == '__main__':
    unittest.main()

