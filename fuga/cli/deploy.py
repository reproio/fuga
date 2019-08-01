class DeployCommand:
    def __init__(self):
        pass

    def run(self):
        '''
        #!/usr/bin/env bash

        set -e

        gcloud composer environments storage dags import --project repro-lab --environment {{cookiecutter.composer_environment_name}} --location asia-northeast1 --source sql --destination {{cookiecutter.experiment_name}}
        gcloud composer environments storage dags import --project repro-lab --environment {{cookiecutter.composer_environment_name}} --location asia-northeast1 --source lib.py --destination {{cookiecutter.experiment_name}}
        gcloud composer environments storage dags import --project repro-lab --environment {{cookiecutter.composer_environment_name}} --location asia-northeast1 --source {{cookiecutter.experiment_name}}.py --destination {{cookiecutter.experiment_name}}
        '''
