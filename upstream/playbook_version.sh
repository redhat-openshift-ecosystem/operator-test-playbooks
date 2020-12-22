#!/bin/bash
export VERSION="v$(date +%Y%m%d)"

echo "VERSION=$VERSION"

echo "::set-env name=VERSION::$VERSION"