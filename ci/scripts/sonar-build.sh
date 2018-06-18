#!/bin/bash

set -e

export TERM=${TERM:-dumb}

MICROFOLDER="${PWD}"
[[ ! -f gradlew ]] || ./gradlew --no-daemon clean assemble
[[ ! -f gradlew ]] || ./gradlew --no-daemon test
[[ ! -f gradlew ]] || ./gradlew --no-daemon jacocoTestReport
cd ..
mkdir sonarqube-analysis-input/src
mkdir sonarqube-analysis-input/classes
mkdir sonarqube-analysis-input/lib
mkdir sonarqube-analysis-input/jacoco
touch sonarqube-analysis-input/jacoco/test.exec
[[ ! -d ${MICROFOLDER}/build/jacoco ]] || cp -rf ${MICROFOLDER}/build/jacoco/test.exec  sonarqube-analysis-input/jacoco/
[[ ! -d ${MICROFOLDER}/build/classes ]] || cp -rf ${MICROFOLDER}/build/classes/*  sonarqube-analysis-input/classes/
[[ ! -d ${MICROFOLDER}/lib ]] || cp -rf ${MICROFOLDER}/lib/*  sonarqube-analysis-input/lib/
[[ ! -d ${MICROFOLDER}/src ]] || cp -rf ${MICROFOLDER}/src/*  sonarqube-analysis-input/src/
mkdir -p sonarqube-analysis-input/src/main
mkdir -p sonarqube-analysis-input/src/test
exit 0