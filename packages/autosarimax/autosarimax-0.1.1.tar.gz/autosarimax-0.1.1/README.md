# AutoSNARIMAX

Using the River and Optuna packages to provide an automatically optimized ARIMA-derived model with the possibility of online updates.

## Overview

`AutoSNARIMAX` is a Python class for automatic hyperparameter optimization of SNARIMAX models using **Optuna** and the **River** library. It supports:

- Automatic hyperparameter tuning for SNARIMAX models.
- Incorporation of additional features, including holidays.
- Online updates: the model can be updated incrementally with new observations.
- Forecasting with uncertainty intervals.

## Installation

```bash
pip install autosarimax
````

## Usage

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from autosarimax import AutoSNARIMAX, add_holiday_feature

# 1️⃣ Create example DataFrame
dates = pd.date_range(start='2025-01-01', periods=30, freq='D')
np.random.seed(42)
y = np.random.randint(50, 150, size=len(dates))
X = pd.DataFrame({'date': dates, 'feature1': np.random.randn(len(dates))})

# 2️⃣ Add holiday feature
X = add_holiday_feature(X, country='BR', date_col='date')
X = X.drop(columns=['date'])

# 3️⃣ Initialize and fit model
model = AutoSNARIMAX(n_trials=5, horizon=1)
model.fit(X, y)

# 4️⃣ Make incremental predictions
pred_df = model.predict(X, force=False)

# 5️⃣ Plot real vs predicted values
plt.figure(figsize=(12, 6))
plt.plot(dates, y, label='Real', marker='o')
plt.plot(dates, pred_df['pred'], label='Predicted', marker='x')
plt.fill_between(dates, pred_df['lower'], pred_df['upper'], color='gray', alpha=0.3, label='Uncertainty')
plt.xlabel('Date')
plt.ylabel('Value')
plt.title('AutoSNARIMAX Forecast vs Real')
plt.legend()
plt.grid(True)
plt.show()
```

## Features

* **`add_holiday_feature(df, country, date_col)`**: Adds a binary column `is_holiday` indicating whether a date is a holiday.
* **`fit(X, y)`**: Optimizes hyperparameters and trains the SNARIMAX model.
* **`update(X, y)`**: Updates the model incrementally with new observations.
* **`predict(X, horizon, force)`**: Makes forecasts.

  * `force=True`: forecasts the full horizon without updating the model.
  * `force=False`: forecasts incrementally and updates the model using the predicted values.

## License

MIT License

[GitHub](https://github.com/danttis/autosarimax)
