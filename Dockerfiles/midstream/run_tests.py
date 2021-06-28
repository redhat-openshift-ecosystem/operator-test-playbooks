#!/usr/bin/env python3
import os
import sys
import json
import unittest
import subprocess
import logging
from os import path


TEST_WORKING_DIR= os.getcwd()
# global variables set
OPERATOR_DIR=TEST_WORKING_DIR+"/operator_dir/"
OPERATOR_WORK_DIR=TEST_WORKING_DIR+"/test_operator_work_dir/"
WORK_DIR=TEST_WORKING_DIR+"/output/"
PLAYBOOKS_DIR="/operator-test-playbooks/"
ERROR_MESSAGE_PATH=TEST_WORKING_DIR+"/.errormessage"
logging.basicConfig(filename=ERROR_MESSAGE_PATH)

class RunMidstreamCVPTests():

    def setUp(self):
        # IMAGE_TO_TESTis an environment variable that takes 
        # operator-bundle-image 
        self.image_to_test = os.getenv('IMAGE_TO_TEST')
        # VERBOSITY is verbosity of output log range varying from 1 to 4
        self.verbosity = int(os.getenv('VERBOSITY', '1'))*"v"

    def run_subprocess_command(self, exec_cmd):
        print(exec_cmd)
        env = os.environ.copy()
        env["ANSIBLE_CONFIG"] = "/operator-test-playbook/Dockerfiles/midstream/"
        env["ANSIBLE_LOCAL_TEMP"] = "/tmp/"

        result = {}
        process = subprocess.run(exec_cmd,
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              shell=True,
                              universal_newlines=True,
                              env=env)
        result["stdout"] = process.stdout
        result["stderr"] = process.stderr
        result["return_code"] = process.returncode
        return result

    def run_extract_operator_bundle(self):
        exec_cmd = "/usr/bin/ansible-playbook -i localhost, -c local -{verbosity} {playbook_dir}/extract-operator-bundle.yml \
                    -e 'bundle_image={bundle_image}' \
                    -e 'operator_work_dir={operator_work_dir}' \
                    -e 'work_dir={work_dir}'".format(
                                                    operator_dir=OPERATOR_DIR,
                                                    playbook_dir=PLAYBOOKS_DIR,
                                                    operator_work_dir=OPERATOR_WORK_DIR,
                                                    bundle_image=self.image_to_test,
                                                    verbosity=self.verbosity,
                                                    work_dir=WORK_DIR)
        result = self.run_subprocess_command(exec_cmd)
        return result

    def run_validate_operator_bundle(self):
        exec_cmd = "/usr/bin/ansible-playbook -{verbosity} -i localhost, --connection local \
                {playbook_dir}/validate-operator-bundle.yml \
                    -e 'operator_dir={operator_dir}' \
                    -e 'operator_work_dir={operator_work_dir}' \
                    -e 'work_dir={work_dir}'".format(operator_dir=OPERATOR_DIR,
                                                     operator_work_dir=OPERATOR_WORK_DIR,
                                                     work_dir=WORK_DIR,
                                                     playbook_dir=PLAYBOOKS_DIR,
                                                     verbosity=self.verbosity)
        result = self.run_subprocess_command(exec_cmd)
        return result

    def test_for_extract_and_validate_bundle_image(self):

        self.setUp()
        global exit_code
        exit_code = 0
        # check if IMAGE_TO_TEST is defined, return exit_code 102 in case it's not
        if (self.image_to_test is None):
            logging.error("Environment variable IMAGE_TO_TEST not set! Stopping the tests.")
            logging.error("Result code: 102 Error message: Environment variable IMAGE_TO_TEST not set!")
            exit_code = 102
            return exit_code
        result = self.run_extract_operator_bundle()
        logging.info(result["stdout"])
        if (result["return_code"] != 0):
            logging.error("Ansible playbook extract-operator-bundle.yml failed with result code: %s , see the file .errormessage for more info." % result["return_code"])
            logging.error("Result code: " + str(result["return_code"]))
            logging.error("Error message: " + str(result["stderr"]))
            logging.error("Result stdout: " + str(result["stdout"]))
            exit_code = 50
            return exit_code
        result = self.run_validate_operator_bundle()
        logging.info(result["stdout"])
        # make sure the validation-rc , validation-output, validation-version 
        # files have been created due to the playbook run
        assert (path.exists(WORK_DIR+"/validation-rc.txt"))
        assert (path.exists(WORK_DIR+"/validation-output.txt"))
        assert (path.exists(WORK_DIR+"/validation-version.txt"))
        with open(WORK_DIR+"/validation-rc.txt", 'r') as reader:
            rc = reader.read()
            if (int(rc) != 0):
                logging.error("Image bundle validation failed with result code: %s , see /project/output/validation-output.txt file for more info." % int(rc))
                exit_code = 70
                return exit_code
        return 0

if __name__ == '__main__':
    resultcodes = [0, 50, 70, 102]
    runTest = RunMidstreamCVPTests()
    if (runTest.test_for_extract_and_validate_bundle_image() not in resultcodes):
        exit_code = 1
        print("Error occured during unit tests, please see .errormessage file for more info.")
    sys.exit(exit_code)
