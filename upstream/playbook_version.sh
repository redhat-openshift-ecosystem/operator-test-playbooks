#!/bin/bash
export VERSION="v$(date +%Y%m%d)"
echo "VERSION=$VERSION"
echo "::set-output name=image_version::${VERSION}"