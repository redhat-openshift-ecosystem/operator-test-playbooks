#!/bin/bash
OP_DEBUG=${OP_DEBUG-0}
OP_TOKEN=${OP_TOKEN-""}
CONTAINER_TOOL=${CONTAINER_TOOL-"docker"}
OP_RUN_IMAGE=${OP_RUN_IMAGE-"quay.io/operator_testing/operator-test-playbooks:latest"}
function DetectFromGit() {
  COMMIT=$(git --no-pager log -n1 --pretty=format:%h | tail -n 1)
  echo
  echo "Target commit $COMMIT"
  echo "git log"
  git --no-pager log --oneline|head
  echo
  echo "Source commit details:"
  git --no-pager log -m -1 --name-only --first-parent $COMMIT
  declare -A CHANGED_FILES
  ##community only
  echo "changed community files:"
  CHANGED_FILES=$(git --no-pager log -m -1 --name-only --first-parent $COMMIT|grep -v 'upstream-community-operators/'|grep 'community-operators/') || { echo '******* No community operator (Openshift) modified, no reason to continue *******'; exit 0; }
  echo
  for sf in ${CHANGED_FILES[@]}; do
  echo $sf
  if [ $(echo $sf| awk -F'/' '{print NF}') -ge 4 ]; then
    OP_NAME="$(echo "$sf" | awk -F'/' '{ print $2 }')"
    OP_VER="$(echo "$sf" | awk -F'/' '{ print $3 }')"
  fi
  done
  echo
  export OP_NAME
  export OP_VER
  export COMMIT
  export STREAM_NAME=community-operators
  echo "STREAM_NAME=$STREAM_NAME"
  echo "OP_NAME=$OP_NAME"
  echo "OP_VER=$OP_VER"
  echo "COMMIT=$COMMIT"

}
rm -rf community-operators
git clone $1
cd community-operators
git checkout $2
DetectFromGit

$CONTAINER_TOOL pull $OP_RUN_IMAGE
$CONTAINER_TOOL rm -f test
$CONTAINER_TOOL run -d --net=host --privileged -e STORAGE_DRIVER=vfs --rm -it --name test $OP_RUN_IMAGE

[ -z "$OP_NAME" ] && { echo "Error: Missing '\$OP_NAME'"; exit 1; }
[ -z "$OP_NAME" ] && { echo "Error: Missing '\$OP_NAME'"; exit 1; }
[ -z "$OP_VER" ] && { echo "Error: Missing '\$OP_VER'"; exit 1; }
[ -z "$COMMIT" ] && { echo "Error: Missing '\$COMMIT'"; exit 1; }
[ -z "$OP_TOKEN" ] && { echo "Error: Missing '\$OP_TOKEN'"; exit 1; }

$CONTAINER_TOOL exec -it \
-e OP_STREAM="$STREAM_NAME" \
-e OP_NAME="$OP_NAME" \
-e OP_VERSION="$OP_VER" \
-e OP_REPO="$1" \
-e OP_BRANCH="$2" \
-e OP_OSR_HASH="quay.io/operator_testing|$OP_TOKEN|$COMMIT" \
-e OP_DEBUG=$OP_DEBUG \
test /playbooks/test/osr_test.sh
