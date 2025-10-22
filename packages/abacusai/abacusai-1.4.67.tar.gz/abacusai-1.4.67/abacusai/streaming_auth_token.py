from .return_class import AbstractApiClass


class StreamingAuthToken(AbstractApiClass):
    """
        A streaming authentication token that is used to authenticate requests to append data to streaming datasets

        Args:
            client (ApiClient): An authenticated API Client instance
            streamingToken (str): The unique token used to authenticate requests
            createdAt (str): When the token was created
    """

    def __init__(self, client, streamingToken=None, createdAt=None):
        super().__init__(client, None)
        self.streaming_token = streamingToken
        self.created_at = createdAt
        self.deprecated_keys = {}

    def __repr__(self):
        repr_dict = {f'streaming_token': repr(
            self.streaming_token), f'created_at': repr(self.created_at)}
        class_name = "StreamingAuthToken"
        repr_str = ',\n  '.join([f'{key}={value}' for key, value in repr_dict.items(
        ) if getattr(self, key, None) is not None and key not in self.deprecated_keys])
        return f"{class_name}({repr_str})"

    def to_dict(self):
        """
        Get a dict representation of the parameters in this class

        Returns:
            dict: The dict value representation of the class parameters
        """
        resp = {'streaming_token': self.streaming_token,
                'created_at': self.created_at}
        return {key: value for key, value in resp.items() if value is not None and key not in self.deprecated_keys}
