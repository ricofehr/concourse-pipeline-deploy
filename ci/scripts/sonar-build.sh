#!/bin/bash

set -e

[[ -z "$MICRONAME" ]] && exit 1

export TERM=${TERM:-dumb}

cd $MICRONAME
[[ ! -f gradlew ]] || ./gradlew --no-daemon clean assemble
cd ..
mkdir sonarqube-analysis-input/src
mkdir sonarqube-analysis-input/classes
mkdir sonarqube-analysis-input/src/$MICRONAME
mkdir sonarqube-analysis-input/classes/$MICRONAME
[[ ! -d ${MICRONAME}/build/classes ]] || cp -rf ${MICRONAME}/build/classes/*  sonarqube-analysis-input/classes/$MICRONAME/
cp -rf ${MICRONAME}/src/*  sonarqube-analysis-input/src/$MICRONAME/

exit 0