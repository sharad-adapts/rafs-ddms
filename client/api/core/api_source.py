from typing import Optional

from client.api_client import APIClient


class APIResource(APIClient):
    """Intermediate class for API resource methods."""

    def __init__(
        self,
        host: str,
        version: str,
        url_prefix: str,
        data_partition: str,
        token: str,
        resource_path: type,
    ) -> None:
        super().__init__(host, version, url_prefix, data_partition, token)
        self.resource_path = resource_path

    def post_record(self, body: list, **kwargs) -> dict:
        """
        :param body: record data
        :return: created record
        """
        return self.post(path=self.resource_path.POST, json=body, **kwargs).json()

    def get_record(
        self,
        record_id: str,
        version: Optional[str] = None,
        **kwargs,
    ) -> dict:
        """
        :param record_id: record id
        :param version: version
        :return: record data
        """
        params_dict = {"version": version}
        return self.get(
            path=self.resource_path.GET.format(record_id=record_id),
            params=params_dict,
            **kwargs,
        ).json()

    def get_record_versions(self, record_id: str, **kwargs) -> dict:
        """Get the versions of a record.

        :param record_id: The ID of the record to retrieve the versions for.
        :param kwargs: Additional keyword arguments.
        :return: The versions of the record.
        """
        return self.get(
            path=self.resource_path.GET_VERSIONS.format(record_id=record_id), **kwargs,
        ).json()

    def get_record_version(self, record_id: str, version: int, **kwargs) -> dict:
        """Get a specific version of a record.

        :param record_id: The ID of the record to retrieve.
        :param version: The version number of the record to retrieve.
        :param kwargs: Additional keyword arguments.
        :return: Requested record version.
        """
        return self.get(
            path=self.resource_path.GET_VERSION.format(record_id=record_id, version=version), **kwargs,
        ).json()

    def soft_delete_record(self, record_id: str, **kwargs) -> None:
        """Soft delete a record.

        :param record_id: The ID of the record to delete.
        :param kwargs: Additional keyword arguments.
        :return: None
        """
        self.delete(
            path=self.resource_path.DELETE.format(record_id=record_id), **kwargs,
        )
