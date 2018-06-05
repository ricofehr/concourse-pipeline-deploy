# concourse-pipeline-deploy

Generate a concourse pipeline deployment yaml for a build & deploy one microservice onto cloudfoundry plateform

## How To

The python script generates two yaml in a dedicated subfolder into out/
- pipeline.yml: contains resources, jobs, and tasks for the build & deploy pipeline
- secret.yml: contains credentials for cf and sonar, ssh private key. This generation can be disabled (--nobuild-secret parameter)

The command has many options
```
python genpipeline.py -g <git_prefix> -d <deploy_repo> -a <cf_api> -u <cf_user> -p <cf_password> -o <cf_org> -s <cf_space> -t <cf_ssocode> -n <micro_name> --private-key <sshkey_file> --gd <git_deploy_prefix> --name <deploy_name> --branch <git_branch> --sonar <sonar_endpoint> --sonar-login <sonar_login>  --sonar-password <sonar_password> --nobuild-secret
```

Mandatory options
```
-d <deploy_repo>: name of the deploy repository (concourse-pipeline-deploy for this one)
-g <git_prefix>: git prefix for the microservice repo to deploy like http://gtihub.com/ricofehr
-n <micro_name>: microservice name to deploy
```

Mandatory options if secret generation is not disabled (--nobuild-secret for disable)
```
-a <cf_api>: cloudfoundry api url
-u <cf_user>: cloudfoundry username
-o <cf_org>: cloudfoundry organization
-s <cf_space>: cloudfoundry space
```

Either password or ssocode must be filled
```
-p <cf_password>: cloudfoundry password
-t <sso passcode>: cloudfoundry sso temporary passcode
```

Facultative options
```
--private-key <sshkey_file>: path to the private sshkey file used for git clone.
--gd <git_deploy_prefix>: git prefix for the deploy repo, https://github.com/ricofehr for this one. Default is same than git_prefix
--deploy-name <deploy_name>: name to identify the generated pipeline, default is "deploy_TIMESTAMP"
--sonar <sonar_endpoint>: sonar ip to reach. If not set, sonar analyse is disabled
--sonar-login <sonar_login>: sonarqube login. Default is admin
--sonar-password <sonar_password>: sonarqube password. Default is admin
--nobuild-secret: Dont generate secret.yml. But assume sonar job enabled and git resource used with sshkey.
```

An example
```
python genpipeline.py -g https://github.com/ricofehr -d concourse-pipeline-deploy -a https://api.local.pcfdev.io -u user -p pass -o pcfdev-org -s pcfdev-space -n springboot-sandbox --sonar http://192.168.1.10:9000/ --sonar-login admin --sonar-password admin
```

And for apply this pipeline into coucourse, got to the pipeline folder and launch fly as follow
```
cd out/deploy_TIMESTAMP
fly -t lite set-pipeline -p deploy_TIMESAMP -c pipeline.yml -l secret.yml
```