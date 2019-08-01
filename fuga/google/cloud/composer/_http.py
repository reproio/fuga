"""Create / interact with Google Cloud Environment connections."""

from google.cloud import _http

from google.cloud.storage import __version__


class Connection(_http.JSONConnection):
    """A connection to Google Cloud Storage via the JSON REST API.

    :type client: :class:`~google.cloud.storage.client.Client`
    :param client: The client that owns the current connection.

    :type client_info: :class:`~google.api_core.client_info.ClientInfo`
    :param client_info: (Optional) instance used to generate user agent.
    """

    def __init__(self, client, client_info=None):
        super(Connection, self).__init__(client, client_info)

        self._client_info.gapic_version = __version__
        self._client_info.client_library_version = __version__

    API_BASE_URL = 'https://composer.googleapis.com'
    """The base of the API call URL."""

    API_VERSION = "v1"
    """The version of the API, used in building the API call's URL."""

    API_URL_TEMPLATE = "{api_base_url}/{api_version}{path}"
    """A template for the URL of a particular API call."""
