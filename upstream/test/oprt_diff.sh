#!/bin/bash
set +o pipefail
OPRT_REPO=${OPRT_REPO-""}
OPRT_SHA=${OPRT_SHA-""}
OPRT_SRC_BRANCH=${OPRT_SRC_BRANCH-"master"}

[ -n "$OPRT_REPO" ] || { echo "Error: '\$OPRT_REPO' is empty !!!"; exit 1; }
[ -n "$OPRT_SHA" ] || { echo "Error: '\$OPRT_SHA' is empty !!!"; exit 1; }

git log --oneline | head

git config --global user.email "test@example.com"
git config --global user.name "Test User"

git remote add upstream https://github.com/operator-framework/community-operators -f
git pull --rebase upstream $OPRT_SRC_BRANCH        
ADDED=$(git diff --diff-filter=A upstream/$OPRT_SRC_BRANCH --name-only | tr '\r\n' ' ')
MODIFIED=$(git diff --diff-filter=M upstream/$OPRT_SRC_BRANCH --name-only | tr '\r\n' ' ')
REMOVED=$(git diff --diff-filter=D upstream/$OPRT_SRC_BRANCH --name-only | tr '\r\n' ' ')
RENAMED=$(git diff --diff-filter=R upstream/$OPRT_SRC_BRANCH --name-only | tr '\r\n' ' ')
echo "ADDED=$ADDED"
echo "MODIFIED=$MODIFIED"
echo "REMOVED=$REMOVED"
echo "RENAMED=$RENAMED"
echo "::set-output name=added::$ADDED"
echo "::set-output name=modified::$MODIFIED"
echo "::set-output name=removed::$REMOVED"
echo "::set-output name=renamed::$RENAMED"
