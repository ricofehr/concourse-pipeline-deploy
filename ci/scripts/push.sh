#!/bin/bash

set -e

[[ -z $CF_API ]] && echo "CF_API env variable is missing" && exit 1
[[ -z $CF_USER ]] && echo "CF_USER env variable is missing" && exit 1
[[ -z $CF_ORG ]] && echo "CF_ORG env variable is missing" && exit 1
[[ -z $CF_SPACE ]] && echo "CF_SPACE env variable is missing" && exit 1

# override buildpack
[[ -n $CF_BUILDPACK ]] && CF_BUILDPACK="-b $CF_BUILDPACK"


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
    sed -i "s,build/libs,${PWD}/build-output," ${service}/manifest.yml
    cf bgd ${service} -f ${service}/manifest.yml $CF_BUILDPACK
    sed -i "s,${PWD}/build-output,build/libs," ${service}/manifest.yml
done