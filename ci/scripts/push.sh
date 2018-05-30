#!/bin/bash

set -e

[[ -z $CF_API ]] && echo "CF_API env variable is missing" && exit 1
[[ -z $CF_USER ]] && echo "CF_USER env variable is missing" && exit 1
[[ -z $CF_ORG ]] && echo "CF_ORG env variable is missing" && exit 1
[[ -z $CF_SPACE ]] && echo "CF_SPACE env variable is missing" && exit 1

if [[ -z $CF_SSOCODE ]] && [[ -z $CF_PASSWORD ]]; then
    echo "CF_SSOCODE env variable is missing" && exit 1
fi

[[ -z "$MICROSLIST" ]] && exit 1

export TERM=${TERM:-dumb}
if [[ -z $CF_SSOCODE ]]; then
    cf login -a $CF_API -u $CF_USER -p $CF_PASSWORD -o $CF_ORG -s $CF_SPACE --skip-ssl-validation
else
    cf login -a $CF_API -u $CF_USER -o $CF_ORG -s $CF_SPACE --skip-ssl-validation --sso-passcode $CF_SSOCODE
fi

for service in $MICROSLIST; do
    sed -i "s,build/libs,build-output,;s,java_buildpack,java_buildpack_offline," source-${service}/manifest.yml
    cf bgd ${service} -f source-${service}/manifest.yml
    sed -i "s,build-output,build/libs,;s,java_buildpack_offline,java_buildpack," source-${service}/manifest.yml
done