#!/bin/bash

# operator-bundle-image validate

ansible-playbook -vvvv --connection local -i localhost, operator-test-playbooks/validate-operator-bundle.yml -e"work_dir=/project/output" -e"operator_work_dir=/project/operator-bundle/"

operatorSDKVersion=$(cat /project/output/validation-version.txt)
operatorBundlevalidationReturnCode=$(cat /project/output/validation-rc.txt)
operatorBundlevalidationOutput=$(cat /project/output/validation-output.txt)

echo -e "operatorSDKVersion is $operatorSDKVersion"
echo -e "Operator bundle validation Return Code is $operatorBundlevalidationReturnCode"
echo -e "Operator bundle Validation output is \n $operatorBundlevalidationOutput"

if [[ $operatorBundlevalidationReturnCode -eq 0 ]];
then
  echo -e "\nBundle image validation is successful"
  exit 0
else
  echo -e "\nBundle image validation Failed"
  exit 1
fi

