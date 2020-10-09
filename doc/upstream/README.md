# Instruction for operator test via ansible

## Standard test on clean machine
```
ansible-playbook -vv -i myhost, local.yml \
-e run_upstream=true \
-e operator_dir=/tmp/community-operators-for-catalog/upstream-community-operators/aqua
```

## Standard test with operator prerequisites (-e run_prereqs=true)
```
ansible-playbook -vv -i myhost, local.yml \
-e run_upstream=true \
-e operator_dir=/tmp/community-operators-for-catalog/upstream-community-operators/aqua \
--tags test
```

## Standard test without operator prerequisites (-e run_prereqs=false)
```
ansible-playbook -vv -i myhost, local.yml \
-e run_upstream=true \
-e operator_dir=/tmp/community-operators-for-catalog/upstream-community-operators/aqua \
--tags pure_test
```
or
```
ansible-playbook -vv -i myhost, local.yml \
-e run_upstream=true \
-e operator_dir=/tmp/community-operators-for-catalog/upstream-community-operators/aqua \
--tags test \
-e run_prereqs=false
```

## Super full test on clean machine
```
ansible-playbook -vv -i myhost, local.yml \
-e run_upstream=true \
-e operator_dir=/tmp/community-operators-for-catalog/upstream-community-operators/aqua \
-e run_manifest_test=true \
-e run_bundle_test=true
```

## Super full test quick (without installation)
```
ansible-playbook -vv -i myhost, local.yml \
-e run_upstream=true \
-e operator_dir=/tmp/community-operators-for-catalog/upstream-community-operators/aqua \
-e run_manifest_test=true \
-e run_bundle_test=true \
--tags pure_test
```

## Install host only
```
ansible-playbook -vv -i myhost, local.yml \
-e run_upstream=true \
--tags install
```

## Reset host (eg. kind, registry)
```
ansible-playbook -vv -i myhost, local.yml \
-e run_upstream=true \
--tags reset
```

## Install dependency in playbook docker image when building
```
ansible-playbook -vv -i myhost, local.yml \
-e run_upstream=true \
--tags image_build
```

## Input source image (not supported now)
```
ansible-playbook -vv -i myhost, local.yml \
-e run_upstream=true \
-e operator_input_image=quay.io/cvpops/test-bundle:tigera-131 \
--tags pure_test
```

## Deploy operators to index
Config file:
```
$ cat test/operators_config.yaml
operator_base_dir: /tmp/community-operators-for-catalog/upstream-community-operators
operators:
- aqua
- prometheus
```

### Deploy starting index image
```
ansible-playbook -vv -i myhost, local.yml \
-e run_upstream=true \
--tags deploy_bundles \
-e operators_config=test/operators_config.yaml
```

### Deploy starting index image
```
ansible-playbook -vv -i myhost, local.yml \
-e run_upstream=true \
--tags deploy_bundles \
-e operators_config=test/operators_config.yaml
-e bundle_registry=quay.io \
-e bundle_image_namespace=operator_testing \
-e bundle_index_image_namespace=operator_testing \
-e bundle_index_image_name=upstream-community-operators-index \
-e quay_api_token=<quay-api-token>
```

### Deploy starting index image and mirror index
```
ansible-playbook -vv -i myhost, local.yml \
-e run_upstream=true \
--tags deploy_bundles \
-e operators_config=test/operators_config.yaml
-e bundle_registry=quay.io \
-e bundle_image_namespace=operator_testing \
-e bundle_index_image_namespace=operator_testing \
-e bundle_index_image_name=upstream-community-operators-index \
-e mirror_index_images="quay.io/operator_testing/upstream-community-operators-index-mirror|<user>|<password>" \
-e quay_api_token=<quay-api-token>
```

### Deploy index image and force channels to be autodetected by playbook
```
ansible-playbook -vv -i myhost, local.yml \
-e run_upstream=true \
--tags deploy_bundles \
-e operators_config=test/operators_config.yaml
-e operator_channel_force=""
```

### Deploy index image and force channels to stable
```
ansible-playbook -vv -i myhost, local.yml \
-e run_upstream=true \
--tags deploy_bundles \
-e operators_config=test/operators_config.yaml
-e operator_channel_force=stable
```

### Remove operator from quay
```
ansible-playbook -vv -i myhost, local.yml \
-e run_upstream=true \
-e operator_dir=/tmp/community-operators-for-catalog/upstream-community-operators/aqua -e operator_version=1.0.2 \
--tags deploy_bundles \
-e bundle_registry=quay.io -e bundle_image_namespace=operator_testing -e bundle_index_image_namespace=operator_testing \
-e bundle_index_image_name=upstream-community-operators-index \
-e quay_api_token=<token>
```

