import click
import os

import git

from fuga.config import get_config


_FUGA_GITHUB_ORG_NAME = 'ayemos'  # XXX: temporary
_FUGA_DEFAULT_TEMPLATE_NAME = 'fuga-experiment-tmp'


def find_experiment_root_dir(max_depth=4):
    cur = os.getcwd()
    depth = 0

    while True:
        if 'fuga.yml' in os.listdir(cur):
            return cur

        if depth >= max_depth:
            raise Exception(
                'Current directry might not be a valid fuga experiment'
                'Could not find any valid fuga configuration files '
                '(`fuga.yml`) within working directory and its '
                'ancestors')
        depth += max_depth
        cur = os.path.dirname(cur)


def find_cookiecutter_template(template_name):
    pass


def find_or_clone_cookiecutter_template(template_name=_FUGA_DEFAULT_TEMPLATE_NAME):
    template = find_cookiecutter_template(template_name)
    if template is not None:
        return template

    click.confirm(
        'Could not find fuga experiment template with name %s.\n'
        'Do you want to clone it?', abort=True)

    local_git_dir = os.path.join(get_config('cookiecutters_dir'), template_name)
    remote_git_repo_name = f'git://github.com.org/{_FUGA_GITHUB_ORG_NAME}/{template_name}.git'
    git.Git(local_git_dir).clone(remote_git_repo_name)
