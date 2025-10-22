from typing import List

from .api_class import PythonFunctionArgument
from .code_source import CodeSource
from .pipeline_reference import PipelineReference
from .pipeline_step import PipelineStep
from .pipeline_version import PipelineVersion
from .return_class import AbstractApiClass


class Pipeline(AbstractApiClass):
    """
        A Pipeline For Steps.

        Args:
            client (ApiClient): An authenticated API Client instance
            pipelineName (str): The name of the pipeline this step is a part of.
            pipelineId (str): The reference to the pipeline this step belongs to.
            createdAt (str): The date and time which the pipeline was created.
            notebookId (str): The reference to the notebook this pipeline belongs to.
            cron (str): A cron-style string that describes when this refresh policy is to be executed in UTC
            nextRunTime (str): The next time this pipeline will be run.
            isProd (bool): Whether this pipeline is a production pipeline.
            warning (str): Warning message for possible errors that might occur if the pipeline is run.
            createdBy (str): The email of the user who created the pipeline
            steps (PipelineStep): A list of the pipeline steps attached to the pipeline.
            pipelineReferences (PipelineReference): A list of references from the pipeline to other objects
            latestPipelineVersion (PipelineVersion): The latest version of the pipeline.
            codeSource (CodeSource): information on the source code
            pipelineVariableMappings (PythonFunctionArgument): A description of the function variables into the pipeline.
    """

    def __init__(self, client, pipelineName=None, pipelineId=None, createdAt=None, notebookId=None, cron=None, nextRunTime=None, isProd=None, warning=None, createdBy=None, steps={}, pipelineReferences={}, latestPipelineVersion={}, codeSource={}, pipelineVariableMappings={}):
        super().__init__(client, pipelineId)
        self.pipeline_name = pipelineName
        self.pipeline_id = pipelineId
        self.created_at = createdAt
        self.notebook_id = notebookId
        self.cron = cron
        self.next_run_time = nextRunTime
        self.is_prod = isProd
        self.warning = warning
        self.created_by = createdBy
        self.steps = client._build_class(PipelineStep, steps)
        self.pipeline_references = client._build_class(
            PipelineReference, pipelineReferences)
        self.latest_pipeline_version = client._build_class(
            PipelineVersion, latestPipelineVersion)
        self.code_source = client._build_class(CodeSource, codeSource)
        self.pipeline_variable_mappings = client._build_class(
            PythonFunctionArgument, pipelineVariableMappings)
        self.deprecated_keys = {}

    def __repr__(self):
        repr_dict = {f'pipeline_name': repr(self.pipeline_name), f'pipeline_id': repr(self.pipeline_id), f'created_at': repr(self.created_at), f'notebook_id': repr(self.notebook_id), f'cron': repr(self.cron), f'next_run_time': repr(self.next_run_time), f'is_prod': repr(self.is_prod), f'warning': repr(
            self.warning), f'created_by': repr(self.created_by), f'steps': repr(self.steps), f'pipeline_references': repr(self.pipeline_references), f'latest_pipeline_version': repr(self.latest_pipeline_version), f'code_source': repr(self.code_source), f'pipeline_variable_mappings': repr(self.pipeline_variable_mappings)}
        class_name = "Pipeline"
        repr_str = ',\n  '.join([f'{key}={value}' for key, value in repr_dict.items(
        ) if getattr(self, key, None) is not None and key not in self.deprecated_keys])
        return f"{class_name}({repr_str})"

    def to_dict(self):
        """
        Get a dict representation of the parameters in this class

        Returns:
            dict: The dict value representation of the class parameters
        """
        resp = {'pipeline_name': self.pipeline_name, 'pipeline_id': self.pipeline_id, 'created_at': self.created_at, 'notebook_id': self.notebook_id, 'cron': self.cron, 'next_run_time': self.next_run_time, 'is_prod': self.is_prod, 'warning': self.warning, 'created_by': self.created_by, 'steps': self._get_attribute_as_dict(
            self.steps), 'pipeline_references': self._get_attribute_as_dict(self.pipeline_references), 'latest_pipeline_version': self._get_attribute_as_dict(self.latest_pipeline_version), 'code_source': self._get_attribute_as_dict(self.code_source), 'pipeline_variable_mappings': self._get_attribute_as_dict(self.pipeline_variable_mappings)}
        return {key: value for key, value in resp.items() if value is not None and key not in self.deprecated_keys}

    def refresh(self):
        """
        Calls describe and refreshes the current object's fields

        Returns:
            Pipeline: The current object
        """
        self.__dict__.update(self.describe().__dict__)
        return self

    def describe(self):
        """
        Describes a given pipeline.

        Args:
            pipeline_id (str): The ID of the pipeline to describe.

        Returns:
            Pipeline: An object describing a Pipeline
        """
        return self.client.describe_pipeline(self.pipeline_id)

    def update(self, project_id: str = None, pipeline_variable_mappings: List = None, cron: str = None, is_prod: bool = None):
        """
        Updates a pipeline for executing multiple steps.

        Args:
            project_id (str): A unique string identifier for the pipeline.
            pipeline_variable_mappings (List): List of Python function arguments for the pipeline.
            cron (str): A cron-like string specifying the frequency of the scheduled pipeline runs.
            is_prod (bool): Whether the pipeline is a production pipeline or not.

        Returns:
            Pipeline: An object that describes a Pipeline.
        """
        return self.client.update_pipeline(self.pipeline_id, project_id, pipeline_variable_mappings, cron, is_prod)

    def rename(self, pipeline_name: str):
        """
        Renames a pipeline.

        Args:
            pipeline_name (str): The new name of the pipeline.

        Returns:
            Pipeline: An object that describes a Pipeline.
        """
        return self.client.rename_pipeline(self.pipeline_id, pipeline_name)

    def delete(self):
        """
        Deletes a pipeline.

        Args:
            pipeline_id (str): The ID of the pipeline to delete.
        """
        return self.client.delete_pipeline(self.pipeline_id)

    def list_versions(self, limit: int = 200):
        """
        Lists the pipeline versions for a specified pipeline

        Args:
            limit (int): The maximum number of pipeline versions to return.

        Returns:
            list[PipelineVersion]: A list of pipeline versions.
        """
        return self.client.list_pipeline_versions(self.pipeline_id, limit)

    def run(self, pipeline_variable_mappings: List = None):
        """
        Runs a specified pipeline with the arguments provided.

        Args:
            pipeline_variable_mappings (List): List of Python function arguments for the pipeline.

        Returns:
            PipelineVersion: The object describing the pipeline
        """
        return self.client.run_pipeline(self.pipeline_id, pipeline_variable_mappings)

    def create_step(self, step_name: str, function_name: str = None, source_code: str = None, step_input_mappings: List = None, output_variable_mappings: List = None, step_dependencies: list = None, package_requirements: list = None, cpu_size: str = None, memory: int = None, timeout: int = None):
        """
        Creates a step in a given pipeline.

        Args:
            step_name (str): The name of the step.
            function_name (str): The name of the Python function.
            source_code (str): Contents of a valid Python source code file. The source code should contain the transform feature group functions. A list of allowed imports and system libraries for each language is specified in the user functions documentation section.
            step_input_mappings (List): List of Python function arguments.
            output_variable_mappings (List): List of Python function outputs.
            step_dependencies (list): List of step names this step depends on.
            package_requirements (list): List of package requirement strings. For example: ['numpy==1.2.3', 'pandas>=1.4.0'].
            cpu_size (str): Size of the CPU for the step function.
            memory (int): Memory (in GB) for the step function.
            timeout (int): Timeout for the step in minutes, default is 300 minutes.

        Returns:
            Pipeline: Object describing the pipeline.
        """
        return self.client.create_pipeline_step(self.pipeline_id, step_name, function_name, source_code, step_input_mappings, output_variable_mappings, step_dependencies, package_requirements, cpu_size, memory, timeout)

    def describe_step_by_name(self, step_name: str):
        """
        Describes a pipeline step by the step name.

        Args:
            step_name (str): The name of the step.

        Returns:
            PipelineStep: An object describing the pipeline step.
        """
        return self.client.describe_pipeline_step_by_name(self.pipeline_id, step_name)

    def unset_refresh_schedule(self):
        """
        Deletes the refresh schedule for a given pipeline.

        Args:
            pipeline_id (str): The id of the pipeline.

        Returns:
            Pipeline: Object describing the pipeline.
        """
        return self.client.unset_pipeline_refresh_schedule(self.pipeline_id)

    def pause_refresh_schedule(self):
        """
        Pauses the refresh schedule for a given pipeline.

        Args:
            pipeline_id (str): The id of the pipeline.

        Returns:
            Pipeline: Object describing the pipeline.
        """
        return self.client.pause_pipeline_refresh_schedule(self.pipeline_id)

    def resume_refresh_schedule(self):
        """
        Resumes the refresh schedule for a given pipeline.

        Args:
            pipeline_id (str): The id of the pipeline.

        Returns:
            Pipeline: Object describing the pipeline.
        """
        return self.client.resume_pipeline_refresh_schedule(self.pipeline_id)

    def create_step_from_function(self,
                                  step_name: str,
                                  function: callable,
                                  step_input_mappings: list = None,
                                  output_variable_mappings: list = None,
                                  step_dependencies: list = None,
                                  package_requirements: list = None,
                                  cpu_size: str = None,
                                  memory: int = None):
        """
        Creates a step in the pipeline from a python function.

        Args:
            step_name (str): The name of the step.
            function (callable): The python function.
            step_input_mappings (List[PythonFunctionArguments]): List of Python function arguments.
            output_variable_mappings (List[OutputVariableMapping]): List of Python function ouputs.
            step_dependencies (List[str]): List of step names this step depends on.
            package_requirements (list): List of package requirement strings. For example: ['numpy==1.2.3', 'pandas>=1.4.0'].
            cpu_size (str): Size of the CPU for the step function.
            memory (int): Memory (in GB) for the step function.
        """
        return self.client.create_pipeline_step_from_function(self.id,
                                                              step_name,
                                                              function,
                                                              step_input_mappings,
                                                              output_variable_mappings,
                                                              step_dependencies,
                                                              package_requirements,
                                                              cpu_size,
                                                              memory)

    def wait_for_pipeline(self, timeout=1200):
        """
        A waiting call until all the stages of the latest pipeline version is completed.

        Args:
            timeout (int): The waiting time given to the call to finish, if it doesn't finish by the allocated time, the call is said to be timed out.
        """
        return self.client._poll(self, {'PENDING', 'RUNNING'}, timeout=timeout)

    def get_status(self):
        """
        Gets the status of the pipeline version.

        Returns:
            str: A string describing the status of a pipeline version (pending, running, complete, etc.).
        """
        pipeline = self.describe()
        return pipeline.latest_pipeline_version.status if pipeline.latest_pipeline_version else None
