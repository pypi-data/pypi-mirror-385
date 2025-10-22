from .return_class import AbstractApiClass


class ModelLocation(AbstractApiClass):
    """
        Provide location information for the plug-and-play model.

        Args:
            client (ApiClient): An authenticated API Client instance
            location (str): Location of the plug-and-play model.
            artifactNames (dict): Representations of the names of the artifacts used to create the model.
    """

    def __init__(self, client, location=None, artifactNames=None):
        super().__init__(client, None)
        self.location = location
        self.artifact_names = artifactNames
        self.deprecated_keys = {}

    def __repr__(self):
        repr_dict = {f'location': repr(
            self.location), f'artifact_names': repr(self.artifact_names)}
        class_name = "ModelLocation"
        repr_str = ',\n  '.join([f'{key}={value}' for key, value in repr_dict.items(
        ) if getattr(self, key, None) is not None and key not in self.deprecated_keys])
        return f"{class_name}({repr_str})"

    def to_dict(self):
        """
        Get a dict representation of the parameters in this class

        Returns:
            dict: The dict value representation of the class parameters
        """
        resp = {'location': self.location,
                'artifact_names': self.artifact_names}
        return {key: value for key, value in resp.items() if value is not None and key not in self.deprecated_keys}
