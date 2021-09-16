#!/usr/bin/env python3
import unittest
import os
import subprocess
import shutil

OUTPUT_DIR = "/tmp/"

class Testing(unittest.TestCase):

    def setUp(self):
        self.env = os.environ.copy()
        self.env["ANSIBLE_CONFIG"] = OUTPUT_DIR
        self.env["ANSIBLE_LOCAL_TEMP"] = "/tmp/"
        self.exec_cmd = "run_tests.py"

    def tearDown(self):
        os.remove(OUTPUT_DIR+".errormessage")
        # removes the output directory created by playbooks
        shutil.rmtree(OUTPUT_DIR+"/output/", ignore_errors=True)
        # removes the test_operator_work_dir directory created by playbooks
        shutil.rmtree(OUTPUT_DIR+"/test_operator_work_dir/", ignore_errors=True)
        # removes the operator-bundle directory created by playbooks
        shutil.rmtree(OUTPUT_DIR+"/operator-bundle/", ignore_errors=True)

    @staticmethod
    def get_error_message_content(output_file=".errormessage"):
        with open(OUTPUT_DIR + output_file) as error_file:
            return error_file.read()


    # Running the container with correctly set environment variables, default channel missing, all tasks should pass
    def test_positive_missing_default_channel(self):
        self.env["IMAGE_TO_TEST"] = "quay.io/cvpops/test-operator:missing-default-channel-v2"
        result = subprocess.run(self.exec_cmd,
                                shell=True,
                                env=self.env,
                                cwd=OUTPUT_DIR)
        self.assertEqual(0, result.returncode)
        self.assertTrue(os.path.exists(OUTPUT_DIR+".errormessage"))

    # Set env variable to custom made image that makes playbook extract-operator-bundle.yml fail
    # Due to parsing error
    def test_negative_parsing(self):
        self.env["IMAGE_TO_TEST"] = "quay.io/cvpops/test-operator:missing-alm-examples-v1"
        result = subprocess.run(self.exec_cmd,
                                shell=True,
                                env=self.env,
                                cwd=OUTPUT_DIR)

        message = self.get_error_message_content()
        self.assertIn("Result code:", message, "Result code not found in .errormessage")
        self.assertEqual(50, result.returncode)
        self.assertTrue(os.path.exists(OUTPUT_DIR+".errormessage"))

    # Set env variable to custom made image that makes validation fails with following error:
    # ERRO[0003] error validating format in /tmp/bundle-688328851: Bundle validation errors: couldn't
    # parse dependency of type olm.crd
    def test_negative_image_bundle_validation(self):
        self.env["IMAGE_TO_TEST"] = "quay.io/cvpops/test-operator:invalid-dependencies-v1"
        result = subprocess.run(self.exec_cmd,
                                shell=True,
                                env=self.env,
                                cwd=OUTPUT_DIR)

        message = self.get_error_message_content()
        self.assertIn("Bundle validation errors: couldn't parse dependency of type olm.crd", message, "Result code not found in .erroremessage")
        self.assertEqual(70, result.returncode)
        self.assertTrue(os.path.exists(OUTPUT_DIR+".errormessage"))

    # Don't set env variable IMAGE_TO_TEST case
    def test_negative_image_to_test_not_set(self):
        self.env.pop('IMAGE_TO_TEST', None)
        result = subprocess.run(self.exec_cmd,
                                shell=True,
                                env=self.env,
                                cwd=OUTPUT_DIR)
        message = self.get_error_message_content()
        self.assertIn("Result code: 102 Error message: Environment variable IMAGE_TO_TEST not set!", message,
                      "Result code not found in %s" % message)
        self.assertEqual(102, result.returncode)
        self.assertTrue(os.path.exists(OUTPUT_DIR+".errormessage"))

    # Run with a test-operator which fails the deprecated image check in the
    # bundle image validation job
    def test_default_negative(self):
        self.env["IMAGE_TO_TEST"] = "quay.io/cvpops/test-operator:test-default-negative-v1"
        result = subprocess.run(self.exec_cmd,
                                shell=True,
                                env=self.env,
                                cwd=OUTPUT_DIR)
        self.assertEqual(70, result.returncode)
        # check if the .errormessage file generated is empty
        self.assertTrue(os.stat(OUTPUT_DIR+".errormessage").st_size != 0)
        # check if the .errormessage exists since its a logger file
        self.assertTrue(os.path.exists(OUTPUT_DIR+".errormessage"))
        message = self.get_error_message_content()
        self.assertIn("this bundle is using APIs which were deprecated and removed in v1.22", message,
                      "Deprecated APIs error not found in '%s'" % message)

    # Run with a test-operator which passes the bundle image validation job
    def test_default_positive(self):
        self.env["IMAGE_TO_TEST"] = "quay.io/cvpops/test-operator:test-default-positive-v1"
        result = subprocess.run(self.exec_cmd,
                                shell=True,
                                env=self.env,
                                cwd=OUTPUT_DIR)
        self.assertEqual(0, result.returncode)
        # check if the .errormessage file generated is empty
        self.assertTrue(os.stat(OUTPUT_DIR+".errormessage").st_size == 0)
        # check if the .errormessage exists since its a logger file
        self.assertTrue(os.path.exists(OUTPUT_DIR+".errormessage"))

    # Run with a test-operator that does not support v4.9 or above which passes the
    # bundle image validation job
    def test_default_positive_below_4_9(self):
        self.env["IMAGE_TO_TEST"] = "quay.io/cvpops/test-operator:test-default-positive-below-4.9-v1"
        result = subprocess.run(self.exec_cmd,
                                shell=True,
                                env=self.env,
                                cwd=OUTPUT_DIR,
                                stdout=subprocess.PIPE,
                                text=True)
        self.assertEqual(0, result.returncode)
        # check if the .errormessage file generated is empty
        self.assertTrue(os.stat(OUTPUT_DIR+".errormessage").st_size == 0)
        # check if the .errormessage exists since its a logger file
        self.assertTrue(os.path.exists(OUTPUT_DIR+".errormessage"))
        self.assertIn(result.stdout, '"support_v4_9": false', "Could not verify that support_v4_9 was set to false")


if __name__ == '__main__':
    unittest.main()
