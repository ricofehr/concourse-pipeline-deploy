#!/bin/bash

set -e

[[ -z "$MICROSLIST" ]] && exit 1

export TERM=${TERM:-dumb}

for service in $MICROSLIST; do
    cd $service
    [[ ! -f gradlew ]] || ./gradlew --no-daemon clean assemble
    cd ..
    cp ${service}/build/libs/${service}-*-SNAPSHOT.jar  build-output/
done

exit 0