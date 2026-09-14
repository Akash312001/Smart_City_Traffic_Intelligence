
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
    """Load the raw dataset and validate its schema."""

    logger.info("Loading dataset: %s", file_path)

    data = pd.read_csv(file_path)

    validate_schema(data)

    logger.info("Dataset loaded successfully. Rows: %d", len(data))

    return data


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

    # Handle invalid temperature values
    invalid_temp_count = (data["temp"] == 0).sum()

    if invalid_temp_count > 0:
        logger.warning(
            "Found %d invalid temperature values.",
            invalid_temp_count
        )

        data.loc[data["temp"] == 0, "temp"] = np.nan

        data["month"] = data["date_time"].dt.month

        data["temp"] = data.groupby("month")["temp"].transform(
            lambda x: x.fillna(x.median())
        )

        logger.info(
            "Invalid temperatures imputed using monthly medians."
        )

    else:
        data["month"] = data["date_time"].dt.month

    # Standardise categorical values
    for column in ["weather_main", "weather_description"]:
        data[column] = data[column].str.strip().str.lower()

    logger.info("Weather categories standardised.")

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

    logger.info(
        "Time feature engineering completed."
    )

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
\n\nif __name__ == "__main__":

    project_root = Path(__file__).resolve().parent

    input_file = (
    project_root.parent
    / "data"
    / "Metro_Interstate_Traffic_Volume.csv"
)

    output_dir = project_root / "data" / "processed"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "pipeline_output.csv"

    log_dir = project_root / "reports" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "pipeline.log"

    configure_logging(log_file)

    run_pipeline(input_file, output_file)
