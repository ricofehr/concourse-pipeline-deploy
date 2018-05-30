#!/bin/bash

set -e -x

[[ -z "$MICROSLIST" ]] && exit 1

export TERM=${TERM:-dumb}

for service in $MICROSLIST; do
    cd source-$service
    ./gradlew --no-daemon clean assemble
    cd ..
    cp source-${service}/build/libs/${service}-*-SNAPSHOT.jar  build-output/
done

exit 0