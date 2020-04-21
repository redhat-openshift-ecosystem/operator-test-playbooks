# Operator testing

## Running operator testing playbooks locally

The operator testing can be run locally using the Ansible playbook at `local-test-operator.yml`.
The playbook roles that run the operator tests used in this are identical to ones used as part of the CVP operator testing pipeline.

One notable exception is the package name uniqueness test which requires access to an internal database.

The playbook finishes successfully if all enabled tests pass. The logs and files for the test run can be found at `/tmp/operator-test` directory by default.

### Prerequisites

The testing playbooks has a number of prerequisites that it requires for a successful run.
Most of these requirements need to be supplied as Ansible parameters when running the playbook.

#### 1. Installed operator-courier

The instructions for installing operator-courier can be found at [this link](https://github.com/operator-framework/operator-courier).

#### 2. Kubeconfig file for a working OCP cluster (for ISV and Community operators only)

The user needs to be currently logged into a working OCP cluster that will be used for testing as `kubeadmin` for the tests to work.

The path to the kubeconfig file for the OCP cluster needs to be supplied as the `kubeconfig_path` parameter, 
for example: `-e kubeconfig_path=~/testing/kubeconfig`

For rapid prototyping, you can spin up an OCP cluster using [Red Hat CodeReady Workspaces](https://developers.redhat.com/products/codeready-workspaces/download)

You can then specify your kubeconfig as follows: `-e kubeconfig_path= ~/.crc/cache/crc_libvirt_4.2.14/kubeconfig`

#### 3. A valid quay.io namespace (for ISV and Community operators only)

A valid quay.io namespace to which the user has access to needs to be supplied as the `quay_namespace` parameter, 
for example: `-e quay_namespace="${QUAY_NAMESPACE}"`

The testing process includes creating a private repository, be advised about the limits on the account owning the namespace.

#### 4. An quay.io access token (for ISV and Community operators only)

The token for the quay.io account that owns the namespace used for testing can be obtained by using the following command:

```bash
QUAY_TOKEN=$(curl -sH "Content-Type: application/json" -XPOST https://quay.io/cnr/api/v1/users/login -d '
{
    "user": {
        "username": "'"${QUAY_USERNAME}"'",
        "password": "'"${QUAY_PASSWORD}"'"
    }
}' | jq -r '.token' | cut -d' ' -f2)
``` 

The token can then be supplied as the `quay_token` parameter, for example: `-e quay_token="${QUAY_TOKEN}"`

#### 5. The operator metadata directory

The operator metadata can be in either flattened or nested format - it will be copied and nested in a temporary directory for the purposes of the test.

The path to the directory containing the operator metadata can be supplied as the `operator_dir` parameter,
for example: `-e operator_dir=~/testing/operator-metadata`

#### 6. Other required binaries

The rest of the required binaries are downloaded by the playbook to a temporary directory in `/tmp/operator-test/bin` and don't need to be installed manually.

If we, for some reason, want to skip the download (for example if we already have the required binaries at that location from a previous playbook run), 
we can set the `run_prereqs` parameter in this way: ``-e run_prereqs=false``

### Selecting operator tests

If we want to enable or disable individual tests, we can use these parameters and set them to true or false:

* `run_lint` for running operator-courier linting, default true
* `run_catalog_init` for running the catalog initialization test, default true
* `run_deploy` for deploying the operator to the testing cluster - this test is required for the subsequent tests, default true
* `run_scorecard` for running the operator scorecard tests on the operator that's deployed to the testing cluster, default true
* `run_imagesource` for checking the image sources of the tested operator - applies to Red Hat and ISV operators, otherwise disable with `-e run_imagesource=false`

### Resource cleanup

The created resources and namespace are cleaned up after the playbook run by default. 
If we want to leave the resources after the run, we can set the `run_cleanup` parameter like this: `-e run_cleanup=false`

### Example usages

#### 1. Testing Red Hat (optional) operators
If we want to run the Red Hat operator tests, we invoke the playbook with the following command:

```bash
ansible-playbook -vv -i "localhost," --connection=local local-test-operator.yml \
    -e run_deploy=false \
    -e production_quay_namespace="redhat-operators" \
    -e operator_dir="${OPERATOR_DIR}"
```
Currently the access to an OCP cluster or an quay.io account is not required

#### 2. Full operator testing for ISV (Certified) operators 
If we want to run the full ISV operator testing, we invoke the playbook with the following command (inserting the aforementioned prerequisites):

```bash
ansible-playbook -vv -i "localhost," --connection=local local-test-operator.yml \
    -e kubeconfig_path="${KUBECONFIG_PATH}" \
    -e quay_token="${QUAY_TOKEN}" \
    -e quay_namespace="${QUAY_NAMESPACE}" \
    -e production_quay_namespace="certified-operators" \
    -e operator_dir="${OPERATOR_DIR}"
```

#### 3. Testing community operators
If we want to run the operator testing for a community operator without running the imagesource test, we invoke the playbook with the following command:

```bash
ansible-playbook -vv -i "localhost," --connection=local local-test-operator.yml \
    -e kubeconfig_path="${KUBECONFIG_PATH}" \
    -e quay_token="${QUAY_TOKEN}" \
    -e quay_namespace="${QUAY_NAMESPACE}" \
    -e production_quay_namespace="community-operators" \
    -e operator_dir="${OPERATOR_DIR}" \
    -e run_imagesource=false
```

#### 4. Creating openshift config file for installing openshift cluster on AWS
```bash
ansible-playbook -vv -i "localhost," --connection=local  \
ansible-playbook -i "localhost," --connection=local prepare-ocp4-aws-config.yml \
    --vault-password-file /path/to/vault_passwd_file \
    -e cluster_name="test_cluster" \
    -e pipeline_repo_path=/path/to/pipelinerepo \
    -e aws_region="us-east-2" \
    -e openshift_install=true \ // optional: if true installs openshift cluster on aws
    -e openshift_installer_log_level=debug
```
