"""Feature engineering utilities for the Smart City Traffic project."""

import logging

import numpy as np
import pandas as pd


logger = logging.getLogger(__name__)


def add_time_features(data):
    """Create time, cyclical, scaling, and congestion features."""

    logger.info("Starting time feature engineering.")

    data = data.copy()

    # Basic time features
    data["year"] = data["date_time"].dt.year
    data["hour"] = data["date_time"].dt.hour
    data["day_of_week"] = data["date_time"].dt.dayofweek
    data["day_of_month"] = data["date_time"].dt.day
    data["month_name"] = data["date_time"].dt.month_name()

    # Cyclical encoding
    data["hour_sin"] = np.sin(
        2 * np.pi * data["hour"] / 24
    )
    data["hour_cos"] = np.cos(
        2 * np.pi * data["hour"] / 24
    )

    data["day_of_week_sin"] = np.sin(
        2 * np.pi * data["day_of_week"] / 7
    )
    data["day_of_week_cos"] = np.cos(
        2 * np.pi * data["day_of_week"] / 7
    )

    logger.info("Cyclical time features created.")

    # Weekend and day-type indicators
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
    temp_std = data["temp"].std()
    clouds_std = data["clouds_all"].std()

    if temp_std != 0:
        data["temp_scaled"] = (
            (data["temp"] - data["temp"].mean())
            / temp_std
        )
    else:
        data["temp_scaled"] = 0.0

    if clouds_std != 0:
        data["clouds_all_scaled"] = (
            (data["clouds_all"] - data["clouds_all"].mean())
            / clouds_std
        )
    else:
        data["clouds_all_scaled"] = 0.0

    logger.info("Scaled continuous features created.")

    # Data-driven congestion categories
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

    logger.info(
        "Feature engineering completed. Shape: %s",
        data.shape
    )

    return data