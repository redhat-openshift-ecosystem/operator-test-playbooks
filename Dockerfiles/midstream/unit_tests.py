#!/usr/bin/env python3
import unittest
import os
import subprocess


class Testing(unittest.TestCase):
    # Running the container with correctly set environment variables, all tasks from run_tests.py should pass
    def test_default_positive(self):
        exec_cmd = """
        export IMAGE_TO_TEST=quay.io/cvpops/test-operator:v1.0-16
        /run_tests.py
        """
        self.assertFalse(os.path.exists(".errormessage"), "File .errormessage should not be present!")
        result = subprocess.run(exec_cmd, shell=True)
        self.assertEqual(0, result.returncode)

    # Set env variable to custom made image that makes playbook extract-operator-bundle.yml fail
    # Due to parsing error
    def test_negative_parsing(self):
        exec_cmd = """
        export IMAGE_TO_TEST=quay.io/cvpops/test-operator:missing-alm-examples-v1
        /run_tests.py
        """
        result = subprocess.run(exec_cmd, shell=True)
        with open(".errormessage") as error_file:
            self.assertIn("Result code:", error_file.read(), "Result code not found in %s" % error_file)
        self.assertEqual(50, result.returncode)

    # Set env variable to custom made image that makes validation fails with following error:
    # ERRO[0003] error validating format in /tmp/bundle-688328851: Bundle validation errors: couldn't
    # parse dependency of type olm.crd
    def test_negative_image_bundle_validation(self):
        exec_cmd = """
        export IMAGE_TO_TEST=quay.io/cvpops/test-operator:invalid-dependencies-v1
        /run_tests.py
        """
        result = subprocess.run(exec_cmd, shell=True)
        with open("/project/output/validation-output.txt") as error_file:
            self.assertIn("Bundle validation errors: couldn't parse dependency of type olm.crd", error_file.read(), "Result code not found in %s" % error_file)
        self.assertEqual(70, result.returncode)

    # Don't set env variable IMAGE_TO_TEST case
    def test_negative_image_to_test_not_set(self):
        exec_cmd = """
        /run_tests.py
        """
        result = subprocess.run(exec_cmd, shell=True)
        with open(".errormessage") as error_file:
            self.assertIn("Result code: 102 Error message: Environment variable IMAGE_TO_TEST not set!", error_file.read(), "Result code not found in %s" % error_file)
        self.assertEqual(102, result.returncode)

    # Set incorrect env variable UMOCI_BIN_PATH for ansible playbook extract-operator-bundle.yml
    def test_negative_extract_operator_bundle(self):
        exec_cmd = """
        export IMAGE_TO_TEST=quay.io/cvpops/test-operator:v1.0-16
        export UMOCI_BIN_PATH=/root
        /run_tests.py
        """
        result = subprocess.run(exec_cmd, shell=True)
        with open(".errormessage") as error_file:
            self.assertIn("Result code: 103 Error message: Environment variable was not set correctly!", error_file.read(), "Result code not found in %s" % error_file)
        self.assertEqual(103, result.returncode)

if __name__ == '__main__':
    unittest.main()
