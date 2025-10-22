from .return_class import AbstractApiClass


class NotebookTemplate(AbstractApiClass):
    """
        A template for notebooks.

        Args:
            client (ApiClient): An authenticated API Client instance
            notebookTemplateId (str): The ID of the notebook template
            name (str): The name of the notebook template
            description (str): The description of the notebook template
            createdAt (str): The date and time which the notebook template was created.
            updatedAt (str): The date and time which the notebook template was updated.
            templateType (str): The type of the notebook template
            filename (str): The file name of the notebook template
            sourceCode (str): The code in the notebook template
            tags (dict): The tags of the notebook template.
            metadata (dict): Some metadata for the notebook template.
            aiEngineerInfo (dict): Additional info about the notebook template required for AI Engineer.
    """

    def __init__(self, client, notebookTemplateId=None, name=None, description=None, createdAt=None, updatedAt=None, templateType=None, filename=None, sourceCode=None, tags=None, metadata=None, aiEngineerInfo=None):
        super().__init__(client, notebookTemplateId)
        self.notebook_template_id = notebookTemplateId
        self.name = name
        self.description = description
        self.created_at = createdAt
        self.updated_at = updatedAt
        self.template_type = templateType
        self.filename = filename
        self.source_code = sourceCode
        self.tags = tags
        self.metadata = metadata
        self.ai_engineer_info = aiEngineerInfo
        self.deprecated_keys = {}

    def __repr__(self):
        repr_dict = {f'notebook_template_id': repr(self.notebook_template_id), f'name': repr(self.name), f'description': repr(self.description), f'created_at': repr(self.created_at), f'updated_at': repr(self.updated_at), f'template_type': repr(
            self.template_type), f'filename': repr(self.filename), f'source_code': repr(self.source_code), f'tags': repr(self.tags), f'metadata': repr(self.metadata), f'ai_engineer_info': repr(self.ai_engineer_info)}
        class_name = "NotebookTemplate"
        repr_str = ',\n  '.join([f'{key}={value}' for key, value in repr_dict.items(
        ) if getattr(self, key, None) is not None and key not in self.deprecated_keys])
        return f"{class_name}({repr_str})"

    def to_dict(self):
        """
        Get a dict representation of the parameters in this class

        Returns:
            dict: The dict value representation of the class parameters
        """
        resp = {'notebook_template_id': self.notebook_template_id, 'name': self.name, 'description': self.description, 'created_at': self.created_at, 'updated_at': self.updated_at,
                'template_type': self.template_type, 'filename': self.filename, 'source_code': self.source_code, 'tags': self.tags, 'metadata': self.metadata, 'ai_engineer_info': self.ai_engineer_info}
        return {key: value for key, value in resp.items() if value is not None and key not in self.deprecated_keys}
