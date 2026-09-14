"""Visualisation utilities for the Smart City Traffic project."""

import logging
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


logger = logging.getLogger(__name__)


def create_visualizations(data, output_dir):
    """Create required traffic analysis visualisations."""

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Average traffic by hour
    hourly = (
        data.groupby("hour")["traffic_volume"]
        .mean()
    )

    plt.figure(figsize=(10, 6))
    hourly.plot(kind="line", marker="o")
    plt.title("Average Traffic Volume by Hour")
    plt.xlabel("Hour")
    plt.ylabel("Average Traffic Volume")
    plt.tight_layout()
    plt.savefig(output_dir / "average_traffic_by_hour.png")
    plt.close()

    logger.info("Created average traffic by hour visualisation.")

    # 2. Average traffic by day type
    day_type = (
        data.groupby("day_type")["traffic_volume"]
        .mean()
    )

    plt.figure(figsize=(8, 6))
    day_type.plot(kind="bar")
    plt.title("Average Traffic Volume by Day Type")
    plt.xlabel("Day Type")
    plt.ylabel("Average Traffic Volume")
    plt.tight_layout()
    plt.savefig(output_dir / "average_traffic_by_day_type.png")
    plt.close()

    logger.info("Created average traffic by day type visualisation.")

    # 3. Average traffic by weather
    weather = (
        data.groupby("weather_main")["traffic_volume"]
        .mean()
        .sort_values(ascending=False)
    )

    plt.figure(figsize=(10, 6))
    weather.plot(kind="bar")
    plt.title("Average Traffic Volume by Weather")
    plt.xlabel("Weather Condition")
    plt.ylabel("Average Traffic Volume")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(output_dir / "average_traffic_by_weather.png")
    plt.close()

    logger.info("Created average traffic by weather visualisation.")

    logger.info(
        "Visualisation generation completed. Output directory: %s",
        output_dir
    )