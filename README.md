# concourse-pipeline-deploy

Generate a concourse pipeline deployment yaml for a build & deploy onto cloudfoundry plateform

## How To

The python script generates two yaml in a dedicated subfolder into out/
- pipeline.yml: contains resources, jobs, and tasks for the build & deploy pipeline
- secret.yml: contains credentials, private key, and microservices list

The command has many options
```
python genpipeline.py -g <git_prefix> -k <sshkey_file> --gd <git_deploy_prefix> -d <deploy_repo> -a <cf_api> -u <cf_user> -o <cf_org> -s <cf_space> -t <cf_ssocode> -n <deploy_name> -m <services_list>
```

Mandatory options
```
-g <git_prefix>: git prefix for the repos to deploy like http://gtihub.com/toto. We assume that all microservices are the same git prefix path.
-d <deploy_repo>: name of the deploy repository (concourse-pipeline-deploy for this one)
-a <cf_api>: cloudfoundry api url
-u <cf_user>: cloudfoundry username
-o <cf_org>: cloudfoundry organization
-s <cf_space>: cloudfoundry space
-m <services_list>: list of microservices repository name to deploy
```

Either password or ssocode must be filled
```
-p <cf_password>: cloudfoundry password
-t <sso passcode>: cloudfoundry sso temporary passcode
```

Facultative options
```
-k <sshkey_file>: path to the private sshkey file used for git clone. Default is ~/.ssh/id_rsa
--gd <git_deploy_prefix>: git prefix for the deploy repo, https://github.com/ricofehr for this one. Default is same than git_prefix
-n <deploy_name>: name to identify the generated pipeline, default is "deploy_TIMESTAMP"
```

An example
```
python genpipeline.py -g https://github.com/ricofehr -d concourse-pipeline-deploy -a https://api.local.pcfdev.io -u user -p pass -o pcfdev-org -s pcfdev-space -m spring-micro1,spring-micro2,spring-micro3
```

And for apply this pipeline into coucourse, got to the pipeline folder and launch fly as follow
```
cd out/deploy_TIMESTAMP
fly -t lite set-pipeline -p deploy_TIMESAMP -c pipeline.yml -l secret.yml
```
