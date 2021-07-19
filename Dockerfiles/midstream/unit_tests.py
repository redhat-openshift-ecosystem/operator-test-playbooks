#!/usr/bin/env python3
import unittest
import os
import subprocess

OUTPUT_DIR = "/tmp/"

class Testing(unittest.TestCase):

    def setUp(self):
        self.env = os.environ.copy()
        self.env["ANSIBLE_CONFIG"] = OUTPUT_DIR
        self.env["ANSIBLE_LOCAL_TEMP"] = "/tmp/"
        self.exec_cmd = "run_tests.py"

    # Running the container with correctly set environment variables, default channel missing, all tasks should pass
    def test_positive_missing_default_channel(self):
        self.env["IMAGE_TO_TEST"] = "quay.io/cvpops/test-operator:missing-default-channel-v1"
        result = subprocess.run(self.exec_cmd,
                                shell=True,
                                env=self.env,
                                cwd=OUTPUT_DIR)
        self.assertEqual(0, result.returncode)
        self.assertTrue(os.path.exists(OUTPUT_DIR+".errormessage"))
        os.remove(OUTPUT_DIR+".errormessage")

    # Set env variable to custom made image that makes playbook extract-operator-bundle.yml fail
    # Due to parsing error
    def test_negative_parsing(self):
        self.env["IMAGE_TO_TEST"] = "quay.io/cvpops/test-operator:missing-alm-examples-v1"
        result = subprocess.run(self.exec_cmd,
                                shell=True,
                                env=self.env,
                                cwd=OUTPUT_DIR)
        with open(OUTPUT_DIR+".errormessage") as error_file:
            self.assertIn("Result code:", error_file.read(), "Result code not found in %s" % error_file)
        self.assertEqual(50, result.returncode)
        self.assertTrue(os.path.exists(OUTPUT_DIR+".errormessage"))
        os.remove(OUTPUT_DIR+".errormessage")

    # Set env variable to custom made image that makes validation fails with following error:
    # ERRO[0003] error validating format in /tmp/bundle-688328851: Bundle validation errors: couldn't
    # parse dependency of type olm.crd
    def test_negative_image_bundle_validation(self):
        self.env["IMAGE_TO_TEST"] = "quay.io/cvpops/test-operator:invalid-dependencies-v1"
        result = subprocess.run(self.exec_cmd,
                                shell=True,
                                env=self.env,
                                cwd=OUTPUT_DIR)
        with open(OUTPUT_DIR+"/output/validation-output.txt") as error_file:
            self.assertIn("Bundle validation errors: couldn't parse dependency of type olm.crd", error_file.read(), "Result code not found in %s" % error_file)
        self.assertEqual(70, result.returncode)
        self.assertTrue(os.path.exists(OUTPUT_DIR+".errormessage"))
        os.remove(OUTPUT_DIR+".errormessage")

    # Don't set env variable IMAGE_TO_TEST case
    def test_negative_image_to_test_not_set(self):
        self.env.pop('IMAGE_TO_TEST', None)
        result = subprocess.run(self.exec_cmd,
                                shell=True,
                                env=self.env,
                                cwd=OUTPUT_DIR)
        with open(OUTPUT_DIR+".errormessage") as error_file:
            self.assertIn("Result code: 102 Error message: Environment variable IMAGE_TO_TEST not set!", error_file.read(), "Result code not found in %s" % error_file)
        self.assertEqual(102, result.returncode)
        self.assertTrue(os.path.exists(OUTPUT_DIR+".errormessage"))
        os.remove(OUTPUT_DIR+".errormessage")
    
    # Run with a test-operator which passes the bundle image validation job
    def test_default_positive(self):
        self.env["IMAGE_TO_TEST"] = "quay.io/cvpops/test-operator:v1.0-16"
        result = subprocess.run(self.exec_cmd,
                                shell=True,
                                env=self.env,
                                cwd=OUTPUT_DIR)
        self.assertEqual(0, result.returncode)
        # check if the .errormessage file generated is empty
        self.assertTrue(os.stat("/tmp/.errormessage").st_size == 0)
        # check if the .errormessage exists since its a logger file
        self.assertTrue(os.path.exists(OUTPUT_DIR+".errormessage"))
        os.remove(OUTPUT_DIR+".errormessage")


if __name__ == '__main__':
    unittest.main()
