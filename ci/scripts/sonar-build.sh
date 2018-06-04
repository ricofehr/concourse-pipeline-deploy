#!/bin/bash

set -e

[[ -z "$MICROSLIST" ]] && exit 1

export TERM=${TERM:-dumb}

for service in $MICROSLIST; do
    cd $service
    [[ ! -f gradlew ]] || ./gradlew --no-daemon clean assemble
    cd ..
    mkdir sonarqube-analysis-input/micros
    mkdir sonarqube-analysis-input/micros/$service
    cp -rf ${service}/build  sonarqube-analysis-input/micros/$service/
    cp -rf ${service}/src  sonarqube-analysis-input/micros/$service/
done

exit 0