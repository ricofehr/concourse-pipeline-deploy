#!/bin/bash

set -e

[[ -z $CF_API ]] && echo "CF_API env variable is missing" && exit 1
[[ -z $CF_USER ]] && echo "CF_USER env variable is missing" && exit 1
[[ -z $CF_ORG ]] && echo "CF_ORG env variable is missing" && exit 1
[[ -z $CF_SPACE ]] && echo "CF_SPACE env variable is missing" && exit 1

if [[ -z $CF_SSOCODE ]] && [[ -z $CF_PASSWORD ]]; then
    echo "CF_SSOCODE env variable is missing" && exit 1
fi

[[ -z "$MICRONAME" ]] && exit 1

export TERM=${TERM:-dumb}
if [[ -z $CF_SSOCODE ]]; then
    cf login -a $CF_API -u $CF_USER -p $CF_PASSWORD -o $CF_ORG -s $CF_SPACE --skip-ssl-validation
else
    cf login -a $CF_API -u $CF_USER -o $CF_ORG -s $CF_SPACE --skip-ssl-validation --sso-passcode $CF_SSOCODE
fi

# Fix jar path
sed -i "s,build/libs,${PWD}/build-output," ${MICRONAME}/manifest.yml
cf bgd ${MICRONAME} -f ${MICRONAME}/manifest.yml
cd ${MICRONAME} && git checkout -- manifest.yml