from .return_class import AbstractApiClass


class DatasetVersionLogs(AbstractApiClass):
    """
        Logs from dataset version.

        Args:
            client (ApiClient): An authenticated API Client instance
            logs (list[str]): List of logs from dataset version.
    """

    def __init__(self, client, logs=None):
        super().__init__(client, None)
        self.logs = logs
        self.deprecated_keys = {}

    def __repr__(self):
        repr_dict = {f'logs': repr(self.logs)}
        class_name = "DatasetVersionLogs"
        repr_str = ',\n  '.join([f'{key}={value}' for key, value in repr_dict.items(
        ) if getattr(self, key, None) is not None and key not in self.deprecated_keys])
        return f"{class_name}({repr_str})"

    def to_dict(self):
        """
        Get a dict representation of the parameters in this class

        Returns:
            dict: The dict value representation of the class parameters
        """
        resp = {'logs': self.logs}
        return {key: value for key, value in resp.items() if value is not None and key not in self.deprecated_keys}
