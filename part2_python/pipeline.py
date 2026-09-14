
import logging
from pathlib import Path

import numpy as np
import pandas as pd


REQUIRED_COLUMNS = [
    "holiday",
    "temp",
    "rain_1h",
    "snow_1h",
    "clouds_all",
    "weather_main",
    "weather_description",
    "date_time",
    "traffic_volume",
]


logger = logging.getLogger(__name__)


def validate_schema(data):
    """Validate that all required columns are present."""

    missing_columns = [
        column for column in REQUIRED_COLUMNS
        if column not in data.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Schema validation failed. Missing columns: {missing_columns}"
        )

    logger.info("Schema validation passed.")


def load_and_validate_data(file_path):
    """Load the raw CSV and validate its schema before processing."""
    try:
        df = pd.read_csv(file_path)
    except (FileNotFoundError, pd.errors.EmptyDataError, pd.errors.ParserError) as exc:
        logger.error("Failed to load input CSV: %s", exc, exc_info=True)
        raise

    validate_schema(df)

    logger.info(
        "Loaded raw data successfully: %d rows, %d columns",
        df.shape[0],
        df.shape[1],
    )

    return df


def clean_traffic_data(data):
    """Clean and standardise the traffic dataset."""

    logger.info("Starting data cleaning.")

    data = data.copy()

    # Parse datetime
    data["date_time"] = pd.to_datetime(
        data["date_time"],
        errors="coerce"
    )

    logger.info("Datetime conversion completed.")

    data["month"] = data["date_time"].dt.month

    # Handle missing holiday values
    missing_holiday = data["holiday"].isna().sum()

    if missing_holiday > 0:
        logger.info(
            "Found %d missing holiday values.",
            missing_holiday
        )

        data["holiday"] = data["holiday"].fillna("None")

    # Remove duplicate rows
    duplicate_count = data.duplicated().sum()

    if duplicate_count > 0:
        logger.warning(
            "Found %d duplicate rows. Removing duplicates.",
            duplicate_count
        )

        data = data.drop_duplicates().copy()

    # Handle implausible rainfall values
    rainfall_outlier_count = (data["rain_1h"] > 9).sum()

    if rainfall_outlier_count > 0:
        logger.warning(
            "Found %d implausible rainfall values above 9 mm. "
            "Replacing with monthly medians.",
            rainfall_outlier_count
        )

        data.loc[data["rain_1h"] > 9, "rain_1h"] = np.nan

        data["rain_1h"] = data.groupby("month")["rain_1h"].transform(
            lambda x: x.fillna(x.median())
        )

        logger.warning(
            "Implausible rainfall values imputed using monthly medians."
        )

    # Validate traffic volume
    if (data["traffic_volume"] < 0).any():
        logger.error("Negative traffic volume detected.")
        raise ValueError(
            "Invalid negative traffic volume detected."
        )

    if data["traffic_volume"].isna().any():
        logger.error("Missing traffic volume detected.")
        raise ValueError(
            "Missing traffic volume detected."
        )

    logger.info(
        "Data cleaning completed. Final rows: %d",
        len(data)
    )

    return data


