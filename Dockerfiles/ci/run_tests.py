#!/usr/bin/env python3

import os
import sys
import json
import unittest
import subprocess
import yaml
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

    def test_extract_operator_bundle_430_channel_success(self):
        operator_work_dir = "{}/test_extract_operator_bundle_430_channel_success".format(self.test_dir)
        work_dir = operator_work_dir
        operator_dir = "{}/test-operator".format(operator_work_dir)
        operator_bundle_dir = "{}/operator-bundle".format(operator_work_dir)
        bundle_image = "quay.io/cvpops/test-operator:test-430-channel-positive-v1"
        exec_cmd = "ansible-playbook -vvv -i localhost, --connection local \
                    operator-test-playbooks/extract-operator-bundle.yml \
                    -e 'operator_dir={operator_dir}' \
                    -e 'bundle_image={bundle_image}' \
                    -e 'operator_work_dir={operator_work_dir}' \
                    -e 'operator_bundle_dir={operator_bundle_dir}' \
                    -e 'work_dir={work_dir}'".format(operator_dir=operator_dir,
                                                     operator_work_dir=operator_work_dir,
                                                     operator_bundle_dir=operator_bundle_dir,
                                                     bundle_image=bundle_image,
                                                     work_dir=work_dir)
        playbook_command = subprocess.run(exec_cmd, shell=True)

        print(playbook_command.returncode)
        self.assertTrue(playbook_command.returncode == 0)
        self.assertTrue(path.exists("{}/parsed_operator_data.yml".format(work_dir)))
        with open("{}/parsed_operator_data.yml".format(work_dir), "r") as fd:
            parsed_output = fd.read()
            print(parsed_output)
            self.assertIn('package_name: "e2e-test-operator"', parsed_output)
            self.assertIn('current_csv: "e2e-test-operator.4.3.1-202002032140"', parsed_output)
            self.assertIn('current_channel: "4.30"', parsed_output)
            self.assertIn('is_bundle_image: True', parsed_output)
            self.assertIn('is_backport: True', parsed_output)
            self.assertIn('ocp_versions: "v4.5"', parsed_output)

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
            #self.assertEqual(validation_rc, "0")
        with open("{}/validation-output.txt".format(work_dir), "r") as fd:
            validation_output = fd.read()
            print(validation_output)
            #self.assertIn("All validation tests have completed successfully", validation_output)

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

    def test_extract_operator_bundle_no_subscription(self):
        operator_work_dir = "{}/test_extract_operator_bundle_no_subscription".format(self.test_dir)
        work_dir = operator_work_dir
        operator_dir = "{}/test-operator".format(operator_work_dir)
        operator_bundle_dir = "{}/operator-bundle".format(operator_work_dir)
        bundle_image = "quay.io/cvpops/test-operator:test-430-channel-positive-v1"
        exec_cmd = "ansible-playbook -vvv -i localhost, --connection local \
                    operator-test-playbooks/extract-operator-bundle.yml \
                    -e 'operator_dir={operator_dir}' \
                    -e 'bundle_image={bundle_image}' \
                    -e 'operator_work_dir={operator_work_dir}' \
                    -e 'operator_bundle_dir={operator_bundle_dir}' \
                    -e 'work_dir={work_dir}'".format(operator_dir=operator_dir,
                                                     operator_work_dir=operator_work_dir,
                                                     operator_bundle_dir=operator_bundle_dir,
                                                     bundle_image=bundle_image,
                                                     work_dir=work_dir)
        playbook_command = subprocess.run(exec_cmd, shell=True)

        print(playbook_command.returncode)
        self.assertTrue(playbook_command.returncode == 0)
        self.assertTrue(path.exists("{}/parsed_operator_data.yml".format(work_dir)))
        with open("{}/parsed_operator_data.yml".format(work_dir), "r") as fd:
            parsed_output = fd.read()
            print(parsed_output)
            self.assertIn('operator_valid_subscription: []', parsed_output)

    def test_extract_operator_bundle_with_subscription(self):
        operator_work_dir = "{}/test_extract_operator_bundle_with_subscription".format(self.test_dir)
        work_dir = operator_work_dir
        operator_dir = "{}/test-operator".format(operator_work_dir)
        operator_bundle_dir = "{}/operator-bundle".format(operator_work_dir)
        bundle_image = "quay.io/cvpops/test-operator:with-subscription"
        exec_cmd = "ansible-playbook -vvv -i localhost, --connection local \
                    operator-test-playbooks/extract-operator-bundle.yml \
                    -e 'operator_dir={operator_dir}' \
                    -e 'bundle_image={bundle_image}' \
                    -e 'operator_work_dir={operator_work_dir}' \
                    -e 'operator_bundle_dir={operator_bundle_dir}' \
                    -e 'work_dir={work_dir}'".format(operator_dir=operator_dir,
                                                     operator_work_dir=operator_work_dir,
                                                     operator_bundle_dir=operator_bundle_dir,
                                                     bundle_image=bundle_image,
                                                     work_dir=work_dir)
        playbook_command = subprocess.run(exec_cmd, shell=True)

        print(playbook_command.returncode)
        self.assertTrue(playbook_command.returncode == 0)
        self.assertTrue(path.exists("{}/parsed_operator_data.yml".format(work_dir)))
        with open("{}/parsed_operator_data.yml".format(work_dir), "r") as fd:
            parsed_output = fd.read()
            print(parsed_output)
            self.assertIn('operator_valid_subscription:\n  - "Test Subscription One"\n  - "Test Subscription Two"', parsed_output)

    def test_current_and_default_channel_parsing(self):
        operator_work_dir = "{}/test_current_and_default_channel_parsing".format(self.test_dir)
        work_dir = operator_work_dir
        operator_dir = "{}/test-operator".format(operator_work_dir)
        operator_bundle_dir = "{}/operator-bundle".format(operator_work_dir)
        bundle_image = "quay.io/cvpops/test-operator:parse-channel"
        exec_cmd = "ansible-playbook -vvv -i localhost, --connection local \
                    operator-test-playbooks/extract-operator-bundle.yml \
                    -e 'operator_dir={operator_dir}' \
                    -e 'bundle_image={bundle_image}' \
                    -e 'operator_work_dir={operator_work_dir}' \
                    -e 'operator_bundle_dir={operator_bundle_dir}' \
                    -e 'work_dir={work_dir}'".format(operator_dir=operator_dir,
                                                     operator_work_dir=operator_work_dir,
                                                     operator_bundle_dir=operator_bundle_dir,
                                                     bundle_image=bundle_image,
                                                     work_dir=work_dir)
        playbook_command = subprocess.run(exec_cmd, shell=True)

        print(playbook_command.returncode)
        self.assertTrue(playbook_command.returncode == 0)
        self.assertTrue(path.exists("{}/parsed_operator_data.yml".format(work_dir)))
        with open("{}/parsed_operator_data.yml".format(work_dir), "r") as fd:
            parsed_output = yaml.safe_load(fd)
            print(parsed_output)
            self.assertEqual(parsed_output["current_channel"], "4.10")
            self.assertEqual(parsed_output["default_channel"], "4.10")

    def test_extract_operator_bundle_no_infrastructure_features(self):
        operator_work_dir = "{}/test_extract_operator_bundle_no_infrastructure_features".format(self.test_dir)
        work_dir = operator_work_dir
        operator_dir = "{}/test-operator".format(operator_work_dir)
        operator_bundle_dir = "{}/operator-bundle".format(operator_work_dir)
        bundle_image = "quay.io/cvpops/test-operator:test-430-channel-positive-v1"
        exec_cmd = "ansible-playbook -vvv -i localhost, --connection local \
                    operator-test-playbooks/extract-operator-bundle.yml \
                    -e 'operator_dir={operator_dir}' \
                    -e 'bundle_image={bundle_image}' \
                    -e 'operator_work_dir={operator_work_dir}' \
                    -e 'operator_bundle_dir={operator_bundle_dir}' \
                    -e 'work_dir={work_dir}'".format(operator_dir=operator_dir,
                                                     operator_work_dir=operator_work_dir,
                                                     operator_bundle_dir=operator_bundle_dir,
                                                     bundle_image=bundle_image,
                                                     work_dir=work_dir)
        playbook_command = subprocess.run(exec_cmd, shell=True)

        print(playbook_command.returncode)
        self.assertTrue(playbook_command.returncode == 0)
        self.assertTrue(path.exists("{}/parsed_operator_data.yml".format(work_dir)))
        with open("{}/parsed_operator_data.yml".format(work_dir), "r") as fd:
            parsed_output = fd.read()
            print(parsed_output)
            self.assertNotIn("operator_feature_disconnected", parsed_output)
            self.assertNotIn("operator_feature_fips_compliant", parsed_output)
            self.assertNotIn("operator_feature_proxy_aware", parsed_output)
            self.assertNotIn("operator_feature_cnf", parsed_output)
            self.assertNotIn("operator_feature_cni", parsed_output)
            self.assertNotIn("operator_feature_csi", parsed_output)
            self.assertNotIn("operator_feature_tls_profiles", parsed_output)
            self.assertNotIn("operator_feature_token_auth_aws", parsed_output)
            self.assertNotIn("operator_feature_token_auth_azure", parsed_output)
            self.assertNotIn("operator_feature_token_auth_gcp", parsed_output)

    def test_extract_operator_bundle_with_infrastructure_features(self):
        operator_work_dir = "{}/test_extract_operator_bundle_with_infrastructure_features".format(self.test_dir)
        work_dir = operator_work_dir
        operator_dir = "{}/test-operator".format(operator_work_dir)
        operator_bundle_dir = "{}/operator-bundle".format(operator_work_dir)
        bundle_image = "quay.io/cvpops/test-operator:with-infrastructure-features-as-strings"
        exec_cmd = "ansible-playbook -vvv -i localhost, --connection local \
                    operator-test-playbooks/extract-operator-bundle.yml \
                    -e 'operator_dir={operator_dir}' \
                    -e 'bundle_image={bundle_image}' \
                    -e 'operator_work_dir={operator_work_dir}' \
                    -e 'operator_bundle_dir={operator_bundle_dir}' \
                    -e 'work_dir={work_dir}'".format(operator_dir=operator_dir,
                                                     operator_work_dir=operator_work_dir,
                                                     operator_bundle_dir=operator_bundle_dir,
                                                     bundle_image=bundle_image,
                                                     work_dir=work_dir)
        playbook_command = subprocess.run(exec_cmd, shell=True)

        print(playbook_command.returncode)
        self.assertTrue(playbook_command.returncode == 0)
        self.assertTrue(path.exists("{}/parsed_operator_data.yml".format(work_dir)))
        with open("{}/parsed_operator_data.yml".format(work_dir), "r") as fd:
            parsed_output = fd.read()
            print(parsed_output)
            self.assertIn('operator_feature_disconnected: "False"', parsed_output)
            self.assertIn('operator_feature_fips_compliant: "True"', parsed_output)
            self.assertIn('operator_feature_proxy_aware: "False"', parsed_output)
            self.assertIn('operator_feature_cnf: "False"', parsed_output)
            self.assertIn('operator_feature_cni: "True"', parsed_output)
            self.assertIn('operator_feature_csi: "True"', parsed_output)
            self.assertIn('operator_feature_tls_profiles: "True"', parsed_output)
            self.assertIn('operator_feature_token_auth_aws: "False"', parsed_output)
            self.assertIn('operator_feature_token_auth_azure: "False"', parsed_output)
            self.assertIn('operator_feature_token_auth_gcp: "False"', parsed_output)

if __name__ == '__main__':
    unittest.main()

