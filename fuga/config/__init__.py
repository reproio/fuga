import json
import os
import copy

import yaml
import click

DEFAULT_CONFIG = {
    'cookiecutters_dir': os.path.expanduser('~/.cookiecutters')
}

_config = copy.deepcopy(DEFAULT_CONFIG)

if 'FUGA_HOME' in os.environ:
    _fuga_home = os.environ['FUGA_HOME']
else:
    _fuga_base_dir = os.path.expanduser('~')
    if not os.access(_fuga_base_dir, os.W_OK):
        _fuga_base_dir = '/tmp'
    _fuga_home = os.path.join(_fuga_base_dir, '.fuga')

if not os.path.exists(_fuga_home):
    os.makedirs(_fuga_home)

_config_path = os.path.expanduser(os.path.join(_fuga_home, 'config.yml'))

if os.path.exists(_config_path):
    try:
        with open(_config_path) as f:
            _config = yaml.load(f)
    except ValueError:
        _config = {}

if not os.path.exists(_config_path):
    _config = {
        'gcp_project_id': os.getenv('FUGA_GCP_PROJECT_ID'),
        'gcs_bucket_name': os.getenv('FUGA_GCS_BUCKET_NAME')}

    with open(_config_path, 'w') as f:
        f.write(yaml.dump(_config, default_flow_style=False))


def validate_config():
    if _config['gcp_project_id'] is None or \
            _config['gcs_bucket_name'] is None:
        import sys
        click.echo('''
Missing required GCP/GCS configurations.

You need to either run `fuga environment init` or set both
`FUGA_GCP_PROJECT_ID` and `FUGA_GCS_BUCKET_NAME` envvars.
        ''')
        sys.exit(1)


def get_config(name):
    env_name = 'FUGA_' + name.upper()
    # Prioritize env var over ~/.fuga/config.yml file
    # (It allows users to use multiple configurations)
    return os.getenv(
        env_name,
        _config.get(name, None))


def write_config(key, value):
    _config[key] = value

    with open(_config_path, 'w') as f:
        f.write(yaml.dump(_config, default_flow_style=False))
