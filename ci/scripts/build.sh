#!/bin/bash

set -e

[[ -z "$MICRONAME" ]] && exit 1

export TERM=${TERM:-dumb}


cd $MICRONAME
[[ ! -f gradlew ]] || ./gradlew --no-daemon clean assemble
cd ..
cp ${MICRONAME}/build/libs/${MICRONAME}-*.jar  build-output/


exit 0