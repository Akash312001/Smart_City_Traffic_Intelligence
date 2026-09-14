# Smart City Traffic Intelligence

End-to-end capstone project using the Metro Interstate Traffic Volume dataset.

The project covers data analytics, Python data processing, machine learning,
deep learning, explainable AI, MLOps, deployment, monitoring, responsible AI,
and traffic timing recommendations.

## Project Structure

- data/Metro_Interstate_Traffic_Volume.csv
- part1_sql/
- part1_powerbi/
- part2_python/
- reports/
- requirements.txt
- README.md
- Smart_City_Traffic_Intelligence_Final_Report.docx

## Environment

Python 3.10+ is recommended.

Create the environment:

python -m venv .venv

Install dependencies:

pip install -r requirements.txt

## Part 1 - SQL and Power BI

Part 1 includes SQLite analysis and a Power BI dashboard.

The SQL analysis covers annual traffic totals, holiday temperature analysis,
traffic statistics, Pearson correlation, probability, conditional probability,
independence analysis and odds ratio analysis.

SQL files:

- part1_sql/traffic_analysis.db
- part1_sql/analysis.sql
- part1_sql/sql_results.txt

Power BI dashboard:

- part1_powerbi/traffic_dashboard.pbix

The dashboard includes traffic KPIs, hourly traffic, daily traffic,
weather analysis, temperature analysis and slicers.

## Part 2 - Python Data Pipeline

The main pipeline is part2_python/pipeline.py.

The pipeline performs:

1. Schema validation
2. Datetime parsing
3. Missing holiday handling
4. Duplicate removal
5. Invalid temperature handling
6. Monthly median temperature imputation
7. Weather standardisation
8. Time-based feature engineering
9. Processed dataset export
10. Logging

Final processed data:

- 48,187 rows
- 25 columns
- 0 missing values
- 0 duplicate rows

CLI commands:

python part2_python/pipeline.py validate --input data/Metro_Interstate_Traffic_Volume.csv

python part2_python/pipeline.py clean --input data/Metro_Interstate_Traffic_Volume.csv --output part2_python/data/processed/cli_cleaned_traffic.csv

python part2_python/pipeline.py run --input data/Metro_Interstate_Traffic_Volume.csv --output part2_python/data/processed/final_pipeline_output.csv

Log file:

part2_python/reports/logs/pipeline.log

## Part 3 - Machine Learning

Because no accident dataset was supplied, a proxy high-risk label was created
using congestion and selected severe-weather conditions.

Congestion categories:

- Low
- Moderate
- High
- Severe

Selected severe-weather categories:

- rain
- thunderstorm
- fog
- mist
- snow
- haze

The proxy label must not be interpreted as actual accident prediction.

### Classification

Models:

- Logistic Regression
- Random Forest
- Neural Network

Metrics:

- Accuracy
- Precision
- Recall
- F1
- ROC AUC

Output: part2_python/data/processed/classification_model_results.csv

### Regression

Models:

- Linear Regression
- Random Forest Regression

Metrics:

- MAE
- R-squared

### Unsupervised Learning

K-means clustering and Apriori association-rule mining were performed.

Output: part2_python/data/processed/association_rules.csv

### Explainable AI

SHAP was used for Random Forest feature importance.

Output: part2_python/reports/shap_feature_importance.png

### MLOps

MLflow was used to track the Random Forest classification experiment.

Output: part2_python/data/processed/mlflow_classification_run.csv

## Deployment

A FastAPI application is provided in part2_python/app.py.

The saved model is:

part2_python/data/processed/random_forest_classification_model.joblib

FastAPI test evidence:

part2_python/reports/fastapi_test_result.txt

## Monitoring

Drift monitoring was performed using the Kolmogorov-Smirnov test.

Output: part2_python/data/processed/drift_monitoring_results.csv

The analysis produced 8 PASS results and 0 ALERT results.

This is an internal historical train/test stability check and not proof of
production drift behaviour.

## Responsible AI

The project considers fairness across weekday and weekend groups, uneven
model performance, proxy-label limitations, dataset coverage limitations,
and potential consequences of incorrect predictions.

Outputs:

- fairness_performance_results.csv
- fairness_prediction_rates.csv
- responsible_ai_fairness_report.txt

The model should not be treated as definitive evidence of accident risk.

## Traffic Timing Recommendation

Because the dataset represents a single corridor, the recommendation focuses
on travel timing rather than route selection.

Historical traffic was substantially lower during early-morning weekday
periods, particularly around 2 AM to 4 AM.

The lowest observed average traffic was approximately 302 vehicles per hour
at 2 AM on weekdays.

This is a historical traffic-pattern recommendation, not a guarantee of
road safety. Weather and real-world operating conditions should still be considered.

Recommendation outputs:

- traffic_timing_recommendations.csv
- traffic_timing_recommendation.txt

## Reproducibility

Install dependencies using requirements.txt.

The main reproducible pipeline is part2_python/pipeline.py.

The analysis notebook is part2_python/part2_traffic_pipeline.ipynb.

Processed datasets and model outputs are stored under part2_python/data/processed/.

## Git and Security

Use incremental commits during development.

Never commit passwords, API keys, authentication tokens or other secrets.
