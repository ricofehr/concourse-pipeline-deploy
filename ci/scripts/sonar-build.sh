#!/bin/bash

set -e

[[ -z "$MICROSLIST" ]] && exit 1

export TERM=${TERM:-dumb}

for service in $MICROSLIST; do
    cd $service
    [[ ! -f gradlew ]] || ./gradlew --no-daemon clean assemble
    cd ..
    mkdir sonarqube-analysis-input/src
    mkdir sonarqube-analysis-input/classes
    mkdir sonarqube-analysis-input/src/$service
    mkdir sonarqube-analysis-input/classes/$service
    cp -rf ${service}/build/classes/*  sonarqube-analysis-input/classes/$service/
    cp -rf ${service}/src/*  sonarqube-analysis-input/src/$service/
done

ls -all
find sonarqube-analysis-input/.

exit 0