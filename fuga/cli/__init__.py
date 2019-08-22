import click

from fuga.cli.deploy import (
    DeployCommand)
from fuga.cli.environment import (
    EnvironmentInitCommand)
from fuga.cli.experiment import (
    ExperimentNewCommand,
    ExperimentDeployCommand)
from fuga.cli.pod_operator import (
    PodOperatorNewCommand,
    PodOperatorDeployCommand)
from fuga.cli.init import (
    InitCommand)


@click.group()
def main(args=None):
    """Console script for fuga."""
    pass
    '''
    click.echo("Replace this message by putting your code into "
               "fuga.cli.main")
    click.echo("See click documentation at http://click.pocoo.org/")
    '''


@main.command()
@click.argument('experiment_name')
def init(experiment_name):
    return InitCommand().run(
        experiment_name=experiment_name)


@main.group()
def pod_operator():
    print('pod_operator')


@pod_operator.command(name='new')
@click.argument('operator_name')
def pod_operator_generate(operator_name):
    return PodOperatorNewCommand().run(
        operator_name=operator_name)


@pod_operator.command(name='deploy')
@click.argument('operator_name')
def pod_operator_deploy(operator_name):
    return PodOperatorDeployCommand().run(
        operator_name=operator_name)


@main.command()
def deploy():
    return DeployCommand().run()


@main.group()
def environment():
    print('environment')


@environment.command(name='init')
def environment_init():
    return EnvironmentInitCommand().run()


@main.group()
def experiment():
    pass


@experiment.command(name='new')
@click.argument('experiment_name')
def experiment_new(experiment_name, *args, **kwargs):
    return ExperimentNewCommand().run(experiment_name, *args, **kwargs)


@experiment.command(name='deploy')
def experiment_deploy(*args, **kwargs):
    return ExperimentDeployCommand().run(*args, **kwargs)
