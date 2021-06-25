#!/usr/bin/env python3
import os
import sys
import json
import unittest
import subprocess
from os import path

# global variables set 
OPERATOR_DIR="/tmp/operator_dir/"
OPERATOR_WORK_DIR="/tmp/test_operator_work_dir/"
WORK_DIR="/tmp/output/"
PLAYBOOKS_DIR="/tmp/operator-test-playbooks/"
UMOCI_BIN_PATH="/usr/local/bin/umoci"

class RunMidstreamCVPTests():

    def setUp(self):
        self.image_to_test = os.getenv('IMAGE_TO_TEST')
        self.verbosity = int(os.getenv('VERBOSITY', '1'))*"v"

    def run_extract_operator_bundle(self):
        exec_cmd = "ansible-playbook -i localhost, -c local -{verbosity} {playbook_dir}/extract-operator-bundle.yml \
                    -e 'bundle_image={bundle_image}' \
                    -e 'operator_work_dir={operator_work_dir}' \
                    -e 'umoci_bin_path={umoci_bin_path}' \
                    -e 'work_dir={work_dir}'".format(
                                                    operator_dir=OPERATOR_DIR,
                                                    playbook_dir=PLAYBOOKS_DIR,
                                                    operator_work_dir=OPERATOR_WORK_DIR,
                                                    bundle_image=self.image_to_test,
                                                    umoci_bin_path=UMOCI_BIN_PATH,
                                                    verbosity=self.verbosity,
                                                    work_dir=WORK_DIR)
        result = subprocess.run(exec_cmd, shell=True, capture_output=True)
        return result

    def run_validate_operator_bundle(self):
        exec_cmd = "ansible-playbook -{verbosity} -i localhost, --connection local \
                {playbook_dir}/validate-operator-bundle.yml \
                    -e 'operator_dir={operator_dir}' \
                    -e 'umoci_bin_path={umoci_bin_path}' \
                    -e 'operator_work_dir={operator_work_dir}' \
                    -e 'work_dir={work_dir}'".format(operator_dir=OPERATOR_DIR,
                                                     operator_work_dir=OPERATOR_WORK_DIR,
                                                     work_dir=WORK_DIR,
                                                     umoci_bin_path=UMOCI_BIN_PATH,
                                                     playbook_dir=PLAYBOOKS_DIR,
                                                     verbosity=self.verbosity)
        result = subprocess.run(exec_cmd, shell=True, capture_output=True)
        return result

    def test_for_extract_and_validate_bundle_image(self):

        self.setUp()
        global exit_code
        exit_code = 0
        # check if IMAGE_TO_TEST is defined, return exit_code 102 in case it's not
        if (self.image_to_test is None):
            print("Environment variable IMAGE_TO_TEST not set! Stopping the tests.")
            with open("/tmp/.errormessage", 'w') as error_msg:
                print("Result code: 102 Error message: Environment variable IMAGE_TO_TEST not set!", file=error_msg)
            exit_code = 102
            return exit_code
        result = self.run_extract_operator_bundle()
        print(result.stdout)
        if (result.returncode != 0):
            print("Ansible playbook extract-operator-bundle.yml failed with result code: %s , see the file .errormessage for more info." % result.returncode)
            with open("/tmp/.errormessage", "w") as error_msg:
                print("Result code: " + str(result.returncode), "Error message: " + str(result.stderr), file=error_msg)
            exit_code = 50
            return exit_code
        result = self.run_validate_operator_bundle()
        print(result.stdout)
        assert (path.exists(WORK_DIR+"/validation-rc.txt"))
        assert (path.exists(WORK_DIR+"/validation-output.txt"))
        assert (path.exists(WORK_DIR+"/validation-version.txt"))
        with open(WORK_DIR+"/validation-rc.txt", 'r') as reader:
            rc = reader.read()
            if (int(rc) != 0):
                print("Image bundle validation failed with result code: %s , see /project/output/validation-output.txt file for more info." % int(rc))
                exit_code = 70
                return exit_code
        return 0

if __name__ == '__main__':
    resultcodes = [0, 50, 70, 102]
    # run fix_etc_passwd.sh to setup random user generated in openshift
    subprocess.call(['sh', PLAYBOOKS_DIR+
                           "/Dockerfiles/midstream/fix_etc_passwd.sh"])
    runTest = RunMidstreamCVPTests()
    with open("/tmp/tests_result.log", 'w') as f:
        if (runTest.test_for_extract_and_validate_bundle_image() not in resultcodes):
            exit_code = 1
            print("Error occured during unit tests, please see .errormessage file for more info.")
            os.rename(r'/tmp/tests_result.log', r'/tmp/.errormessage')
    sys.exit(exit_code)
