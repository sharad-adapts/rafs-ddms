from loguru import logger
from starlette import status

from client.api.settings import ApiClientSettings
from client.api_client import APIClient


class APIStorage(APIClient):
    """API storage service methods."""

    def __init__(self, data_partition: str, token: str) -> None:
        super().__init__(ApiClientSettings().service_host_storage, "", data_partition, token)

    def purge_record(self, record_id: str, **kwargs) -> None:
        """Method to delete record completely from storage service."""
        logger.info(f"Deleting a PVT record from Storage service with ID {record_id}")
        self.delete(path=f"/records/{record_id}", allowed_codes=[status.HTTP_204_NO_CONTENT], **kwargs)
