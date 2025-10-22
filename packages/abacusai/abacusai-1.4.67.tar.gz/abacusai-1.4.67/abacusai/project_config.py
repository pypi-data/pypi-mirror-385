from .api_class import ProjectFeatureGroupConfig
from .return_class import AbstractApiClass


class ProjectConfig(AbstractApiClass):
    """
        Project-specific config for a feature group

        Args:
            client (ApiClient): An authenticated API Client instance
            type (str): Type of project config
            config (ProjectFeatureGroupConfig): Project-specific config for this feature group
    """

    def __init__(self, client, type=None, config={}):
        super().__init__(client, None)
        self.type = type
        self.config = client._build_class(ProjectFeatureGroupConfig, config)
        self.deprecated_keys = {}

    def __repr__(self):
        repr_dict = {f'type': repr(self.type), f'config': repr(self.config)}
        class_name = "ProjectConfig"
        repr_str = ',\n  '.join([f'{key}={value}' for key, value in repr_dict.items(
        ) if getattr(self, key, None) is not None and key not in self.deprecated_keys])
        return f"{class_name}({repr_str})"

    def to_dict(self):
        """
        Get a dict representation of the parameters in this class

        Returns:
            dict: The dict value representation of the class parameters
        """
        resp = {'type': self.type,
                'config': self._get_attribute_as_dict(self.config)}
        return {key: value for key, value in resp.items() if value is not None and key not in self.deprecated_keys}
