#!/usr/bin/env python3
import os
import sys
import json
import unittest
import subprocess
from os import path


class RunMidstreamCVPTests():

    def setUp(self):
        self.operator_dir = os.getenv('OPERATOR_DIR',
                                      "/project/operator_dir/")
        self.operator_work_dir = os.getenv('OPERATOR_WORK_DIR',
                                           "/project/test_operator_work_dir/")
        self.work_dir = os.getenv('WORK_DIR',
                                  "/project/output/")
        self.playbooks_dir = os.getenv('PLAYBOOKS_DIR',
                                       "/project/operator-test-playbooks/")
        self.image_to_test = os.getenv('IMAGE_TO_TEST')
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
        result = subprocess.run(exec_cmd, shell=True, capture_output=True)
        return result

    def run_validate_operator_bundle(self):
        exec_cmd = "ansible-playbook -vvv -i localhost, --connection local \
                    operator-test-playbooks/validate-operator-bundle.yml \
                    -e 'operator_dir={operator_dir}' \
                    -e 'operator_work_dir={operator_work_dir}' \
                    -e 'work_dir={work_dir}'".format(operator_dir=self.operator_dir,
                                                     operator_work_dir=self.operator_work_dir,
                                                     work_dir=self.work_dir)
        result = subprocess.run(exec_cmd, shell=True, capture_output=True)
        return result

    def test_for_extract_and_validate_bundle_image(self):

        self.setUp()
        global exit_code
        exit_code = 0
        # check if IMAGE_TO_TEST is defined, return exit_code 102 in case it's not
        if (self.image_to_test is None):
            print("Environment variable IMAGE_TO_TEST not set! Stopping the tests.")
            with open(".errormessage", 'w') as error_msg:
                print("Result code: 102 Error message: Environment variable IMAGE_TO_TEST not set!", file=error_msg)
            exit_code = 102
            return exit_code
        if (self.operator_dir != '/project/operator_dir/' or
           self.operator_work_dir != '/project/test_operator_work_dir/' or
           self.playbooks_dir != '/project/operator-test-playbooks/' or
           self.umoci_bin_path != '/usr/local/bin/umoci' or
           self.work_dir != '/project/output/'):
            print("Environment variable misconfigured!")
            with open(".errormessage", 'w') as error_msg:
                print("Result code: 103 Error message: Environment variable was not set correctly!", file=error_msg)
            exit_code = 103
            return exit_code
        result = self.run_extract_operator_bundle()
        print(result)
        print(result.stdout)
        if (result.returncode != 0):
            print("Ansible playbook extract-operator-bundle.yml failed with result code: %s , see the file .errormessage for more info." % result.returncode)
            with open(".errormessage", "w") as error_msg:
                print("Result code: " + str(result.returncode), "Error message: " + str(result.stderr), file=error_msg)
            exit_code = 50
            return exit_code
        result = self.run_validate_operator_bundle()
        print(result)
        print(result.stdout)
        assert (path.exists("/project/output/validation-rc.txt"))
        assert (path.exists("/project/output/validation-output.txt"))
        assert (path.exists("/project/output/validation-version.txt"))
        with open('/project/output/validation-rc.txt', 'r') as reader:
            rc = reader.read()
            if (int(rc) != 0):
                print("Image bundle validation failed with result code: %s , see /project/output/validation-output.txt file for more info." % int(rc))
                exit_code = 70
                return exit_code
        return 0

if __name__ == '__main__':
    resultcodes = [0, 50, 70, 102, 103]
    # run fix_etc_passwd.sh to setup random user generated in openshift
    subprocess.call(['sh', "/usr/bin/fix_etc_passwd.sh"])
    runTest = RunMidstreamCVPTests()
    with open("tests_result.log", 'w') as f:
        if (runTest.test_for_extract_and_validate_bundle_image() not in resultcodes):
            exit_code = 1
            print("Error occured during unit tests, please see .errormessage file for more info.")
            os.rename(r'tests_result.log', r'.errormessage')
    sys.exit(exit_code)
