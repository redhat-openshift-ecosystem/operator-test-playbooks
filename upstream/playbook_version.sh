#!/bin/bash

VERSION="v$(date +%Y%m%d)"
if [ "$1" = "refs/heads/upstream-community" ];then
    TAG="latest"
elif [ "$1" = "refs/heads/upstream-community-dev" ];then
    TAG="latest"
    # VERSION="${VERSION}_${1}"
    VERSION=dev
    TAG=dev
else
    echo "Not supported branch: '$1'"
    exit 1
fi

echo "VERSION=${VERSION}"
echo "::set-output name=image_version::${VERSION}"
echo "::set-output name=image_tag::${TAG}"
