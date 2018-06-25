#!/bin/bash

set -e

[[ -z $CF_API ]] && echo "CF_API env variable is missing" && exit 1
[[ -z $CF_USER ]] && echo "CF_USER env variable is missing" && exit 1
[[ -z $CF_ORG ]] && echo "CF_ORG env variable is missing" && exit 1
[[ -z $CF_SPACE ]] && echo "CF_SPACE env variable is missing" && exit 1

if [[ -z $CF_SSOCODE ]] && [[ -z $CF_PASSWORD ]]; then
    echo "CF_SSOCODE env variable is missing" && exit 1
fi

export TERM=${TERM:-dumb}
if [[ -z $CF_SSOCODE ]]; then
    cf login -a $CF_API -u $CF_USER -p $CF_PASSWORD -o $CF_ORG -s $CF_SPACE --skip-ssl-validation
else
    cf login -a $CF_API -u $CF_USER -o $CF_ORG -s $CF_SPACE --skip-ssl-validation --sso-passcode $CF_SSOCODE
fi

# Fix jar path
sed -i "s,build/libs,${PWD}/../build-output," manifest.yml

# Get app name
CF_APP="$(grep "name:" manifest.yml | sed "s;^.*name:;;" | tr -d ' ' | tr -d '\n')"

# Blue-green deploy
cf bgd $CF_APP -f manifest.yml

# Remove old app
cf delete -f -r "${CF_APP}-old"

# Revert jar path fix
git checkout -- manifest.yml