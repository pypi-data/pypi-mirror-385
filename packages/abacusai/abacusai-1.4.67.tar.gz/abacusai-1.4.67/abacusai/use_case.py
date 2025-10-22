from .return_class import AbstractApiClass


class UseCase(AbstractApiClass):
    """
        A Project Use Case

        Args:
            client (ApiClient): An authenticated API Client instance
            useCase (str): The enum value for this use case
            prettyName (str): A user-friendly name
            description (str): A description for this use case
            problemType (str): Name for the underlying problem type
    """

    def __init__(self, client, useCase=None, prettyName=None, description=None, problemType=None):
        super().__init__(client, None)
        self.use_case = useCase
        self.pretty_name = prettyName
        self.description = description
        self.problem_type = problemType
        self.deprecated_keys = {}

    def __repr__(self):
        repr_dict = {f'use_case': repr(self.use_case), f'pretty_name': repr(
            self.pretty_name), f'description': repr(self.description), f'problem_type': repr(self.problem_type)}
        class_name = "UseCase"
        repr_str = ',\n  '.join([f'{key}={value}' for key, value in repr_dict.items(
        ) if getattr(self, key, None) is not None and key not in self.deprecated_keys])
        return f"{class_name}({repr_str})"

    def to_dict(self):
        """
        Get a dict representation of the parameters in this class

        Returns:
            dict: The dict value representation of the class parameters
        """
        resp = {'use_case': self.use_case, 'pretty_name': self.pretty_name,
                'description': self.description, 'problem_type': self.problem_type}
        return {key: value for key, value in resp.items() if value is not None and key not in self.deprecated_keys}