def add_time_features(data):
    """Add time-based features."""

    logger.info("Starting time feature engineering.")

    data = data.copy()

    data["year"] = data["date_time"].dt.year
    data["hour"] = data["date_time"].dt.hour
    data["day_of_week"] = data["date_time"].dt.dayofweek

    # Cyclical encoding for time features
    data["hour_sin"] = np.sin(2 * np.pi * data["hour"] / 24)
    data["hour_cos"] = np.cos(2 * np.pi * data["hour"] / 24)

    data["day_of_week_sin"] = np.sin(
        2 * np.pi * data["day_of_week"] / 7
    )
    data["day_of_week_cos"] = np.cos(
        2 * np.pi * data["day_of_week"] / 7
    )

    logger.info("Cyclical time features created.")

    data["day_of_month"] = data["date_time"].dt.day
    data["month_name"] = data["date_time"].dt.month_name()

    data["is_weekend"] = data["day_of_week"] >= 5

    data["day_type"] = data["is_weekend"].map({
        True: "Weekend",
        False: "Weekday"
    })

    data["month_year"] = (
        data["date_time"]
        .dt.to_period("M")
        .astype(str)
    )

    # Scaled continuous variables
    data["temp_scaled"] = (
        (data["temp"] - data["temp"].mean())
        / data["temp"].std()
    )

    data["clouds_all_scaled"] = (
        (data["clouds_all"] - data["clouds_all"].mean())
        / data["clouds_all"].std()
    )

    logger.info("Scaled continuous features created.")

    # Data-driven congestion category using traffic-volume quartiles
    q1 = data["traffic_volume"].quantile(0.25)
    q2 = data["traffic_volume"].quantile(0.50)
    q3 = data["traffic_volume"].quantile(0.75)

    data["congestion_category"] = pd.cut(
        data["traffic_volume"],
        bins=[-np.inf, q1, q2, q3, np.inf],
        labels=["Low", "Moderate", "High", "Severe"],
        include_lowest=True
    )

    logger.info(
        "Congestion categories created using traffic-volume quartiles: "
        "Q1=%.2f, Q2=%.2f, Q3=%.2f",
        q1,
        q2,
        q3
    )

    logger.info("Time feature engineering completed.")

    return data


def run_pipeline(input_file, output_file):
    """Run the complete traffic data pipeline."""

    logger.info("Pipeline started.")

    raw_data = load_and_validate_data(input_file)

    cleaned_data = clean_traffic_data(raw_data)

    processed_data = add_time_features(cleaned_data)

    processed_data.to_csv(output_file, index=False)

    logger.info(
        "Processed dataset saved to: %s",
        output_file
    )

    logger.info(
        "Pipeline completed successfully. Final shape: %s",
        processed_data.shape
    )

    return processed_data


def configure_logging(log_file):
    """Configure console and file logging."""

    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)



import argparse


def main():
    parser = argparse.ArgumentParser(
        description="Smart City Traffic Intelligence Pipeline"
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True
    )

    # Validate command
    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate the raw dataset schema"
    )
    validate_parser.add_argument(
        "--input",
        required=True,
        help="Path to the input CSV file"
    )

    # Clean command
    clean_parser = subparsers.add_parser(
        "clean",
        help="Clean the traffic dataset"
    )
    clean_parser.add_argument(
        "--input",
        required=True,
        help="Path to the input CSV file"
    )
    clean_parser.add_argument(
        "--output",
        required=True,
        help="Path for the cleaned CSV file"
    )

    # Run command
    run_parser = subparsers.add_parser(
        "run",
        help="Run the complete pipeline"
    )
    run_parser.add_argument(
        "--input",
        required=True,
        help="Path to the input CSV file"
    )
    run_parser.add_argument(
        "--output",
        required=True,
        help="Path for the processed CSV file"
    )

    args = parser.parse_args()

    configure_logging(
    Path(__file__).resolve().parent / "reports" / "logs" / "pipeline.log"
)

    if args.command == "validate":
        data = load_and_validate_data(args.input)
        logger.info(
            "Validation completed successfully. Rows: %d",
            len(data)
        )

    elif args.command == "clean":
        data = load_and_validate_data(args.input)
        cleaned = clean_traffic_data(data)

        Path(args.output).parent.mkdir(
            parents=True,
            exist_ok=True
        )

        cleaned.to_csv(args.output, index=False)

        logger.info(
            "Cleaned dataset saved to: %s",
            args.output
        )

    elif args.command == "run":
        Path(args.output).parent.mkdir(
            parents=True,
            exist_ok=True
        )

        run_pipeline(
            args.input,
            args.output
        )
if __name__ == "__main__":
    main()
