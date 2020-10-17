#!/bin/bash
OP_TEST_IMAGE=${OP_TEST_IMAGE-"quay.io/operator_testing/operator-test-playbooks:latest"}
OP_TEST_CERT_DIR=${OP_TEST_CERT_DIR-"/tmp/certs"}
OP_TEST_CONTAINER_TOOL=${OP_TEST_CONTAINER_TOOL-"docker"}
OP_TEST_NAME=${OPT_TEST_NAME-"op-test"}
OP_TEST_ANSIBLE_PULL_REPO=${OP_TEST_ANSIBLE_PULL_REPO-"https://github.com/redhat-operator-ecosystem/operator-test-playbooks"}
OP_TEST_ANSIBLE_PULL_BRANCH=${OP_TEST_ANSIBLE_PULL_BRANCH-"upstream-community"}
OP_TEST_ANSIBLE_DEFAULT_ARGS=${OP_TEST_ANSIBLE_DEFAULT_ARGS-"-i localhost, -e ansible_connection=local -e run_upstream=true"}
OP_TEST_ANSIBLE_EXTRA_ARGS=${OP_TEST_ANSIBLE_EXTRA_ARGS-"--tags kubectl,kind"}
OP_TEST_CONAINER_RUN_DEFAULT_ARGS=${OP_TEST_CONAINER_RUN_DEFAULT_ARGS-"--net host --cap-add SYS_ADMIN --cap-add SYS_RESOURCE --security-opt seccomp=unconfined --security-opt label=disable -v $OP_TEST_CERT_DIR/domain.crt:/usr/share/pki/ca-trust-source/anchors/ca.crt -v /tmp/.kube:/root/.kube -e STORAGE_DRIVER=vfs"}
OP_TEST_CONTAINER_RUN_EXTRA_ARGS=${OP_TEST_CONTAINER_RUN_EXTRA_ARGS-""}
OP_TEST_CONTAINER_EXEC_DEFAULT_ARGS=${OP_TEST_CONTAINER_EXEC_DEFAULT_ARGS-""}
OP_TEST_CONTAINER_EXEC_EXTRA_ARGS=${OP_TEST_CONTAINER_EXEC_EXTRA_ARGS-""}
OP_TEST_EXEC_BASE=${OP_TEST_EXEC_BASE-"ansible-playbook -i localhost, -e ansible_connection=local local.yml -e run_upstream=true -e image_protocol='docker://' -vv"}
OP_TEST_EXEC_EXTRA=${OP_TEST_EXEC_EXTRA-""}
OP_TEST_DEBUG=${OP_TEST_DEBUG-0}
OP_TEST_FORCE_INSTALL=${OP_TEST_FORCE_INSTALL-0}

[ "$OP_TEST_RUN_MODE" = "privileged" ] && OP_TEST_CONAINER_RUN_DEFAULT_ARGS="--privileged --net host -v $OP_TEST_CERT_DIR/domain.crt:/usr/share/pki/ca-trust-source/anchors/ca.crt -v $HOME/.kube:/root/.kube -e STORAGE_DRIVER=vfs"


OP_TEST_EXEC_USER="-e operator_dir=/tmp/community-operators-for-catalog/upstream-community-operators/aqua -e operator_version=1.0.2 --tags pure_test"

if ! command -v ansible > /dev/null 2>&1; then
    echo "Error: Ansible is not installed. Please install it first !!!"
    echo "    e.g. : pip install ansible jmespath"
    exit 1
fi

if [ "$OP_TEST_CONTAINER_TOOL" = "podman" ];then
    OP_TEST_ANSIBLE_EXTRA_ARGS="$OP_TEST_ANSIBLE_EXTRA_ARGS -e opm_container_tool=podman -e container_tool=podman -e opm_container_tool_index="
    OP_TEST_EXEC_EXTRA="$OP_TEST_EXEC_EXTRA -e opm_container_tool=podman -e container_tool=podman -e opm_container_tool_index="
fi

if [ "$OP_TEST_CONTAINER_TOOL" = "docker" ];then
    OP_TEST_CONTAINER_TOOL="sudo docker"
