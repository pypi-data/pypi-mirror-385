from .iclient_connection_builder import IClientConnectionBuilder
from .exceptions import InvalidClientOptionsException

class ClientConnectionBuilder(IClientConnectionBuilder):
    """Implementation of the client connection builder."""

    def __init__(self):
        self._host = "ws://localhost:8080"
        self._token = ""
        self._reconnect = False

    def with_host(self, host: str) -> 'ClientConnectionBuilder':
        """Set the host URL for the connection."""
        self._host = host
        return self

    def with_token(self, token: str) -> 'ClientConnectionBuilder':
        """Set the authentication token for the connection."""
        self._token = token
        return self

    def with_reconnect(self) -> 'ClientConnectionBuilder':
        """Enable automatic reconnection."""
        self._reconnect = True
        return self

    def build(self) -> 'ClientConnection':
        """Build and return the client connection."""
        # Import here to avoid circular import issues
        from client_connection import ClientConnection

        if not self._host or self._host.isspace():
            raise InvalidClientOptionsException("Host cannot be null or empty")

        # Create headers with authorization token
        headers = {}
        if self._token:
            headers["Authorization"] = f"Bearer {self._token}"

        return ClientConnection(self._host, headers, self._reconnect)
