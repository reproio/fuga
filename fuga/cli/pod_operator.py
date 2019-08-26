import json
import os
import sys

import click

from git import Repo
from git.exc import InvalidGitRepositoryError

from cookiecutter.main import cookiecutter
from cookiecutter.exceptions import (
    OutputDirExistsException,
    InvalidModeException,
    FailedHookException,
    UndefinedVariableInTemplate,
    UnknownExtension,
    InvalidZipRepository,
    RepositoryNotFound,
    RepositoryCloneFailed
)

from fuga.utils import find_experiment_root_dir
from fuga.experiment import Experiment
from fuga.config import get_config

OPERATOR_DIR_PREFIX = os.getenv('FUGA_OPERATOR_DIR_PREFIX', 'operators')
DEFAULT_REMOTE_CONTAINER_REPO_HOST = 'gcr.io'


class PodOperatorNewCommand:
    # XXX: Temporary location for templates
    DEFAULT_TEMPLATE_REPO = os.path.expanduser(
        '~/.cookiecutters/fuga-cookiecutter-pod-operator-default')

    def __init__(self):
        pass

    def run(self,
            operator_name,
            template=DEFAULT_TEMPLATE_REPO,
            checkout=None,
            no_input=True,
            output_dir=None,
            extra_context=None,
            replay=False,
            overwrite_if_exists=False,
            config_file=None,
            default_config=False,
            password=None):
        output_dir = output_dir \
            or os.path.join(
                find_experiment_root_dir(),
                OPERATOR_DIR_PREFIX)

        extra_context = {
            'operator_name': operator_name
        }

        # powering cookiecutter to generate experiment from templates
        try:
            cookiecutter(
                template,
                checkout,
                no_input=no_input,
                extra_context=extra_context,
                replay=replay,
                overwrite_if_exists=overwrite_if_exists,
                output_dir=output_dir,
                config_file=config_file,
                default_config=default_config,
                password=os.environ.get('COOKIECUTTER_REPO_PASSWORD')
            )
        except (OutputDirExistsException,
                InvalidModeException,
                FailedHookException,
                UnknownExtension,
                InvalidZipRepository,
                RepositoryNotFound,
                RepositoryCloneFailed) as e:
            click.echo(e)
            sys.exit(1)
        except UndefinedVariableInTemplate as undefined_err:
            click.echo('{}'.format(undefined_err.message))
            click.echo('Error message: {}'.format(undefined_err.error.message))

            context_str = json.dumps(
                undefined_err.context,
                indent=4,
                sort_keys=True
            )
            click.echo('Context: {}'.format(context_str))
            sys.exit(1)


class PodOperatorDeployCommand:
    def run(
            self,
            operator_name,
            dockerfile='./Dockerfile',
            image_name=None,
            version_tag=None,
            dryrun=False,
            remote_container_repo=None):
        import docker
        client = docker.from_env()
        experiment = Experiment.from_path(find_experiment_root_dir())

        build_path = os.path.join(
            experiment.root_path,
            OPERATOR_DIR_PREFIX,
            operator_name)
        if not os.path.isdir(build_path):
            raise Exception(f'{build_path} is not a directory')

        try:
            repo = Repo(find_experiment_root_dir())
            if len(repo.head.commit.diff(None)) > 0 \
                    or len(repo.untracked_files) > 0:
                import sys
                click.echo(
                    'Current Git working tree has either '
                    'untracked file or diff to HEAD. '
                    'Please commit your changes/new files before '
                    'any deployment.')
                sys.exit(0)
            version_hash = repo.head.commit.hexsha
        except InvalidGitRepositoryError:
            raise Exception(
                f'Experiment directory ({experiment.root_path}) needs to '
                'be a valid Git repository.\n'
                'Run `git init` in your experiment root')
        except ValueError as e:
            raise Exception(
                f'ValueError ({e}) has occured.\n'
                'Current Git repository might not have any commit.')

        image_name = image_name or f'{experiment.name}__{operator_name}'
        version_tag = version_tag or version_hash
        click.echo(f'Building docker image {image_name}:{version_tag}')
        image, _logs = client.images.build(
            path=build_path,
            dockerfile=dockerfile,
            tag=f'{image_name}:{version_tag}')
        click.echo('Done')

        remote_container_repo = remote_container_repo or \
            os.path.join(
                DEFAULT_REMOTE_CONTAINER_REPO_HOST,
                get_config('gcp_project_id'))
        remote_tag = os.path.join(
            remote_container_repo,
            f'{image_name}:{version_tag}')
        image.tag(remote_tag)
        latest_tag = os.path.join(
            remote_container_repo,
            f'{image_name}:LATEST')
        image.tag(latest_tag)
        click.echo(f'Pushing images to {remote_container_repo}')
        click.echo('\t' + remote_tag)
        click.echo('\t' + latest_tag)
        client.images.push(remote_tag)
        client.images.push(latest_tag)
        click.echo('Done')
