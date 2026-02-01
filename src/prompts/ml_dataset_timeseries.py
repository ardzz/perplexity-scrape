"""Time series dataset research prompt template."""

TEMPLATE = """Research "{topic}" time series dataset for temporal machine learning.

Provide comprehensive guidance for working with this time series data:

1. **Dataset Characterization**: Analyze sampling frequency and temporal resolution including regular versus irregular time steps. Identify seasonality at multiple scales (hourly, daily, weekly, yearly) using autocorrelation and spectral analysis. Detect trends, level shifts, and structural breaks in the series. Determine if univariate single-variable or multivariate with multiple correlated variables. Assess series length and temporal coverage.

2. **Data Quality Assessment**: Identify missing timestamps, gaps in temporal coverage, and irregular sampling intervals. Detect point anomalies and contextual outliers using statistical and ML methods. Check non-stationarity using Augmented Dickey-Fuller and KPSS tests. Examine autocorrelation structure with ACF and PACF plots to understand temporal dependencies. Identify potential data leakage.

3. **Preprocessing Pipeline**: Apply differencing operations to achieve stationarity when statistical tests indicate non-stationary behavior. Implement windowing strategies and sliding window approaches for creating supervised samples from sequential data. Handle missing values using forward fill, linear interpolation, or model-based imputation. Apply normalization preserving temporal ordering.

4. **Feature Engineering**: Create lag features at multiple time steps and rolling window statistics including mean, standard deviation, and quantiles. Extract Fourier features to capture seasonal patterns. Generate calendar features like day of week, month, and holiday indicators. Compute domain-specific technical indicators for specialized series. Apply wavelet transforms for multi-resolution analysis when appropriate.

5. **Model Selection Framework**: For simple patterns, use statistical methods like ARIMA, SARIMA, and exponential smoothing (ETS). For complex non-linear patterns, use deep learning with LSTM, GRU, and Transformer architectures. For probabilistic forecasts requiring prediction intervals, apply Bayesian approaches or quantile regression. Consider forecast horizon length.

6. **Supervised Learning Approaches**: Implement ARIMA, SARIMA, Prophet, and exponential smoothing models using statsmodels. Apply deep learning architectures like LSTM, GRU, and Temporal Fusion Transformer. Use modern architectures like N-BEATS and N-HiTS for state-of-the-art forecasting. Consider gradient boosting with engineered features as strong baselines.

7. **Unsupervised Learning Approaches**: Apply time series clustering using DTW similarity or shape-based distance measures. Implement anomaly detection with isolation forests, autoencoders, and statistical process control. Detect changepoints using PELT or neural changepoint methods. Use matrix profile for pattern and motif discovery.

8. **Self-Supervised and Semi-Supervised Methods**: Apply contrastive learning like TS2Vec, TNC, and TS-TCC for temporal representation learning. Implement pseudo-labeling for time series classification by training on confident predictions. Use self-supervised pretraining on large unlabeled temporal datasets before fine-tuning.

9. **Code Implementation**: Use pandas for datetime indexing, resampling, and temporal manipulation with timezone handling. Implement time-based train-validation splits ensuring no future data leakage. Create forecasting pipelines using statsmodels and pytorch-forecasting. Structure code for systematic backtesting with multiple origins. Apply early stopping.

10. **Evaluation Strategy**: Use time-based cross-validation with expanding or sliding windows to simulate realistic forecasting. Calculate MAE, RMSE, MAPE, and symmetric MAPE metrics. Assess prediction intervals using coverage probability and width. Compare against naive baselines including seasonal naive. Visualize forecasts with confidence bands.

Include code examples using pandas, statsmodels, sktime, and pytorch-forecasting with proper temporal validation."""
