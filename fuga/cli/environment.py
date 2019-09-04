import re

import click
from google.cloud import resource_manager, storage
from google.api_core.exceptions import Forbidden

from fuga.config import get_config, write_config
from fuga.google.cloud import composer


def _call_api_with_credentials_catch(f, *args, **kwargs):
    try:
        return f(*args, **kwargs)
    except Forbidden as e:
        click.echo('Fuga has encountered a credential related error during an api call to GCP.')
        click.echo('Please check your authentication settings. ')
        click.echo(
            'hint: an explicit credential (`GOOGLE_APPLICATION_CREDENTIALS`) would '
            'precedes one configured with gcloud.')
        click.echo('(Original error message: ' + e.message + ')')
        import sys
        sys.exit(1)


class EnvironmentInitCommand:
    _STORAGE_LOCATIONS = [
        'northamerica-northeast1',
        'us-central1',
        'us-east1',
        'us-east4',
        'us-west1',
        'us-west2',
        'southamerica-east1',
        'europe-north1',
        'europe-west1',
        'europe-west2',
        'europe-west3',
        'europe-west4',
        'europe-west6',
        'asia-east1',
        'asia-east2',
        'asia-northeast1',
        'asia-northeast2',
        'asia-south1',
        'asia-southeast1',
        'australia-southeast1']

    def __init__(self):
        pass

    def _setup_gcp_project(self):
        resource_manager_client = resource_manager.Client()
        projects = list(
            _call_api_with_credentials_catch(resource_manager_client.list_projects))

        if len(projects) > 0:
            # Let user choose a project to use
            msg = '''
Please choose a GCP project to use with fuga.

0 - Create new'''

            for i, p in enumerate(projects):
                msg += f'\n{i + 1} - {p.name} ({p.project_id})'
            msg += '\n'

            choice = click.prompt(msg, type=int, default=1)
            assert choice >= 0 and choice <= len(projects)

            if choice > 0:
                project = projects[choice - 1]  # 1-based
            else:
                project_name = click.prompt(
                    'Please name your new project.', type=str)
                project_id = click.prompt(
                    'Please choose a project id',
                    type=int,
                    default=re.sub(r'\s+', '_', project_name).lower())
                project = _call_api_with_credentials_catch(
                    resource_manager_client.new_project, project_id, name=project_name)
                project.create()
        else:
            # Ask user if he/she wants to create new GCP project
            if click.confirm("""
    There's no GCP project configured locally.
    Do you want to create one now OR abort?"""):
                # Create a new project
                project_name = click.prompt(
                    'Please name your new project.', type=str)
                project_id = click.prompt(
                    'Please choose a project id',
                    type=int,
                    default=re.sub(r'\s+', '_', project_name).lower())
                project = _call_api_with_credentials_catch(
                    resource_manager_client.new_project, project_id, name=project_name)
                project.create()
            else:
                import sys
                click.echo('aborting.')
                sys.exit(0)

        return project

    def _setup_gcs_bucket(self, project):
        storage_client = storage.Client()
        buckets_per_page = 10
        candidates = []
        bucket = None
        for candidate_bucket in _call_api_with_credentials_catch(
                storage_client.list_buckets):
            candidates.append(candidate_bucket)

            if len(candidates) >= buckets_per_page:
                # Let user choose a bucket to use
                msg = '''
Please choose a GCS bucket to use with fuga.

0 - Create new (recommended)'''

                for i, c in enumerate(candidates):
                    msg += f'\n{i + 1} - {c.name} ({c.id})'

                if i + 1 >= buckets_per_page:
                    msg += f'\n{i + 2} - Show next {buckets_per_page} buckets\n'

                choice = click.prompt(msg, type=int, default=1)
                assert choice >= 0 and choice <= len(candidates) + 1

                if choice > 0 and choice <= len(candidates):
                    bucket = candidates[choice - 1]  # 1-based
                    break
                elif choice == len(candidates) + 1:
                    # Next
                    candidates = []
                    continue
                else:  # choice == 0
                    bucket_name = click.prompt(
                        'Please name your new GCS bucket.', type=str)
                    bucket = storage.Bucket(
                        storage_client,
                        bucket_name)
                    msg = 'Prease choose a location for the bucket.'
                    for i, l in enumerate(
                            EnvironmentInitCommand._STORAGE_LOCATIONS):
                        msg += f'\n{i + 1} - {l}'
                    msg += '\n'

                    location_choice = click.prompt(
                        msg,
                        type=int,
                        default=1)
                    location = \
                        EnvironmentInitCommand._STORAGE_LOCATIONS[
                            location_choice - 1]
                    # XXX: bucket.storage_class = "COLDLINE"
                    bucket.create(
                        storage_client,
                        project=project.project_id,
                        location=location)
                    break

        if bucket is None and len(candidates) > 0:
            # Process remainder(s)
            msg = '''
Please choose a GCS bucket to use with fuga.

0 - Create new (recommended)'''

            for i, c in enumerate(candidates):
                msg += f'\n{i + 1} - {c.name} ({c.id})'
            msg += '\n'

            choice = click.prompt(msg, type=int, default=1)
            assert choice >= 0 and choice <= len(candidates)

            if choice > 0 and choice <= len(candidates):
                bucket = candidates[choice - 1]  # 1-based
            else:  # choice == 0
                bucket_name = click.prompt(
                    'Please name your new GCS bucket.', type=str)
                bucket = storage.Bucket(
                    storage_client,
                    bucket_name)
                msg = 'Prease choose a location for the bucket.'
                for i, l in enumerate(
                        EnvironmentInitCommand._STORAGE_LOCATIONS):
                    msg += f'\n{i + 1} - {l}'
                msg += '\n'

                location_choice = click.prompt(
                    msg,
                    type=int,
                    default=1)
                location = \
                    EnvironmentInitCommand._STORAGE_LOCATIONS[
                        location_choice - 1]
                # XXX: bucket.storage_class = "COLDLINE"
                # TODO: catch google exception conflict 409 errors
                bucket.create(
                    storage_client,
                    project=project.project_id,
                    location=location)
                click.echo(f'Created a bucket "{bucket_name}"')

        return bucket

    def _setup_composer_environment(self, project, location):
        environments_per_page = 10
        composer_client = composer.Client(project=project.project_id)

        environment = None
        candidates = []
        for candidate_environment in \
                _call_api_with_credentials_catch(composer_client.list_environments, location=location):
            candidates.append(candidate_environment)

            # XXX: Support creating environment
            if len(candidates) >= environments_per_page:
                # Let user choose a bucket to use
                msg = '''
Please choose a Cloud Composer Environment to use with fuga.

(Creating new Cloud Composer Environment is not supported with fuga at the moment. Until it's supported, please create the environment beforehand on your own.)

'''

                for i, c in enumerate(candidates):
                    msg += f'\n{i + 1} - {c.name} ({c.id})'

                if i + 1 >= environments_per_page:
                    msg += f'\n{i + 2} - Show next {environments_per_page} buckets\n'

                choice = click.prompt(msg, type=int, default=1)
                assert choice >= 1 and choice <= len(candidates) + 1

                if choice == len(candidates) + 1:
                    # Next
                    candidates = []
                    continue
                else:
                    environment = candidates[choice - 1]  # 1-based
                    break

        if environment is None and len(candidates) > 0:
            # Process remainder(s)
            msg = '''
Please choose a Cloud Composer Environment to use with fuga.

(Creating new Cloud Composer Environment is not supported with fuga at the moment. Until it's supported, please create the environment beforehand on your own.)

'''

            for i, c in enumerate(candidates):
                msg += f'\n{i + 1} - {c.name} ({c.id})'
            msg += '\n'

            choice = click.prompt(msg, type=int, default=1)
            assert choice >= 1 and choice <= len(candidates)

            if choice >= 1 and choice <= len(candidates):
                environment = candidates[choice - 1]  # 1-based

        return environment

    def run(self):
        config_overrides = {}
        if get_config('gcp_project_id'):
            resource_manager_client = resource_manager.Client()
            project = _call_api_with_credentials_catch(
                resource_manager_client.fetch_project,
                get_config('gcp_project_id'))
        else:
            project = self._setup_gcp_project()
            config_overrides['gcp_project_id'] = project.project_id

        if get_config('gcs_bucket_name'):
            storage_client = storage.Client(project=project.project_id)
            bucket = _call_api_with_credentials_catch(
                storage_client.get_bucket, get_config('gcs_bucket_name'))
        else:
            bucket = self._setup_gcs_bucket(project)
            config_overrides['gcs_bucket_name'] = bucket.name

        if get_config('composer_environment_full_path'):
            composer_client = composer.Client(project=project.project_id)
            environment = _call_api_with_credentials_catch(
                composer_client.get_environment, get_config('composer_environment_full_path'))
        else:
            environment = self._setup_composer_environment(
                project,
                location=bucket.location.lower())  # XXX: make it configurable
            config_overrides['composer_environment_full_path'] = \
                environment.full_path

        # Overwrite configurations
        for k, v in config_overrides.items():
            write_config(k, v)

        click.echo(
            'fuga environment is initialized. Now you can proceed to create '
            'environments by running `fuga experiment new`')
