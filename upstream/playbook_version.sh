#!/bin/bash

VERSION="v$(date +%Y%m%d)"
if [ "$1" = "upstream-community-dev" ];then
    # VERSION="${VERSION}_${1}"
    VERSION=dev
    TAG=dev
else
    TAG="latest"
fi

echo "VERSION=${VERSION}"
echo "::set-output name=image_version::${VERSION}"
echo "::set-output name=image_tag::${TAG}"
