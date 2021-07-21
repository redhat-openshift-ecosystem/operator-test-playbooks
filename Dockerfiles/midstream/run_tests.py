#!/usr/bin/env python3
import os
import sys
import subprocess
import logging


TEST_WORKING_DIR= os.getcwd()
OUTPUT_DIRECTORY = "/tmp/"# global variables set
OPERATOR_DIR=OUTPUT_DIRECTORY+"/operator_dir/"
OPERATOR_WORK_DIR=OUTPUT_DIRECTORY+"/test_operator_work_dir/"
WORK_DIR=OUTPUT_DIRECTORY+"/output/"
PLAYBOOKS_DIR="/project/operator-test-playbooks/"
ERROR_MESSAGE_PATH=TEST_WORKING_DIR+"/.errormessage"

logging.basicConfig(handlers=[logging.StreamHandler()],
                    level=logging.INFO)
VALIDATION_LOGGER = logging.getLogger('.errormessage')
# by default will be logged logs to stderr but also add the same messages
# to the file which midstream expects
VALIDATION_LOGGER.addHandler(logging.FileHandler(ERROR_MESSAGE_PATH))


class RunMidstreamCVPTests():

    def __init__(self):
        # IMAGE_TO_TESTis an environment variable that takes 
        # operator-bundle-image 
        self.image_to_test = os.getenv('IMAGE_TO_TEST')
        # VERBOSITY is verbosity of output log range varying from 1 to 4
        self.verbosity = int(os.getenv('VERBOSITY', '1'))*"v"

    @staticmethod
    def run_subprocess_command(exec_cmd):
        logging.info("Running the subprocess ansible command ")
        logging.info(exec_cmd)
        env = os.environ.copy()
        process = subprocess.run(exec_cmd,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 shell=True,
                                 universal_newlines=True,
                                 env=env)
        return {
            "stdout": process.stdout,
            "stderr": process.stderr,
            "return_code": process.returncode,
        }

    def run_extract_operator_bundle(self):
        exec_cmd = "/usr/bin/ansible-playbook -i localhost, -c local -{verbosity} {playbook_dir}/extract-operator-bundle.yml \
                    -e 'bundle_image={bundle_image}' \
                    -e 'operator_work_dir={operator_work_dir}' \
                    -e 'work_dir={work_dir}'".format(verbosity=self.verbosity,
                                                     playbook_dir=PLAYBOOKS_DIR,
                                                     bundle_image=self.image_to_test,
                                                     operator_work_dir=OPERATOR_WORK_DIR,
                                                     work_dir=WORK_DIR)
        return RunMidstreamCVPTests.run_subprocess_command(exec_cmd)

    def run_validate_operator_bundle(self):
        exec_cmd = "/usr/bin/ansible-playbook -i localhost, -c local -{verbosity} \
                    {playbook_dir}/validate-operator-bundle.yml \
                         -e 'operator_dir={operator_dir}' \
                         -e 'operator_work_dir={operator_work_dir}' \
                         -e 'work_dir={work_dir}'".format(verbosity=self.verbosity,
                                                          playbook_dir=PLAYBOOKS_DIR,
                                                          operator_work_dir=OPERATOR_WORK_DIR,
                                                          operator_dir=OPERATOR_DIR,
                                                          work_dir=WORK_DIR)
        return RunMidstreamCVPTests.run_subprocess_command(exec_cmd)

    def test_for_extract_and_validate_bundle_image(self):

        # check if IMAGE_TO_TEST is defined, return exit_code 102 in case it's not
        if not self.image_to_test:
            VALIDATION_LOGGER.error("Environment variable IMAGE_TO_TEST not set! Stopping the tests.")
            VALIDATION_LOGGER.error("Result code: 102 Error message: Environment variable IMAGE_TO_TEST not set!")
            return 102

        result = self.run_extract_operator_bundle()
        if result["return_code"] != 0:
            VALIDATION_LOGGER.error("Ansible playbook extract-operator-bundle.yml failed with result code: %s , see the file .errormessage for more info.", result["return_code"])
            VALIDATION_LOGGER.error("Result code: %d", result["return_code"])
            VALIDATION_LOGGER.error("Error message: %s", result["stderr"])
            VALIDATION_LOGGER.error("Result stdout: %s", result["stdout"])
            return 50
        result = self.run_validate_operator_bundle()
        with open(WORK_DIR + "/validation-rc.txt", 'r') as reader:
            validation_rc = reader.read()
            if int(validation_rc) != 0:
                with open(WORK_DIR + "/validation-output.txt", 'r') as validate_reader:
                    validation_output = validate_reader.read()
                VALIDATION_LOGGER.error("Image bundle validation failed with result code: %s and error:\n%s", validation_rc, validation_output)
                return 70

        logging.info("Image: %s has passed operator bundle image validation test", self.image_to_test)
        return 0

if __name__ == '__main__':
    subprocess.run(['fix_etc_passwd.sh'], check=True)
    resultcodes = [0, 50, 70, 102]
    test_runner = RunMidstreamCVPTests()
    return_code = test_runner.test_for_extract_and_validate_bundle_image()
    if return_code not in resultcodes:
        VALIDATION_LOGGER.error("Unexpected error (%d) occured during unit tests, please see .errormessage file for more info.", return_code)
        return_code = 1
    sys.exit(return_code)
