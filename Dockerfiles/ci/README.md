# CVP upstream image for testing in github actions
This readme describes how to build and execute a container that validates an upstream operator bundle.

## Building image on local machine 

```
git clone https://github.com/redhat-operator-ecosystem/operator-test-playbooks.git
cd operator-test-playbooks

### podman build -t <image_name>:<tagname> -f <filepath> --build-arg OPERATOR_SDK_VERSION=<operator_sdk_version>
### example:
podman build -t upstream_ci_image:latest -f Dockerfiles/ci/Dockerfile --build-arg OPERATOR_SDK_VERSION=v1.4.0
```

## Running tests locally with built image

```
// Create empty directories to hold artifacts from the test container
mkdir test_operator_work_dir output_logs
// Run the test container. Artifacts will be saved in the mounted directories.
// OPERATOR_DIR contains a manifest files of operator bundle
// OPERATOR_WORK_DIR is an empty directory needed for bundle validations
podman run -it -v $PWD:/project/operator-test-playbooks -v ./Dockerfiles/ci/example-metadata-without-alm-annotations:/project/operator_dir -v ./output_logs:/project/output -v ./test_operator_work_dir:/project/test_operator_work_dir -e TEST_NAME=test_for_report_failed_empty_alm_examples -e OPERATOR_DIR=/project/operator_dir -e WORK_DIR=/project/output -e OPERATOR_WORK_DIR=/project/test_operator_work_dir/ upstream_ci_image:latest
```

---
** NOTE **

currently there is only one test inside the container image i.e., test_for_report_failed_empty_alm_examples
In order to add more tests please add more functions to run_tests.py inside the Dockerfiles/ci folder in operator-test-playbooks

---


#### Example Output of the container 
```
/project/output/parse_operator_metadata_results.json:6:        "msg": "Failed due to CSV.metadata.annotations['alm-examples'] is set to empty"
Exit code for grep 0
test_for_alm_examples Test passed
```
