#!/bin/bash

set -e

export TERM=${TERM:-dumb}

[[ -f gradlew ]] || exit 0
./gradlew --no-daemon clean assemble
cp build/libs/*.jar  ../build-output/


exit 0