from loguru import logger

from client.api_client import APIClient


class APIStorage(APIClient):
    """API storage service methods."""

    def __init__(self, host: str, data_partition: str, token: str, url_prefix: str = "api/storage/v2") -> None:
        super().__init__(host, url_prefix, data_partition, token)

    def purge_record(self, record_id: str, **kwargs) -> None:
        """Method to delete record completely from storage service."""
        logger.info(f"Deleting a PVT record from Storage service with ID {record_id}")
        self.delete(path=f"/records/{record_id}", **kwargs)
