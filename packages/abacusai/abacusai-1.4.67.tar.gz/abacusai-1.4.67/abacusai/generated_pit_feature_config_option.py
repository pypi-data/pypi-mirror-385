from .return_class import AbstractApiClass


class GeneratedPitFeatureConfigOption(AbstractApiClass):
    """
        The options to display for possible generated PIT aggregation functions

        Args:
            client (ApiClient): An authenticated API Client instance
            name (str): The short name of the aggregation type.
            displayName (str): The display name of the aggregation type.
            default (bool): The default value for the option.
            description (str): The description of the aggregation type.
    """

    def __init__(self, client, name=None, displayName=None, default=None, description=None):
        super().__init__(client, None)
        self.name = name
        self.display_name = displayName
        self.default = default
        self.description = description
        self.deprecated_keys = {}

    def __repr__(self):
        repr_dict = {f'name': repr(self.name), f'display_name': repr(
            self.display_name), f'default': repr(self.default), f'description': repr(self.description)}
        class_name = "GeneratedPitFeatureConfigOption"
        repr_str = ',\n  '.join([f'{key}={value}' for key, value in repr_dict.items(
        ) if getattr(self, key, None) is not None and key not in self.deprecated_keys])
        return f"{class_name}({repr_str})"

    def to_dict(self):
        """
        Get a dict representation of the parameters in this class

        Returns:
            dict: The dict value representation of the class parameters
        """
        resp = {'name': self.name, 'display_name': self.display_name,
                'default': self.default, 'description': self.description}
        return {key: value for key, value in resp.items() if value is not None and key not in self.deprecated_keys}