### Remove operator from quay (force to remove it from git just after git clone )
```
ansible-playbook -vv -i myhost, local.yml \
-e run_upstream=true \
-e operator_dir=/tmp/community-operators-for-catalog/upstream-community-operators/aqua \
--tags deploy_bundles -e remove_operators_dir=/tmp/community-operators-for-catalog/upstream-community-operators/aqua \
-e bundle_registry=quay.io -e bundle_image_namespace=operator_testing -e bundle_index_image_namespace=operator_testing \
-e bundle_index_image_name=upstream-community-operators-index \
-e quay_api_token=<token>
```

### Remove operator from quay (force to remove it from git just after git clone )
```
ansible-playbook -vv -i myhost, local.yml \
-e run_upstream=true \
-e operator_dir=/tmp/community-operators-for-catalog/upstream-community-operators/aqua \
--tags deploy_bundles -e quay_api_token=<token> \
-e bundle_registry=quay.io -e bundle_image_namespace=operator_testing \
-e bundle_index_image_namespace=operator_testing -e bundle_index_image_name=upstream-community-operators-index  \
-e remove_base_dir=/tmp/community-operators-for-catalog/upstream-community-operators -e remove_operator_dirs="aqua/1.0.2,aqua/1.0.1"
```

## Recreate catalog (operatorhubio)
```
TOKEN="<token>"

ansible-pull -U https://github.com/J0zi/operator-test-playbooks -C upstream-community -vv -i localhost, local.yml \
-e run_upstream=true --tags deploy_bundles \
-e regenerate_operators_path=/tmp/community-operators-for-catalog/upstream-community-operators \
-e bundle_registry=quay.io \
-e bundle_image_namespace=operatorhubio \
-e bundle_index_image_namespace=operatorhubio \
-e bundle_index_image_name=catalog \
-e quay_api_token=$TOKEN \
-e opm_index_add_mode=semver -e operator_channel_force="" \
| tee -a $HOME/recreate_operatorhubio-$(date +%F_%H%M).log 1>&2
```

## Mirror exiting index image to different location
```
ansible-playbook -vv -i myhost, local.yml \
-e run_upstream=true \
--tags mirror_index \
-e bundle_registry=quay.io \
-e bundle_index_image_namespace=operator_testing \
-e bundle_index_image_name=upstream-community-operators-index \
-e mirror_index_images="quay.io/operator_testing/upstream-community-operators-index-mirror|<user>|<password>,quay.io/operator_testing/upstream-community-operators-index-mirror-second|<user2>|<password2>" \
-e quay_api_token=<quay-api-token>
```

## Test all operators
```
export ANSIBLE_STDOUT_CALLBACK=yaml
time ansible-pull -U https://github.com/J0zi/operator-test-playbooks -C upstream-community -vv -i localhost, local.yml \
-e run_upstream=true --tags pure_test_all -e operator_base_dir=/tmp/community-operators-for-catalog/upstream-community-operators  \
-e permisive=true -e pod_start_retries=30 -e pod_start_delay=5 \
-e opm_index_add_mode=semver -e operator_channel_force="" \
-e all_operator_find_excludes="planetscale"| tee -a $HOME/test_all_upstream-$(date +%F_%H%M).log 1>&2
```


## Generate app registry (List of operators from index image)
```
export ANSIBLE_STDOUT_CALLBACK=yaml
time ansible-playbook -vv -i localhost, local.yml \
-e run_upstream=true --tags app_registry \
-e bundle_index_image=quay.io/operatorhubio/catalog:latest
```

## Generate app registry in parallel (List of operators from index image) and then push it
```
export ANSIBLE_STDOUT_CALLBACK=yaml
time ansible-playbook -vv -i localhost, local.yml \
-e run_upstream=true --tags app_registry \
-e bundle_index_image=quay.io/operatorhubio/catalog:latest \
-e index_export_parallel=true \
-e app_registry_image="kind-registry:5000/test-operator/app-registry"
```

## Generate app registry (List of operators from git)

```
export ANSIBLE_STDOUT_CALLBACK=yaml
time ansible-playbook -vv -i localhost, local.yml \
-e run_upstream=true --tags app_registry \
-e operator_base_dir=/tmp/community-operators-for-catalog/upstream-community-operators \
-e bundle_index_image=quay.io/operatorhubio/catalog:latest
```

## Generate app registry in parallel (List of operators from git)
```
export ANSIBLE_STDOUT_CALLBACK=yaml
time ansible-playbook -vv -i localhost, local.yml \
-e run_upstream=true --tags app_registry \
-e operator_base_dir=/tmp/community-operators-for-catalog/upstream-community-operators \
-e bundle_index_image=quay.io/operatorhubio/catalog:latest \
-e index_export_parallel=true
```

## Misc options to use

Usage:

```
-e <option>=<value>
```

