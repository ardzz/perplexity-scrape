"""Tabular/structured dataset research prompt template."""

TEMPLATE = """Research "{topic}" tabular/structured dataset for machine learning applications.

Provide comprehensive guidance for effectively working with this tabular data:

1. **Dataset Characterization**: Thoroughly analyze the dataset size thresholds (small datasets under 10K rows, medium datasets between 10K-1M rows, and large datasets exceeding 1M rows). Examine feature types including numeric continuous variables, categorical nominal and ordinal features, and mixed-type columns. Identify the target variable type for classification or regression prediction tasks. Document the feature-to-sample ratio and its implications.

2. **Data Quality Assessment**: Systematically examine missing value patterns and mechanisms including MCAR (Missing Completely At Random), MAR (Missing At Random), and MNAR (Missing Not At Random). Detect outliers using statistical methods like IQR (Interquartile Range), z-score analysis, and Mahalanobis distance for multivariate outliers. Assess class imbalance ratios and severity. Identify potential data leakage sources between features and the target variable.

3. **Preprocessing Pipeline**: Apply appropriate encoding strategies including one-hot encoding for low-cardinality categorical features, label encoding for ordinal variables, and target encoding for high-cardinality categorical features. Implement scaling methods like StandardScaler for normally distributed features and MinMaxScaler for bounded ranges based on algorithm requirements. Handle missing data through imputation using mean, median, mode, KNN-based, or iterative imputation methods like IterativeImputer.

4. **Feature Engineering**: Create binned features for continuous variables using quantile-based or domain-knowledge binning. Generate interaction terms between important features to capture combined effects. Implement polynomial features for modeling non-linear relationships. Extract datetime components like day, month, hour, and create cyclical features. Calculate aggregate statistics including group-wise means and counts.

5. **Model Selection Framework**: For small datasets with limited samples, prefer simpler models like logistic regression, decision trees, and regularized linear models to avoid overfitting. For medium-sized datasets, use gradient boosting methods like XGBoost, LightGBM, and CatBoost that handle tabular data effectively. For large datasets, consider neural network approaches like TabNet, MLP with batch normalization, or FT-Transformer with proper regularization strategies.

6. **Supervised Learning Approaches**: Implement tree-based ensembles including Random Forest for baseline performance and XGBoost with careful hyperparameter tuning via cross-validation grid or random search. Consider MLP architectures and TabNet specifically designed for deep learning on tabular data. Apply regularization techniques like L1 (Lasso), L2 (Ridge), elastic net, and dropout to prevent overfitting.

7. **Unsupervised Learning Approaches**: Apply K-means clustering for partitioning and DBSCAN for density-based clustering with automatic outlier detection. Use PCA for linear dimensionality reduction and UMAP or t-SNE for non-linear visualization. Implement autoencoders for anomaly detection, feature learning, and data denoising applications.

8. **Self-Supervised and Semi-Supervised Methods**: Leverage contrastive learning approaches like SCARF (Self-supervised Contrastive Learning for Tabular Data) for representation learning without labels. Apply pseudo-labeling techniques to effectively utilize unlabeled data in semi-supervised settings. Use self-training with high-confidence predictions to expand training data iteratively.

9. **Code Implementation**: Use pandas for data manipulation, exploration, and preprocessing pipelines. Implement scikit-learn Pipeline and ColumnTransformer for reproducible preprocessing. Apply proper train-validation-test splitting with stratification for classification. Create baseline XGBoost model with early stopping on validation set. Structure code with cross-validation loops and systematic hyperparameter search using Optuna or scikit-learn GridSearchCV.

10. **Evaluation Strategy**: Apply stratified K-fold cross-validation for classification tasks to preserve class distribution in each fold. Use appropriate metrics including accuracy, precision, recall, F1-score, and AUC-ROC for classification problems, and MAE, MSE, RMSE, R-squared, and MAPE for regression problems. Implement proper holdout validation sets and carefully monitor for overfitting through learning curves.

Include specific working code examples using scikit-learn, pandas, and XGBoost with proper data validation and error handling."""
