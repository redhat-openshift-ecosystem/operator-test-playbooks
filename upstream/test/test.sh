#!/bin/bash
set +o pipefail

ACTION=${1-""}
TESTS=$1

[[ $TESTS == all* ]] && TESTS="kiwi,lemon,orange"
TESTS=${TESTS//,/ }
OP_SCRIPT_URL=${OP_SCRIPT_URL-"https://cutt.ly/WhkV76k"}

OP_TEST_BASE_DEP="ansible curl openssl git"

INDEX_SAFETY="-e enable_production=true"
OP_TEST_IMAGE=${OP_TEST_IMAGE-"quay.io/operator_testing/operator-test-playbooks:latest"}
OP_TEST_CERT_DIR=${OP_TEST_CERT_DIR-"$HOME/.optest/certs"}
OP_TEST_CONTAINER_TOOL=${OP_TEST_CONTAINER_TOOL-"docker"}
OP_TEST_CONTAINER_OPT=${OP_TEST_CONTAINER_OPT-"-it"}
OP_TEST_NAME=${OPT_TEST_NAME-"op-test"}
# OP_TEST_ANSIBLE_PULL_REPO=${OP_TEST_ANSIBLE_PULL_REPO-"https://github.com/redhat-operator-ecosystem/operator-test-playbooks"}
# OP_TEST_ANSIBLE_PULL_BRANCH=${OP_TEST_ANSIBLE_PULL_BRANCH-"upstream-community"}
OP_TEST_ANSIBLE_PULL_REPO=${OP_TEST_ANSIBLE_PULL_REPO-"https://github.com/operator-framework/operator-test-playbooks"}
OP_TEST_ANSIBLE_PULL_BRANCH=${OP_TEST_ANSIBLE_PULL_BRANCH-"master"}
OP_TEST_ANSIBLE_DEFAULT_ARGS=${OP_TEST_ANSIBLE_DEFAULT_ARGS-"-i localhost, -e ansible_connection=local -e run_upstream=true -e run_remove_catalog_repo=false upstream/local.yml"}
OP_TEST_ANSIBLE_EXTRA_ARGS=${OP_TEST_ANSIBLE_EXTRA_ARGS-"--tags kubectl,install_kind"}
OP_TEST_CONAINER_RUN_DEFAULT_ARGS=${OP_TEST_CONAINER_RUN_DEFAULT_ARGS-"--net host --cap-add SYS_ADMIN --cap-add SYS_RESOURCE --security-opt seccomp=unconfined --security-opt label=disable -v $OP_TEST_CERT_DIR/domain.crt:/usr/share/pki/ca-trust-source/anchors/ca.crt -e STORAGE_DRIVER=vfs -e BUILDAH_FORMAT=docker"}
OP_TEST_CONTAINER_RUN_EXTRA_ARGS=${OP_TEST_CONTAINER_RUN_EXTRA_ARGS-""}
OP_TEST_CONTAINER_EXEC_DEFAULT_ARGS=${OP_TEST_CONTAINER_EXEC_DEFAULT_ARGS-""}
OP_TEST_CONTAINER_EXEC_EXTRA_ARGS=${OP_TEST_CONTAINER_EXEC_EXTRA_ARGS-""}
OP_TEST_EXEC_BASE=${OP_TEST_EXEC_BASE-"ansible-playbook -i localhost, -e ansible_connection=local upstream/local.yml -e run_upstream=true -e image_protocol='docker://'"}
OP_TEST_EXEC_EXTRA=${OP_TEST_EXEC_EXTRA-"-e container_tool=podman"}
# OP_TEST_EXEC_EXTRA=${OP_TEST_EXEC_EXTRA-""}
OP_TEST_RUN_MODE=${OP_TEST_RUN_MODE-"privileged"}
OP_TEST_LABELS=${OP_TEST_LABELS-""}
OP_TEST_PROD=${OP_TEST_PROD-0}
OP_TEST_PRETEST_CUSTOM_SCRIPT=${OP_TEST_PRETEST_CUSTOM_SCRIPT-""}
OP_TEST_DEBUG=${OP_TEST_DEBUG-0}
OP_TEST_DRY_RUN=${OP_TEST_DRY_RUN-0}
OP_TEST_FORCE_INSTALL=${OP_TEST_FORCE_INSTALL-0}
OP_TEST_RESET=${OP_TEST_RESET-1}
OP_TEST_IIB_INSTALL=${OP_TEST_IIB_INSTALL-0}
OP_TEST_LOG_DIR=${OP_TEST_LOG_DIR-"/tmp/op-test"}
OP_TEST_NOCOLOR=${OP_TEST_NOCOLOR-0}

OHIO_INPUT_CATALOG_IMAGE=${OHIO_INPUT_CATALOG_IMAGE-"quay.io/operatorhubio/catalog:latest"}
OHIO_REGISTRY_IMAGE=${OHIO_REGISTRY_IMAGE-"quay.io/operator-framework/upstream-community-operators:latest"}

IIB_PUSH_IMAGE=${IIB_PUSH_IMAGE-"quay.io/operator_testing/catalog:latest"}
IIB_INPUT_REGISTRY_USER=${IIB_INPUT_REGISTRY_USER-"mvalahtv"}
IIB_INPUT_REGISTRY_TOKEN=${IIB_INPUT_REGISTRY_TOKEN-""}
IIB_OUTPUT_REGISTRY_USER=${IIB_OUTPUT_REGISTRY_USER-"redhat+iib_community"}
IIB_OUTPUT_REGISTRY_TOKEN=${IIB_OUTPUT_REGISTRY_TOKEN-""}

OP_TEST_VER_OVERWRITE=${OP_TEST_VER_OVERWRITE-0}
OP_TEST_RECREATE=${OP_TEST_RECREATE-0}
OP_TEST_FORCE_DEPLOY_ON_K8S=${OP_TEST_FORCE_DEPLOY_ON_K8S-0}
OP_TEST_CI_YAML_ONLY=${OP_TEST_CI_YAML_ONLY-0}
OP_TEST_UNCOMPLETE="/tmp/operators_uncomplete-localhost.yaml"
OP_TEST_MIRROR_LATEST_TAG=${OP_TEST_MIRROR_LATEST_TAG-"v4.6"}
DELETE_APPREG=${DELETE_APPREG-0}

export GODEBUG=${GODEBUG-x509ignoreCN=0}

[[ $OP_TEST_NOCOLOR -eq 1 ]] && ANSIBLE_NOCOLOR=1

function help() {
    echo ""
    echo "op-test <test1,test2,...,testN> [<rebo>] [<branch>]"
    echo ""
    echo "Note: 'op-test' can be substituted by 'bash <(curl -sL $OP_SCRIPT_URL)'"
    echo ""
    echo -e "Examples:\n"
    echo -e "\top-test all upstream-community-operators/aqua/1.0.2\n"
    echo -e "\top-test all upstream-community-operators/aqua/1.0.2 https://github.com/operator-framework/community-operators master\n"
    echo -e "\top-test kiwi upstream-community-operators/aqua/1.0.2 https://github.com/operator-framework/community-operators master\n"
    echo -e "\top-test lemon,orange upstream-community-operators/aqua/1.0.2 https://github.com/operator-framework/community-operators master\n"
    exit 1
}

function checkExecutable() {
    local pm=""
    for p in $*;do
        ! command -v $p > /dev/null 2>&1 && pm="$p $pm"
    done
    if [[ "$pm" != "" ]]; then
        echo "Error: Following packages needs to be installed !!!"
        for p in $pm;do
            echo -e "\t$p\n"
        done
        echo ""
        exit 1
    fi
}

function clean() {
    echo "Removing testing container '$OP_TEST_NAME' ..."
    $OP_TEST_CONTAINER_TOOL rm -f $OP_TEST_NAME > /dev/null 2>&1
    echo "Removing kind registry 'kind-registry' ..."
    $OP_TEST_CONTAINER_TOOL rm -f kind-registry > /dev/null 2>&1
    command -v kind > /dev/null 2>&1 && kind delete cluster --name operator-test
    echo "Removing cert dir '$OP_TEST_CERT_DIR' ..."
    rm -rf $OP_TEST_CERT_DIR > /dev/null 2>&1
    echo "Done"
    exit 0
}

function iib_install() {
    echo "Installing iib ..."
    set -o pipefail
    $DRY_RUN_CMD ansible-pull -U $OP_TEST_ANSIBLE_PULL_REPO -C $OP_TEST_ANSIBLE_PULL_BRANCH $OP_TEST_ANSIBLE_DEFAULT_ARGS -e run_prepare_catalog_repo_upstream=false --tags iib
    # -e iib_push_image="$IIB_PUSH_IMAGE" -e iib_push_registry="$(echo $IIB_PUSH_IMAGE | cut -d '/' -f 1)"
    if [[ $? -eq 0 ]];then
        echo "Loging to registry.redhat.io ..."
        if [ -n "$IIB_INPUT_REGISTRY_TOKEN" ];then
          echo "$IIB_INPUT_REGISTRY_TOKEN" | $OP_TEST_CONTAINER_TOOL login registry.redhat.io -u $IIB_INPUT_REGISTRY_USER --password-stdin || { echo "Problem to login to 'registry.redhat.io' !!!"; exit 1; }
          if [ -n "$IIB_OUTPUT_REGISTRY_TOKEN" ];then
            echo "$IIB_OUTPUT_REGISTRY_TOKEN" | $OP_TEST_CONTAINER_TOOL login quay.io -u $IIB_OUTPUT_REGISTRY_USER --password-stdin || { echo "Problem to login to 'quay.io' !!!"; exit 1; }
          fi
          $OP_TEST_CONTAINER_TOOL cp $HOME/.docker/config.json iib_iib-worker_1:/root/.docker/config.json.template || exit 1
        else
            echo "Variable \$IIB_INPUT_REGISTRY_TOKEN is not set or is empty !!!"
            exit 1
        fi
        echo -e "\n=================================================================================="
        echo -e "IIB was installed successfully !!!"
        echo -e "==================================================================================\n"
    else
        echo "Problem installing iib !!!"
        exit 1
    fi
    set +o pipefail
}

function run() {
        if [[ $OP_TEST_DEBUG -ge 4 ]] ; then
                v=$(exec 2>&1 && set -x && set -- "$@")
                echo "#${v#*--}"
                set -o pipefail
                "$@" | tee -a $OP_TEST_LOG_DIR/log.out
                [[ $? -eq 0 ]] || { echo -e "\nFailed with rc=$? !!!\nLogs are in '$OP_TEST_LOG_DIR/log.out'."; exit $?; }
                set +o pipefail
        elif [[ $OP_TEST_DEBUG -ge 1 ]] ; then
                set -o pipefail
                "$@" | tee -a $OP_TEST_LOG_DIR/log.out
                [[ $? -eq 0 ]] || { echo -e "\nFailed with rc=$? !!!\nLogs are in '$OP_TEST_LOG_DIR/log.out'."; exit $?; }
                set +o pipefail
        else
                set -o pipefail
                "$@" | tee -a $OP_TEST_LOG_DIR/log.out >/dev/null 2>&1
                [[ $? -eq 0 ]] || { echo -e "\nFailed with rc=$? !!!\nLogs are in '$OP_TEST_LOG_DIR/log.out'."; exit $?; }
                set +o pipefail
        fi
}

[ "$OP_TEST_RUN_MODE" = "privileged" ] && OP_TEST_CONAINER_RUN_DEFAULT_ARGS="--privileged --net host -v $OP_TEST_CERT_DIR:/usr/share/pki/ca-trust-source/anchors -e STORAGE_DRIVER=vfs -e BUILDAH_FORMAT=docker"
[ "$OP_TEST_RUN_MODE" = "user" ] && OP_TEST_CONAINER_RUN_DEFAULT_ARGS="--net host -v $OP_TEST_CERT_DIR:/usr/share/pki/ca-trust-source/anchors -e STORAGE_DRIVER=vfs -e BUILDAH_FORMAT=docker"

# OP_TEST_EXEC_USER="-e operator_dir=/tmp/community-operators-for-catalog/upstream-community-operators/aqua -e operator_version=1.0.2 --tags pure_test"

checkExecutable $OP_TEST_BASE_DEP

if ! command -v ansible > /dev/null 2>&1; then
    echo "Error: Ansible is not installed. Please install it first !!!"
    echo "    e.g.  : pip install ansible jmespath"
    echo "    or    : apt install ansible"
    echo "    or    : yum install ansible"
    echo -e "\nRun 'ansible --version' to make sure it is installed\n"

    exit 1
fi

if [ "$OP_TEST_CONTAINER_TOOL" = "podman" ];then
    OP_TEST_ANSIBLE_EXTRA_ARGS="$OP_TEST_ANSIBLE_EXTRA_ARGS -e opm_container_tool=podman -e container_tool=podman -e opm_container_tool_index=none"
    # OP_TEST_EXEC_EXTRA="$OP_TEST_EXEC_EXTRA -e opm_container_tool=podman -e container_tool=podman -e opm_container_tool_index="
fi

[ -d $OP_TEST_LOG_DIR ] || mkdir -p $OP_TEST_LOG_DIR
[ -f $OP_TEST_LOG_DIR/log.out ] && rm -f $OP_TEST_LOG_DIR/log.out

# Handle labels
if [ -n "$OP_TEST_LABELS" ];then
    for l in $(echo $OP_TEST_LABELS);do
    echo "Handling label '$l' ..."
    [[ "$l" = "allow/operator-version-overwrite" ]] && export OP_TEST_VER_OVERWRITE=1
    [[ "$l" = "allow/operator-recreate" ]] && export OP_TEST_RECREATE=1
    [[ "$l" = "allow/serious-changes-to-existing" ]] && export OP_ALLOW_BIG_CHANGES_TO_EXISTING=1
    [[ "$l" = "test/force-deploy-on-kubernetes" ]] && export OP_TEST_FORCE_DEPLOY_ON_K8S=1
    [[ "$l" = "verbosity/high" ]] && export OP_TEST_DEBUG=2
    [[ "$l" = "verbosity/debug" ]] && export OP_TEST_DEBUG=3
    done
else
    echo "Info: No labels defined"
fi
[[ $OP_TEST_DEBUG -eq 0 ]] && OP_TEST_EXEC_EXTRA="-vv $OP_TEST_EXEC_EXTRA"
# [[ $OP_TEST_DEBUG -eq 1 ]] && OP_TEST_EXEC_EXTRA="$OP_TEST_EXEC_EXTRA"
[[ $OP_TEST_DEBUG -eq 2 ]] && OP_TEST_EXEC_EXTRA="-v $OP_TEST_EXEC_EXTRA"
[[ $OP_TEST_DEBUG -eq 3 ]] && OP_TEST_EXEC_EXTRA="-vv $OP_TEST_EXEC_EXTRA"
[[ $OP_TEST_DRY_RUN -eq 1 ]] && DRY_RUN_CMD="echo"


# Hide secrets in dry run
if [[ $OP_TEST_DRY_RUN -eq 1 ]];then
    QUAY_API_TOKEN_OPENSHIFT_COMMUNITY_OP=""
    QUAY_API_TOKEN_OPERATORHUBIO=""
    QUAY_API_TOKEN_OPERATOR_TESTING=""
    OHIO_REGISTRY_TOKEN=""
    QUAY_APPREG_TOKEN=""
    QUAY_COURIER_TOKEN=""
fi

echo "debug=$OP_TEST_DEBUG"

# Handle test types
[ -z $1 ] && help

[ "$ACTION" = "clean" ] && clean
if [ "$ACTION" = "docker" ];then
    echo "Installing docker ..."
    $DRY_RUN_CMD ansible-pull -U $OP_TEST_ANSIBLE_PULL_REPO -C $OP_TEST_ANSIBLE_PULL_BRANCH $OP_TEST_ANSIBLE_DEFAULT_ARGS -e run_prepare_catalog_repo_upstream=false --tags docker
    if [[ $? -eq 0 ]];then
        echo -e "\n=================================================================================="
        echo -e "Make sure that you logout and login after docker installation to apply changes !!!"
        echo -e "==================================================================================\n"
    else
        echo "Problem installing docker !!!"
        exit 1
    fi
    exit 0
fi

[ "$ACTION" = "iib" ] && { iib_install; exit 0; }

if ! command -v $OP_TEST_CONTAINER_TOOL > /dev/null 2>&1; then
    echo -e "\nError: '$OP_TEST_CONTAINER_TOOL' is missing !!! Install it via:"
    [ "$OP_TEST_CONTAINER_TOOL" = "docker" ] && echo -e "\n\tbash <(curl -sL $OP_SCRIPT_URL) $OP_TEST_CONTAINER_TOOL"
    [ "$OP_TEST_CONTAINER_TOOL" = "podman" ] && echo -e "\n\tContainer tool '$OP_TEST_CONTAINER_TOOL' is not supported yet"
    echo
    exit 1
fi


# Handle operator info
OP_TEST_BASE_DIR=${OP_TEST_BASE_DIR-"/tmp/community-operators-for-catalog"}
OP_TEST_STREAM=${OP_TEST_STREAM-"upstream-community-operators"}
OP_TEST_OPERATOR=${OP_TEST_OPERATOR-"aqua"}
OP_TEST_VERSION=${OP_TEST_VERSION-"1.0.2"}

if [ -n "$2" ];then
    if [ -n "$3" ];then
        p=$2
        OP_TEST_VERSION=$(echo $p | rev | cut -d'/' -f 1 | rev);p=$(dirname $p)
        OP_TEST_OPERATOR=$(echo $p | rev | cut -d'/' -f 1 | rev);p=$(dirname $p)
        OP_TEST_STREAM=$(echo $p | rev | cut -d'/' -f 1 | rev);p=$(dirname $p)
        OP_TEST_REPO="$3"
        OP_TEST_BRANCH="master"
        [ -n "$4" ] && OP_TEST_BRANCH=$4
    elif [ -d $2 ];then
        p=$(readlink -f $2)
        OP_TEST_VERSION=$(echo $p | rev | cut -d'/' -f 1 | rev);p=$(dirname $p)
        OP_TEST_OPERATOR=$(echo $p | rev | cut -d'/' -f 1 | rev);p=$(dirname $p)
        OP_TEST_STREAM=$(echo $p | rev | cut -d'/' -f 1 | rev);p=$(dirname $p)
        OP_TEST_CONTAINER_RUN_EXTRA_ARGS="$OP_TEST_CONTAINER_RUN_EXTRA_ARGS -v $p:/tmp/community-operators-for-catalog"
    else
        echo -e "\nError: Full path to operator/version '$PWD/$2' was not found !!!\n"
        exit 1
    fi

else
    p=${PWD}
    echo "Running locally from '$p' ..."
    OP_TEST_VERSION=$(echo $p | rev | cut -d'/' -f 1 | rev);p=$(dirname $p)
    OP_TEST_OPERATOR=$(echo $p | rev | cut -d'/' -f 1 | rev);p=$(dirname $p)
    OP_TEST_STREAM=$(echo $p | rev | cut -d'/' -f 1 | rev);p=$(dirname $p)
    OP_TEST_CONTAINER_RUN_EXTRA_ARGS="$OP_TEST_CONTAINER_RUN_EXTRA_ARGS -v $p:/tmp/community-operators-for-catalog"
fi

OP_TEST_CHECK_STEAM_OK=0
[ "$OP_TEST_STREAM" = "." ] && [ "$OP_TEST_VERSION" = "sync" ] && OP_TEST_STREAM=$OP_TEST_OPERATOR && OP_TEST_OPERATOR=$OP_TEST_VERSION
[ "$OP_TEST_STREAM" = "." ] && [ "$OP_TEST_VERSION" = "update" ] && OP_TEST_STREAM=$OP_TEST_OPERATOR && OP_TEST_OPERATOR=$OP_TEST_VERSION
[ "$OP_TEST_STREAM" = "community-operators" ] && OP_TEST_CHECK_STEAM_OK=1
[ "$OP_TEST_STREAM" = "upstream-community-operators" ] && OP_TEST_CHECK_STEAM_OK=1

[[ $OP_TEST_CHECK_STEAM_OK -eq 0 ]] && { echo "Error : Unknwn value for 'OP_TEST_STREAM=$OP_TEST_STREAM' !!!"; exit 1; }

function ExecParameters() {
    OP_TEST_EXEC_USER=
    OP_TEST_EXEC_USER_SECRETS=
    OP_TEST_EXEC_USER_INDEX_CHECK=
    OP_TEST_SKIP=0
    [[ $1 == kiwi* ]] && OP_TEST_EXEC_USER="-e operator_dir=$OP_TEST_BASE_DIR/$OP_TEST_STREAM/$OP_TEST_OPERATOR -e operator_version=$OP_TEST_VERSION --tags pure_test -e operator_channel_force=optest"
    [[ $1 == kiwi* ]] && [ "$OP_TEST_STREAM" = "community-operators" ] && [[ $OP_TEST_FORCE_DEPLOY_ON_K8S -eq 0 ]] && OP_TEST_EXEC_USER="$OP_TEST_EXEC_USER -e test_skip_deploy=true"
    [[ $1 == lemon* ]] && OP_TEST_EXEC_USER="-e operator_dir=$OP_TEST_BASE_DIR/$OP_TEST_STREAM/$OP_TEST_OPERATOR --tags deploy_bundles"
    [[ $1 == orange* ]] && [ "$OP_TEST_VERSION" != "sync" ] && OP_TEST_EXEC_USER="-e operator_dir=$OP_TEST_BASE_DIR/$OP_TEST_STREAM/$OP_TEST_OPERATOR --tags deploy_bundles"
    # [[ $1 == orange* ]] && [ "$OP_TEST_VERSION" = "update" ] && [[ $OP_TEST_PROD -ge 1 ]] && [[ $OP_TEST_RECREATE -eq 1 ]] && OP_TEST_EXEC_USER="$OP_TEST_EXEC_USER,remove_operator"
    [[ $1 == orange* ]] &&  [ "$OP_TEST_VERSION" = "sync" ] && OP_TEST_EXEC_USER="--tags deploy_bundles"
    # [[ $1 == orange_* ]] && [[ $OP_TEST_PROD -eq 1 ]] && [ "$OP_TEST_STREAM" = "community-operators" ] && OP_TEST_EXEC_USER="$OP_TEST_EXEC_USER,iib"

    ## TODO check if needed for sync in prod
    [[ $1 == orange* ]] && [ "$OP_TEST_STREAM" = "community-operators" ] && [ "$OP_TEST_VERSION" != "sync" ] && [[ $OP_TEST_PROD -lt 2 ]] && OP_TEST_EXEC_USER="$OP_TEST_EXEC_USER -e production_registry_namespace=quay.io/openshift-community-operators"
    [[ $1 == orange* ]] && [ "$OP_TEST_STREAM" = "upstream-community-operators" ] && [ "$OP_TEST_VERSION" != "sync" ] && [[ $OP_TEST_PROD -lt 2 ]] && OP_TEST_EXEC_USER="$OP_TEST_EXEC_USER -e production_registry_namespace=quay.io/operatorhubio"

    # Handle index_check
    [[ $1 == orange* ]] &&[ "$OP_TEST_STREAM" = "community-operators" ] && OP_TEST_EXEC_USER_INDEX_CHECK="-e run_prepare_catalog_repo_upstream=true -e bundle_index_image=quay.io/openshift-community-operators/catalog:latest -e operator_base_dir=$OP_TEST_BASE_DIR/$OP_TEST_STREAM"
    [[ $1 == orange* ]] &&[ "$OP_TEST_STREAM" = "community-operators" ] && [[ $OP_TEST_PROD -ge 2 ]] && OP_TEST_EXEC_USER_INDEX_CHECK="-e run_prepare_catalog_repo_upstream=true -e bundle_index_image=quay.io/operator_testing/catalog:latest -e operator_base_dir=$OP_TEST_BASE_DIR/$OP_TEST_STREAM"
    [[ $1 == orange_* ]] && [ "$OP_TEST_STREAM" = "community-operators" ] && OP_TEST_EXEC_USER_INDEX_CHECK="-e run_prepare_catalog_repo_upstream=true -e bundle_index_image=quay.io/openshift-community-operators/catalog:${1/orange_/} -e operator_base_dir=$OP_TEST_BASE_DIR/$OP_TEST_STREAM"
    [[ $1 == orange_* ]] && [ "$OP_TEST_STREAM" = "community-operators" ] && [[ $OP_TEST_PROD -ge 2 ]] && OP_TEST_EXEC_USER_INDEX_CHECK="-e run_prepare_catalog_repo_upstream=true -e bundle_index_image=quay.io/operator_testing/catalog:${1/orange_/} -e operator_base_dir=$OP_TEST_BASE_DIR/$OP_TEST_STREAM"
    [[ $1 == orange* ]] && [ "$OP_TEST_STREAM" = "upstream-community-operators" ] && OP_TEST_EXEC_USER_INDEX_CHECK="-e run_prepare_catalog_repo_upstream=true -e bundle_index_image=quay.io/operatorhubio/catalog:latest -e operator_base_dir=$OP_TEST_BASE_DIR/$OP_TEST_STREAM"
    [[ $1 == orange* ]] && [ "$OP_TEST_STREAM" = "upstream-community-operators" ] && [[ $OP_TEST_PROD -ge 2 ]] && OP_TEST_EXEC_USER_INDEX_CHECK="-e run_prepare_catalog_repo_upstream=true -e bundle_index_image=quay.io/operator_testing/catalog:latest -e operator_base_dir=$OP_TEST_BASE_DIR/$OP_TEST_STREAM"
    [[ $1 == orange_* ]] && [ "$OP_TEST_STREAM" = "upstream-community-operators" ] && { echo "Error: orange_xxx is not supported for 'upstream-community-operators' !!! Exiting ..."; exit 1; }

    # Fix default of k8s in tests (not needed anymore)
    # [[ $1 == orange* ]] && [[ $OP_TEST_PROD -eq 0 ]] && [ "$OP_TEST_STREAM" = "upstream-community-operators" ] && OP_TEST_EXEC_USER="$OP_TEST_EXEC_USER -e use_cluster_filter=false -e supported_cluster_versions=latest"

    [[ $1 == orange* ]] && [[ $OP_TEST_PROD -eq 1 ]] && [ "$OP_TEST_STREAM" = "community-operators" ] && OP_TEST_EXEC_USER="$OP_TEST_EXEC_USER -e bundle_registry=quay.io -e bundle_image_namespace=openshift-community-operators -e bundle_index_image_namespace=openshift-community-operators -e bundle_index_image_name=catalog"
    
    # Fix default of k8s in tests (not needed anymore) 
    # [[ $1 == orange* ]] && [[ $OP_TEST_PROD -eq 1 ]] && [ "$OP_TEST_STREAM" = "upstream-community-operators" ] && OP_TEST_EXEC_USER="$OP_TEST_EXEC_USER -e bundle_registry=quay.io -e bundle_image_namespace=operatorhubio -e bundle_index_image_namespace=operatorhubio -e bundle_index_image_name=catalog -e use_cluster_filter=false -e supported_cluster_versions=latest"
    # Using default "-e use_cluster_filter=false -e supported_cluster_versions=latest" for k8s
    [[ $1 == orange* ]] && [[ $OP_TEST_PROD -eq 1 ]] && [ "$OP_TEST_STREAM" = "upstream-community-operators" ] && OP_TEST_EXEC_USER="$OP_TEST_EXEC_USER -e bundle_registry=quay.io -e bundle_image_namespace=operatorhubio -e bundle_index_image_namespace=operatorhubio -e bundle_index_image_name=catalog"
    
    [[ $1 == orange* ]] && [[ $OP_TEST_PROD -ge 2 ]] && OP_TEST_EXEC_USER="$OP_TEST_EXEC_USER -e bundle_registry=quay.io -e bundle_image_namespace=operator_testing -e bundle_index_image_namespace=operator_testing -e bundle_index_image_name=catalog"

    [[ $1 == orange* ]] && [[ $OP_TEST_PROD -eq 1 ]] && [ "$OP_TEST_STREAM" = "community-operators" ] && OP_TEST_EXEC_USER_SECRETS="$OP_TEST_EXEC_USER_SECRETS -e quay_api_token=$QUAY_API_TOKEN_OPENSHIFT_COMMUNITY_OP"
    [[ $1 == orange* ]] && [[ $OP_TEST_PROD -eq 1 ]] && [ "$OP_TEST_STREAM" = "upstream-community-operators" ] && OP_TEST_EXEC_USER_SECRETS="$OP_TEST_EXEC_USER_SECRETS -e quay_api_token=$QUAY_API_TOKEN_OPERATORHUBIO"
    [[ $1 == orange* ]] && [[ $OP_TEST_PROD -ge 2 ]] && OP_TEST_EXEC_USER_SECRETS="$OP_TEST_EXEC_USER_SECRETS -e quay_api_token=$QUAY_API_TOKEN_OPERATOR_TESTING"

    # If community and doing orange_<version>
    [[ $1 == orange* ]] && [[ $1 != orange_* ]] && [ "$OP_TEST_STREAM" = "community-operators" ] && OP_TEST_EXEC_USER="$OP_TEST_EXEC_USER -e stream_kind=openshift_upstream"
    [[ $1 == orange_* ]] && [ "$OP_TEST_STREAM" = "community-operators" ] && OP_TEST_EXEC_USER="$OP_TEST_EXEC_USER -e stream_kind=openshift_upstream -e supported_cluster_versions=${1/orange_/} -e bundle_index_image_version=${1/orange_/}"
    [[ $1 == lemon_* ]] && [ "$OP_TEST_STREAM" = "community-operators" ] && OP_TEST_EXEC_USER="$OP_TEST_EXEC_USER -e stream_kind=openshift_upstream -e supported_cluster_versions=${1/lemon_/} -e bundle_index_image_version=${1/lemon_/}"
    [[ $1 == orange_* ]] && [ "$OP_TEST_STREAM" = "community-operators" ] && [[ $OP_TEST_PROD -eq 1 ]] && OP_TEST_EXEC_USER="$OP_TEST_EXEC_USER -e mirror_multiarch_image=registry.redhat.io/openshift4/ose-operator-registry:v4.5 -e mirror_apply=true"
    [[ $1 == orange_* ]] && [ "$OP_TEST_STREAM" = "community-operators" ] && [[ $OP_TEST_PROD -eq 1 ]] && [ "$OP_TEST_MIRROR_LATEST_TAG" != "${1/orange_/}" ]&& OP_TEST_EXEC_USER_SECRETS="$OP_TEST_EXEC_USER_SECRETS -e mirror_index_images=\"quay.io/redhat/redhat----community-operator-index:${1/orange_/}|redhat+iib_community|$QUAY_RH_INDEX_PW\""
    [[ $1 == orange_* ]] && [ "$OP_TEST_STREAM" = "community-operators" ] && [[ $OP_TEST_PROD -eq 1 ]] && [ "$OP_TEST_MIRROR_LATEST_TAG" = "${1/orange_/}" ] && OP_TEST_EXEC_USER_SECRETS="$OP_TEST_EXEC_USER_SECRETS -e mirror_index_images=\"quay.io/redhat/redhat----community-operator-index:${1/orange_/}|redhat+iib_community|$QUAY_RH_INDEX_PW|quay.io/redhat/redhat----community-operator-index:latest\""
    [[ OP_ALLOW_BIG_CHANGES_TO_EXISTING -eq 1 ]] && OP_TEST_EXEC_USER="$OP_TEST_EXEC_USER -e allow_big_changes_to_existing=true"

    # Failing test when upstream and orgage_<version> (not supported yet)
    [[ $1 == orange_* ]] && [ "$OP_TEST_STREAM" = "upstream-community-operators" ] && OP_TEST_EXEC_USER="" && { echo "Warning: Index versions are not supported for 'upstream-community-operators' !!! Skipping ..."; OP_TEST_SKIP=1; }

    # Don't reset kind when production (It should speedup deploy when kind and registry is not needed)
    [[ $1 == orange* ]] && [[ $OP_TEST_PROD -ge 1 ]] && OP_TEST_RESET=0

    [[ $1 == orange* ]] && [[ $OP_TEST_VER_OVERWRITE -eq 0 ]] && [ "$OP_TEST_VERSION" != "update" ] && OP_TEST_EXEC_USER="$OP_TEST_EXEC_USER -e fail_on_no_index_change=true"
    [[ $1 == orange* ]] && [[ $OP_TEST_PROD -ge 1 ]] && [[ $OP_TEST_VER_OVERWRITE -eq 0 ]] && [ "$OP_TEST_VERSION" == "sync" ] && OP_TEST_EXEC_USER="$OP_TEST_EXEC_USER -e index_force_update=true"
    [[ $1 == orange* ]] && [[ $OP_TEST_PROD -ge 1 ]] && [[ $OP_TEST_CI_YAML_ONLY -eq 1 ]] && [ "$OP_TEST_VERSION" == "sync" ] && OP_TEST_EXEC_USER="$OP_TEST_EXEC_USER -e operator_dir=/tmp/community-operators-for-catalog/$OP_TEST_STREAM/$OP_TEST_OPERATOR"
    # [[ $1 == orange* ]] && [[ $OP_TEST_VER_OVERWRITE -eq 0 ]] && [[ $OP_TEST_RECREATE -eq 0 ]] && [ "$OP_TEST_VERSION" != "update" ] && OP_TEST_EXEC_USER="$OP_TEST_EXEC_USER -e fail_on_no_index_change=true"
    [[ $1 == orange* ]] && [[ $OP_TEST_VER_OVERWRITE -eq 0 ]] && [ "$OP_TEST_VERSION" = "update" ] && OP_TEST_EXEC_USER="$OP_TEST_EXEC_USER -e fail_on_no_index_change=false -e strict_mode=true -e index_force_update=true"
    # Handle OP_TEST_VER_OVERWRITE
    [[ $1 == orange* ]] && [[ $OP_TEST_VER_OVERWRITE -eq 1 ]] && [ "$OP_TEST_VERSION" != "sync" ] && [ "$OP_TEST_VERSION" != "update" ] && OP_TEST_EXEC_USER="$OP_TEST_EXEC_USER -e operator_version=$OP_TEST_VERSION -e bundle_force_rebuild=true -e fail_on_no_index_change=false"
    # Handle OP_TEST_RECREATE
    [[ $1 == orange* ]] && [[ $OP_TEST_RECREATE -eq 1 ]] && [[ $OP_TEST_PROD -eq 0 ]] && OP_TEST_SKIP=1

    # Skipping when version is not defined in case OP_TEST_VER_OVERWRITE=1
    [[ $OP_TEST_VER_OVERWRITE -eq 1 ]] && [ -z $OP_TEST_VERSION ] && { echo "Warning: OP_TEST_VER_OVERWRITE=1 and no version specified 'OP_TEST_VERSION=$OP_TEST_VERSION' !!! Skipping ..."; OP_TEST_SKIP=1; }

    # Skipping case when sync in non prod mode
    [[ $OP_TEST_PROD -eq 0 ]] && [ "$OP_TEST_VERSION" = "sync" ] && { echo "Warning: No support for 'sync' (try 'update') when 'OP_TEST_PROD=$OP_TEST_PROD' !!! Skipping ..."; OP_TEST_SKIP=1; }

    [[ $OP_TEST_PROD -eq 0 ]] && [ "$OP_TEST_OPERATOR" = "update" ] && { echo "Warning: No support for 'update' when 'OP_TEST_PROD=$OP_TEST_PROD' when operator name is not defined !!! Skipping ..."; OP_TEST_SKIP=1; }

    # Handling when kiwi and lemon case for production mode
    [[ $OP_TEST_PROD -ge 1 ]] && [[ $1 == kiwi* ]] && { echo "Warning: No support for 'kiwi' test when 'OP_TEST_PROD=$OP_TEST_PROD' !!! Skipping ..."; OP_TEST_SKIP=1; }
    [[ $OP_TEST_PROD -ge 1 ]] && [[ $1 == lemon* ]] && { echo "Warning: No support for 'lemon' test when 'OP_TEST_PROD=$OP_TEST_PROD' !!! Skipping ..."; OP_TEST_SKIP=1; }

    [[ $1 == push_to_quay* ]] && [ "$OP_TEST_STREAM" = "community-operators" ] && OP_TEST_RESET=1 && OP_TEST_EXEC_USER="$OP_TEST_EXEC_USER --tags deploy_bundles -e operator_dir=/tmp/community-operators-for-catalog/$OP_TEST_STREAM/$OP_TEST_OPERATOR -e quay_appregistry_api_token=$QUAY_APPREG_TOKEN -e quay_appregistry_courier_token=$QUAY_COURIER_TOKEN -e production_registry_namespace=quay.io/openshift-community-operators -e index_force_update=true -e bundle_index_image_name=catalog -e op_test_operator_version=$OP_TEST_VERSION"
    [[ $1 == push_to_quay* ]] && [ "$OP_TEST_STREAM" = "community-operators" ] && OP_TEST_RESET=1 && [[ DELETE_APPREG -eq 1 ]] && OP_TEST_EXEC_USER="$OP_TEST_EXEC_USER -e delete_appreg='true'"
    [[ $1 == push_to_quay* ]] && [ "$OP_TEST_STREAM" = "upstream-community-operators" ] && OP_TEST_RESET=0 && OP_TEST_EXEC_USER="" && { echo "Warning: Push to quay is not supported for 'upstream-community-operators' !!! Skipping ..."; OP_TEST_SKIP=1; }

    [[ $1 == ohio_image* ]] && OP_TEST_RESET=0 && OP_TEST_EXEC_USER="$OP_TEST_EXEC_USER --tags app_registry -e bundle_index_image=$OHIO_INPUT_CATALOG_IMAGE -e index_export_parallel=true -e app_registry_image=$OHIO_REGISTRY_IMAGE -e quay_api_token=$OHIO_REGISTRY_TOKEN"

    [[ $1 == op_delete* ]] && OP_TEST_RESET=0 && OP_TEST_EXEC_USER="$OP_TEST_EXEC_USER --tags remove_operator -e operator_dir=/tmp/community-operators-for-catalog/$OP_TEST_STREAM/$OP_TEST_OPERATOR"
    [[ $1 == op_delete* ]] && [[ $OP_TEST_PROD -eq 1 ]] && [ "$OP_TEST_STREAM" = "community-operators" ] && OP_TEST_EXEC_USER="$OP_TEST_EXEC_USER -e bundle_registry=quay.io -e bundle_image_namespace=openshift-community-operators -e bundle_index_image_namespace=openshift-community-operators -e bundle_index_image_name=catalog"
    [[ $1 == op_delete* ]] && [[ $OP_TEST_PROD -eq 1 ]] && [ "$OP_TEST_STREAM" = "upstream-community-operators" ] && OP_TEST_EXEC_USER="$OP_TEST_EXEC_USER -e bundle_registry=quay.io -e bundle_image_namespace=operatorhubio -e bundle_index_image_namespace=operatorhubio -e bundle_index_image_name=catalog"
    [[ $1 == op_delete* ]] && [[ $OP_TEST_PROD -eq 1 ]] && [ "$OP_TEST_STREAM" = "community-operators" ] && OP_TEST_EXEC_USER_SECRETS="$OP_TEST_EXEC_USER_SECRETS -e quay_api_token=$QUAY_API_TOKEN_OPENSHIFT_COMMUNITY_OP"
    [[ $1 == op_delete* ]] && [[ $OP_TEST_PROD -eq 1 ]] && [ "$OP_TEST_STREAM" = "upstream-community-operators" ] && OP_TEST_EXEC_USER_SECRETS="$OP_TEST_EXEC_USER_SECRETS -e quay_api_token=$QUAY_API_TOKEN_OPERATORHUBIO"
    [[ $1 == op_delete* ]] && [[ $OP_TEST_PROD -ge 2 ]] && OP_TEST_EXEC_USER_SECRETS="$OP_TEST_EXEC_USER_SECRETS -e quay_api_token=$QUAY_API_TOKEN_OPERATOR_TESTING"
    [[ $1 == op_delete_* ]] && [ "$OP_TEST_STREAM" = "community-operators" ] && OP_TEST_EXEC_USER="$OP_TEST_EXEC_USER -e bundle_index_image_version=${1/op_delete_/}"

    # index safety - avoid accidental index destroy
    [[ $1 == orange* ]] && [[ $OP_TEST_PROD -eq 1 ]] && OP_TEST_EXEC_USER="$OP_TEST_EXEC_USER $INDEX_SAFETY" && OP_TEST_EXEC_USER_INDEX_CHECK="$OP_TEST_EXEC_USER_INDEX_CHECK $INDEX_SAFETY"

    # Force strict mode (force to fail on 'bundle add' and 'index add')
    [[ $OP_TEST_PROD -eq 0 ]] && OP_TEST_EXEC_USER="$OP_TEST_EXEC_USER -e strict_mode=true"


# bundle_index_image_version
    # TODO redhat mirror
    #"-e mirror_index_images=quay.io/redhat/redhat----community-operator-index|redhat+iib_community|$QUAY_RH_INDEX_PW"
}

echo "Using $(ansible --version | head -n 1) on host ..."
if [[ $OP_TEST_DEBUG -ge 2 ]];then
    run echo "OP_TEST_DEBUG='$OP_TEST_DEBUG'"
    run echo "OP_TEST_DRY_RUN='$OP_TEST_DRY_RUN'"
    run echo "OP_TEST_EXEC_USER='$OP_TEST_EXEC_USER'"
    run echo "OP_TEST_IMAGE='$OP_TEST_IMAGE'"
    run echo "OP_TEST_CONTAINER_EXEC_EXTRA_ARGS='$OP_TEST_CONTAINER_EXEC_EXTRA_ARGS'"
    run echo "OP_TEST_CERT_DIR='$OP_TEST_CERT_DIR'"
    run echo "OP_TEST_CONTAINER_TOOL='$OP_TEST_CONTAINER_TOOL'"
    run echo "OP_TEST_NAME='$OP_TEST_NAME'"
    run echo "OP_TEST_ANSIBLE_PULL_REPO='$OP_TEST_ANSIBLE_PULL_REPO'"
    run echo "OP_TEST_ANSIBLE_PULL_BRANCH='$OP_TEST_ANSIBLE_PULL_BRANCH'"
    run echo "OP_TEST_ANSIBLE_DEFAULT_ARGS='$OP_TEST_ANSIBLE_DEFAULT_ARGS'"
    run echo "OP_TEST_ANSIBLE_EXTRA_ARGS='$OP_TEST_ANSIBLE_EXTRA_ARGS'"
    run echo "OP_TEST_CONAINER_RUN_DEFAULT_ARGS='$OP_TEST_CONAINER_RUN_DEFAULT_ARGS'"
    run echo "OP_TEST_CONTAINER_RUN_EXTRA_ARGS='$OP_TEST_CONTAINER_RUN_EXTRA_ARGS'"
    run echo "OP_TEST_CONTAINER_EXEC_DEFAULT_ARGS='$OP_TEST_CONTAINER_EXEC_EXTRA_ARGS'"
    run echo "OP_TEST_CONTAINER_EXEC_EXTRA_ARGS='$OP_TEST_CONTAINER_EXEC_EXTRA_ARGS'"
    run echo "OP_TEST_RUN_MODE='$OP_TEST_RUN_MODE'"
    run echo "OP_TEST_FORCE_INSTALL='$OP_TEST_FORCE_INSTALL'"
    run echo "OP_TEST_LOG_DIR='$OP_TEST_LOG_DIR'"
fi

echo -e "\nOne can do 'tail -f $OP_TEST_LOG_DIR/log.out' from second console to see full logs\n"


# Check if kind is installed
echo -e "Checking for kind binary ..."
if ! $DRY_RUN_CMD command -v kind > /dev/null 2>&1; then
    OP_TEST_FORCE_INSTALL=1
# else
#     echo -e "Testing existance of kind cluster ..."
#     # Check if kind cluster is running
#     if ! $DRY_RUN_CMD kind get clusters | grep operator-test > /dev/null 2>&1; then
#         OP_TEST_FORCE_INSTALL=1
#         echo
#     fi
fi

# Install prerequisites (kind cluster)
[[ $OP_TEST_FORCE_INSTALL -eq 1 ]] && run echo -e " [ Installing prerequisites ] "
[[ $OP_TEST_FORCE_INSTALL -eq 1 ]] && run $DRY_RUN_CMD ansible-pull -U $OP_TEST_ANSIBLE_PULL_REPO -C $OP_TEST_ANSIBLE_PULL_BRANCH $OP_TEST_ANSIBLE_DEFAULT_ARGS $OP_TEST_ANSIBLE_EXTRA_ARGS -e run_prepare_catalog_repo_upstream=false

# [[ $OP_TEST_IIB_INSTALL -eq 1 ]] && iib_install 

if [ -n "$OP_TEST_REPO" ];then
    OP_TEST_EXEC_EXTRA="$OP_TEST_EXEC_EXTRA -e catalog_repo=$OP_TEST_REPO -e catalog_repo_branch=$OP_TEST_BRANCH"
else
    OP_TEST_EXEC_EXTRA="$OP_TEST_EXEC_EXTRA -e run_prepare_catalog_repo_upstream=false"
fi
# Start container
echo -e " [ Preparing testing container '$OP_TEST_NAME' from '$OP_TEST_IMAGE' ] "
$DRY_RUN_CMD $OP_TEST_CONTAINER_TOOL pull $OP_TEST_IMAGE > /dev/null 2>&1 || { echo "Error: Problem pulling image '$OP_TEST_IMAGE' !!!"; exit 1; }

OP_TEST_CONTAINER_OPT="$OP_TEST_CONTAINER_OPT -e ANSIBLE_CONFIG=/playbooks/upstream/ansible.cfg"
OP_TEST_CONTAINER_OPT="$OP_TEST_CONTAINER_OPT -e GODEBUG=$GODEBUG"

OP_TEST_SKIP=0
for t in $TESTS;do

    ExecParameters $t
    [[ $OP_TEST_SKIP -eq 1 ]] && echo "Skipping test '$t' for '$OP_TEST_STREAM $OP_TEST_OPERATOR $OP_TEST_VERSION' ..." && continue

    [ -z "$OP_TEST_EXEC_USER" ] && { echo "Error: Unknown test '$t' for '$OP_TEST_STREAM $OP_TEST_OPERATOR $OP_TEST_VERSION' !!! Exiting ..."; help; }
    echo -e "Test '$t' for '$OP_TEST_STREAM $OP_TEST_OPERATOR $OP_TEST_VERSION' ..."
    if [[ $OP_TEST_RESET -eq 1 ]];then
        echo -e "[$t] Reseting kind cluster ..."
        run $DRY_RUN_CMD ansible-pull -U $OP_TEST_ANSIBLE_PULL_REPO -C $OP_TEST_ANSIBLE_PULL_BRANCH $OP_TEST_ANSIBLE_DEFAULT_ARGS -e run_prepare_catalog_repo_upstream=false --tags reset
    fi
    if [ -n "$OP_TEST_PRETEST_CUSTOM_SCRIPT" ];then
        echo "Running custom script '$OP_TEST_PRETEST_CUSTOM_SCRIPT' ..."
        [ -f $OP_TEST_PRETEST_CUSTOM_SCRIPT ] || { echo "Custom script '$OP_TEST_PRETEST_CUSTOM_SCRIPT' was not found. Exiting ..."; exit 1; }
        [[ -x "$OP_TEST_PRETEST_CUSTOM_SCRIPT" ]] || { echo "Custom script '$OP_TEST_PRETEST_CUSTOM_SCRIPT' is not executable. Do 'chmod +x $OP_TEST_PRETEST_CUSTOM_SCRIPT' first !!! Exiting ..."; exit 1; }
        run $OP_TEST_PRETEST_CUSTOM_SCRIPT
        echo "Custom script '$OP_TEST_PRETEST_CUSTOM_SCRIPT' done ..."
    fi
    echo -e "[$t] Running test ..."
    [[ $OP_TEST_DEBUG -ge 3 ]] && echo "OP_TEST_EXEC_EXTRA=$OP_TEST_EXEC_EXTRA"
    $DRY_RUN_CMD $OP_TEST_CONTAINER_TOOL rm -f $OP_TEST_NAME > /dev/null 2>&1
    run $DRY_RUN_CMD $OP_TEST_CONTAINER_TOOL run -d --rm $OP_TEST_CONTAINER_OPT --name $OP_TEST_NAME $OP_TEST_CONAINER_RUN_DEFAULT_ARGS $OP_TEST_CONTAINER_RUN_EXTRA_ARGS $OP_TEST_IMAGE
    [[ $OP_TEST_RESET -eq 1 ]] && run $DRY_RUN_CMD $OP_TEST_CONTAINER_TOOL cp $HOME/.kube $OP_TEST_NAME:/root/
    set -e
    if [[ $1 == orange* ]] && [[ $OP_TEST_PROD -ge 1 ]] && [[ $OP_TEST_CI_YAML_ONLY -eq 0 ]] && [ "$OP_TEST_VERSION" = "sync" ];then
        echo "$OP_TEST_EXEC_BASE $OP_TEST_EXEC_EXTRA --tags index_check $OP_TEST_EXEC_USER_INDEX_CHECK"
        run $DRY_RUN_CMD $OP_TEST_CONTAINER_TOOL exec $OP_TEST_CONTAINER_OPT $OP_TEST_NAME /bin/bash -c "update-ca-trust && $OP_TEST_EXEC_BASE $OP_TEST_EXEC_EXTRA --tags index_check $OP_TEST_EXEC_USER_INDEX_CHECK"
        $DRY_RUN_CMD $OP_TEST_CONTAINER_TOOL exec $OP_TEST_CONTAINER_OPT $OP_TEST_NAME /bin/bash -c "ls $OP_TEST_UNCOMPLETE" > /dev/null 2>&1 || continue
        OP_TEST_EXEC_USER="$OP_TEST_EXEC_USER -e operators_config=$OP_TEST_UNCOMPLETE"
        [[ $OP_TEST_IIB_INSTALL -eq 1 ]] && iib_install 
    fi
 
    echo "$OP_TEST_EXEC_BASE $OP_TEST_EXEC_EXTRA $OP_TEST_EXEC_USER"
    run $DRY_RUN_CMD $OP_TEST_CONTAINER_TOOL exec $OP_TEST_CONTAINER_OPT $OP_TEST_NAME /bin/bash -c "update-ca-trust && $OP_TEST_EXEC_BASE $OP_TEST_EXEC_EXTRA $OP_TEST_EXEC_USER $OP_TEST_EXEC_USER_SECRETS"
    set +e
    echo -e "Test '$t' : [ OK ]\n"
done

echo "Done"

# For playbook developers
# OP_TEST_DEBUG=2 bash <(curl -sL https://raw.githubusercontent.com/operator-framework/operator-test-playbooks/master/upstream/test/test.sh) orange community-operators/aqua/5.3.0 https://github.com/operator-framework/community-operators master
# export CURLOPT_FRESH_CONNECT=true
