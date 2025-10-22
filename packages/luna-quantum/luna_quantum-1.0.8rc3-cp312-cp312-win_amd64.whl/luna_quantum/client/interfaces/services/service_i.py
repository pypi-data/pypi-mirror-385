from abc import ABC, abstractmethod

from httpx import Client


class IService(ABC):
    """Interface for luna services."""

    @property
    @abstractmethod
    def client(self) -> Client:
        """
        Return the httpx client.

        Returns
        -------
        Client
            A httpx client.
        """

    @classmethod
    @abstractmethod
    def authenticate(cls, api_key: str) -> None:
        """
        Authenticate the client with the given API key.

        Parameters
        ----------
        api_key : str
            The API key used to authenticate the client.

        Returns
        -------
        None
            This method does not return any value.
        """

    @abstractmethod
    def is_same(
        self,
        api_key: str | None = None,
    ) -> bool:
        """
        Whether the service is created with the current environment variables.

        Parameters
        ----------
        api_key: str
            User's API key

        Returns
        -------
        bool:
            True if the service is created with the current environment variables.
            False otherwise.
        """
