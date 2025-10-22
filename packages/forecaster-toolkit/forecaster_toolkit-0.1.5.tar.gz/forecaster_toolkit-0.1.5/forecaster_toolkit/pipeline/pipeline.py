import warnings
from typing import Literal

import pandas as pd
from catboost import CatBoostRegressor
from coreforecast.seasonal import find_season_length
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor

from forecaster_toolkit.data.feature_engineering.time_features import (
    extend_time_series_for_prediction,
)
from forecaster_toolkit.data.preprocess.preprocess_tools import TimeSeriesPreprocessor
from forecaster_toolkit.models.ml.MLModel import MLModel
from forecaster_toolkit.models.model_selection._model_factory import (
    MLModelFactory,
    StatisticalModelFactory,
)
from forecaster_toolkit.models.model_selection.model_selection import ModelSelectionCV
from forecaster_toolkit.models.statistical.StatisticalModel import StatisticalModel

warnings.filterwarnings("ignore", category=UserWarning)


class Pipeline:
    """
    Pipeline for time series forecasting. Aims to provide a script that
    runs an end to end forecasting pipeline.

    Attributes
    ----------
    data : pd.DataFrame
        The data to be used for forecasting.
    target_column : str
        The target column to be used for forecasting.
    features : pd.DataFrame
        The features to be used for forecasting.
    model_list : list[str]
        The list of models to be used for forecasting. Can take following values:
            - "ArimaModel"
            - "AutoArimaModel"
            - "AutoCESModel"
            - "AutoETSModel"
            - "AutoThetaModel"
            - "ETSModel"
    preprocessor : TimeSeriesPreprocessor
        The preprocessor to be used for the data.
    metrics : list[str]
         The metrics to be used for the model selection. Can take following values:
            - "rmse"
            - "mae"
            - "mape"
            - "smape"
            - "mase"
            - "mase"
    normalize : Optional[Literal["standard", "minmax"]]
        The normalization method to be used for the data.
    season_length : int
        The season length to be used for the data.
    forecast_horizon_statistical : int
        The forecast horizon to be used for the statistical model.
    forecast_horizon_ml : int
        The forecast horizon to be used for the ML model.
    saving_method : Literal["csv", "parquet"]
        The saving method to be used for the data.
    model_selection : ModelSelectionCV
        The model selection to be used for the data.
    interpolation_method : str
        The interpolation method to be used for the data.

    Methods
    -------
    set_data(data: pd.DataFrame) -> None:
        Set the data for the pipeline.

    _remove_ml_models() -> None:
        Remove the ML models from the model list.

    _check_features_for_ml_predictions() -> None:
        Check if the features are correctly chosen for ML predictions.

    preprocess_data() -> pd.DataFrame:
        Preprocess the data using the forecaster toolkitpreprocessor.

    save_statistical_predictions_to_parquet(data: pd.DataFrame, last_actual_date: pd.Timestamp, file_name: str) -> None:
        Save the data to a parquet file.

    save_ml_predictions_to_parquet(data: pd.DataFrame, last_actual_date: pd.Timestamp, file_name: str) -> None:
        Save the data to a parquet file.

    __call__(save_predictions: bool = False) -> tuple[object, pd.Series, pd.DataFrame]:
        Run the pipeline for an end to end forecasting process.
    """

    def __init__(
        self,
        freq: str,
        target_column: str,
        interpolation_method: str,
        model_list: list[str] | None = None,
        metrics: list[str] | None = None,
        normalize: Literal["standard", "minmax"] | None = None,
        forecast_horizon_statistical: int = 52,
        forecast_horizon_ml: int = 3,
        season_length: int | None = None,
        saving_method: Literal["csv", "parquet"] = "parquet",
    ):
        """
        Initialize the pipeline.

        Parameters
        ----------
        data : pd.DataFrame
            The data to be used for forecasting.
        freq : str
            The frequency of the data.
        target_column : str
            The target column to be used for forecasting.
        interpolation_method : str
            The interpolation method to be used for the data.
        model_list : list[str]
            The list of models to be used for forecasting.
        metrics : list[str]
            The metrics to be used for the model selection.
        """
        if not isinstance(target_column, str):
            raise TypeError("target_column must be a string")
        if model_list is not None and not isinstance(model_list, list):
            raise TypeError("model_list must be a list or None")
        if not isinstance(freq, str):
            raise TypeError("Freq should be a string")
        # Replace the Literal check with a simple value check
        if saving_method not in ["csv", "parquet"]:
            raise ValueError("saving_method must be either 'csv' or 'parquet'")

        self.freq = freq
        self.target_column = target_column
        self.model_list = model_list
        self.preprocessor = TimeSeriesPreprocessor(
            interpolation_method=interpolation_method,
            freq=freq,
        )
        self.metrics = metrics
        self.normalize = normalize
        self.season_length = season_length
        self.forecast_horizon_statistical = forecast_horizon_statistical
        self.forecast_horizon_ml = forecast_horizon_ml
        self.saving_method = saving_method

    def set_data(self, data: pd.DataFrame):
        """
        Set the data for the pipeline.

        Arguments
        ----------
        data : pd.DataFrame
            The data to be used for forecasting.
        """
        if not isinstance(data, pd.DataFrame):
            raise TypeError("Data should be a dataframe")

        self.data = data

    def _set_season_length(self, season_length: int):
        """
        Set the season length for the pipeline.

        Parameters
        ----------
        season_length : int
            The season length to be used for the data.
        """
        self.season_length = season_length

    def _set_model_list(self, model_list: list[str | object | tuple[str, object]]):
        """
        Set the model list for the pipeline.
        """
        self.model_list = model_list

    def _remove_ml_models(self):
        """
        Remove the ML models from the model list.
        """
        for model in self.model_list:
            if model in MLModelFactory.get_models():
                self.model_list.remove(model)

    def _check_features_for_ml_predictions(self):
        """
        Check if the features are correctly chosen for ML predictions.

        If the features are not correctly chosen, the ML models will not be considered for this forecast.
        """

        if self.data.shape[1] == 0:
            self._remove_ml_models()
        else:
            try:
                self.data_forecast = extend_time_series_for_prediction(
                    df=self.data,
                    nb_periods=self.forecast_horizon_ml,
                )
            except ValueError as e:
                print(e)
                print(
                    f"Inconsistent features for ML predictions for {self.forecast_horizon_ml} periods"
                )
                print("ML models will not be considered for this forecast")
                self._remove_ml_models()

    def preprocess_data(self):
        """
        Preprocess the data using the forecaster toolkitpreprocessor.
        """
        if self.data is not None and not self.data.empty:
            self.data = self.preprocessor.transform(
                self.data,
                cols_name=self.target_column,
            )
            return self.data
        else:
            raise AttributeError(
                "data has not been set, use set_data() before trying to preprocess"
            )

    def save_statistical_predictions_to_parquet(
        self, data: pd.DataFrame, last_actual_date: pd.Timestamp, file_name: str
    ):
        """
        Save the data to a parquet file.

        Parameters
        ----------
        data : pd.DataFrame
            The data to be saved.
        last_actual_date : pd.Timestamp
            The last actual date in the data.
        file_name : str
            The name of the file to be saved.
        """
        data = pd.DataFrame(
            {
                "data_pred": data["mean"],
                "pred_lower_0.05": data["lo-5"],
                "pred_upper_0.05": data["hi-5"],
                "pred_lower_0.22360679774997896": data["lo-22.36"],
                "pred_upper_0.22360679774997896": data["hi-22.36"],
            },
            index=pd.date_range(
                start=last_actual_date,
                periods=self.forecast_horizon_statistical + 1,
                freq=self.freq,
            )[1:],
        )
        data.to_parquet(file_name)
        print(f"Saved predictions to {file_name} in {self.saving_method} format")

    def save_ml_predictions_to_parquet(
        self, data: pd.DataFrame, last_actual_date: pd.Timestamp, file_name: str
    ):
        """
        Save the data to a parquet file.

        Arguments
        ----------
        data : pd.DataFrame
            The data to be saved.
        last_actual_date : pd.Timestamp
            The last actual date in the data.
        file_name : str
            The name of the file to be saved.
        """
        data = pd.DataFrame(
            data,
            index=pd.date_range(
                start=last_actual_date, periods=len(data) + 1, freq=self.freq
            )[1:],
        )
        data.to_parquet(file_name)
        print(f"Saved predictions to {file_name} in {self.saving_method} format")

    def run_model_selection(self, data: pd.DataFrame, save_predictions: bool = False):
        """
        Run the pipeline for an end to end forecasting process.

        Parameters
        ----------
        data : pd.DataFrame
            Data to train on
        save_predictions : bool
            Whether to save the predictions to a parquet file.
        """
        if self.model_list is None:
            raise AttributeError(
                "Model list is not set, please provide it in the constructor"
            )

        self.set_data(data=data)
        self.features = self.data.drop(columns=self.target_column, inplace=False)

        # Preprocess data
        self.preprocess_data()

        season_length = find_season_length(
            self.data.loc[:, self.target_column], max_season_length=52
        )

        if any(isinstance(model, MLModel) for model in self.model_list):
            print("Checking features for ML predictions")
            self._check_features_for_ml_predictions()

        kwargs = {"season_length": season_length}

        self.model_selection = ModelSelectionCV(
            model_list=self.model_list,
            metrics=self.metrics,
            normalize=self.normalize,
            **kwargs,
        )

        best_model, _ = self.model_selection.fit(
            df=self.data,
            lambda_exp=0.1,
            target_column=self.target_column,
            forecast_horizon=self.forecast_horizon_statistical,
        )

        print("model selection done")

        actual_season_length = getattr(best_model, "season_length", self.season_length)
        print(
            f"BEST MODEL: {best_model.__class__.__name__} with season length {actual_season_length}"
        )

        last_actual_date = self.data.index[-1]

        if isinstance(best_model, StatisticalModel):
            try:
                predictions = best_model.predict(
                    self.forecast_horizon_statistical, level=[5, 22.36]
                )
            except RuntimeError as e:
                print(e)
                print("Error predicting statistical model")
                print("Model will not be considered for this forecast")
                return None, None, None
            if save_predictions:
                self.save_statistical_predictions_to_parquet(
                    predictions, last_actual_date, "predictions.parquet"
                )
        elif isinstance(
            best_model,
            (
                CatBoostRegressor,
                RandomForestRegressor,
                XGBRegressor,
            ),
        ):
            predictions = best_model.predict(
                self.data_forecast.drop(columns=[self.target_column])
            )
            if save_predictions:
                self.save_ml_predictions_to_parquet(
                    predictions, last_actual_date, "predictions.parquet"
                )

        return best_model, predictions, self.model_selection.get_summary()

    def run_forecast(self, data: pd.DataFrame, model: str, season_length: int):
        """
        Run pipeline for forecast only given a specific model

        Parameters
        ----------
        data : pd.DataFrame
            Data to train on
        model : str
            Name of the model to use to forecast
        season_length : int
            Seasonnality of the time serie
        """
        self.set_data(data=data)
        self.features = self.data.drop(columns=self.target_column, inplace=False)

        self.preprocess_data()

        kwargs = {"season_length": season_length}
        forecaster = StatisticalModelFactory.create(model, **kwargs)

        forecaster.fit(X=self.data[self.target_column])

        return forecaster.predict(h=self.forecast_horizon_statistical)
