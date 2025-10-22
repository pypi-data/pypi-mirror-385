import io
from typing import List, Union

from .annotation_config import AnnotationConfig
from .api_class import (
    CPUSize, FeatureGroupExportConfig, MemorySize, MergeConfig, OperatorConfig,
    ProjectFeatureGroupConfig, SamplingConfig
)
from .code_source import CodeSource
from .concatenation_config import ConcatenationConfig
from .feature import Feature
from .feature_group_refresh_export_config import FeatureGroupRefreshExportConfig
from .feature_group_template import FeatureGroupTemplate
from .feature_group_version import FeatureGroupVersion
from .indexing_config import IndexingConfig
from .natural_language_explanation import NaturalLanguageExplanation
from .point_in_time_group import PointInTimeGroup
from .refresh_schedule import RefreshSchedule
from .return_class import AbstractApiClass


class FeatureGroup(AbstractApiClass):
    """
        A feature group.

        Args:
            client (ApiClient): An authenticated API Client instance
            featureGroupId (str): Unique identifier for this feature group.
            modificationLock (bool): If feature group is locked against a change or not.
            name (str): 
            featureGroupSourceType (str): The source type of the feature group
            tableName (str): Unique table name of this feature group.
            sql (str): SQL definition creating this feature group.
            datasetId (str): Dataset ID the feature group is sourced from.
            functionSourceCode (str): Source definition creating this feature group.
            functionName (str): Function name to execute from the source code.
            sourceTables (list[str]): Source tables for this feature group.
            createdAt (str): Timestamp at which the feature group was created.
            description (str): Description of the feature group.
            sqlError (str): Error message with this feature group.
            latestVersionOutdated (bool): Is latest materialized feature group version outdated.
            referencedFeatureGroups (list[str]): Feature groups this feature group is used in.
            tags (list[str]): Tags added to this feature group.
            primaryKey (str): Primary index feature.
            updateTimestampKey (str): Primary timestamp feature.
            lookupKeys (list[str]): Additional indexed features for this feature group.
            streamingEnabled (bool): If true, the feature group can have data streamed to it.
            incremental (bool): If feature group corresponds to an incremental dataset.
            mergeConfig (dict): Merge configuration settings for the feature group.
            samplingConfig (dict): Sampling configuration for the feature group.
            cpuSize (str): CPU size specified for the Python feature group.
            memory (int): Memory in GB specified for the Python feature group.
            streamingReady (bool): If true, the feature group is ready to receive streaming data.
            featureTags (dict): Tags for features in this feature group
            moduleName (str): Path to the file with the feature group function.
            templateBindings (dict): Config specifying variable names and values to use when resolving a feature group template.
            featureExpression (str): If the dataset feature group has custom features, the SQL select expression creating those features.
            useOriginalCsvNames (bool): If true, the feature group will use the original column names in the source dataset.
            pythonFunctionBindings (dict): Config specifying variable names, types, and values to use when resolving a Python feature group.
            pythonFunctionName (str): Name of the Python function the feature group was built from.
            useGpu (bool): Whether this feature group is using gpu
            versionLimit (int): Version limit for the feature group.
            exportOnMaterialization (bool): Whether to export the feature group on materialization.
            features (Feature): List of resolved features.
            duplicateFeatures (Feature): List of duplicate features.
            pointInTimeGroups (PointInTimeGroup): List of Point In Time Groups.
            annotationConfig (AnnotationConfig): Annotation config for this feature
            latestFeatureGroupVersion (FeatureGroupVersion): Latest feature group version.
            concatenationConfig (ConcatenationConfig): Feature group ID whose data will be concatenated into this feature group.
            indexingConfig (IndexingConfig): Indexing config for the feature group for feature store
            codeSource (CodeSource): If a Python feature group, information on the source code.
            featureGroupTemplate (FeatureGroupTemplate): FeatureGroupTemplate to use when this feature group is attached to a template.
            explanation (NaturalLanguageExplanation): Natural language explanation of the feature group
            refreshSchedules (RefreshSchedule): List of schedules that determines when the next version of the feature group will be created.
            exportConnectorConfig (FeatureGroupRefreshExportConfig): The export config (file connector or database connector information) for feature group exports.
            operatorConfig (OperatorConfig): Operator configuration settings for the feature group.
    """

    def __init__(self, client, featureGroupId=None, modificationLock=None, name=None, featureGroupSourceType=None, tableName=None, sql=None, datasetId=None, functionSourceCode=None, functionName=None, sourceTables=None, createdAt=None, description=None, sqlError=None, latestVersionOutdated=None, referencedFeatureGroups=None, tags=None, primaryKey=None, updateTimestampKey=None, lookupKeys=None, streamingEnabled=None, incremental=None, mergeConfig=None, samplingConfig=None, cpuSize=None, memory=None, streamingReady=None, featureTags=None, moduleName=None, templateBindings=None, featureExpression=None, useOriginalCsvNames=None, pythonFunctionBindings=None, pythonFunctionName=None, useGpu=None, versionLimit=None, exportOnMaterialization=None, features={}, duplicateFeatures={}, pointInTimeGroups={}, annotationConfig={}, concatenationConfig={}, indexingConfig={}, codeSource={}, featureGroupTemplate={}, explanation={}, refreshSchedules={}, exportConnectorConfig={}, latestFeatureGroupVersion={}, operatorConfig={}):
        super().__init__(client, featureGroupId)
        self.feature_group_id = featureGroupId
        self.modification_lock = modificationLock
        self.name = name
        self.feature_group_source_type = featureGroupSourceType
        self.table_name = tableName
        self.sql = sql
        self.dataset_id = datasetId
        self.function_source_code = functionSourceCode
        self.function_name = functionName
        self.source_tables = sourceTables
        self.created_at = createdAt
        self.description = description
        self.sql_error = sqlError
        self.latest_version_outdated = latestVersionOutdated
        self.referenced_feature_groups = referencedFeatureGroups
        self.tags = tags
        self.primary_key = primaryKey
        self.update_timestamp_key = updateTimestampKey
        self.lookup_keys = lookupKeys
        self.streaming_enabled = streamingEnabled
        self.incremental = incremental
        self.merge_config = mergeConfig
        self.sampling_config = samplingConfig
        self.cpu_size = cpuSize
        self.memory = memory
        self.streaming_ready = streamingReady
        self.feature_tags = featureTags
        self.module_name = moduleName
        self.template_bindings = templateBindings
        self.feature_expression = featureExpression
        self.use_original_csv_names = useOriginalCsvNames
        self.python_function_bindings = pythonFunctionBindings
        self.python_function_name = pythonFunctionName
        self.use_gpu = useGpu
        self.version_limit = versionLimit
        self.export_on_materialization = exportOnMaterialization
        self.features = client._build_class(Feature, features)
        self.duplicate_features = client._build_class(
            Feature, duplicateFeatures)
        self.point_in_time_groups = client._build_class(
            PointInTimeGroup, pointInTimeGroups)
        self.annotation_config = client._build_class(
            AnnotationConfig, annotationConfig)
        self.concatenation_config = client._build_class(
            ConcatenationConfig, concatenationConfig)
        self.indexing_config = client._build_class(
            IndexingConfig, indexingConfig)
        self.code_source = client._build_class(CodeSource, codeSource)
        self.feature_group_template = client._build_class(
            FeatureGroupTemplate, featureGroupTemplate)
        self.explanation = client._build_class(
            NaturalLanguageExplanation, explanation)
        self.refresh_schedules = client._build_class(
            RefreshSchedule, refreshSchedules)
        self.export_connector_config = client._build_class(
            FeatureGroupRefreshExportConfig, exportConnectorConfig)
        self.latest_feature_group_version = client._build_class(
            FeatureGroupVersion, latestFeatureGroupVersion)
        self.operator_config = client._build_class(
            OperatorConfig, operatorConfig)
        self.deprecated_keys = {'name'}

    def __repr__(self):
        repr_dict = {f'feature_group_id': repr(self.feature_group_id), f'modification_lock': repr(self.modification_lock), f'name': repr(self.name), f'feature_group_source_type': repr(self.feature_group_source_type), f'table_name': repr(self.table_name), f'sql': repr(self.sql), f'dataset_id': repr(self.dataset_id), f'function_source_code': repr(self.function_source_code), f'function_name': repr(self.function_name), f'source_tables': repr(self.source_tables), f'created_at': repr(self.created_at), f'description': repr(self.description), f'sql_error': repr(self.sql_error), f'latest_version_outdated': repr(self.latest_version_outdated), f'referenced_feature_groups': repr(self.referenced_feature_groups), f'tags': repr(self.tags), f'primary_key': repr(self.primary_key), f'update_timestamp_key': repr(self.update_timestamp_key), f'lookup_keys': repr(self.lookup_keys), f'streaming_enabled': repr(self.streaming_enabled), f'incremental': repr(self.incremental), f'merge_config': repr(self.merge_config), f'sampling_config': repr(self.sampling_config), f'cpu_size': repr(self.cpu_size), f'memory': repr(self.memory), f'streaming_ready': repr(self.streaming_ready), f'feature_tags': repr(
            self.feature_tags), f'module_name': repr(self.module_name), f'template_bindings': repr(self.template_bindings), f'feature_expression': repr(self.feature_expression), f'use_original_csv_names': repr(self.use_original_csv_names), f'python_function_bindings': repr(self.python_function_bindings), f'python_function_name': repr(self.python_function_name), f'use_gpu': repr(self.use_gpu), f'version_limit': repr(self.version_limit), f'export_on_materialization': repr(self.export_on_materialization), f'features': repr(self.features), f'duplicate_features': repr(self.duplicate_features), f'point_in_time_groups': repr(self.point_in_time_groups), f'annotation_config': repr(self.annotation_config), f'concatenation_config': repr(self.concatenation_config), f'indexing_config': repr(self.indexing_config), f'code_source': repr(self.code_source), f'feature_group_template': repr(self.feature_group_template), f'explanation': repr(self.explanation), f'refresh_schedules': repr(self.refresh_schedules), f'export_connector_config': repr(self.export_connector_config), f'latest_feature_group_version': repr(self.latest_feature_group_version), f'operator_config': repr(self.operator_config)}
        class_name = "FeatureGroup"
        repr_str = ',\n  '.join([f'{key}={value}' for key, value in repr_dict.items(
        ) if getattr(self, key, None) is not None and key not in self.deprecated_keys])
        return f"{class_name}({repr_str})"

    def to_dict(self):
        """
        Get a dict representation of the parameters in this class

        Returns:
            dict: The dict value representation of the class parameters
        """
        resp = {'feature_group_id': self.feature_group_id, 'modification_lock': self.modification_lock, 'name': self.name, 'feature_group_source_type': self.feature_group_source_type, 'table_name': self.table_name, 'sql': self.sql, 'dataset_id': self.dataset_id, 'function_source_code': self.function_source_code, 'function_name': self.function_name, 'source_tables': self.source_tables, 'created_at': self.created_at, 'description': self.description, 'sql_error': self.sql_error, 'latest_version_outdated': self.latest_version_outdated, 'referenced_feature_groups': self.referenced_feature_groups, 'tags': self.tags, 'primary_key': self.primary_key, 'update_timestamp_key': self.update_timestamp_key, 'lookup_keys': self.lookup_keys, 'streaming_enabled': self.streaming_enabled, 'incremental': self.incremental, 'merge_config': self.merge_config, 'sampling_config': self.sampling_config, 'cpu_size': self.cpu_size, 'memory': self.memory, 'streaming_ready': self.streaming_ready, 'feature_tags': self.feature_tags, 'module_name': self.module_name, 'template_bindings': self.template_bindings, 'feature_expression': self.feature_expression, 'use_original_csv_names': self.use_original_csv_names,
                'python_function_bindings': self.python_function_bindings, 'python_function_name': self.python_function_name, 'use_gpu': self.use_gpu, 'version_limit': self.version_limit, 'export_on_materialization': self.export_on_materialization, 'features': self._get_attribute_as_dict(self.features), 'duplicate_features': self._get_attribute_as_dict(self.duplicate_features), 'point_in_time_groups': self._get_attribute_as_dict(self.point_in_time_groups), 'annotation_config': self._get_attribute_as_dict(self.annotation_config), 'concatenation_config': self._get_attribute_as_dict(self.concatenation_config), 'indexing_config': self._get_attribute_as_dict(self.indexing_config), 'code_source': self._get_attribute_as_dict(self.code_source), 'feature_group_template': self._get_attribute_as_dict(self.feature_group_template), 'explanation': self._get_attribute_as_dict(self.explanation), 'refresh_schedules': self._get_attribute_as_dict(self.refresh_schedules), 'export_connector_config': self._get_attribute_as_dict(self.export_connector_config), 'latest_feature_group_version': self._get_attribute_as_dict(self.latest_feature_group_version), 'operator_config': self._get_attribute_as_dict(self.operator_config)}
        return {key: value for key, value in resp.items() if value is not None and key not in self.deprecated_keys}

    def add_to_project(self, project_id: str, feature_group_type: str = 'CUSTOM_TABLE'):
        """
        Adds a feature group to a project.

        Args:
            project_id (str): The unique ID associated with the project.
            feature_group_type (str): The feature group type of the feature group, based on the use case under which the feature group is being created.
        """
        return self.client.add_feature_group_to_project(self.feature_group_id, project_id, feature_group_type)

    def set_project_config(self, project_id: str, project_config: Union[dict, ProjectFeatureGroupConfig] = None):
        """
        Sets a feature group's project config

        Args:
            project_id (str): Unique string identifier for the project.
            project_config (ProjectFeatureGroupConfig): Feature group's project configuration.
        """
        return self.client.set_project_feature_group_config(self.feature_group_id, project_id, project_config)

    def get_project_config(self, project_id: str):
        """
        Gets a feature group's project config

        Args:
            project_id (str): Unique string identifier for the project.

        Returns:
            ProjectConfig: The feature group's project configuration.
        """
        return self.client.get_project_feature_group_config(self.feature_group_id, project_id)

    def remove_from_project(self, project_id: str):
        """
        Removes a feature group from a project.

        Args:
            project_id (str): The unique ID associated with the project.
        """
        return self.client.remove_feature_group_from_project(self.feature_group_id, project_id)

    def set_type(self, project_id: str, feature_group_type: str = 'CUSTOM_TABLE'):
        """
        Update the feature group type in a project. The feature group must already be added to the project.

        Args:
            project_id (str): Unique identifier associated with the project.
            feature_group_type (str): The feature group type to set the feature group as.
        """
        return self.client.set_feature_group_type(self.feature_group_id, project_id, feature_group_type)

    def describe_annotation(self, feature_name: str = None, doc_id: str = None, feature_group_row_identifier: str = None):
        """
        Get the latest annotation entry for a given feature group, feature, and document.

        Args:
            feature_name (str): The name of the feature the annotation is on.
            doc_id (str): The ID of the primary document the annotation is on. At least one of the doc_id or feature_group_row_identifier must be provided in order to identify the correct annotation.
            feature_group_row_identifier (str): The key value of the feature group row the annotation is on (cast to string). Usually the feature group's primary / identifier key value. At least one of the doc_id or feature_group_row_identifier must be provided in order to identify the correct annotation.

        Returns:
            AnnotationEntry: The latest annotation entry for the given feature group, feature, document, and/or annotation key value.
        """
        return self.client.describe_annotation(self.feature_group_id, feature_name, doc_id, feature_group_row_identifier)

    def verify_and_describe_annotation(self, feature_name: str = None, doc_id: str = None, feature_group_row_identifier: str = None):
        """
        Get the latest annotation entry for a given feature group, feature, and document along with verification information.

        Args:
            feature_name (str): The name of the feature the annotation is on.
            doc_id (str): The ID of the primary document the annotation is on. At least one of the doc_id or feature_group_row_identifier must be provided in order to identify the correct annotation.
            feature_group_row_identifier (str): The key value of the feature group row the annotation is on (cast to string). Usually the feature group's primary / identifier key value. At least one of the doc_id or feature_group_row_identifier must be provided in order to identify the correct annotation.

        Returns:
            AnnotationEntry: The latest annotation entry for the given feature group, feature, document, and/or annotation key value. Includes the verification information.
        """
        return self.client.verify_and_describe_annotation(self.feature_group_id, feature_name, doc_id, feature_group_row_identifier)

    def update_annotation_status(self, feature_name: str, status: str, doc_id: str = None, feature_group_row_identifier: str = None, save_metadata: bool = False):
        """
        Update the status of an annotation entry.

        Args:
            feature_name (str): The name of the feature the annotation is on.
            status (str): The new status of the annotation. Must be one of the following: 'TODO', 'IN_PROGRESS', 'DONE'.
            doc_id (str): The ID of the primary document the annotation is on. At least one of the doc_id or feature_group_row_identifier must be provided in order to identify the correct annotation.
            feature_group_row_identifier (str): The key value of the feature group row the annotation is on (cast to string). Usually the feature group's primary / identifier key value. At least one of the doc_id or feature_group_row_identifier must be provided in order to identify the correct annotation.
            save_metadata (bool): If True, save the metadata for the annotation entry.

        Returns:
            AnnotationEntry: The updated annotation entry.
        """
        return self.client.update_annotation_status(self.feature_group_id, feature_name, status, doc_id, feature_group_row_identifier, save_metadata)

    def get_document_to_annotate(self, project_id: str, feature_name: str, feature_group_row_identifier: str = None, get_previous: bool = False):
        """
        Get an available document that needs to be annotated for a annotation feature group.

        Args:
            project_id (str): The ID of the project that the annotation is associated with.
            feature_name (str): The name of the feature the annotation is on.
            feature_group_row_identifier (str): The key value of the feature group row the annotation is on (cast to string). Usually the primary key value. If provided, fetch the immediate next (or previous) available document.
            get_previous (bool): If True, get the previous document instead of the next document. Applicable if feature_group_row_identifier is provided.

        Returns:
            AnnotationDocument: The document to annotate.
        """
        return self.client.get_document_to_annotate(self.feature_group_id, project_id, feature_name, feature_group_row_identifier, get_previous)

    def get_annotations_status(self, feature_name: str = None, check_for_materialization: bool = False):
        """
        Get the status of the annotations for a given feature group and feature.

        Args:
            feature_name (str): The name of the feature the annotation is on.
            check_for_materialization (bool): If True, check if the feature group needs to be materialized before using for annotations.

        Returns:
            AnnotationsStatus: The status of the annotations for the given feature group and feature.
        """
        return self.client.get_annotations_status(self.feature_group_id, feature_name, check_for_materialization)

    def import_annotation_labels(self, file: io.TextIOBase, annotation_type: str):
        """
        Imports annotation labels from csv file. All valid values in the file will be imported as labels (including header row if present).

        Args:
            file (io.TextIOBase): The file to import. Must be a csv file.
            annotation_type (str): The type of the annotation.

        Returns:
            AnnotationConfig: The annotation config for the feature group.
        """
        return self.client.import_annotation_labels(self.feature_group_id, file, annotation_type)

    def create_sampling(self, table_name: str, sampling_config: Union[dict, SamplingConfig], description: str = None):
        """
        Creates a new Feature Group defined as a sample of rows from another Feature Group.

        For efficiency, sampling is approximate unless otherwise specified. (e.g. the number of rows may vary slightly from what was requested).


        Args:
            table_name (str): The unique name to be given to this sampling Feature Group. Can be up to 120 characters long and can only contain alphanumeric characters and underscores.
            sampling_config (SamplingConfig): Dictionary defining the sampling method and its parameters.
            description (str): A human-readable description of this Feature Group.

        Returns:
            FeatureGroup: The created Feature Group.
        """
        return self.client.create_sampling_feature_group(self.feature_group_id, table_name, sampling_config, description)

    def set_sampling_config(self, sampling_config: Union[dict, SamplingConfig]):
        """
        Set a FeatureGroup’s sampling to the config values provided, so that the rows the FeatureGroup returns will be a sample of those it would otherwise have returned.

        Args:
            sampling_config (SamplingConfig): A JSON string object specifying the sampling method and parameters specific to that sampling method. An empty sampling_config indicates no sampling.

        Returns:
            FeatureGroup: The updated FeatureGroup.
        """
        return self.client.set_feature_group_sampling_config(self.feature_group_id, sampling_config)

    def set_merge_config(self, merge_config: Union[dict, MergeConfig]):
        """
        Set a MergeFeatureGroup’s merge config to the values provided, so that the feature group only returns a bounded range of an incremental dataset.

        Args:
            merge_config (MergeConfig): JSON object string specifying the merge rule. An empty merge_config will default to only including the latest dataset version.

        Returns:
            FeatureGroup: The updated FeatureGroup.
        """
        return self.client.set_feature_group_merge_config(self.feature_group_id, merge_config)

    def set_operator_config(self, operator_config: Union[dict, OperatorConfig]):
        """
        Set a OperatorFeatureGroup’s operator config to the values provided.

        Args:
            operator_config (OperatorConfig): A dictionary object specifying the pre-defined operations.

        Returns:
            FeatureGroup: The updated FeatureGroup.
        """
        return self.client.set_feature_group_operator_config(self.feature_group_id, operator_config)

    def set_schema(self, schema: list):
        """
        Creates a new schema and points the feature group to the new feature group schema ID.

        Args:
            schema (list): JSON string containing an array of objects with 'name' and 'dataType' properties.
        """
        return self.client.set_feature_group_schema(self.feature_group_id, schema)

    def get_schema(self, project_id: str = None):
        """
        Returns a schema for a given FeatureGroup in a project.

        Args:
            project_id (str): The unique ID associated with the project.

        Returns:
            list[Feature]: A list of objects for each column in the specified feature group.
        """
        return self.client.get_feature_group_schema(self.feature_group_id, project_id)

    def create_feature(self, name: str, select_expression: str):
        """
        Creates a new feature in a Feature Group from a SQL select statement.

        Args:
            name (str): The name of the feature to add.
            select_expression (str): SQL SELECT expression to create the feature.

        Returns:
            FeatureGroup: A Feature Group object with the newly added feature.
        """
        return self.client.create_feature(self.feature_group_id, name, select_expression)

    def add_tag(self, tag: str):
        """
        Adds a tag to the feature group

        Args:
            tag (str): The tag to add to the feature group.
        """
        return self.client.add_feature_group_tag(self.feature_group_id, tag)

    def remove_tag(self, tag: str):
        """
        Removes a tag from the specified feature group.

        Args:
            tag (str): The tag to remove from the feature group.
        """
        return self.client.remove_feature_group_tag(self.feature_group_id, tag)

    def add_annotatable_feature(self, name: str, annotation_type: str):
        """
        Add an annotatable feature in a Feature Group

        Args:
            name (str): The name of the feature to add.
            annotation_type (str): The type of annotation to set.

        Returns:
            FeatureGroup: The feature group after the feature has been set
        """
        return self.client.add_annotatable_feature(self.feature_group_id, name, annotation_type)

    def set_feature_as_annotatable_feature(self, feature_name: str, annotation_type: str, feature_group_row_identifier_feature: str = None, doc_id_feature: str = None):
        """
        Sets an existing feature as an annotatable feature (Feature that can be annotated).

        Args:
            feature_name (str): The name of the feature to set as annotatable.
            annotation_type (str): The type of annotation label to add.
            feature_group_row_identifier_feature (str): The key value of the feature group row the annotation is on (cast to string) and uniquely identifies the feature group row. At least one of the doc_id or key value must be provided so that the correct annotation can be identified.
            doc_id_feature (str): The name of the document ID feature.

        Returns:
            FeatureGroup: A feature group object with the newly added annotatable feature.
        """
        return self.client.set_feature_as_annotatable_feature(self.feature_group_id, feature_name, annotation_type, feature_group_row_identifier_feature, doc_id_feature)

    def set_annotation_status_feature(self, feature_name: str):
        """
        Sets a feature as the annotation status feature for a feature group.

        Args:
            feature_name (str): The name of the feature to set as the annotation status feature.

        Returns:
            FeatureGroup: The updated feature group.
        """
        return self.client.set_annotation_status_feature(self.feature_group_id, feature_name)

    def unset_feature_as_annotatable_feature(self, feature_name: str):
        """
        Unsets a feature as annotatable

        Args:
            feature_name (str): The name of the feature to unset.

        Returns:
            FeatureGroup: The feature group after unsetting the feature
        """
        return self.client.unset_feature_as_annotatable_feature(self.feature_group_id, feature_name)

    def add_annotation_label(self, label_name: str, annotation_type: str, label_definition: str = None):
        """
        Adds an annotation label

        Args:
            label_name (str): The name of the label.
            annotation_type (str): The type of the annotation to set.
            label_definition (str): the definition of the label.

        Returns:
            FeatureGroup: The feature group after adding the annotation label
        """
        return self.client.add_feature_group_annotation_label(self.feature_group_id, label_name, annotation_type, label_definition)

    def remove_annotation_label(self, label_name: str):
        """
        Removes an annotation label

        Args:
            label_name (str): The name of the label to remove.

        Returns:
            FeatureGroup: The feature group after adding the annotation label
        """
        return self.client.remove_feature_group_annotation_label(self.feature_group_id, label_name)

    def add_feature_tag(self, feature: str, tag: str):
        """
        Adds a tag on a feature

        Args:
            feature (str): The feature to set the tag on.
            tag (str): The tag to set on the feature.
        """
        return self.client.add_feature_tag(self.feature_group_id, feature, tag)

    def remove_feature_tag(self, feature: str, tag: str):
        """
        Removes a tag from a feature

        Args:
            feature (str): The feature to remove the tag from.
            tag (str): The tag to remove.
        """
        return self.client.remove_feature_tag(self.feature_group_id, feature, tag)

    def create_nested_feature(self, nested_feature_name: str, table_name: str, using_clause: str, where_clause: str = None, order_clause: str = None):
        """
        Creates a new nested feature in a feature group from a SQL statement.

        Args:
            nested_feature_name (str): The name of the feature.
            table_name (str): The table name of the feature group to nest. Can be up to 120 characters long and can only contain alphanumeric characters and underscores.
            using_clause (str): The SQL join column or logic to join the nested table with the parent.
            where_clause (str): A SQL WHERE statement to filter the nested rows.
            order_clause (str): A SQL clause to order the nested rows.

        Returns:
            FeatureGroup: A feature group object with the newly added nested feature.
        """
        return self.client.create_nested_feature(self.feature_group_id, nested_feature_name, table_name, using_clause, where_clause, order_clause)

    def update_nested_feature(self, nested_feature_name: str, table_name: str = None, using_clause: str = None, where_clause: str = None, order_clause: str = None, new_nested_feature_name: str = None):
        """
        Updates a previously existing nested feature in a feature group.

        Args:
            nested_feature_name (str): The name of the feature to be updated.
            table_name (str): The name of the table. Can be up to 120 characters long and can only contain alphanumeric characters and underscores.
            using_clause (str): The SQL join column or logic to join the nested table with the parent.
            where_clause (str): An SQL WHERE statement to filter the nested rows.
            order_clause (str): An SQL clause to order the nested rows.
            new_nested_feature_name (str): New name for the nested feature.

        Returns:
            FeatureGroup: A feature group object with the updated nested feature.
        """
        return self.client.update_nested_feature(self.feature_group_id, nested_feature_name, table_name, using_clause, where_clause, order_clause, new_nested_feature_name)

    def delete_nested_feature(self, nested_feature_name: str):
        """
        Delete a nested feature.

        Args:
            nested_feature_name (str): The name of the feature to be deleted.

        Returns:
            FeatureGroup: A feature group object without the specified nested feature.
        """
        return self.client.delete_nested_feature(self.feature_group_id, nested_feature_name)

    def create_point_in_time_feature(self, feature_name: str, history_table_name: str, aggregation_keys: list, timestamp_key: str, historical_timestamp_key: str, expression: str, lookback_window_seconds: float = None, lookback_window_lag_seconds: float = 0, lookback_count: int = None, lookback_until_position: int = 0):
        """
        Creates a new point in time feature in a feature group using another historical feature group, window spec, and aggregate expression.

        We use the aggregation keys and either the lookbackWindowSeconds or the lookbackCount values to perform the window aggregation for every row in the current feature group.

        If the window is specified in seconds, then all rows in the history table which match the aggregation keys and with historicalTimeFeature greater than or equal to lookbackStartCount and less than the value of the current rows timeFeature are considered. An optional lookbackWindowLagSeconds (+ve or -ve) can be used to offset the current value of the timeFeature. If this value is negative, we will look at the future rows in the history table, so care must be taken to ensure that these rows are available in the online context when we are performing a lookup on this feature group. If the window is specified in counts, then we order the historical table rows aligning by time and consider rows from the window where the rank order is greater than or equal to lookbackCount and includes the row just prior to the current one. The lag is specified in terms of positions using lookbackUntilPosition.


        Args:
            feature_name (str): The name of the feature to create.
            history_table_name (str): The table name of the history table.
            aggregation_keys (list): List of keys to use for joining the historical table and performing the window aggregation.
            timestamp_key (str): Name of feature which contains the timestamp value for the point in time feature.
            historical_timestamp_key (str): Name of feature which contains the historical timestamp.
            expression (str): SQL aggregate expression which can convert a sequence of rows into a scalar value.
            lookback_window_seconds (float): If window is specified in terms of time, number of seconds in the past from the current time for start of the window.
            lookback_window_lag_seconds (float): Optional lag to offset the closest point for the window. If it is positive, we delay the start of window. If it is negative, we are looking at the "future" rows in the history table.
            lookback_count (int): If window is specified in terms of count, the start position of the window (0 is the current row).
            lookback_until_position (int): Optional lag to offset the closest point for the window. If it is positive, we delay the start of window by that many rows. If it is negative, we are looking at those many "future" rows in the history table.

        Returns:
            FeatureGroup: A feature group object with the newly added nested feature.
        """
        return self.client.create_point_in_time_feature(self.feature_group_id, feature_name, history_table_name, aggregation_keys, timestamp_key, historical_timestamp_key, expression, lookback_window_seconds, lookback_window_lag_seconds, lookback_count, lookback_until_position)

    def update_point_in_time_feature(self, feature_name: str, history_table_name: str = None, aggregation_keys: list = None, timestamp_key: str = None, historical_timestamp_key: str = None, expression: str = None, lookback_window_seconds: float = None, lookback_window_lag_seconds: float = None, lookback_count: int = None, lookback_until_position: int = None, new_feature_name: str = None):
        """
        Updates an existing Point-in-Time (PiT) feature in a feature group. See `createPointInTimeFeature` for detailed semantics.

        Args:
            feature_name (str): The name of the feature.
            history_table_name (str): The table name of the history table. If not specified, we use the current table to do a self join.
            aggregation_keys (list): List of keys to use for joining the historical table and performing the window aggregation.
            timestamp_key (str): Name of the feature which contains the timestamp value for the PiT feature.
            historical_timestamp_key (str): Name of the feature which contains the historical timestamp.
            expression (str): SQL Aggregate expression which can convert a sequence of rows into a scalar value.
            lookback_window_seconds (float): If the window is specified in terms of time, the number of seconds in the past from the current time for the start of the window.
            lookback_window_lag_seconds (float): Optional lag to offset the closest point for the window. If it is positive, we delay the start of the window. If it is negative, we are looking at the "future" rows in the history table.
            lookback_count (int): If the window is specified in terms of count, the start position of the window (0 is the current row).
            lookback_until_position (int): Optional lag to offset the closest point for the window. If it is positive, we delay the start of the window by that many rows. If it is negative, we are looking at those many "future" rows in the history table.
            new_feature_name (str): New name for the PiT feature.

        Returns:
            FeatureGroup: A feature group object with the newly added nested feature.
        """
        return self.client.update_point_in_time_feature(self.feature_group_id, feature_name, history_table_name, aggregation_keys, timestamp_key, historical_timestamp_key, expression, lookback_window_seconds, lookback_window_lag_seconds, lookback_count, lookback_until_position, new_feature_name)

    def create_point_in_time_group(self, group_name: str, window_key: str, aggregation_keys: list, history_table_name: str = None, history_window_key: str = None, history_aggregation_keys: list = None, lookback_window: float = None, lookback_window_lag: float = 0, lookback_count: int = None, lookback_until_position: int = 0):
        """
        Create a Point-in-Time Group

        Args:
            group_name (str): The name of the point in time group.
            window_key (str): Name of feature to use for ordering the rows on the source table.
            aggregation_keys (list): List of keys to perform on the source table for the window aggregation.
            history_table_name (str): The table to use for aggregating, if not provided, the source table will be used.
            history_window_key (str): Name of feature to use for ordering the rows on the history table. If not provided, the windowKey from the source table will be used.
            history_aggregation_keys (list): List of keys to use for join the historical table and performing the window aggregation. If not provided, the aggregationKeys from the source table will be used. Must be the same length and order as the source table's aggregationKeys.
            lookback_window (float): Number of seconds in the past from the current time for the start of the window. If 0, the lookback will include all rows.
            lookback_window_lag (float): Optional lag to offset the closest point for the window. If it is positive, the start of the window is delayed. If it is negative, "future" rows in the history table are used.
            lookback_count (int): If window is specified in terms of count, the start position of the window (0 is the current row).
            lookback_until_position (int): Optional lag to offset the closest point for the window. If it is positive, the start of the window is delayed by that many rows. If it is negative, those many "future" rows in the history table are used.

        Returns:
            FeatureGroup: The feature group after the point in time group has been created.
        """
        return self.client.create_point_in_time_group(self.feature_group_id, group_name, window_key, aggregation_keys, history_table_name, history_window_key, history_aggregation_keys, lookback_window, lookback_window_lag, lookback_count, lookback_until_position)

    def generate_point_in_time_features(self, group_name: str, columns: list, window_functions: list, prefix: str = None):
        """
        Generates and adds PIT features given the selected columns to aggregate over, and the operations to include.

        Args:
            group_name (str): Name of the point-in-time group.
            columns (list): List of columns to generate point-in-time features for.
            window_functions (list): List of window functions to operate on.
            prefix (str): Prefix for generated features, defaults to group name

        Returns:
            FeatureGroup: Feature group object with newly added point-in-time features.
        """
        return self.client.generate_point_in_time_features(self.feature_group_id, group_name, columns, window_functions, prefix)

    def update_point_in_time_group(self, group_name: str, window_key: str = None, aggregation_keys: list = None, history_table_name: str = None, history_window_key: str = None, history_aggregation_keys: list = None, lookback_window: float = None, lookback_window_lag: float = None, lookback_count: int = None, lookback_until_position: int = None):
        """
        Update Point-in-Time Group

        Args:
            group_name (str): The name of the point-in-time group.
            window_key (str): Name of feature which contains the timestamp value for the point-in-time feature.
            aggregation_keys (list): List of keys to use for joining the historical table and performing the window aggregation.
            history_table_name (str): The table to use for aggregating, if not provided, the source table will be used.
            history_window_key (str): Name of feature to use for ordering the rows on the history table. If not provided, the windowKey from the source table will be used.
            history_aggregation_keys (list): List of keys to use for joining the historical table and performing the window aggregation. If not provided, the aggregationKeys from the source table will be used. Must be the same length and order as the source table's aggregationKeys.
            lookback_window (float): Number of seconds in the past from the current time for the start of the window.
            lookback_window_lag (float): Optional lag to offset the closest point for the window. If it is positive, the start of the window is delayed. If it is negative, future rows in the history table are looked at.
            lookback_count (int): If window is specified in terms of count, the start position of the window (0 is the current row).
            lookback_until_position (int): Optional lag to offset the closest point for the window. If it is positive, the start of the window is delayed by that many rows. If it is negative, those many future rows in the history table are looked at.

        Returns:
            FeatureGroup: The feature group after the update has been applied.
        """
        return self.client.update_point_in_time_group(self.feature_group_id, group_name, window_key, aggregation_keys, history_table_name, history_window_key, history_aggregation_keys, lookback_window, lookback_window_lag, lookback_count, lookback_until_position)

    def delete_point_in_time_group(self, group_name: str):
        """
        Delete point in time group

        Args:
            group_name (str): The name of the point in time group.

        Returns:
            FeatureGroup: The feature group after the point in time group has been deleted.
        """
        return self.client.delete_point_in_time_group(self.feature_group_id, group_name)

    def create_point_in_time_group_feature(self, group_name: str, name: str, expression: str):
        """
        Create point in time group feature

        Args:
            group_name (str): The name of the point-in-time group.
            name (str): The name of the feature to add to the point-in-time group.
            expression (str): A SQL aggregate expression which can convert a sequence of rows into a scalar value.

        Returns:
            FeatureGroup: The feature group after the update has been applied.
        """
        return self.client.create_point_in_time_group_feature(self.feature_group_id, group_name, name, expression)

    def update_point_in_time_group_feature(self, group_name: str, name: str, expression: str):
        """
        Update a feature's SQL expression in a point in time group

        Args:
            group_name (str): The name of the point-in-time group.
            name (str): The name of the feature to add to the point-in-time group.
            expression (str): SQL aggregate expression which can convert a sequence of rows into a scalar value.

        Returns:
            FeatureGroup: The feature group after the update has been applied.
        """
        return self.client.update_point_in_time_group_feature(self.feature_group_id, group_name, name, expression)

    def set_feature_type(self, feature: str, feature_type: str, project_id: str = None):
        """
        Set the type of a feature in a feature group. Specify the feature group ID, feature name, and feature type, and the method will return the new column with the changes reflected.

        Args:
            feature (str): The name of the feature.
            feature_type (str): The machine learning type of the data in the feature.
            project_id (str): Optional unique ID associated with the project.

        Returns:
            Schema: The feature group after the data_type is applied.
        """
        return self.client.set_feature_type(self.feature_group_id, feature, feature_type, project_id)

    def concatenate_data(self, source_feature_group_id: str, merge_type: str = 'UNION', replace_until_timestamp: int = None, skip_materialize: bool = False):
        """
        Concatenates data from one Feature Group to another. Feature Groups can be merged if their schemas are compatible, they have the special `updateTimestampKey` column, and (if set) the `primaryKey` column. The second operand in the concatenate operation will be appended to the first operand (merge target).

        Args:
            source_feature_group_id (str): The Feature Group to concatenate with the destination Feature Group.
            merge_type (str): `UNION` or `INTERSECTION`.
            replace_until_timestamp (int): The UNIX timestamp to specify the point until which we will replace data from the source Feature Group.
            skip_materialize (bool): If `True`, will not materialize the concatenated Feature Group.
        """
        return self.client.concatenate_feature_group_data(self.feature_group_id, source_feature_group_id, merge_type, replace_until_timestamp, skip_materialize)

    def remove_concatenation_config(self):
        """
        Removes the concatenation config on a destination feature group.

        Args:
            feature_group_id (str): Unique identifier of the destination feature group to remove the concatenation configuration from.
        """
        return self.client.remove_concatenation_config(self.feature_group_id)

    def refresh(self):
        """
        Calls describe and refreshes the current object's fields

        Returns:
            FeatureGroup: The current object
        """
        self.__dict__.update(self.describe().__dict__)
        return self

    def describe(self):
        """
        Describe a Feature Group.

        Args:
            feature_group_id (str): A unique string identifier associated with the feature group.

        Returns:
            FeatureGroup: The feature group object.
        """
        return self.client.describe_feature_group(self.feature_group_id)

    def set_indexing_config(self, primary_key: str = None, update_timestamp_key: str = None, lookup_keys: list = None):
        """
        Sets various attributes of the feature group used for primary key, deployment lookups and streaming updates.

        Args:
            primary_key (str): Name of the feature which defines the primary key of the feature group.
            update_timestamp_key (str): Name of the feature which defines the update timestamp of the feature group. Used in concatenation and primary key deduplication.
            lookup_keys (list): List of feature names which can be used in the lookup API to restrict the computation to a set of dataset rows. These feature names have to correspond to underlying dataset columns.
        """
        return self.client.set_feature_group_indexing_config(self.feature_group_id, primary_key, update_timestamp_key, lookup_keys)

    def update(self, description: str = None):
        """
        Modify an existing Feature Group.

        Args:
            description (str): Description of the Feature Group.

        Returns:
            FeatureGroup: Updated Feature Group object.
        """
        return self.client.update_feature_group(self.feature_group_id, description)

    def detach_from_template(self):
        """
        Update a feature group to detach it from a template.

        Args:
            feature_group_id (str): Unique string identifier associated with the feature group.

        Returns:
            FeatureGroup: The updated feature group.
        """
        return self.client.detach_feature_group_from_template(self.feature_group_id)

    def update_template_bindings(self, template_bindings: list = None):
        """
        Update the feature group template bindings for a template feature group.

        Args:
            template_bindings (list): Values in these bindings override values set in the template.

        Returns:
            FeatureGroup: Updated feature group.
        """
        return self.client.update_feature_group_template_bindings(self.feature_group_id, template_bindings)

    def update_python_function_bindings(self, python_function_bindings: List):
        """
        Updates an existing Feature Group's Python function bindings from a user-provided Python Function. If a list of feature groups are supplied within the Python function bindings, we will provide DataFrames (Pandas in the case of Python) with the materialized feature groups for those input feature groups as arguments to the function.

        Args:
            python_function_bindings (List): List of python function arguments.
        """
        return self.client.update_feature_group_python_function_bindings(self.feature_group_id, python_function_bindings)

    def update_python_function(self, python_function_name: str, python_function_bindings: List = None, cpu_size: Union[dict, CPUSize] = None, memory: Union[dict, MemorySize] = None, use_gpu: bool = None, use_original_csv_names: bool = None):
        """
        Updates an existing Feature Group's python function from a user provided Python Function. If a list of feature groups are supplied within the python function

        bindings, we will provide as arguments to the function DataFrame's (pandas in the case of Python) with the materialized
        feature groups for those input feature groups.


        Args:
            python_function_name (str): The name of the python function to be associated with the feature group.
            python_function_bindings (List): List of python function arguments.
            cpu_size (CPUSize): Size of the CPU for the feature group python function.
            memory (MemorySize): Memory (in GB) for the feature group python function.
            use_gpu (bool): Whether the feature group needs a gpu or not. Otherwise default to CPU.
            use_original_csv_names (bool): If enabled, it uses the original column names for input feature groups from CSV datasets.
        """
        return self.client.update_feature_group_python_function(self.feature_group_id, python_function_name, python_function_bindings, cpu_size, memory, use_gpu, use_original_csv_names)

    def update_sql_definition(self, sql: str):
        """
        Updates the SQL statement for a feature group.

        Args:
            sql (str): The input SQL statement for the feature group.

        Returns:
            FeatureGroup: The updated feature group.
        """
        return self.client.update_feature_group_sql_definition(self.feature_group_id, sql)

    def update_dataset_feature_expression(self, feature_expression: str):
        """
        Updates the SQL feature expression for a Dataset FeatureGroup's custom features

        Args:
            feature_expression (str): The input SQL statement for the feature group.

        Returns:
            FeatureGroup: The updated feature group.
        """
        return self.client.update_dataset_feature_group_feature_expression(self.feature_group_id, feature_expression)

    def update_version_limit(self, version_limit: int):
        """
        Updates the version limit for the feature group.

        Args:
            version_limit (int): The maximum number of versions permitted for the feature group. Once this limit is exceeded, the oldest versions will be purged in a First-In-First-Out (FIFO) order.

        Returns:
            FeatureGroup: The updated feature group.
        """
        return self.client.update_feature_group_version_limit(self.feature_group_id, version_limit)

    def update_feature(self, name: str, select_expression: str = None, new_name: str = None):
        """
        Modifies an existing feature in a feature group.

        Args:
            name (str): Name of the feature to be updated.
            select_expression (str): SQL statement for modifying the feature.
            new_name (str): New name of the feature.

        Returns:
            FeatureGroup: Updated feature group object.
        """
        return self.client.update_feature(self.feature_group_id, name, select_expression, new_name)

    def list_exports(self):
        """
        Lists all of the feature group exports for the feature group

        Args:
            feature_group_id (str): Unique identifier of the feature group

        Returns:
            list[FeatureGroupExport]: List of feature group exports
        """
        return self.client.list_feature_group_exports(self.feature_group_id)

    def set_modifier_lock(self, locked: bool = True):
        """
        Lock a feature group to prevent modification.

        Args:
            locked (bool): Whether to disable or enable feature group modification (True or False).
        """
        return self.client.set_feature_group_modifier_lock(self.feature_group_id, locked)

    def list_modifiers(self):
        """
        List the users who can modify a given feature group.

        Args:
            feature_group_id (str): Unique string identifier of the feature group.

        Returns:
            ModificationLockInfo: Information about the modification lock status and groups/organizations added to the feature group.
        """
        return self.client.list_feature_group_modifiers(self.feature_group_id)

    def add_user_to_modifiers(self, email: str):
        """
        Adds a user to a feature group.

        Args:
            email (str): The email address of the user to be added.
        """
        return self.client.add_user_to_feature_group_modifiers(self.feature_group_id, email)

    def add_organization_group_to_modifiers(self, organization_group_id: str):
        """
        Add OrganizationGroup to a feature group modifiers list

        Args:
            organization_group_id (str): Unique string identifier of the organization group.
        """
        return self.client.add_organization_group_to_feature_group_modifiers(self.feature_group_id, organization_group_id)

    def remove_user_from_modifiers(self, email: str):
        """
        Removes a user from a specified feature group.

        Args:
            email (str): The email address of the user to be removed.
        """
        return self.client.remove_user_from_feature_group_modifiers(self.feature_group_id, email)

    def remove_organization_group_from_modifiers(self, organization_group_id: str):
        """
        Removes an OrganizationGroup from a feature group modifiers list

        Args:
            organization_group_id (str): The unique ID associated with the organization group.
        """
        return self.client.remove_organization_group_from_feature_group_modifiers(self.feature_group_id, organization_group_id)

    def delete_feature(self, name: str):
        """
        Removes a feature from the feature group.

        Args:
            name (str): Name of the feature to be deleted.

        Returns:
            FeatureGroup: Updated feature group object.
        """
        return self.client.delete_feature(self.feature_group_id, name)

    def delete(self):
        """
        Deletes a Feature Group.

        Args:
            feature_group_id (str): Unique string identifier for the feature group to be removed.
        """
        return self.client.delete_feature_group(self.feature_group_id)

    def create_version(self, variable_bindings: dict = None):
        """
        Creates a snapshot for a specified feature group. Triggers materialization of the feature group. The new version of the feature group is created after it has materialized.

        Args:
            variable_bindings (dict): Dictionary defining variable bindings that override parent feature group values.

        Returns:
            FeatureGroupVersion: A feature group version.
        """
        return self.client.create_feature_group_version(self.feature_group_id, variable_bindings)

    def list_versions(self, limit: int = 100, start_after_version: str = None):
        """
        Retrieves a list of all feature group versions for the specified feature group.

        Args:
            limit (int): The maximum length of the returned versions.
            start_after_version (str): Results will start after this version.

        Returns:
            list[FeatureGroupVersion]: A list of feature group versions.
        """
        return self.client.list_feature_group_versions(self.feature_group_id, limit, start_after_version)

    def set_export_connector_config(self, feature_group_export_config: Union[dict, FeatureGroupExportConfig] = None):
        """
        Sets FG export config for the given feature group.

        Args:
            feature_group_export_config (FeatureGroupExportConfig): The export config to be set for the given feature group.
        """
        return self.client.set_feature_group_export_connector_config(self.feature_group_id, feature_group_export_config)

    def set_export_on_materialization(self, enable: bool):
        """
        Can be used to enable or disable exporting feature group data to the export connector associated with the feature group.

        Args:
            enable (bool): If true, will enable exporting feature group to the connector. If false, will disable.
        """
        return self.client.set_export_on_materialization(self.feature_group_id, enable)

    def create_template(self, name: str, template_sql: str, template_variables: list, description: str = None, template_bindings: list = None, should_attach_feature_group_to_template: bool = False):
        """
        Create a feature group template.

        Args:
            name (str): User-friendly name for this feature group template.
            template_sql (str): The template SQL that will be resolved by applying values from the template variables to generate SQL for a feature group.
            template_variables (list): The template variables for resolving the template.
            description (str): Description of this feature group template.
            template_bindings (list): If the feature group will be attached to the newly created template, set these variable bindings on that feature group.
            should_attach_feature_group_to_template (bool): Set to `True` to convert the feature group to a template feature group and attach it to the newly created template.

        Returns:
            FeatureGroupTemplate: The created feature group template.
        """
        return self.client.create_feature_group_template(self.feature_group_id, name, template_sql, template_variables, description, template_bindings, should_attach_feature_group_to_template)

    def suggest_template_for(self):
        """
        Suggest values for a feature gruop template, based on a feature group.

        Args:
            feature_group_id (str): Unique identifier associated with the feature group to use for suggesting values to use in the template.

        Returns:
            FeatureGroupTemplate: The suggested feature group template.
        """
        return self.client.suggest_feature_group_template_for_feature_group(self.feature_group_id)

    def get_recent_streamed_data(self):
        """
        Returns recently streamed data to a streaming feature group.

        Args:
            feature_group_id (str): Unique string identifier associated with the feature group.
        """
        return self.client.get_recent_feature_group_streamed_data(self.feature_group_id)

    def append_data(self, streaming_token: str, data: dict):
        """
        Appends new data into the feature group for a given lookup key recordId.

        Args:
            streaming_token (str): The streaming token for authenticating requests.
            data (dict): The data to record as a JSON object.
        """
        return self.client.append_data(self.feature_group_id, streaming_token, data)

    def append_multiple_data(self, streaming_token: str, data: list):
        """
        Appends new data into the feature group for a given lookup key recordId.

        Args:
            streaming_token (str): Streaming token for authenticating requests.
            data (list): Data to record, as a list of JSON objects.
        """
        return self.client.append_multiple_data(self.feature_group_id, streaming_token, data)

    def upsert_data(self, data: dict, streaming_token: str = None, blobs: None = None):
        """
        Update new data into the feature group for a given lookup key record ID if the record ID is found; otherwise, insert new data into the feature group.

        Args:
            data (dict): The data to record, in JSON format.
            streaming_token (str): Optional streaming token for authenticating requests if upserting to streaming FG.
            blobs (None): A dictionary of binary data to populate file fields' in data to upsert to the streaming FG.

        Returns:
            FeatureGroupRow: The feature group row that was upserted.
        """
        return self.client.upsert_data(self.feature_group_id, data, streaming_token, blobs)

    def delete_data(self, primary_key: str):
        """
        Deletes a row from the feature group given the primary key

        Args:
            primary_key (str): The primary key value for which to delete the feature group row
        """
        return self.client.delete_data(self.feature_group_id, primary_key)

    def get_data(self, primary_key: str = None, num_rows: int = None):
        """
        Gets the feature group rows for online updatable feature groups.

        If primary key is set, row corresponding to primary_key is returned.
        If num_rows is set, we return maximum of num_rows latest updated rows.


        Args:
            primary_key (str): The primary key value for which to retrieve the feature group row (only for online feature groups).
            num_rows (int): Maximum number of rows to return from the feature group

        Returns:
            list[FeatureGroupRow]: A list of feature group rows.
        """
        return self.client.get_data(self.feature_group_id, primary_key, num_rows)

    def get_natural_language_explanation(self, feature_group_version: str = None, model_id: str = None):
        """
        Returns the saved natural language explanation of an artifact with given ID. The artifact can be - Feature Group or Feature Group Version or Model

        Args:
            feature_group_version (str): A unique string identifier associated with the Feature Group Version.
            model_id (str): A unique string identifier associated with the Model.

        Returns:
            NaturalLanguageExplanation: The object containing natural language explanation(s) as field(s).
        """
        return self.client.get_natural_language_explanation(self.feature_group_id, feature_group_version, model_id)

    def generate_natural_language_explanation(self, feature_group_version: str = None, model_id: str = None):
        """
        Generates natural language explanation of an artifact with given ID. The artifact can be - Feature Group or Feature Group Version or Model

        Args:
            feature_group_version (str): A unique string identifier associated with the Feature Group Version.
            model_id (str): A unique string identifier associated with the Model.

        Returns:
            NaturalLanguageExplanation: The object containing natural language explanation(s) as field(s).
        """
        return self.client.generate_natural_language_explanation(self.feature_group_id, feature_group_version, model_id)

    def wait_for_dataset(self, timeout: int = 7200):
        """
            A waiting call until the feature group's dataset, if any, is ready for use.

        Args:
            timeout (int): The waiting time given to the call to finish, if it doesn't finish by the allocated time, the call is said to be timed out. Default value given is 7200 seconds.
        """
        dataset_id = self.dataset_id
        if not dataset_id:
            return  # todo check return value type
        dataset = self.client.describe_dataset(dataset_id=dataset_id)
        dataset.wait_for_inspection(timeout=timeout)
        return self.refresh()

    def wait_for_upload(self, timeout: int = 7200):
        """
            Waits for a feature group created from a dataframe to be ready for materialization and version creation.

        Args:
            timeout (int): The waiting time given to the call to finish, if it doesn't finish by the allocated time, the call is said to be timed out. Default value given is 7200 seconds.
        """
        self.wait_for_dataset(timeout=timeout)
        return self.refresh()

    def wait_for_materialization(self, timeout: int = 7200):
        """
        A waiting call until feature group is materialized.

        Args:
            timeout (int): The waiting time given to the call to finish, if it doesn't finish by the allocated time, the call is said to be timed out. Default value given is 7200 seconds.
        """
        latest_feature_group_version = self.describe().latest_feature_group_version
        if not latest_feature_group_version:
            from .client import ApiException
            raise ApiException(
                409, 'This feature group does not have any versions')
        self.latest_feature_group_version = latest_feature_group_version.wait_for_materialization(
            timeout=timeout)
        return self

    def wait_for_streaming_ready(self, timeout: int = 600):
        """
        Waits for the feature group indexing config to be applied for streaming

        Args:
            timeout (int): The waiting time given to the call to finish, if it doesn't finish by the allocated time, the call is said to be timed out. Default value given is 600 seconds.
        """
        if not self.streaming_enabled:
            from .client import ApiException
            raise ApiException(409, 'Feature group is not streaming enabled')
        return self.client._poll(self, {False}, poll_args={'streaming_status': True}, timeout=timeout)

    def get_status(self, streaming_status: bool = False):
        """
        Gets the status of the feature group.

        Returns:
            str: A string describing the status of a feature group (pending, complete, etc.).
        """
        if streaming_status:
            return self.describe().streaming_ready
        return self.describe().latest_feature_group_version.status

    def load_as_pandas(self):
        """
        Loads the feature groups into a python pandas dataframe.

        Returns:
            DataFrame: A pandas dataframe with annotations and text_snippet columns.
        """
        latest_version = self.materialize().latest_feature_group_version
        return latest_version.load_as_pandas()

    def load_as_pandas_documents(self, doc_id_column: str = 'doc_id', document_column: str = 'page_infos'):
        """
        Loads a feature group with documents data into a pandas dataframe.

        Args:
            doc_id_column (str): The name of the feature / column containing the document ID.
            document_column (str): The name of the feature / column which either contains the document data itself or page infos with path to remotely stored documents. This column will be replaced with the extracted document data.

        Returns:
            DataFrame: A pandas dataframe containing the extracted document data.
        """
        latest_version = self.materialize().latest_feature_group_version
        return latest_version.load_as_pandas_documents(doc_id_column, document_column)

    def describe_dataset(self):
        """
        Displays the dataset attached to a feature group.

        Returns:
            Dataset: A dataset object with all the relevant information about the dataset.
        """
        if self.dataset_id:
            return self.client.describe_dataset(self.dataset_id)

    def materialize(self):
        """
        Materializes the feature group's latest change at the api call time. It'll skip materialization if no change since the current latest version.

        Returns:
            FeatureGroup: A feature group object with the lastest changes materialized.
        """
        self.refresh()
        if not self.latest_feature_group_version or self.latest_version_outdated:
            self.latest_feature_group_version = self.create_version()
        return self.wait_for_materialization()
