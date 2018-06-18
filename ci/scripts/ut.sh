#!/bin/bash

set -e

export TERM=${TERM:-dumb}

[[ ! -f gradlew ]] || ./gradlew test

exit 0