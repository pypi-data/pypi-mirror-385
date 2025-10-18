"""Using the River and Optuna packages to provide 
an automatically optimized ARIMA-derived model
with the possibility of online updates."""

import holidays
import numpy as np
import optuna
import pandas as pd
from river import (
    linear_model,
    metrics,
    optim,
    preprocessing,
    time_series,
)

def add_holiday_feature(df, country='BR', date_col='date'):
    """Adds a binary column indicating whether the date is a holiday."""
    br_holidays = holidays.CountryHoliday(country)
    df['is_holiday'] = df[date_col].apply(lambda x: 1 if x in br_holidays else 0)
    return df
    

class AutoSNARIMAX:
    def __init__(self, n_trials=20, metric=metrics.RMSLE(), horizon=1, warmup=20):
        """Hyperparameter optimization of SNARIMAX using Optuna."""
        self.n_trials = n_trials
        self.metric = metric or metrics.MAE()
        self.horizon = horizon
        self.warmup = warmup
        self.best_params_ = None
        self.best_model_ = None
        self._std = 0
        self.res = []

    def _convert_to_records(self, X):
        """Converts X to a list of dictionaries compatible with River."""
        if isinstance(X, pd.DataFrame):
            return X.to_dict(orient="records")
        elif isinstance(X, pd.Series):
            return [X.to_dict()]
        elif isinstance(X, dict):
            return [X]
        elif isinstance(X, np.ndarray):
            if X.ndim == 1:
                return [dict(enumerate(X))]
            else:
                return [dict(enumerate(row)) for row in X]
        else:
            raise ValueError(f"Unsupported X format: {type(X)}")

    def _build_model(self, trial):
        """Defines the hyperparameter search space."""
        p = trial.suggest_int("p", 0, 3)
        d = trial.suggest_int("d", 0, 2)
        q = trial.suggest_int("q", 0, 3)

        m = trial.suggest_categorical("m", [1, 6, 12])
        sp = trial.suggest_int("sp", 0, 3)
        sq = trial.suggest_int("sq", 0, 3)

        lr = trial.suggest_float("lr", 1e-4, 0.1, log=True)
        intercept_lr = trial.suggest_float("intercept_lr", 0.01, 1.0)

        regressor = (
            preprocessing.StandardScaler() |
            linear_model.LinearRegression(
                optimizer=optim.SGD(lr),
                intercept_init=trial.suggest_float("intercept_init", 50, 150),
                intercept_lr=intercept_lr
            )
        )

        model = time_series.SNARIMAX(
            p=p, d=d, q=q,
            m=m,
            sp=sp, sq=sq,
            regressor=regressor
        )
        return model

    def _evaluate_model(self, model, X, y):
        metric = self.metric.clone()
        X_records = self._convert_to_records(X)
        for i, (row_x, row_y) in enumerate(zip(X_records, y)):
            if i >= self.warmup:
                try:
                    forecast = model.forecast(horizon=1)
                    if forecast is not None and len(forecast) > 0:
                        y_pred = forecast[0]
                        metric.update(row_y, y_pred)
                except Exception:
                    pass

            model.learn_one(row_y, row_x)

        return metric.get()

    def fit(self, X, y):
        def objective(trial):
            model = self._build_model(trial)
            score = self._evaluate_model(model, X, y)  
            return score

        study = optuna.create_study(direction="minimize")
        study.optimize(objective, n_trials=self.n_trials)

        self.best_params_ = study.best_params
        self.best_model_ = self._build_model(study.best_trial)


        X_records  = self._convert_to_records(X)
        for row_x, row_y in zip(X_records, y):
            self.best_model_.learn_one(row_y, row_x)
            y_pred = self.best_model_.forecast(horizon=1)
            self.res.append(np.array(row_y) - np.array(y_pred[0]))
        self._std = np.std(self.res, ddof=1)

        return self

    def update(self, X, y):
        X_records  = self._convert_to_records(X)
        for row_x, row_y in zip(X_records, y):
            self.best_model_.learn_one(row_y, row_x)
            y_pred = self.best_model_.forecast(horizon=1)
            self.res.append(np.array(row_y) - np.array(y_pred[0]))
        self._std = np.std(self.res, ddof=1)

    def predict(self, X, horizon=1, force=False):

        X_records = self._convert_to_records(X)
        
        if force:
            y_forecast = self.best_model_.forecast(horizon=horizon)
            preds = y_forecast
            lowers = y_forecast - self._std
            uppers = y_forecast + self._std
            return pd.DataFrame({
                'pred': preds,
                'lower': lowers,
                'upper': uppers
            })
        
        tmp_model = self.best_model_
        preds, lowers, uppers = [], [], []

        for row_x in X_records:
            y_forecast = tmp_model.forecast(horizon=1)
            y_pred = y_forecast[0] if y_forecast is not None and len(y_forecast) > 0 else np.nan

            preds.append(y_pred)
            lowers.append(y_pred - self._std)
            uppers.append(y_pred + self._std)

            if not np.isnan(y_pred):
                tmp_model.learn_one(y_pred, row_x)

        return pd.DataFrame({
            'pred': preds,
            'lower': lowers,
            'upper': uppers
        })


