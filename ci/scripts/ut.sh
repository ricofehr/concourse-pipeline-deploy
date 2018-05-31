#!/bin/bash

set -e

[[ -z "$MICROSLIST" ]] && exit 1

export TERM=${TERM:-dumb}

for service in $MICROSLIST; do
    cd $service
    [[ ! -f gradlew ]] || ./gradlew test
    cd ..
done

exit 0