from typing import Union

from .api_class import (
    ApplicationConnectorDatasetConfig, AttachmentParsingConfig,
    DatasetDocumentProcessingConfig, DataType, DocumentProcessingConfig,
    ParsingConfig
)
from .dataset_column import DatasetColumn
from .dataset_version import DatasetVersion
from .refresh_schedule import RefreshSchedule
from .return_class import AbstractApiClass


class Dataset(AbstractApiClass):
    """
        A dataset reference

        Args:
            client (ApiClient): An authenticated API Client instance
            datasetId (str): The unique identifier of the dataset.
            sourceType (str): The source of the Dataset. EXTERNAL_SERVICE, UPLOAD, or STREAMING.
            dataSource (str): Location of data. It may be a URI such as an s3 bucket or the database table.
            createdAt (str): The timestamp at which this dataset was created.
            ignoreBefore (str): The timestamp at which all previous events are ignored when training.
            ephemeral (bool): The dataset is ephemeral and not used for training.
            lookbackDays (int): Specific to streaming datasets, this specifies how many days worth of data to include when generating a snapshot. Value of 0 indicates leaves this selection to the system.
            databaseConnectorId (str): The Database Connector used.
            databaseConnectorConfig (dict): The database connector query used to retrieve data.
            connectorType (str): The type of connector used to get this dataset FILE or DATABASE.
            featureGroupTableName (str): The table name of the dataset's feature group
            applicationConnectorId (str): The Application Connector used.
            applicationConnectorConfig (dict): The application connector query used to retrieve data.
            incremental (bool): If dataset is an incremental dataset.
            isDocumentset (bool): If dataset is a documentset.
            extractBoundingBoxes (bool): Signifies whether to extract bounding boxes out of the documents. Only valid if is_documentset if True.
            mergeFileSchemas (bool): If the merge file schemas policy is enabled.
            referenceOnlyDocumentset (bool): Signifies whether to save the data reference only. Only valid if is_documentset if True.
            versionLimit (int): Version limit for the dataset.
            latestDatasetVersion (DatasetVersion): The latest version of this dataset.
            schema (DatasetColumn): List of resolved columns.
            refreshSchedules (RefreshSchedule): List of schedules that determines when the next version of the dataset will be created.
            parsingConfig (ParsingConfig): The parsing config used for dataset.
            documentProcessingConfig (DocumentProcessingConfig): The document processing config used for dataset (when is_documentset is True).
            attachmentParsingConfig (AttachmentParsingConfig): The attachment parsing config used for dataset (eg. for salesforce attachment parsing)
    """

    def __init__(self, client, datasetId=None, sourceType=None, dataSource=None, createdAt=None, ignoreBefore=None, ephemeral=None, lookbackDays=None, databaseConnectorId=None, databaseConnectorConfig=None, connectorType=None, featureGroupTableName=None, applicationConnectorId=None, applicationConnectorConfig=None, incremental=None, isDocumentset=None, extractBoundingBoxes=None, mergeFileSchemas=None, referenceOnlyDocumentset=None, versionLimit=None, schema={}, refreshSchedules={}, latestDatasetVersion={}, parsingConfig={}, documentProcessingConfig={}, attachmentParsingConfig={}):
        super().__init__(client, datasetId)
        self.dataset_id = datasetId
        self.source_type = sourceType
        self.data_source = dataSource
        self.created_at = createdAt
        self.ignore_before = ignoreBefore
        self.ephemeral = ephemeral
        self.lookback_days = lookbackDays
        self.database_connector_id = databaseConnectorId
        self.database_connector_config = databaseConnectorConfig
        self.connector_type = connectorType
        self.feature_group_table_name = featureGroupTableName
        self.application_connector_id = applicationConnectorId
        self.application_connector_config = applicationConnectorConfig
        self.incremental = incremental
        self.is_documentset = isDocumentset
        self.extract_bounding_boxes = extractBoundingBoxes
        self.merge_file_schemas = mergeFileSchemas
        self.reference_only_documentset = referenceOnlyDocumentset
        self.version_limit = versionLimit
        self.schema = client._build_class(DatasetColumn, schema)
        self.refresh_schedules = client._build_class(
            RefreshSchedule, refreshSchedules)
        self.latest_dataset_version = client._build_class(
            DatasetVersion, latestDatasetVersion)
        self.parsing_config = client._build_class(ParsingConfig, parsingConfig)
        self.document_processing_config = client._build_class(
            DocumentProcessingConfig, documentProcessingConfig)
        self.attachment_parsing_config = client._build_class(
            AttachmentParsingConfig, attachmentParsingConfig)
        self.deprecated_keys = {}

    def __repr__(self):
        repr_dict = {f'dataset_id': repr(self.dataset_id), f'source_type': repr(self.source_type), f'data_source': repr(self.data_source), f'created_at': repr(self.created_at), f'ignore_before': repr(self.ignore_before), f'ephemeral': repr(self.ephemeral), f'lookback_days': repr(self.lookback_days), f'database_connector_id': repr(self.database_connector_id), f'database_connector_config': repr(self.database_connector_config), f'connector_type': repr(self.connector_type), f'feature_group_table_name': repr(self.feature_group_table_name), f'application_connector_id': repr(self.application_connector_id), f'application_connector_config': repr(
            self.application_connector_config), f'incremental': repr(self.incremental), f'is_documentset': repr(self.is_documentset), f'extract_bounding_boxes': repr(self.extract_bounding_boxes), f'merge_file_schemas': repr(self.merge_file_schemas), f'reference_only_documentset': repr(self.reference_only_documentset), f'version_limit': repr(self.version_limit), f'schema': repr(self.schema), f'refresh_schedules': repr(self.refresh_schedules), f'latest_dataset_version': repr(self.latest_dataset_version), f'parsing_config': repr(self.parsing_config), f'document_processing_config': repr(self.document_processing_config), f'attachment_parsing_config': repr(self.attachment_parsing_config)}
        class_name = "Dataset"
        repr_str = ',\n  '.join([f'{key}={value}' for key, value in repr_dict.items(
        ) if getattr(self, key, None) is not None and key not in self.deprecated_keys])
        return f"{class_name}({repr_str})"

    def to_dict(self):
        """
        Get a dict representation of the parameters in this class

        Returns:
            dict: The dict value representation of the class parameters
        """
        resp = {'dataset_id': self.dataset_id, 'source_type': self.source_type, 'data_source': self.data_source, 'created_at': self.created_at, 'ignore_before': self.ignore_before, 'ephemeral': self.ephemeral, 'lookback_days': self.lookback_days, 'database_connector_id': self.database_connector_id, 'database_connector_config': self.database_connector_config, 'connector_type': self.connector_type, 'feature_group_table_name': self.feature_group_table_name, 'application_connector_id': self.application_connector_id, 'application_connector_config': self.application_connector_config, 'incremental': self.incremental, 'is_documentset': self.is_documentset,
                'extract_bounding_boxes': self.extract_bounding_boxes, 'merge_file_schemas': self.merge_file_schemas, 'reference_only_documentset': self.reference_only_documentset, 'version_limit': self.version_limit, 'schema': self._get_attribute_as_dict(self.schema), 'refresh_schedules': self._get_attribute_as_dict(self.refresh_schedules), 'latest_dataset_version': self._get_attribute_as_dict(self.latest_dataset_version), 'parsing_config': self._get_attribute_as_dict(self.parsing_config), 'document_processing_config': self._get_attribute_as_dict(self.document_processing_config), 'attachment_parsing_config': self._get_attribute_as_dict(self.attachment_parsing_config)}
        return {key: value for key, value in resp.items() if value is not None and key not in self.deprecated_keys}

    def get_raw_data_from_realtime(self, check_permissions: bool = False, start_time: str = None, end_time: str = None, column_filter: dict = None):
        """
        Returns raw data from a realtime dataset. Only Microsoft Teams datasets are supported currently due to data size constraints in realtime datasets.

        Args:
            check_permissions (bool): If True, checks user permissions using session email.
            start_time (str): Start time filter (inclusive) for created_date_time_t in ISO 8601 format (e.g. 2025-05-13T08:25:11Z or 2025-05-13T08:25:11+00:00).
            end_time (str): End time filter (inclusive) for created_date_time_t in ISO 8601 format (e.g. 2025-05-13T08:25:11Z or 2025-05-13T08:25:11+00:00).
            column_filter (dict): Dictionary mapping column names to filter values. Only rows matching all column filters will be returned.
        """
        return self.client.get_raw_data_from_realtime_dataset(self.dataset_id, check_permissions, start_time, end_time, column_filter)

    def create_version_from_file_connector(self, location: str = None, file_format: str = None, csv_delimiter: str = None, merge_file_schemas: bool = None, parsing_config: Union[dict, ParsingConfig] = None, sql_query: str = None):
        """
        Creates a new version of the specified dataset.

        Args:
            location (str): External URI to import the dataset from. If not specified, the last location will be used.
            file_format (str): File format to be used. If not specified, the service will try to detect the file format.
            csv_delimiter (str): If the file format is CSV, use a specific CSV delimiter.
            merge_file_schemas (bool): Signifies if the merge file schema policy is enabled.
            parsing_config (ParsingConfig): Custom config for dataset parsing.
            sql_query (str): The SQL query to use when fetching data from the specified location. Use `__TABLE__` as a placeholder for the table name. For example: "SELECT * FROM __TABLE__ WHERE event_date > '2021-01-01'". If not provided, the entire dataset from the specified location will be imported.

        Returns:
            DatasetVersion: The new Dataset Version created.
        """
        return self.client.create_dataset_version_from_file_connector(self.dataset_id, location, file_format, csv_delimiter, merge_file_schemas, parsing_config, sql_query)

    def create_version_from_database_connector(self, object_name: str = None, columns: str = None, query_arguments: str = None, sql_query: str = None):
        """
        Creates a new version of the specified dataset.

        Args:
            object_name (str): The name/ID of the object in the service to query. If not specified, the last name will be used.
            columns (str): The columns to query from the external service object. If not specified, the last columns will be used.
            query_arguments (str): Additional query arguments to filter the data. If not specified, the last arguments will be used.
            sql_query (str): The full SQL query to use when fetching data. If present, this parameter will override object_name, columns, and query_arguments.

        Returns:
            DatasetVersion: The new Dataset Version created.
        """
        return self.client.create_dataset_version_from_database_connector(self.dataset_id, object_name, columns, query_arguments, sql_query)

    def create_version_from_application_connector(self, dataset_config: Union[dict, ApplicationConnectorDatasetConfig] = None):
        """
        Creates a new version of the specified dataset.

        Args:
            dataset_config (ApplicationConnectorDatasetConfig): Dataset config for the application connector. If any of the fields are not specified, the last values will be used.

        Returns:
            DatasetVersion: The new Dataset Version created.
        """
        return self.client.create_dataset_version_from_application_connector(self.dataset_id, dataset_config)

    def create_version_from_upload(self, file_format: str = None):
        """
        Creates a new version of the specified dataset using a local file upload.

        Args:
            file_format (str): File format to be used. If not specified, the service will attempt to detect the file format.

        Returns:
            Upload: Token to be used when uploading file parts.
        """
        return self.client.create_dataset_version_from_upload(self.dataset_id, file_format)

    def create_version_from_document_reprocessing(self, document_processing_config: Union[dict, DatasetDocumentProcessingConfig] = None):
        """
        Creates a new dataset version for a source docstore dataset with the provided document processing configuration. This does not re-import the data but uses the same data which is imported in the latest dataset version and only performs document processing on it.

        Args:
            document_processing_config (DatasetDocumentProcessingConfig): The document processing configuration to use for the new dataset version. If not specified, the document processing configuration from the source dataset will be used.

        Returns:
            DatasetVersion: The new dataset version created.
        """
        return self.client.create_dataset_version_from_document_reprocessing(self.dataset_id, document_processing_config)

    def snapshot_streaming_data(self):
        """
        Snapshots the current data in the streaming dataset.

        Args:
            dataset_id (str): The unique ID associated with the dataset.

        Returns:
            DatasetVersion: The new Dataset Version created by taking a snapshot of the current data in the streaming dataset.
        """
        return self.client.snapshot_streaming_data(self.dataset_id)

    def set_column_data_type(self, column: str, data_type: Union[dict, DataType]):
        """
        Set a Dataset's column type.

        Args:
            column (str): The name of the column.
            data_type (DataType): The type of the data in the column. Note: Some ColumnMappings may restrict the options or explicitly set the DataType.

        Returns:
            Dataset: The dataset and schema after the data type has been set.
        """
        return self.client.set_dataset_column_data_type(self.dataset_id, column, data_type)

    def set_streaming_retention_policy(self, retention_hours: int = None, retention_row_count: int = None, ignore_records_before_timestamp: int = None):
        """
        Sets the streaming retention policy.

        Args:
            retention_hours (int): Number of hours to retain streamed data in memory.
            retention_row_count (int): Number of rows to retain streamed data in memory.
            ignore_records_before_timestamp (int): The Unix timestamp (in seconds) to use as a cutoff to ignore all entries sent before it
        """
        return self.client.set_streaming_retention_policy(self.dataset_id, retention_hours, retention_row_count, ignore_records_before_timestamp)

    def get_schema(self):
        """
        Retrieves the column schema of a dataset.

        Args:
            dataset_id (str): Unique string identifier of the dataset schema to look up.

        Returns:
            list[DatasetColumn]: List of column schema definitions.
        """
        return self.client.get_dataset_schema(self.dataset_id)

    def set_database_connector_config(self, database_connector_id: str, object_name: str = None, columns: str = None, query_arguments: str = None, sql_query: str = None):
        """
        Sets database connector config for a dataset. This method is currently only supported for streaming datasets.

        Args:
            database_connector_id (str): Unique String Identifier of the Database Connector to import the dataset from.
            object_name (str): If applicable, the name/ID of the object in the service to query.
            columns (str): The columns to query from the external service object.
            query_arguments (str): Additional query arguments to filter the data.
            sql_query (str): The full SQL query to use when fetching data. If present, this parameter will override `object_name`, `columns` and `query_arguments`.
        """
        return self.client.set_dataset_database_connector_config(self.dataset_id, database_connector_id, object_name, columns, query_arguments, sql_query)

    def update_version_limit(self, version_limit: int):
        """
        Updates the version limit for the specified dataset.

        Args:
            version_limit (int): The maximum number of versions permitted for the feature group. Once this limit is exceeded, the oldest versions will be purged in a First-In-First-Out (FIFO) order.

        Returns:
            Dataset: The updated dataset.
        """
        return self.client.update_dataset_version_limit(self.dataset_id, version_limit)

    def refresh(self):
        """
        Calls describe and refreshes the current object's fields

        Returns:
            Dataset: The current object
        """
        self.__dict__.update(self.describe().__dict__)
        return self

    def describe(self):
        """
        Retrieves a full description of the specified dataset, with attributes such as its ID, name, source type, etc.

        Args:
            dataset_id (str): The unique ID associated with the dataset.

        Returns:
            Dataset: The dataset.
        """
        return self.client.describe_dataset(self.dataset_id)

    def list_versions(self, limit: int = 100, start_after_version: str = None):
        """
        Retrieves a list of all dataset versions for the specified dataset.

        Args:
            limit (int): The maximum length of the list of all dataset versions.
            start_after_version (str): The ID of the version after which the list starts.

        Returns:
            list[DatasetVersion]: A list of dataset versions.
        """
        return self.client.list_dataset_versions(self.dataset_id, limit, start_after_version)

    def delete(self):
        """
        Deletes the specified dataset from the organization.

        Args:
            dataset_id (str): Unique string identifier of the dataset to delete.
        """
        return self.client.delete_dataset(self.dataset_id)

    def wait_for_import(self, timeout=900):
        """
        A waiting call until dataset is imported.

        Args:
            timeout (int): The waiting time given to the call to finish, if it doesn't finish by the allocated time, the call is said to be timed out.

        """
        latest_dataset_version = self.describe().latest_dataset_version
        if not latest_dataset_version:
            from .client import ApiException
            raise ApiException(409, 'This dataset does not have any versions')
        self.latest_dataset_version = latest_dataset_version.wait_for_import(
            timeout=timeout)
        return self

    def wait_for_inspection(self, timeout=None):
        """
        A waiting call until dataset is completely inspected.

        Args:
            timeout (int): The waiting time given to the call to finish, if it doesn't finish by the allocated time, the call is said to be timed out.
        """
        latest_dataset_version = self.describe().latest_dataset_version
        if not latest_dataset_version:
            from .client import ApiException
            raise ApiException(409, 'This dataset does not have any versions')
        self.latest_dataset_version = latest_dataset_version.wait_for_inspection(
            timeout=timeout)
        return self

    def get_status(self):
        """
        Gets the status of the latest dataset version.

        Returns:
            str: A string describing the status of a dataset (importing, inspecting, complete, etc.).
        """
        return self.describe().latest_dataset_version.status

    def describe_feature_group(self):
        """
        Gets the feature group attached to the dataset.

        Returns:
            FeatureGroup: A feature group object.
        """
        return self.client.describe_feature_group_by_table_name(self.feature_group_table_name)

    def create_refresh_policy(self, cron: str):
        """
        To create a refresh policy for a dataset.

        Args:
            cron (str): A cron style string to set the refresh time.

        Returns:
            RefreshPolicy: The refresh policy object.
        """
        return self.client.create_refresh_policy(self.feature_group_table_name, cron, 'DATASET', dataset_ids=[self.id])

    def list_refresh_policies(self):
        """
        Gets the refresh policies in a list.

        Returns:
            List[RefreshPolicy]: A list of refresh policy objects.
        """
        return self.client.list_refresh_policies(dataset_ids=[self.id])
