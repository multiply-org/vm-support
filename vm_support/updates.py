from pathlib import Path
from subprocess import call
import git
import os
import pkg_resources
import shutil
import yaml

MULTIPLY_DIR_NAME = '.multiply'
REPOS_FILE_NAME = 'repositories.yml'
PATH_TO_REQUIRED_REPOS_FILE = pkg_resources.resource_filename(__name__, 'required_repos.yml')


def _is_newer_than(latest_git_version: str, installed_version: str):
    git_version_array = latest_git_version[1:].split('.')
    installed_version_array = installed_version[1:].split('.')
    i = 0
    while i < len(git_version_array) and i < len(installed_version_array):
        if int(git_version_array[i]) > int(installed_version_array[i]):
            return True
        elif int(git_version_array[i]) < int(installed_version_array[i]):
            return False
        i += 1
    if len(git_version_array) > len(installed_version_array):
        return True
    elif len(git_version_array) < len(installed_version_array):
        return False


def _get_multiply_home_dir() -> str:
    home_dir = str(Path.home())
    multiply_home_dir = '{0}/{1}'.format(home_dir, MULTIPLY_DIR_NAME)
    if not os.path.exists(multiply_home_dir):
        os.mkdir(multiply_home_dir)
    return multiply_home_dir


def _install_repo(new_path: str, branch: str) -> str:
    cmd_git = git.cmd.Git(new_path)
    cmd_git.checkout(branch)
    latest_tag = cmd_git.tag().split('\n')[-1]
    cmd_git.checkout('tags/{}'.format(latest_tag), '-b', branch)
    os.chdir(new_path)
    call(["python", "setup.py", "develop"])
    return latest_tag


def update():
    multiply_home_dir = _get_multiply_home_dir()
    _update(multiply_home_dir)


def _update(default_dir: str):
    provided_repos_file = '{0}/{1}'.format(default_dir, REPOS_FILE_NAME)
    _update(default_dir, provided_repos_file)


def _update(default_dir: str, provided_repos_file: str):
    actual_repos = []
    with open(PATH_TO_REQUIRED_REPOS_FILE, 'r') as required_repos_stream:
        required_repos = yaml.safe_load(required_repos_stream)
        if not os.path.exists(provided_repos_file):
            repos_dict = {'default_software_dir': default_dir, 'repo_list': []}
            yaml.safe_dump(provided_repos_file, repos_dict)
        with open(provided_repos_file, 'r') as provided_repos_stream:
            provided_repos = yaml.safe_load(provided_repos_stream)
            default_software_dir = provided_repos['default_software_dir']
            if not os.path.exists(default_software_dir):
                default_software_dir = default_dir
            for required_repo in required_repos['repo_list']:
                corresponding_provided_repo = None
                for provided_repo in provided_repos['repo_list']:
                    if required_repo['name'] == provided_repo['name']:
                        corresponding_provided_repo = provided_repo
                        break
                if corresponding_provided_repo is None:
                    cmd_git = git.cmd.Git(default_software_dir)
                    cmd_git.clone(required_repo['path_on_github'])
                    repo_name = required_repo['path_on_github'].split('/')[-1][:-4]
                    new_path = '{0}\\{1}'.format(default_software_dir, repo_name)
                    branch = required_repo['branch']
                    tag = _install_repo(new_path, branch)
                    new_repo = {'name': required_repo['name'], 'path_on_disk': new_path,
                                'path_on_github': required_repo['path_on_github'], 'branch': branch,
                                'version': tag}
                    actual_repos.append(new_repo)
                else:
                    if not required_repo['path_on_github'] == corresponding_provided_repo['path_on_github']:
                        os.chdir(corresponding_provided_repo['path_on_disk'])
                        call(["python", "setup.py", "develop", "--uninstall"])
                        shutil.rmtree(corresponding_provided_repo['path_on_disk'])
                        base_path = os.pardir(corresponding_provided_repo['path_on_disk'])
                        old_repo_name = os.path.basename(os.path.normpath(corresponding_provided_repo['path_on_disk']))
                        cmd_git = git.cmd.Git(base_path)
                        cmd_git.clone(required_repo['path_on_github'], old_repo_name)
                        branch = required_repo['branch']
                        tag = _install_repo(corresponding_provided_repo['path_on_disk'], branch)
                        new_repo = {'name': required_repo['name'],
                                    'path_on_disk': corresponding_provided_repo['path_on_disk'],
                                    'path_on_github': required_repo['path_on_github'], 'branch': branch,
                                    'version': tag}
                        actual_repos.append(new_repo)
                    elif not required_repo['branch'] == corresponding_provided_repo['branch']:
                        os.chdir(corresponding_provided_repo['path_on_disk'])
                        latest_tag = _install_repo(corresponding_provided_repo['path_on_disk'], required_repo['branch'])
                        new_repo = {'name': required_repo['name'],
                                    'path_on_disk': corresponding_provided_repo['path_on_disk'],
                                    'path_on_github': required_repo['path_on_github'],
                                    'branch': required_repo['branch'], 'version': latest_tag}
                        actual_repos.append(new_repo)
                    else:
                        cmd_git = git.cmd.Git(corresponding_provided_repo['path_on_disk'])
                        latest_tag = cmd_git.tag().split('\n')[-1]
                        if _is_newer_than(latest_tag, corresponding_provided_repo['version']):
                            cmd_git.checkout('tags/{}'.format(latest_tag), corresponding_provided_repo['branch'])
                            os.chdir(corresponding_provided_repo['path_on_disk'])
                            call(["python", "setup.py", "develop"])
                        actual_repos.append(corresponding_provided_repo)
    updated_repos_dict = {'default_software_dir': default_software_dir, 'repo_list': actual_repos}
    yaml.safe_dump(provided_repos_file, updated_repos_dict)


def _clone_new_repo(base_dir: str, required_repo: dict) -> dict:
    cmd_git = git.cmd.Git(base_dir)
    cmd_git.clone(required_repo['path_on_github'])
    repo_name = required_repo['path_on_github'].split('/')[-1][:-4]
    new_path = '{0}\\{1}'.format(base_dir, repo_name)
    branch = required_repo['branch']
    tag = _install_repo(new_path, branch)
    return {'name': required_repo['name'], 'path_on_disk': new_path, 'path_on_github': required_repo['path_on_github'],
            'branch': branch, 'version': tag}