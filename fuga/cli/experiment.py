import glob
import json
import os
import sys
import re
from urllib.parse import urlparse

import click

from google.cloud import storage
from fuga.utils import find_experiment_root_dir
from fuga.google.cloud import composer
from fuga.config import get_config
from fuga.experiment import Experiment
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


class ExperimentNewCommand:
    # XXX: Temporary location for templates
    DEFAULT_TEMPLATE_REPO = os.path.expanduser(
        '~/.cookiecutters/fuga-cookiecutter-experiment-default')

    def run(
            self,
            experiment_name,
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
        output_dir = output_dir or os.getcwd()
        extra_context = {
            'experiment_name': experiment_name
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


class ExperimentDeployCommand:
    _DEFAULT_IGNORE = ['.*/.git/.*']

    def run(self):
        experiment_root_dir = find_experiment_root_dir()
        experiment = Experiment.from_path(experiment_root_dir)
        storage_client = storage.Client()
        composer_client = composer.Client()
        environment = composer_client.get_environment(
            get_config('composer_environment_full_path'))

        if environment.state != 'RUNNING':
            raise Exception(
                'Composer environment %s is in invalid state %s.\n'
                'You need to wait until the environment is running '
                'or fix it if it\'s broken.' % (
                    environment.name,
                    environment.state))

        if not environment.config.get('dagGcsPrefix', None):
            raise Exception(
                'Missing dagGcsPrefix config with environment %s.\n'
                'The environment may be in an invalid state or '
                'failed to launch.' % (
                    environment.name))

        bucket_url = urlparse(environment.config['dagGcsPrefix'])
        bucket_name = bucket_url.netloc
        bucket_prefix = bucket_url.path[1:]  # omit slash
        bucket = storage_client.get_bucket(bucket_name)

        pairs = []
        for target in ['py', 'sql', 'pod_operators']:
            for local_path in glob.iglob(
                    os.path.join(experiment_root_dir, target, '**/*'),
                    recursive=True):
                if self._is_ignored(local_path):
                    continue
                remote_path = os.path.join(
                    bucket_prefix,
                    experiment.name,
                    local_path[len(experiment_root_dir) + 1:])
                pairs.append((local_path, remote_path))

        click.echo('''
Following files are going to uploaded to GCS bucket %s
''' % bucket_name)
        click.echo(
            '\n'.join(
                '\t%s to %s'
                % (l, r) for l, r in pairs))

        click.echo('')
        click.confirm('Do you want to conitnue?', abort=True)

        for l, r in pairs:
            new_blob = bucket.blob(r)
            new_blob.upload_from_filename(l)

    def _is_ignored(self, path):
        ignores = ExperimentDeployCommand._DEFAULT_IGNORE

        return any(
            re.match(ignore, path)
            for ignore in ignores)
