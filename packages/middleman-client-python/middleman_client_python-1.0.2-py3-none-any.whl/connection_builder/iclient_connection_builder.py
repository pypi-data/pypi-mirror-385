from abc import ABC, abstractmethod

class IClientConnectionBuilder(ABC):
    """Interface for building client connections."""

    @abstractmethod
    def with_host(self, host: str) -> 'IClientConnectionBuilder':
        """Set the host URL for the connection."""
        pass

    @abstractmethod
    def with_token(self, token: str) -> 'IClientConnectionBuilder':
        """Set the authentication token for the connection."""
        pass

    @abstractmethod
    def with_reconnect(self) -> 'IClientConnectionBuilder':
        """Enable automatic reconnection."""
        pass

    @abstractmethod
    def build(self):
        """Build and return the client connection."""
        pass
