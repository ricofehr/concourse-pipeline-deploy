#!/bin/bash

set -e

[[ -z "$MICROSLIST" ]] && exit 1

export TERM=${TERM:-dumb}

for service in $MICROSLIST; do
    cd source-$service
    [[ ! -f gradlew ]] || ./gradlew test
    cd ..
    cp source-${service}/build/libs/${service}-*-SNAPSHOT.jar  build-output/
done

exit 0