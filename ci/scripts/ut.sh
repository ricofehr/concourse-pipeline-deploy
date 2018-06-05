#!/bin/bash

set -e

[[ -z "$MICRONAME" ]] && exit 1

export TERM=${TERM:-dumb}


cd $MICRONAME
[[ ! -f gradlew ]] || ./gradlew test
cd ..

exit 0