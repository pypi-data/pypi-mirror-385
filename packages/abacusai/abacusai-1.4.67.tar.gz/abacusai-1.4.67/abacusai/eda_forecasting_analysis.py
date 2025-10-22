from .forecasting_analysis_graph_data import ForecastingAnalysisGraphData
from .return_class import AbstractApiClass


class EdaForecastingAnalysis(AbstractApiClass):
    """
        Eda Forecasting Analysis of the latest version of the data.

        Args:
            client (ApiClient): An authenticated API Client instance
            primaryKeys (list): Name of the primary keys in the data
            forecastingTargetFeature (str): Feature in the data that represents the target.
            timestampFeature (str): Feature in the data that represents the timestamp column.
            forecastFrequency (str): Frequency of data, could be hourly, daily, weekly, monthly, quarterly or yearly.
            salesAcrossTime (ForecastingAnalysisGraphData): Data showing average, p10, p90, median sales across time
            cummulativeContribution (ForecastingAnalysisGraphData): Data showing what percent of items contribute to what amount of sales.
            missingValueDistribution (ForecastingAnalysisGraphData): Data showing missing or null value distribution
            historyLength (ForecastingAnalysisGraphData): Data showing length of history distribution
            numRowsHistogram (ForecastingAnalysisGraphData): Data showing number of rows for an item distribution
            productMaturity (ForecastingAnalysisGraphData): Data showing length of how long a product has been alive with average, p10, p90 and median
            seasonalityYear (ForecastingAnalysisGraphData): Data showing average, p10, p90, median sales across grouped years
            seasonalityMonth (ForecastingAnalysisGraphData): Data showing average, p10, p90, median sales across grouped months
            seasonalityWeekOfYear (ForecastingAnalysisGraphData): Data showing average, p10, p90, median sales across week of year seasonality
            seasonalityDayOfYear (ForecastingAnalysisGraphData): Data showing average, p10, p90, median sales across day of year seasonality
            seasonalityDayOfMonth (ForecastingAnalysisGraphData): Data showing average, p10, p90, median sales across day of month seasonality
            seasonalityDayOfWeek (ForecastingAnalysisGraphData): Data showing average, p10, p90, median sales across day of week seasonality
            seasonalityQuarter (ForecastingAnalysisGraphData): Data showing average, p10, p90, median sales across grouped quarters
            seasonalityHour (ForecastingAnalysisGraphData): Data showing average, p10, p90, median sales across grouped hours
            seasonalityMinute (ForecastingAnalysisGraphData): Data showing average, p10, p90, median sales across grouped minutes
            seasonalitySecond (ForecastingAnalysisGraphData): Data showing average, p10, p90, median sales across grouped seconds
            autocorrelation (ForecastingAnalysisGraphData): Data showing the correlation of the forecasting target and its lagged values at different time lags.
            partialAutocorrelation (ForecastingAnalysisGraphData): Data showing the correlation of the forecasting target and its lagged values, controlling for the effects of intervening lags.
    """

    def __init__(self, client, primaryKeys=None, forecastingTargetFeature=None, timestampFeature=None, forecastFrequency=None, salesAcrossTime={}, cummulativeContribution={}, missingValueDistribution={}, historyLength={}, numRowsHistogram={}, productMaturity={}, seasonalityYear={}, seasonalityMonth={}, seasonalityWeekOfYear={}, seasonalityDayOfYear={}, seasonalityDayOfMonth={}, seasonalityDayOfWeek={}, seasonalityQuarter={}, seasonalityHour={}, seasonalityMinute={}, seasonalitySecond={}, autocorrelation={}, partialAutocorrelation={}):
        super().__init__(client, None)
        self.primary_keys = primaryKeys
        self.forecasting_target_feature = forecastingTargetFeature
        self.timestamp_feature = timestampFeature
        self.forecast_frequency = forecastFrequency
        self.sales_across_time = client._build_class(
            ForecastingAnalysisGraphData, salesAcrossTime)
        self.cummulative_contribution = client._build_class(
            ForecastingAnalysisGraphData, cummulativeContribution)
        self.missing_value_distribution = client._build_class(
            ForecastingAnalysisGraphData, missingValueDistribution)
        self.history_length = client._build_class(
            ForecastingAnalysisGraphData, historyLength)
        self.num_rows_histogram = client._build_class(
            ForecastingAnalysisGraphData, numRowsHistogram)
        self.product_maturity = client._build_class(
            ForecastingAnalysisGraphData, productMaturity)
        self.seasonality_year = client._build_class(
            ForecastingAnalysisGraphData, seasonalityYear)
        self.seasonality_month = client._build_class(
            ForecastingAnalysisGraphData, seasonalityMonth)
        self.seasonality_week_of_year = client._build_class(
            ForecastingAnalysisGraphData, seasonalityWeekOfYear)
        self.seasonality_day_of_year = client._build_class(
            ForecastingAnalysisGraphData, seasonalityDayOfYear)
        self.seasonality_day_of_month = client._build_class(
            ForecastingAnalysisGraphData, seasonalityDayOfMonth)
        self.seasonality_day_of_week = client._build_class(
            ForecastingAnalysisGraphData, seasonalityDayOfWeek)
        self.seasonality_quarter = client._build_class(
            ForecastingAnalysisGraphData, seasonalityQuarter)
        self.seasonality_hour = client._build_class(
            ForecastingAnalysisGraphData, seasonalityHour)
        self.seasonality_minute = client._build_class(
            ForecastingAnalysisGraphData, seasonalityMinute)
        self.seasonality_second = client._build_class(
            ForecastingAnalysisGraphData, seasonalitySecond)
        self.autocorrelation = client._build_class(
            ForecastingAnalysisGraphData, autocorrelation)
        self.partial_autocorrelation = client._build_class(
            ForecastingAnalysisGraphData, partialAutocorrelation)
        self.deprecated_keys = {}

    def __repr__(self):
        repr_dict = {f'primary_keys': repr(self.primary_keys), f'forecasting_target_feature': repr(self.forecasting_target_feature), f'timestamp_feature': repr(self.timestamp_feature), f'forecast_frequency': repr(self.forecast_frequency), f'sales_across_time': repr(self.sales_across_time), f'cummulative_contribution': repr(self.cummulative_contribution), f'missing_value_distribution': repr(self.missing_value_distribution), f'history_length': repr(self.history_length), f'num_rows_histogram': repr(self.num_rows_histogram), f'product_maturity': repr(self.product_maturity), f'seasonality_year': repr(self.seasonality_year), f'seasonality_month': repr(
            self.seasonality_month), f'seasonality_week_of_year': repr(self.seasonality_week_of_year), f'seasonality_day_of_year': repr(self.seasonality_day_of_year), f'seasonality_day_of_month': repr(self.seasonality_day_of_month), f'seasonality_day_of_week': repr(self.seasonality_day_of_week), f'seasonality_quarter': repr(self.seasonality_quarter), f'seasonality_hour': repr(self.seasonality_hour), f'seasonality_minute': repr(self.seasonality_minute), f'seasonality_second': repr(self.seasonality_second), f'autocorrelation': repr(self.autocorrelation), f'partial_autocorrelation': repr(self.partial_autocorrelation)}
        class_name = "EdaForecastingAnalysis"
        repr_str = ',\n  '.join([f'{key}={value}' for key, value in repr_dict.items(
        ) if getattr(self, key, None) is not None and key not in self.deprecated_keys])
        return f"{class_name}({repr_str})"

    def to_dict(self):
        """
        Get a dict representation of the parameters in this class

        Returns:
            dict: The dict value representation of the class parameters
        """
        resp = {'primary_keys': self.primary_keys, 'forecasting_target_feature': self.forecasting_target_feature, 'timestamp_feature': self.timestamp_feature, 'forecast_frequency': self.forecast_frequency, 'sales_across_time': self._get_attribute_as_dict(self.sales_across_time), 'cummulative_contribution': self._get_attribute_as_dict(self.cummulative_contribution), 'missing_value_distribution': self._get_attribute_as_dict(self.missing_value_distribution), 'history_length': self._get_attribute_as_dict(self.history_length), 'num_rows_histogram': self._get_attribute_as_dict(self.num_rows_histogram), 'product_maturity': self._get_attribute_as_dict(self.product_maturity), 'seasonality_year': self._get_attribute_as_dict(self.seasonality_year), 'seasonality_month': self._get_attribute_as_dict(
            self.seasonality_month), 'seasonality_week_of_year': self._get_attribute_as_dict(self.seasonality_week_of_year), 'seasonality_day_of_year': self._get_attribute_as_dict(self.seasonality_day_of_year), 'seasonality_day_of_month': self._get_attribute_as_dict(self.seasonality_day_of_month), 'seasonality_day_of_week': self._get_attribute_as_dict(self.seasonality_day_of_week), 'seasonality_quarter': self._get_attribute_as_dict(self.seasonality_quarter), 'seasonality_hour': self._get_attribute_as_dict(self.seasonality_hour), 'seasonality_minute': self._get_attribute_as_dict(self.seasonality_minute), 'seasonality_second': self._get_attribute_as_dict(self.seasonality_second), 'autocorrelation': self._get_attribute_as_dict(self.autocorrelation), 'partial_autocorrelation': self._get_attribute_as_dict(self.partial_autocorrelation)}
        return {key: value for key, value in resp.items() if value is not None and key not in self.deprecated_keys}
