#!/bin/bash

set -e

[[ -z "$MICROSLIST" ]] && exit 1

export TERM=${TERM:-dumb}

for service in $MICROSLIST; do
    cd $service
    [[ ! -f gradlew ]] || ./gradlew --no-daemon clean assemble
    cd ..
    cp -rf ${service}/build  sonarqube-analysis-input/
    cp -rf ${service}/src  sonarqube-analysis-input/
done

exit 0