fi

echo "Using $(ansible --version | head -n 1) ..."
echo "OP_TEST_EXEC_USER='$OP_TEST_EXEC_USER'"
echo "OP_TEST_DEBUG='$OP_TEST_DEBUG'"
if [[ $OP_TEST_DEBUG -eq 1 ]];then
    OP_TEST_EXEC_EXTRA="-vv $OP_TEST_EXEC_EXTRA"
    echo "OP_TEST_IMAGE='$OP_TEST_IMAGE'"
    echo "OP_TEST_CONTAINER_EXEC_EXTRA_ARGS='$OP_TEST_CONTAINER_EXEC_EXTRA_ARGS'"
    echo "OP_TEST_CERT_DIR='$OP_TEST_CERT_DIR'"
    echo "OP_TEST_CONTAINER_TOOL='$OP_TEST_CONTAINER_TOOL'"
    echo "OP_TEST_NAME='$OP_TEST_NAME'"
    echo "OP_TEST_ANSIBLE_PULL_REPO='$OP_TEST_ANSIBLE_PULL_REPO'"
    echo "OP_TEST_ANSIBLE_PULL_BRANCH='$OP_TEST_ANSIBLE_PULL_BRANCH'"
    echo "OP_TEST_ANSIBLE_DEFAULT_ARGS='$OP_TEST_ANSIBLE_DEFAULT_ARGS'"
    echo "OP_TEST_ANSIBLE_EXTRA_ARGS='$OP_TEST_ANSIBLE_EXTRA_ARGS'"
    echo "OP_TEST_CONAINER_RUN_DEFAULT_ARGS='$OP_TEST_CONTAINER_RUN_EXTRA_ARGS'"
    echo "OP_TEST_CONTAINER_RUN_EXTRA_ARGS='$OP_TEST_CONTAINER_RUN_EXTRA_ARGS'"
    echo "OP_TEST_CONTAINER_EXEC_DEFAULT_ARGS='$OP_TEST_CONTAINER_EXEC_EXTRA_ARGS'"
    echo "OP_TEST_CONTAINER_EXEC_EXTRA_ARGS='$OP_TEST_CONTAINER_EXEC_EXTRA_ARGS'"
fi

# Check if kind is installed
if ! command -v kind > /dev/null 2>&1; then
    OP_TEST_FORCE_INSTALL=1
fi

# Check if kind cluster is running
if ! command -v kind get clusters | grep operator-test > /dev/null 2>&1; then
    OP_TEST_FORCE_INSTALL=1
fi

# Install prerequisites (kind cluster)
[[ $OP_TEST_FORCE_INSTALL -eq 1 ]] && ansible-pull -U $OP_TEST_ANSIBLE_PULL_REPO -C $OP_TEST_ANSIBLE_PULL_BRANCH $OP_TEST_ANSIBLE_DEFAULT_ARGS $OP_TEST_ANSIBLE_EXTRA_ARGS

# Start container
$OP_TEST_CONTAINER_TOOL rm -f $OP_TEST_NAME > /dev/null 2>&1
$OP_TEST_CONTAINER_TOOL run -d --rm -it --name $OP_TEST_NAME $OP_TEST_CONAINER_RUN_DEFAULT_ARGS $OP_TEST_CONTAINER_RUN_EXTRA_ARGS $OP_TEST_IMAGE

# Exec test
$OP_TEST_CONTAINER_TOOL exec -it $OP_TEST_NAME /bin/bash -c "update-ca-trust && $OP_TEST_EXEC_BASE $OP_TEST_EXEC_EXTRA $OP_TEST_EXEC_USER"

# For playbook developers
# export OP_TEST_ANSIBLE_PULL_REPO="https://github.com/J0zi/operator-test-playbooks"
# OP_TEST_DEBUG=1 OP_TEST_ANSIBLE_PULL_REPO="https://github.com/J0zi/operator-test-playbooks" bash <(curl -s https://raw.githubusercontent.com/J0zi/operator-test-playbooks/upstream-community/test/test.sh)

