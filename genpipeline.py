import os
import sys
import optparse
import time

# easy_install jinja2
from jinja2 import Template

def fly_output(deploy_name):
    print("cd out/%s" % deploy_name)
    print("fly -t lite set-pipeline -p %s -c pipeline.yml -l secret.yml" % deploy_name)

def generate_secret(deploy_name, cf, priv_key, sonar):
    # format priv_key
    if priv_key != '':
        priv_key = '        '.join(str(l) for l in priv_key)
        priv_key = '        ' + priv_key
    # write secret file
    with open('./templates/secret.yml.j2') as j2_file:
        template = Template(j2_file.read())
        with open('./out/%s/secret.yml' % deploy_name, 'w') as secret_file:
            secret_file.write(template.render(cf_api=cf['cf_api'],
                                              cf_user=cf['cf_user'],
                                              cf_password=cf['cf_password'],
                                              cf_ssocode=cf['cf_ssocode'],
                                              cf_org=cf['cf_org'],
                                              cf_space=cf['cf_space'],
                                              priv_key=priv_key,
                                              sonar_url=sonar['sonar_url'],
                                              sonar_login=sonar['sonar_login'],
                                              sonar_password=sonar['sonar_password']))
            secret_file.close()
        j2_file.close()

def generate_pipeline(micro, git, sonar):
    # local vars
    deploy_name = micro['deploy_name']
    micro_name = micro['name']
    is_gen_secret = micro['is_gen_secret']
    git_prefix = git['git_prefix']
    git_deploy_prefix = git['git_deploy_prefix']
    git_deploy_repo = git['git_deploy_repo']
    git_branch = git['git_branch']

    # Assume that if secret already present (gen_secret false),
    # we have sonar enabled and ssh key
    is_priv_key = True
    if (is_gen_secret == True) & (git['git_ssh_key'] == ''):
        is_priv_key = False
    is_sonar = True
    if (is_gen_secret == True) & (sonar == ''):
        is_sonar = False

    # prepare jobs
    jobs = []

    job = {}
    job['name'] = 'unit-tests'
    # prepare tasks list
    job['tasks'] = []
    job['tasks'].append(get_task(deploy_name, "ut", micro_name, git_prefix))
    jobs.append(job)

    if sonar != '':
        job = {}
        job['name'] = 'sonar-check'
        job['passed'] = 'unit-tests'
        # prepare tasks list
        job['tasks'] = []
        job['tasks'].append(get_task(deploy_name, "sonar-build", micro_name, git_prefix))
        job['tasks'].append(get_task(deploy_name, "sonar-put-code", micro_name, git_prefix))
        job['tasks'].append(get_task(deploy_name, "sonar-gate", micro_name, git_prefix))
        jobs.append(job)

    job = {}
    job['name'] = 'deploy'
    if sonar != '':
        job['passed'] = 'sonar-check'
    else:
        job['passed'] = 'unit-tests'
    # prepare tasks list
    job['tasks'] = []
    job['tasks'].append(get_task(deploy_name, "build", micro_name, git_prefix))
    job['tasks'].append(get_task(deploy_name, "push", micro_name, git_prefix))
    jobs.append(job)

    # write pipeline file
    with open('./templates/pipeline.yml.j2') as j2_file:
        template = Template(j2_file.read())
        with open('./out/%s/pipeline.yml' % deploy_name, 'w') as pipeline_file:
            pipeline_file.write(template.render(micro_name=micro_name,
                                                git_prefix=git_prefix,
                                                jobs=jobs,
                                                git_deploy_prefix=git_deploy_prefix,
                                                git_deploy_repo=git_deploy_repo,
                                                branch=git_branch,
                                                is_sonar=is_sonar,
                                                is_priv_key=is_priv_key))
            pipeline_file.close()
        j2_file.close()

