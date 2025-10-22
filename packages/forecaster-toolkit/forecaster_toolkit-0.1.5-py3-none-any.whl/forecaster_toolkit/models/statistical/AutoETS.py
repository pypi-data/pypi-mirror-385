import numpy as np
import pandas as pd
from statsforecast.models import AutoETS

from forecaster_toolkit.models.statistical.StatisticalModel import StatisticalModel


class AutoETSModel(StatisticalModel):
    """
    AutoETS model.

    Attributes
    ----------
    model : statsforecast.models.AutoETS
        The AutoETS model instance

    Methods
    -------
    fit(self, X: Union[pd.DataFrame, pd.Series, np.ndarray]) -> None:
        Fit the model to the training data.
    predict(self, h: int, level: Optional[list[float]] = None, **kwargs) -> np.ndarray:
        Make predictions using the model.
    """

    def __init__(self, season_length: int, **kwargs):
        """
        Initialize the AutoETS model.

        Parameters
        ----------
        season_length : int
            The seasonal length to use for the model
        **kwargs : dict
            Additional keyword arguments for the model
        """
        super().__init__()
        self.season_length = season_length
        self.model = AutoETS(season_length=self.season_length, **kwargs)

    def fit(self, X: pd.DataFrame | pd.Series | np.ndarray) -> None:
        """
        Fit the model to the training data.

        Parameters
        ----------
        X : Union[pd.DataFrame, pd.Series, np.ndarray]
            Training input samples
        """
        super().fit(X)

    def predict(self, h: int, level: list[float] | None = None, **kwargs) -> np.ndarray:
        """
        Make predictions using the fitted model.

        Parameters
        ----------
        h : int
            Number of steps to forecast
        level : list[float]
            The confidence levels for the prediction intervals
        **kwargs : dict
            Additional keyword arguments for the model

        Returns
        -------
        dict[str, np.ndarray]
            Predicted values stored in a dictionary
        """
        return super().predict(h, level, **kwargs)
