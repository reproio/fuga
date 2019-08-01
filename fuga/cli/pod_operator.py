import json
import os
import sys

import click

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


class PodOperatorNewCommand:
    # XXX: Temporary location for templates
    DEFAULT_TEMPLATE_REPO = os.path.expanduser(
        '~/.cookiecutters/fuga-pod-operator-tmp')

    def __init__(self):
        pass

    def find_experiment_root_dir(self, max_depth=4):
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
                self.find_experiment_root_dir(),
                'operators')

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
