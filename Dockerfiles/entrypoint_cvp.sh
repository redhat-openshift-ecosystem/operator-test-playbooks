#!/bin/bash

# operator-bundle-image validate
validate_operator_bundle () {
    echo -e "operatorSDKVersion is $operatorSDKVersion"
    ansible-playbook -vvvv --connection local -i localhost, operator-test-playbooks/validate-operator-bundle.yml -e"work_dir=/project/output" -e"operator_work_dir=/project/operator-bundle/"

    operatorSDKVersion=$(cat /project/output/validation-version.txt)
    cat /project/output/validation-output.txt

    if [[ $? -eq 0 ]];
    then
      echo -e "\nBundle image validation is successful"
      echo -e "Operator bundle validation Return Code is $operatorBundlevalidationReturnCode"
      cat /project/output/validation-rc.txt
      exit 0
    else
      echo -e "\nBundle image validation Failed"
      exit 1
    fi
}

#prepare-operator-metadata
prepare_operator_metadata () {
    ansible-playbook -vvv -i localhost, --connection local operator-test-playbooks/prepare-operator-metadata.yml -e "operator_dir=/project/operator_dir/" -e "operator_work_dir=/project/test_operator_work_dir/" -e"work_dir=/project/output/"
    cat /project/output/parse_operator_metadata_results.json
    cp /project/operator-test-playbooks/parse_operator_metadata_results.json /project/output
}

TEST_NAME_ENV="${TEST_NAME:-validate_operator_bundle}"
if [[ "$TEST_NAME_ENV" = 'validate_operator_bundle' ]]; then
    echo "TEST_NAME is set to $TEST_NAME_ENV"
    echo "Running operator bundle validation"
    validate_operator_bundle
elif [[ "$TEST_NAME_ENV" = 'prepare_operator_metadata' ]]; then
    echo "TEST_NAME is set to $TEST_NAME_ENV"
    echo "Running prepare_operator_metadata"
    prepare_operator_metadata
else
    echo "TEST_NAME is set to $TEST_NAME_ENV"
    echo "$TEST_NAME_ENV not found in entrypoint.sh"
fi
