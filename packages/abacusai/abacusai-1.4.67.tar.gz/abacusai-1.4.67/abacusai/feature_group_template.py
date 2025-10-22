from .return_class import AbstractApiClass


class FeatureGroupTemplate(AbstractApiClass):
    """
        A template for creating feature groups.

        Args:
            client (ApiClient): An authenticated API Client instance
            featureGroupTemplateId (str): The unique identifier for this feature group template.
            description (str): A user-friendly text description of this feature group template.
            featureGroupId (str): The unique identifier for the feature group used to create this template.
            isSystemTemplate (bool): True if this is a system template returned from a user organization.
            name (str): The user-friendly name of this feature group template.
            templateSql (str): SQL that can include variables which will be replaced by values from the template config to resolve this template SQL into a valid SQL query for a feature group.
            templateVariables (dict): A map, from template variable names to parameters for replacing those template variables with values (e.g. to values and metadata on how to resolve those values).
            createdAt (str): When the feature group template was created.
            updatedAt (str): When the feature group template was updated.
    """

    def __init__(self, client, featureGroupTemplateId=None, description=None, featureGroupId=None, isSystemTemplate=None, name=None, templateSql=None, templateVariables=None, createdAt=None, updatedAt=None):
        super().__init__(client, featureGroupTemplateId)
        self.feature_group_template_id = featureGroupTemplateId
        self.description = description
        self.feature_group_id = featureGroupId
        self.is_system_template = isSystemTemplate
        self.name = name
        self.template_sql = templateSql
        self.template_variables = templateVariables
        self.created_at = createdAt
        self.updated_at = updatedAt
        self.deprecated_keys = {}

    def __repr__(self):
        repr_dict = {f'feature_group_template_id': repr(self.feature_group_template_id), f'description': repr(self.description), f'feature_group_id': repr(self.feature_group_id), f'is_system_template': repr(
            self.is_system_template), f'name': repr(self.name), f'template_sql': repr(self.template_sql), f'template_variables': repr(self.template_variables), f'created_at': repr(self.created_at), f'updated_at': repr(self.updated_at)}
        class_name = "FeatureGroupTemplate"
        repr_str = ',\n  '.join([f'{key}={value}' for key, value in repr_dict.items(
        ) if getattr(self, key, None) is not None and key not in self.deprecated_keys])
        return f"{class_name}({repr_str})"

    def to_dict(self):
        """
        Get a dict representation of the parameters in this class

        Returns:
            dict: The dict value representation of the class parameters
        """
        resp = {'feature_group_template_id': self.feature_group_template_id, 'description': self.description, 'feature_group_id': self.feature_group_id, 'is_system_template': self.is_system_template,
                'name': self.name, 'template_sql': self.template_sql, 'template_variables': self.template_variables, 'created_at': self.created_at, 'updated_at': self.updated_at}
        return {key: value for key, value in resp.items() if value is not None and key not in self.deprecated_keys}

    def delete(self):
        """
        Delete an existing feature group template.

        Args:
            feature_group_template_id (str): Unique string identifier associated with the feature group template.
        """
        return self.client.delete_feature_group_template(self.feature_group_template_id)

    def refresh(self):
        """
        Calls describe and refreshes the current object's fields

        Returns:
            FeatureGroupTemplate: The current object
        """
        self.__dict__.update(self.describe().__dict__)
        return self

    def describe(self):
        """
        Describe a Feature Group Template.

        Args:
            feature_group_template_id (str): The unique identifier of a feature group template.

        Returns:
            FeatureGroupTemplate: The feature group template object.
        """
        return self.client.describe_feature_group_template(self.feature_group_template_id)

    def update(self, template_sql: str = None, template_variables: list = None, description: str = None, name: str = None):
        """
        Update a feature group template.

        Args:
            template_sql (str): If provided, the new value to use for the template SQL.
            template_variables (list): If provided, the new value to use for the template variables.
            description (str): Description of this feature group template.
            name (str): User-friendly name for this feature group template.

        Returns:
            FeatureGroupTemplate: The updated feature group template.
        """
        return self.client.update_feature_group_template(self.feature_group_template_id, template_sql, template_variables, description, name)

    def preview_resolution(self, template_bindings: list = None, template_sql: str = None, template_variables: list = None, should_validate: bool = True):
        """
        Resolve template sql using template variables and template bindings.

        Args:
            template_bindings (list): Values to override the template variable values specified by the template.
            template_sql (str): If specified, use this as the template SQL instead of the feature group template's SQL.
            template_variables (list): Template variables to use. If a template is provided, this overrides the template's template variables.
            should_validate (bool): If true, validates the resolved SQL.

        Returns:
            ResolvedFeatureGroupTemplate: The resolved template
        """
        return self.client.preview_feature_group_template_resolution(self.feature_group_template_id, template_bindings, template_sql, template_variables, should_validate)
