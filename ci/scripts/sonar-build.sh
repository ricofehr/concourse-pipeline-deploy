#!/bin/bash

set -e

[[ -z "$MICRONAME" ]] && exit 1

export TERM=${TERM:-dumb}

cd $MICRONAME
[[ ! -f gradlew ]] || ./gradlew --no-daemon clean assemble
cd ..
mkdir sonarqube-analysis-input/src
mkdir sonarqube-analysis-input/classes
[[ ! -d ${MICRONAME}/build/classes ]] || cp -rf ${MICRONAME}/build/classes/*  sonarqube-analysis-input/classes/
cp -rf ${MICRONAME}/src/*  sonarqube-analysis-input/src/

exit 0