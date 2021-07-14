#!/bin/bash
set +o pipefail

[[ ! $# -eq 2 ]] && { echo "$0 <index_tag> <operators comma separated>"; exit 1; }

OPM="/tmp/opm"
NAMESPACE=community-operators-pipeline
TOKEN=${TOKEN-""}
INDEX="quay.io/$NAMESPACE/catalog"
CONTAINER_TOOL=${CONTAINER_TOOL-podman}
export BUILDAH_FORMAT=docker
ECHO=""
# ECHO="echo"

echo "$INDEX"

if [ ! -f $OPM ];then
  curl -L https://github.com/operator-framework/operator-registry/releases/download/v1.17.3/linux-amd64-opm -o $OPM
  chmod +x $OPM
fi

echo "Login to quay.io"
$CONTAINER_TOOL login -u='$oauthtoken' -p=$TOKEN quay.io


for op in $(echo $2 | tr ',' '\n');do
  echo $op
  $ECHO curl -X DELETE -H "Authorization: Bearer ${TOKEN}" https://quay.io/api/v1/repository/$NAMESPACE/$op
done


for i in $(echo $1 | tr ',' '\n');do
  $ECHO $OPM index rm -o $2 -f $INDEX:$i -t $INDEX:$i -c $CONTAINER_TOOL
  $ECHO $CONTAINER_TOOL push $INDEX:$i
  $ECHO $OPM index rm -o $2 -f $INDEX:${i}s -t $INDEX:${i}s -c $CONTAINER_TOOL
  $ECHO $CONTAINER_TOOL push $INDEX:${i}s
done
