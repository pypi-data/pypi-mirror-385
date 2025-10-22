from .return_class import AbstractApiClass


class ModelMonitorSummary(AbstractApiClass):
    """
        A summary of model monitor

        Args:
            client (ApiClient): An authenticated API Client instance
            modelAccuracy (list): A list of model accuracy objects including accuracy and monitor version information.
            modelDrift (list): A list of model drift objects including label and prediction drifts and monitor version information.
            dataIntegrity (list): A list of data integrity objects including counts of violations and monitor version information.
            biasViolations (list): A list of bias objects including bias counts and monitor version information.
            alerts (list): A list of alerts by type for each model monitor instance
    """

    def __init__(self, client, modelAccuracy=None, modelDrift=None, dataIntegrity=None, biasViolations=None, alerts=None):
        super().__init__(client, None)
        self.model_accuracy = modelAccuracy
        self.model_drift = modelDrift
        self.data_integrity = dataIntegrity
        self.bias_violations = biasViolations
        self.alerts = alerts
        self.deprecated_keys = {}

    def __repr__(self):
        repr_dict = {f'model_accuracy': repr(self.model_accuracy), f'model_drift': repr(self.model_drift), f'data_integrity': repr(
            self.data_integrity), f'bias_violations': repr(self.bias_violations), f'alerts': repr(self.alerts)}
        class_name = "ModelMonitorSummary"
        repr_str = ',\n  '.join([f'{key}={value}' for key, value in repr_dict.items(
        ) if getattr(self, key, None) is not None and key not in self.deprecated_keys])
        return f"{class_name}({repr_str})"

    def to_dict(self):
        """
        Get a dict representation of the parameters in this class

        Returns:
            dict: The dict value representation of the class parameters
        """
        resp = {'model_accuracy': self.model_accuracy, 'model_drift': self.model_drift,
                'data_integrity': self.data_integrity, 'bias_violations': self.bias_violations, 'alerts': self.alerts}
        return {key: value for key, value in resp.items() if value is not None and key not in self.deprecated_keys}