def get_task(deploy_name, task_name, micro_name, git_prefix):
    task = {}
    with open('./templates/tasks/%s.yml.j2' % task_name) as j2_file:
        template = Template(j2_file.read())
        task = template.render(micro_name=micro_name,
                               git_prefix=git_prefix, deploy_key=deploy_name)
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
    params = {}
    # Parse args
    parser = optparse.OptionParser('python %s -g <git_prefix> -d <deploy_repo>'
                                   ' -a <cf_api> -u <cf_user> -p <cf_password>'
                                   ' -o <cf_org> -s <cf_space> -t <cf_ssocode>'
                                   ' -n <micro_name>'
                                   ' --private-key <sshkey_file> --gd <git_deploy_prefix>'
                                   ' --deploy-name <deploy_name> --branch <git_branch>'
                                   ' --sonar <sonar_endpoint> --sonar-login <sonar_login>'
                                   '  --sonar-password <sonar_password> --nobuild-secret'
                                   % sys.argv[0])
    parser.add_option('-g', dest='git_prefix', type='string',
                      help='git prefix like ssh://127.0.0.1:22/root, mandatory')
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
    parser.add_option('-n', dest='micro_name', type='string',
                      help='microservice name, mandatory')
    parser.add_option('--private-key', dest='priv_key', type='string',
                      help='Ssh private key, default is ~/.ssh/id_rsa')
    parser.add_option('--gd', dest='git_deploy_prefix', type='string',
                      help='git prefix for deploy repo like ssh://127.0.0.1:22/root,'
                           ' default is same of git_prefix')
    parser.add_option('--deploy-name', dest='deploy_name', type='string',
                      help='Deploy name, default is random generated')
    parser.add_option('--branch', dest='git_branch', type='string',
                      help='Specify git branch to deploy, default is master')
    parser.add_option('--sonar', dest='sonar', type='string',
                      help='Sonarqube http://ip:port/. If present, enable the sonar job.')
    parser.add_option('--sonar-login', dest='sonar_login', type='string',
                      help='Sonarqube login. Default is admin')
    parser.add_option('--sonar-password', dest='sonar_password', type='string',
                      help='Sonarqube password. Default is admin')
    parser.add_option("--nobuild-secret", action="store_false", dest="is_gen_secret", default=True,
                      help="don't generate secret file")
    (options, args) = parser.parse_args()

    # Ensure mandatory fields are present
    if (options.git_prefix == None) | \
       (options.git_deploy_repo == None) | \
       (options.micro_name == None):
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

    if options.git_branch == None:
        options.git_branch = 'master'

    if options.sonar == None:
        options.sonar = ''

    if options.sonar_login == None:
        options.sonar_login = 'admin'

    if options.sonar_password == None:
        options.sonar_password = 'admin'

    # Set default values for missings args
    if options.priv_key == None or \
       not os.path.isfile(os.path.expanduser(options.priv_key)):
        options.priv_key = ''
        print('No ssh key %s found !' % options.priv_key)
        print('Assumes that all git repositories are public')
    else:
        try:
            s = open(os.path.expanduser(options.priv_key), 'r')
            options.priv_key = s.readlines()
        except Exception as e:
            print(e)
            exit(1)

    if options.deploy_name == None:
        options.deploy_name = 'deploy_%s' % int(time.time())

    if options.git_deploy_prefix == None:
        options.git_deploy_prefix = options.git_prefix

    params['git'] = {}
    params['git']['git_prefix'] = options.git_prefix
    params['git']['git_deploy_repo'] = options.git_deploy_repo
    params['git']['git_deploy_prefix'] = options.git_deploy_prefix
    params['git']['git_ssh_key'] = options.priv_key
    params['git']['git_branch'] = options.git_branch

    params['cf'] = {}
    params['cf']['cf_api'] = options.cf_api
    params['cf']['cf_user'] = options.cf_user
    params['cf']['cf_password'] = options.cf_password
    params['cf']['cf_ssocode'] = options.cf_ssocode
    params['cf']['cf_org'] = options.cf_org
    params['cf']['cf_space'] = options.cf_space

    params['sonar'] = {}
    params['sonar']['sonar_url'] = options.sonar
    params['sonar']['sonar_login'] = options.sonar_login
    params['sonar']['sonar_password'] = options.sonar_password

    params['micro'] = {}
    params['micro']['is_gen_secret'] = options.is_gen_secret
    params['micro']['deploy_name'] = options.deploy_name
    params['micro']['name'] = options.micro_name

    return params

def main():
    # Get input parameters
    params = parse_args()
    cf = params['cf']
    micro = params['micro']
    git = params['git']
    sonar = params['sonar']

    # Generate secret, tasks and pipelines
    prepare_pipeline(micro['deploy_name'])
    if micro['is_gen_secret']:
        generate_secret(micro['deploy_name'], cf, git['git_ssh_key'], sonar)
    generate_pipeline(micro, git, sonar['sonar_url'])
    fly_output(micro['deploy_name'])

if __name__ == '__main__':
    main()