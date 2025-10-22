from .code_source import CodeSource
from .return_class import AbstractApiClass


class CustomLossFunction(AbstractApiClass):
    """
        Custom Loss Function

        Args:
            client (ApiClient): An authenticated API Client instance
            notebookId (str): The unique identifier of the notebook used to create/edit the loss function.
            name (str): Name assigned to the custom loss function.
            createdAt (str): When the loss function was created.
            lossFunctionName (str): The name of the function defined in the source code.
            lossFunctionType (str): The category of problems that this loss would be applicable to, e.g. regression, multi-label classification, etc.
            codeSource (CodeSource): Information about the source code of the loss function.
    """

    def __init__(self, client, notebookId=None, name=None, createdAt=None, lossFunctionName=None, lossFunctionType=None, codeSource={}):
        super().__init__(client, None)
        self.notebook_id = notebookId
        self.name = name
        self.created_at = createdAt
        self.loss_function_name = lossFunctionName
        self.loss_function_type = lossFunctionType
        self.code_source = client._build_class(CodeSource, codeSource)
        self.deprecated_keys = {}

    def __repr__(self):
        repr_dict = {f'notebook_id': repr(self.notebook_id), f'name': repr(self.name), f'created_at': repr(self.created_at), f'loss_function_name': repr(
            self.loss_function_name), f'loss_function_type': repr(self.loss_function_type), f'code_source': repr(self.code_source)}
        class_name = "CustomLossFunction"
        repr_str = ',\n  '.join([f'{key}={value}' for key, value in repr_dict.items(
        ) if getattr(self, key, None) is not None and key not in self.deprecated_keys])
        return f"{class_name}({repr_str})"

    def to_dict(self):
        """
        Get a dict representation of the parameters in this class

        Returns:
            dict: The dict value representation of the class parameters
        """
        resp = {'notebook_id': self.notebook_id, 'name': self.name, 'created_at': self.created_at, 'loss_function_name': self.loss_function_name,
                'loss_function_type': self.loss_function_type, 'code_source': self._get_attribute_as_dict(self.code_source)}
        return {key: value for key, value in resp.items() if value is not None and key not in self.deprecated_keys}
