from .return_class import AbstractApiClass


class ResolvedFeatureGroupTemplate(AbstractApiClass):
    """
        Final SQL from resolving a feature group template.

        Args:
            client (ApiClient): An authenticated API Client instance
            featureGroupTemplateId (str): Unique identifier for this feature group template.
            resolvedVariables (dict): Map from template variable names to parameters available during template resolution.
            resolvedSql (str): SQL resulting from resolving the SQL template by applying the resolved bindings.
            templateSql (str): SQL that can include variables to be replaced by values from the template config to resolve this template SQL into a valid SQL query for a feature group.
            sqlError (str): if invalid, the sql error message
    """

    def __init__(self, client, featureGroupTemplateId=None, resolvedVariables=None, resolvedSql=None, templateSql=None, sqlError=None):
        super().__init__(client, None)
        self.feature_group_template_id = featureGroupTemplateId
        self.resolved_variables = resolvedVariables
        self.resolved_sql = resolvedSql
        self.template_sql = templateSql
        self.sql_error = sqlError
        self.deprecated_keys = {}

    def __repr__(self):
        repr_dict = {f'feature_group_template_id': repr(self.feature_group_template_id), f'resolved_variables': repr(
            self.resolved_variables), f'resolved_sql': repr(self.resolved_sql), f'template_sql': repr(self.template_sql), f'sql_error': repr(self.sql_error)}
        class_name = "ResolvedFeatureGroupTemplate"
        repr_str = ',\n  '.join([f'{key}={value}' for key, value in repr_dict.items(
        ) if getattr(self, key, None) is not None and key not in self.deprecated_keys])
        return f"{class_name}({repr_str})"

    def to_dict(self):
        """
        Get a dict representation of the parameters in this class

        Returns:
            dict: The dict value representation of the class parameters
        """
        resp = {'feature_group_template_id': self.feature_group_template_id, 'resolved_variables': self.resolved_variables,
                'resolved_sql': self.resolved_sql, 'template_sql': self.template_sql, 'sql_error': self.sql_error}
        return {key: value for key, value in resp.items() if value is not None and key not in self.deprecated_keys}