| Option  | Description  | Default value | Prod default|
|---|---|---| --- |
| run_upstream | Flag when running upstream part of playbooks. [bool] | false | true |
| run_remove_catalog_repo | Removes existing git repo for comunity-operators. [bool] | true | true |
| catalog_repo | Community operators repo url. [string] | https://github.com/operator-framework/community-operators.git | as default |
| catalog_repo_branch | Community operators branch in repo. [string] | master | as default |
| operators_config | Path to operators config file using when deploying multiple operators. Examle in test/operators_config.yaml. [string] | undefined  | operators_config.yaml |
| quay_user | Username in quay registry login. [string] | undefined | undefined |
| quay_password | Password in quay registry login. [string] | undefined  | undefined |
| quay_api_token | Quay api token to create project, delete tag. If 'quay_user' or 'quay_password' is undefined. This token is used to push images to quay as '$oauthtoken' user. More info about creating token is [here](https://docs.quay.io/api/).  [string] | undefined | hidden |
| bundle_registry | Quay bundle and index registry url. [string] | kind-registry:5000 | quay.io |
| bundle_image_namespace | Quay registry url. [string] | test-operator | operator_testing |
| bundle_index_image_namespace | Quay registry url. [string] | test-operator | operator_testing |
| bundle_index_image_name | Quay registry url. [string] | index | upstream-community-operators-index |
| opm_container_tool | Container tool to use when using opm tool. [string] | docker  | as default |
| operator_channel_force | Forcing to adde channel and default channed to current string value. When empty string it is autodetected by playbook. [string] | undefined | undefined |
| index_force_update | Force to rebuild currently running operators in index. [bool] | false | false |
| index_skip | Skip building index (it will build bundle only). [bool] | undefined | undefined |
| package_name_strict | Test if package name is same as operator directory name. [bool] | undefined | undefined |
| run_bundle_scorecard_test | Runs bundle scorecard test. [bool] | undefined | undefined |
| bundle_scorecard_test_config | Config file where scorecard tests are defined. [string] | generated | n/a |
| bundle_scorecard_test_select | Runs specific scorecard tests. [string] | basic-check-spec-test,olm-bundle-validation-test,olm-status-descriptors-test | n/a |
| recreate_skip_repo_clean | Skip removing all repos in namespace from registry. (Applied only when is defined and value is true). [bool] | undefined | undefined |
| remove_base_dir | Sepcify base directory right after cloning comunity-operators project. Needs to specify `remove_operator_dirs`. See bellow. [string] | undefined | undefined |
| remove_operator_dirs | List directory right after cloning comunity-operators project relative to `remove_base_dir`. [string] | undefined | undefined |
| all_operator_find_filter | Filter pattern to find list of operators when running all tests (tags: test_all, pure_test_all). [string] | undefined | undefined |
| all_operator_find_excludes | Comma separated list of operators that should be excluded (tags: test_all, pure_test_all). [string] | undefined | undefined |
| permisive | Olm deploy will not fail when this flag is true. [bool] | undefined | undefined |
| test_all_reset_kind | Force to reset kind cluster before every test (undefined means true). [bool] | undefined | undefined |
| production_registry_namespace | Check if bundle exists in production registry. Used in local `deploy_bundle` test. (e.g. "quay.io/operatorhubio") [string] | undefined | undefined |
| mirror_index_images | List of mirror images for index. (e.g. "kind-registry:5000/test-operator/catalog_mirror_auth|<user>|<password>,kind-registry:5000/test-operator/catalog_mirror_no_auth") [string] | undefined | undefined |
| index_mode_from_ci | Enable autodetect index add mode from <operator>/ci.yaml file [bool] | undefined | undefined |


## Tags to use

Usage:

```
--tags <tag1>,<tag2>...<tagN>
```

| Tag  | Description |
|---|---|
|host_build| Installs base packages needed to run on host (docker,kind,registry, ...) |
|install| Installs all packages incluing operator testing tools (--tags host_build + testing tools). |
|uninstall| Uninstall packages that were installed by `install` tag|
|reset| Resets kind cluster and recreate kind registry |
|reset_tools| Reinstall testing tools (operator-sdk,olm,opm,umoci,yq,jq). Used when updating versions of these tools. |
|test| Runs test including installing operator prerequisites |
|pure_test| Runs test excluding installing operator prerequisites (Faster then `test` once operator tools are installed. ) |
|test_lite| Runs test if operator bundle exists on production registry. The variable `production_registry_namespace` needs to be set.|
|pure_test_lite| Runs test if operator bundle exists on production registry. The variable `production_registry_namespace` needs to be set. (Installation of the operator prerequisites is excluded) |
|deploy_bundles| Deploy all bundles defined by `operator_dir` or `operator_config` |


# Scripts

## Recreate
```
#!/bin/bash
export ANSIBLE_STDOUT_CALLBACK=yaml
export MY_OPT=""
#export MY_OPT="-e opm_index_add_mode=semver -e operator_channel_force=\"\" $*"

# operatorhubio
TOKEN="<token>"
time ansible-pull -U https://github.com/J0zi/operator-test-playbooks -C sprint-8 -vv -i localhost, local.yml \
-e run_upstream=true --tags deploy_bundles \
-e regenerate_operators_path=/tmp/community-operators-for-catalog/upstream-community-operators \
-e bundle_registry=quay.io \
-e bundle_image_namespace=operatorhubio \
-e bundle_index_image_namespace=operatorhubio \
-e bundle_index_image_name=catalog \
-e quay_api_token=$TOKEN \
$MY_OPT \
| tee -a $HOME/recreate_operatorhubio-$(date +%F_%H%M).log 1>&2

date +%F_%H%M
```

# Test all
```
#!/bin/bash
export MY_OPT="-e permisive=true"
#export MY_OPT="$MY_OPT -e pod_start_retries=30 -e pod_start_delay=5"
#export MY_OPT="$MY_OPT -e all_operator_find_excludes=\"planetscale\""
export ANSIBLE_STDOUT_CALLBACK=yaml
time ansible-pull -U https://github.com/J0zi/operator-test-playbooks -C sprint-8 -vv -i localhost, local.yml \
-e run_upstream=true --tags pure_test_all -e operator_base_dir=/tmp/community-operators-for-catalog/upstream-community-operators  \
-e opm_index_add_mode=semver -e operator_channel_force="" \
$MY_OPT | tee -a $HOME/test_all_upstream-$(date +%F_%H%M).log 1>&2
```

# Check index

```
ansible-pull -U https://github.com/J0zi/operator-test-playbooks -C upstream-community -vv -i localhost, local.yml \
-e run_upstream=true --tags index_check \
-e bundle_index_image=quay.io/operatorhubio/catalog \
-e operator_base_dir=/tmp/community-operators-for-catalog/upstream-community-operators
```


# Travis configuration

## operator-test-playbooks
| name  | value |
|---|---|
|ANSIBLE_CONFIG|"$PWD/ansible.cfg"|
|ANSIBLE_BASE_ARGS|"-i localhost, local.yml -e ansible_connection=local -e run_upstream=true -e run_remove_catalog_repo=false"|


## community-operators
| name  | value |
|---|---|
|ANSIBLE_CONFIG|"$PWD/ansible.cfg"|
|ANSIBLE_BASE_ARGS|"-i localhost, local.yml -e ansible_connection=local -e run_remove_catalog_repo=false"|
|ANSIBLE_EXTRA_ARGS|""|
|ANSIBLE_PULL_REPO|"https://github.com/redhat-operator-ecosystem/operator-test-playbooks"|
|ANSIBLE_PULL_BRANCH|"upstream-community"|
|AUTOMATION_TOKEN_OPERATOR_TESTING|on master|
|AUTOMATION_TOKEN_RELEASE_COMMUNITY|on release-pipeline-running|
|AUTOMATION_TOKEN_RELEASE_UPSTREAM|on release-pipeline-running|
|CI_OHIO_TRIGGER_TOKEN|on master|
|FRAMEWORK_AUTOMATION_ON_TRAVIS|on master|
|QUAY_APPREG_TOKEN|on master|
|QUAY_COURIER_TOKEN|on master|


## community-operator-catalog
| name  | value |
|---|---|
|ANSIBLE_CONFIG|"$PWD/ansible.cfg"|
|ANSIBLE_BASE_ARGS|"-i localhost, local.yml -e ansible_connection=local -e run_remove_catalog_repo=false"|
|ANSIBLE_EXTRA_ARGS|""|
|ANSIBLE_PULL_REPO|"https://github.com/redhat-operator-ecosystem/operator-test-playbooks"|
|ANSIBLE_PULL_BRANCH|"upstream-community"|
|AUTOMATION_TOKEN_RELEASE_COMMUNITY|all branches|
|AUTOMATION_TOKEN_RELEASE_COMMUNITY_TEST|all branches|
|AUTOMATION_TOKEN_RELEASE_UPSTREAM|all branches|
|AUTOMATION_TOKEN_RELEASE_UPSTREAM_TEST|all branches|
|QUAY_RH_INDEX_PW|on master|
|QUAY_RH_INDEX_PW|on job/update-community-index-manually|
|INPUT_CATALOG_IMAGE|"quay.io/operatorhubio/catalog:latest" (default, when nothing is set)|
|APP_REGISTRY_IMAGE|"quay.io/operator-framework/upstream-community-operators:latest" (default, when nothing is set)|
|APP_REGISTRY_TOKEN|on master|
