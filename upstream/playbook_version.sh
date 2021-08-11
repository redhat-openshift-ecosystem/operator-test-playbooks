#!/bin/bash

VERSION="v$(date +%Y%m%d)"
if [ -n "$1" ];then
    # VERSION="${VERSION}_${1}"
    VERSION=$1
    TAG=$1
else
    TAG="latest"
fi

echo "VERSION=${VERSION}"
echo "::set-output name=image_version::${VERSION}"
echo "::set-output name=image_tag::${TAG}"
