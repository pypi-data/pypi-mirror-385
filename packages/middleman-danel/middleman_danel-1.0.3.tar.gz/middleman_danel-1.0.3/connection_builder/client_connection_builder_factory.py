from .client_connection_builder import ClientConnectionBuilder
from .iclient_connection_builder import IClientConnectionBuilder

class ClientConnectionBuilderFactory:
    """Factory for creating client connection builders."""

    @staticmethod
    def create() -> IClientConnectionBuilder:
        """Create a new client connection builder instance."""
        return ClientConnectionBuilder()
