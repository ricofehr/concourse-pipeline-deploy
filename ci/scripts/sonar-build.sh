#!/bin/bash

set -e

[[ -z "$MICRONAME" ]] && exit 1

export TERM=${TERM:-dumb}

cd $MICRONAME
[[ ! -f gradlew ]] || ./gradlew --no-daemon clean assemble
[[ ! -f gradlew ]] || ./gradlew --no-daemon test
[[ ! -f gradlew ]] || ./gradlew --no-daemon jacocoTestReport
cd ..
mkdir sonarqube-analysis-input/src
mkdir sonarqube-analysis-input/classes
mkdir sonarqube-analysis-input/jacoco
touch sonarqube-analysis-input/jacoco/test.exec
[[ ! -d ${MICRONAME}/build/jacoco ]] || cp -rf ${MICRONAME}/build/jacoco/test.exec  sonarqube-analysis-input/jacoco/
[[ ! -d ${MICRONAME}/build/classes ]] || cp -rf ${MICRONAME}/build/classes/*  sonarqube-analysis-input/classes/
cp -rf ${MICRONAME}/src/*  sonarqube-analysis-input/src/
mkdir -p sonarqube-analysis-input/src/main
mkdir -p sonarqube-analysis-input/src/test
find sonarqube-analysis-input/
exit 0