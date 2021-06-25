#!/usr/bin/env python3
import unittest
import os
import subprocess


class Testing(unittest.TestCase):
    # Running the container with correctly set environment variables, all tasks from run_tests.py should pass
    def test_default_positive(self):
        exec_cmd = """
        export IMAGE_TO_TEST=quay.io/cvpops/test-operator:v1.0-16
        /tmp/operator-test-playbooks/Dockerfiles/midstream/run_tests.py
        """
        result = subprocess.run(exec_cmd, shell=True)
        self.assertFalse(os.path.exists("/tmp/.errormessage"), "File .errormessage should not be present!")
        self.assertEqual(0, result.returncode)

    # Running the container with correctly set environment variables, default channel missing, all tasks should pass
    def test_positive_missing_default_channel(self):
        exec_cmd = """
        export IMAGE_TO_TEST=quay.io/cvpops/test-operator:missing-default-channel-v1
        /tmp/operator-test-playbooks/Dockerfiles/midstream/run_tests.py
        """
        result = subprocess.run(exec_cmd, shell=True)
        self.assertFalse(os.path.exists("/tmp/.errormessage"), "File .errormessage should not be present!")
        self.assertEqual(0, result.returncode)

    # Set env variable to custom made image that makes playbook extract-operator-bundle.yml fail
    # Due to parsing error
    def test_negative_parsing(self):
        exec_cmd = """
        export IMAGE_TO_TEST=quay.io/cvpops/test-operator:missing-alm-examples-v1
        /tmp/operator-test-playbooks/Dockerfiles/midstream/run_tests.py
        """
        result = subprocess.run(exec_cmd, shell=True)
        with open("/tmp/.errormessage") as error_file:
            self.assertIn("Result code:", error_file.read(), "Result code not found in %s" % error_file)
        self.assertEqual(50, result.returncode)
        os.remove("/tmp/.errormessage")

    # Set env variable to custom made image that makes validation fails with following error:
    # ERRO[0003] error validating format in /tmp/bundle-688328851: Bundle validation errors: couldn't
    # parse dependency of type olm.crd
    def test_negative_image_bundle_validation(self):
        exec_cmd = """
        export IMAGE_TO_TEST=quay.io/cvpops/test-operator:invalid-dependencies-v1
        /tmp/operator-test-playbooks/Dockerfiles/midstream/run_tests.py
        """
        result = subprocess.run(exec_cmd, shell=True)
        with open("/tmp/output/validation-output.txt") as error_file:
            self.assertIn("Bundle validation errors: couldn't parse dependency of type olm.crd", error_file.read(), "Result code not found in %s" % error_file)
        self.assertEqual(70, result.returncode)
        os.remove("/tmp/output/validation-output.txt")

    # Don't set env variable IMAGE_TO_TEST case
    def test_negative_image_to_test_not_set(self):
        exec_cmd = """
        /tmp/operator-test-playbooks/Dockerfiles/midstream/run_tests.py
        """
        result = subprocess.run(exec_cmd, shell=True)
        with open("/tmp/.errormessage") as error_file:
            self.assertIn("Result code: 102 Error message: Environment variable IMAGE_TO_TEST not set!", error_file.read(), "Result code not found in %s" % error_file)
        self.assertEqual(102, result.returncode)
        os.remove("/tmp/.errormessage")


if __name__ == '__main__':
    unittest.main()
