from .return_class import AbstractApiClass


class ChatllmTask(AbstractApiClass):
    """
        A chatllm task

        Args:
            client (ApiClient): An authenticated API Client instance
            chatllmTaskId (str): The id of the chatllm task.
            daemonTaskId (str): The id of the daemon task.
            taskType (str): The type of task ('chatllm' or 'daemon').
            name (str): The name of the chatllm task.
            instructions (str): The instructions of the chatllm task.
            lifecycle (str): The lifecycle of the chatllm task.
            scheduleInfo (dict): The schedule info of the chatllm task.
            externalApplicationId (str): The external application id associated with the chatllm task.
            deploymentConversationId (str): The deployment conversation id associated with the chatllm task.
            sourceDeploymentConversationId (str): The source deployment conversation id associated with the chatllm task.
            enableEmailAlerts (bool): Whether email alerts are enabled for the chatllm task.
            email (str): The email to send alerts to.
            numUnreadTaskInstances (int): The number of unread task instances for the chatllm task.
            computePointsUsed (int): The compute points used for the chatllm task.
            displayMarkdown (str): The display markdown for the chatllm task.
    """

    def __init__(self, client, chatllmTaskId=None, daemonTaskId=None, taskType=None, name=None, instructions=None, lifecycle=None, scheduleInfo=None, externalApplicationId=None, deploymentConversationId=None, sourceDeploymentConversationId=None, enableEmailAlerts=None, email=None, numUnreadTaskInstances=None, computePointsUsed=None, displayMarkdown=None):
        super().__init__(client, chatllmTaskId)
        self.chatllm_task_id = chatllmTaskId
        self.daemon_task_id = daemonTaskId
        self.task_type = taskType
        self.name = name
        self.instructions = instructions
        self.lifecycle = lifecycle
        self.schedule_info = scheduleInfo
        self.external_application_id = externalApplicationId
        self.deployment_conversation_id = deploymentConversationId
        self.source_deployment_conversation_id = sourceDeploymentConversationId
        self.enable_email_alerts = enableEmailAlerts
        self.email = email
        self.num_unread_task_instances = numUnreadTaskInstances
        self.compute_points_used = computePointsUsed
        self.display_markdown = displayMarkdown
        self.deprecated_keys = {}

    def __repr__(self):
        repr_dict = {f'chatllm_task_id': repr(self.chatllm_task_id), f'daemon_task_id': repr(self.daemon_task_id), f'task_type': repr(self.task_type), f'name': repr(self.name), f'instructions': repr(self.instructions), f'lifecycle': repr(self.lifecycle), f'schedule_info': repr(self.schedule_info), f'external_application_id': repr(self.external_application_id), f'deployment_conversation_id': repr(
            self.deployment_conversation_id), f'source_deployment_conversation_id': repr(self.source_deployment_conversation_id), f'enable_email_alerts': repr(self.enable_email_alerts), f'email': repr(self.email), f'num_unread_task_instances': repr(self.num_unread_task_instances), f'compute_points_used': repr(self.compute_points_used), f'display_markdown': repr(self.display_markdown)}
        class_name = "ChatllmTask"
        repr_str = ',\n  '.join([f'{key}={value}' for key, value in repr_dict.items(
        ) if getattr(self, key, None) is not None and key not in self.deprecated_keys])
        return f"{class_name}({repr_str})"

    def to_dict(self):
        """
        Get a dict representation of the parameters in this class

        Returns:
            dict: The dict value representation of the class parameters
        """
        resp = {'chatllm_task_id': self.chatllm_task_id, 'daemon_task_id': self.daemon_task_id, 'task_type': self.task_type, 'name': self.name, 'instructions': self.instructions, 'lifecycle': self.lifecycle, 'schedule_info': self.schedule_info, 'external_application_id': self.external_application_id, 'deployment_conversation_id':
                self.deployment_conversation_id, 'source_deployment_conversation_id': self.source_deployment_conversation_id, 'enable_email_alerts': self.enable_email_alerts, 'email': self.email, 'num_unread_task_instances': self.num_unread_task_instances, 'compute_points_used': self.compute_points_used, 'display_markdown': self.display_markdown}
        return {key: value for key, value in resp.items() if value is not None and key not in self.deprecated_keys}
