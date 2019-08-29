"""Create / interact with Google Cloud Composer environments."""

import os


_API_ACCESS_ENDPOINT = "https://composer.googleapis.com"


class Environment:
    """A class representing an Environment on Cloud Composer.
    """

    '''(WIP)
    _DEFAULT_SOFTWARE_CONFIG_0_1 = {
        "imageVersion": 'composer-1.7.2-airflow-1.10.2',
        "airflowConfigOverrides": {},
        "pypiPackages": {},
        "envVariables": {},
        'pythonVersion': '3'}

    _DEFAULT_NODE_CONFIG_0_1 = {
        {
            "location": 'asia-northeast1',
            "machineType": string,
            "network": string,
            "subnetwork": string,
            "diskSizeGb": 100,
            "oauthScopes": [
            ],
            "serviceAccount": string,
            "tags": [
            ]
        }
    }
    '''

    def __init__(
            self,
            client=None,
            project=None,
            name=None,
            location=None,
            uuid=None,
            full_path=None):
        self.name = name
        self.full_path = full_path
        self.uuid = uuid
        self.project = project
        self.location = location
        self._client = client

        if self.name is None and self.full_path is None:
            raise ValueError('Both `name` and `full_path` are not set.')

        full_path_from_name = None
        if self.name is not None:
            if self.project is None or self.location is None:
                raise ValueError('`project` and `location` are required when initializing environment with its short name.')
            full_path_from_name = os.path.join(
                'projects',
                self.project.project_id,
                'locations',
                self.location,
                'environments',
                self.name)
            if self.full_path is None:
                self.full_path = full_path_from_name
            elif self.full_path != full_path_from_name:
                raise ValueError('Both `name` and `full_path` are given but not compatible (`name` = %s, `full_path` = %s)' % (self.name, self.full_path))

        else:
            self.name = os.path.basename(self.full_path)

    @property
    def id(self):
        '''Alias of uuid'''
        return self.uuid

    @classmethod
    def from_api_repr(cls, resource, client):
        environment = cls(
            full_path=resource['name'],
            uuid=resource['uuid'],
            client=client)
        environment.set_properties_from_api_repr(resource)
        return environment

    def set_properties_from_api_repr(self, resource):
        self.state = resource['state']
        self.config = resource['config']

    def __repr__(self):
        return "<Environment: %s>" % (self.name,)

    def reload(self, client=None):
        """API call:  reload the project via a ``GET`` request.
        """
        client = client or self._client

        resp = client._connection.api_request(
            method='GET',
            path='/' + self.full_path)  # clumsy but necessary
        self.set_properties_from_api_repr(resource=resp)

    '''(WIP)
    def create(self, client=None, project=None, location=None):
        """Creates current environment.
        """
        client = client or self._client
        project = project or client.project
        location = location or self.location

        if project is None:
            raise ValueError(
                "Client project not set:  pass an explicit project.")

        if location is None:
            raise ValueError(
                "Location not set:  pass an explicit location.")

        query_params = {"project": project}
        properties = {
            'name': self.full_path,
            'config': {
                'nodeCount': self.config.get(
                    'nodeCount', 3),
                'softwareConfig': self.config.get(
                    'sofwareConfig', Environment._DEFAULT_SOFTWARE_CONFIG_0_1),
                'nodeConfig': self.config.get(
                    'nodeConnfig', Environment._DEFAULT_NODE_CONFIG_0_1)
            },
            'labels': {}  # XXX: make it configurable
        }

        api_response = client._connection.api_request(
            method="POST",
            path="/projects/%s/locations/%s" % (
                self.project.project_id, self.location),
            query_params=query_params,
            data=properties,
            _target_object=self,
        )
        print(api_response)
        '''
