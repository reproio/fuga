"""Client for interacting with the Google Cloud Composer API."""


from google.api_core import page_iterator
from google.cloud.client import ClientWithProject

from fuga.google.cloud.composer._http import Connection
from fuga.google.cloud.composer import Environment


_marker = object()


class Client(ClientWithProject):
    """Client to bundle configuration needed for API requests.
    """

    SCOPE = (
        "https://www.googleapis.com/auth/cloud-platform",
    )

    def __init__(
            self,
            project=None,
            credentials=None,
            _http=None,
            client_info=None):
        super(Client, self).__init__(
            project=project, credentials=credentials, _http=_http
        )
        self._base_connection = None
        self.project = project

        self._connection = Connection(self, client_info=client_info)

    def environment(self, environment_name):
        """Factory constructor for envirionment object.
        """
        return Environment(client=self, name=environment_name)

    def create_environment(self, environment_name, project=None):
        """API call: create a new environment via a POST request.
        """
        environment = Environment(client=self, name=environment_name)
        environment.create(client=self, project=project)
        return environment

    def list_environments(
            self,
            location,
            max_results=None,
            page_token=None,
            prefix=None,
            projection="noAcl",
            fields=None,
            project=None):
        """Get all environments in the project associated to the client.
        """
        if project is None:
            project = self.project

        if project is None:
            raise ValueError("Client project not set:  pass an explicit project.")

        return page_iterator.HTTPIterator(
            client=self,
            api_request=self._connection.api_request,
            path=f'/projects/{project}/locations/{location}/environments',
            items_key='environments',
            item_to_value=_item_to_environment,
            page_token=page_token,
            max_results=max_results)

    def get_environment(self, full_path):
        environment = Environment(client=self, full_path=full_path)
        environment.reload()
        return environment


def _item_to_environment(iterator, item):
    """Convert a JSON environment to the native object.
    """
    return Environment.from_api_repr(item, client=iterator.client)
