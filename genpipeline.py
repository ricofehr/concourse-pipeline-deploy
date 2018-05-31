import os
import sys
import optparse
import time

# easy_install jinja2
from jinja2 import Template

def fly_output(deploy_name):
    print("cd out/%s" % deploy_name)
    print("fly -t lite set-pipeline -p %s -c pipeline.yml -l secret.yml" % deploy_name)

def generate_secret(deploy_name, cf_api, cf_user, cf_password, cf_ssocode,
                    cf_org, cf_space, priv_key):
    with open('./templates/secret.yml.j2') as j2_file:
        template = Template(j2_file.read())
        with open('./out/%s/secret.yml' % deploy_name, 'w') as secret_file:
            secret_file.write(template.render(cf_api=cf_api,
                                              cf_user=cf_user,
                                              cf_password=cf_password,
                                              cf_ssocode=cf_ssocode,
                                              cf_org=cf_org,
                                              cf_space=cf_space,
                                              priv_key='        '.join(str(l) for l in priv_key)))
            secret_file.close()
        j2_file.close()

def generate_pipeline(deploy_name, micros_list, git_prefix, git_deploy_prefix, git_deploy_repo):
    # prepare jobs
    jobs = []

    job = {}
    job['name'] = 'unit-tests'
    # prepare tasks list
    job['tasks'] = []
    job['tasks'].append(get_task(deploy_name, "ut", micros_list, git_prefix))
    jobs.append(job)

    job = {}
    job['name'] = 'deploy'
    job['passed'] = 'unit-tests'
    # prepare tasks list
    job['tasks'] = []
    job['tasks'].append(get_task(deploy_name, "build", micros_list, git_prefix))
    job['tasks'].append(get_task(deploy_name, "push", micros_list, git_prefix))
    jobs.append(job)

    # write pipeline file
    with open('./templates/pipeline.yml.j2') as j2_file:
        template = Template(j2_file.read())
        with open('./out/%s/pipeline.yml' % deploy_name, 'w') as pipeline_file:
            pipeline_file.write(template.render(micros_list=micros_list,
                                                micros_list_str=' '.join(str(m) for m in micros_list),
                                                git_prefix=git_prefix,
                                                jobs=jobs,
                                                git_deploy_prefix=git_deploy_prefix,
                                                git_deploy_repo=git_deploy_repo))
            pipeline_file.close()
        j2_file.close()

def get_task(deploy_name, task_name, micros_list, git_prefix):
    with open('./templates/tasks/%s.yml.j2' % task_name) as j2_file:
        template = Template(j2_file.read())
        task = template.render(micros_list=micros_list, git_prefix=git_prefix)
        j2_file.close()
    return task

def prepare_pipeline(deploy_name):
    if os.path.exists("out/%s" % deploy_name):
        print("This deploy pipeline already exists")
        exit(0)

    try:
        os.makedirs("out/%s" % deploy_name)
    except Exception as e:
        print(e)
        exit(1)

# Parse cmd args, exit with error if mandatory field is missing
def parse_args():
    # Parse args
    parser = optparse.OptionParser('python %s -g <git_prefix> -k <sshkey_file>'
                                   ' --gd <git_deploy_prefix> -d <deploy_repo>'
                                   ' -a <cf_api> -u <cf_user> -o <cf_org>'
                                   ' -s <cf_space> -t <cf_ssocode>'
                                   ' -n <deploy_name> -m <services_list> -c'
                                   % sys.argv[0])
    parser.add_option('-g', dest='git_prefix', type='string',
                      help='git prefix like ssh://127.0.0.1:22/root, mandatory')
    parser.add_option('-k', dest='priv_key', type='string',
                      help='Ssh private key, default is ~/.ssh/id_rsa')
    parser.add_option('--gd', dest='git_deploy_prefix', type='string',
                      help='git prefix for deploy repo like ssh://127.0.0.1:22/root,'
                           ' default is same of git_prefix')
    parser.add_option('-d', dest='git_deploy_repo', type='string',
                      help='name of the deploy repo, mandatory')
    parser.add_option('-a', dest='cf_api', type='string',
                      help='CloudFoundry api url, mandatory field if gen secret')
    parser.add_option('-u', dest='cf_user', type='string',
                      help='CloudFoundry username, mandatory field if gen secret')
    parser.add_option('-p', dest='cf_password', type='string',
                      help='CloudFoundry password, not used if ssocode present')
    parser.add_option('-o', dest='cf_org', type='string',
                      help='CloudFoundry organization, mandatory field if gen secret')
    parser.add_option('-s', dest='cf_space', type='string',
                      help='CloudFoundry space, mandatory field if gen secret')
    parser.add_option('-t', dest='cf_ssocode', type='string',
                      help='CloudFoundry ssocode, default is empty')
    parser.add_option('-n', dest='deploy_name', type='string',
                      help='Deploy name, default is random generated')
    parser.add_option('-m', dest='micros_list', type='string',
                      help='microservices list, with a space delimitator, mandatory')
    parser.add_option("-c", action="store_false", dest="is_gen_secret", default=True,
                      help="don't generate secret file")
    (options, args) = parser.parse_args()

    # Ensure mandatory fields are present
    if (options.git_prefix == None) | \
       (options.git_deploy_repo == None) | \
       (options.micros_list == None):
        print(parser.usage)
        exit(1)


    if (options.is_gen_secret):
        if (options.cf_api == None) | \
           (options.cf_user == None) | \
           (options.cf_org == None) | \
           (options.cf_space == None):
            print(parser.usage)
            exit(1)

        if (options.cf_password == None) & (options.cf_ssocode == None):
            print(parser.usage)
            exit(1)

    if options.cf_password == None:
        options.cf_password = ''

    if options.cf_ssocode == None:
        options.cf_ssocode = ''

    # Set default values for missings args
    if (options.priv_key == None):
        options.priv_key = "~/.ssh/id_rsa"

    if not os.path.isfile(os.path.expanduser(options.priv_key)):
        print('No ssh key %s found !' % options.priv_key)
        print('Assumes that all git repositories are public')
    else:
        try:
            s = open(os.path.expanduser(options.priv_key), 'r')
            options.priv_key = s.readlines()
        except Exception as e:
            print(e)
            exit(1)

    if (options.deploy_name == None):
        options.deploy_name = 'deploy_%s' % int(time.time())

    if (options.git_deploy_prefix == None):
        options.git_deploy_prefix = options.git_prefix

    # Format micros_list
    options.micros_list = str(options.micros_list).split(',')

    return options

def main():
    params = parse_args()
    prepare_pipeline(params.deploy_name)
    if params.is_gen_secret:
        generate_secret(params.deploy_name, params.cf_api, params.cf_user,
                        params.cf_password, params.cf_ssocode, params.cf_org,
                        params.cf_space, params.priv_key)
    generate_pipeline(params.deploy_name, params.micros_list, params.git_prefix,
                      params.git_deploy_prefix, params.git_deploy_repo)
    fly_output(params.deploy_name)

if __name__ == '__main__':
    main()