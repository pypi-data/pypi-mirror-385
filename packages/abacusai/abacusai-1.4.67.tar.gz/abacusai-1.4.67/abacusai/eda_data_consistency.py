from .data_consistency_duplication import DataConsistencyDuplication
from .return_class import AbstractApiClass


class EdaDataConsistency(AbstractApiClass):
    """
        Eda Data Consistency, contained the duplicates in the base version, Comparison version, Deletions between the base and comparison and feature transformations between the base and comparison data.

        Args:
            client (ApiClient): An authenticated API Client instance
            columnNames (list): Name of all the features in the data
            primaryKeys (list): Name of the primary keys in the data
            transformationColumnNames (list): Name of all the features that are not the primary keys
            baseDuplicates (DataConsistencyDuplication): A DataConsistencyDuplication describing the number of duplicates within the data
            compareDuplicates (DataConsistencyDuplication): A DataConsistencyDuplication describing the number of duplicates within the data
            deletions (DataConsistencyDuplication): A DataConsistencyDeletion describing the number of deletion between two versions in the data
            transformations (DataConsistencyTransformation): A DataConsistencyTransformation the number of changes that occured per feature in the data
    """

    def __init__(self, client, columnNames=None, primaryKeys=None, transformationColumnNames=None, baseDuplicates={}, compareDuplicates={}, deletions={}, transformations={}):
        super().__init__(client, None)
        self.column_names = columnNames
        self.primary_keys = primaryKeys
        self.transformation_column_names = transformationColumnNames
        self.base_duplicates = client._build_class(
            DataConsistencyDuplication, baseDuplicates)
        self.compare_duplicates = client._build_class(
            DataConsistencyDuplication, compareDuplicates)
        self.deletions = client._build_class(
            DataConsistencyDuplication, deletions)
        self.transformations = client._build_class(
            DataConsistencyTransformation, transformations)
        self.deprecated_keys = {}

    def __repr__(self):
        repr_dict = {f'column_names': repr(self.column_names), f'primary_keys': repr(self.primary_keys), f'transformation_column_names': repr(self.transformation_column_names), f'base_duplicates': repr(
            self.base_duplicates), f'compare_duplicates': repr(self.compare_duplicates), f'deletions': repr(self.deletions), f'transformations': repr(self.transformations)}
        class_name = "EdaDataConsistency"
        repr_str = ',\n  '.join([f'{key}={value}' for key, value in repr_dict.items(
        ) if getattr(self, key, None) is not None and key not in self.deprecated_keys])
        return f"{class_name}({repr_str})"

    def to_dict(self):
        """
        Get a dict representation of the parameters in this class

        Returns:
            dict: The dict value representation of the class parameters
        """
        resp = {'column_names': self.column_names, 'primary_keys': self.primary_keys, 'transformation_column_names': self.transformation_column_names, 'base_duplicates': self._get_attribute_as_dict(
            self.base_duplicates), 'compare_duplicates': self._get_attribute_as_dict(self.compare_duplicates), 'deletions': self._get_attribute_as_dict(self.deletions), 'transformations': self._get_attribute_as_dict(self.transformations)}
        return {key: value for key, value in resp.items() if value is not None and key not in self.deprecated_keys}
