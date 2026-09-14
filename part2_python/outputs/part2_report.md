# Part 2 — Python Pipeline Report

## Methodology

The pipeline validates the source schema before processing, parses timestamps, standardises categorical text, removes exact duplicate records, validates physical ranges, and replaces impossible temperature/rainfall readings with monthly medians. The pipeline uses named Python loggers and a main-script configuration that writes timestamp, level, module and message to both console and `pipeline.log`.

The raw file contains 48,204 rows and 9 columns. Cleaning removed 17 exact duplicates and imputed 10 non-physical temperature readings (<=0 K) plus 120 rainfall readings above the assignment's 9 mm plausibility threshold. The resulting cleaned dataset contains 48,187 rows.

Feature engineering creates hour, day of week, day name, month, year, weekend and holiday indicators, sine/cosine cyclical encodings for hour and day of week, Celsius temperature, weather risk indicators, z-normalised temperature/cloud cover, a four-level data-driven congestion category and the documented proxy high-risk label.

## Visualisation findings

1. **Traffic by hour:** demand is strongly time-dependent, with the highest average around 16:00 and the lowest in the early morning.
2. **Weekday vs weekend:** weekdays average about 3,534 vehicles/hour versus about 2,571 on weekends.
3. **Weather:** observed average traffic differs by weather condition, with Clouds highest and Squall lowest; rare categories should be treated cautiously.
4. **Temperature vs traffic:** the scatter plot shows a broad cloud rather than a strong linear relationship, consistent with the weak Pearson correlation.

## Mini application

The CLI supports `traffic-at`, `high-periods`, `weekday-weekend` and `recommend`. It logs the command and arguments and handles malformed input with an error message rather than an unhandled traceback.

## Reproducibility

The repository contains scripts, generated figures, processed data, a sample pipeline log, README instructions and a suggested incremental Git commit history. The pipeline can be rerun from the raw CSV.
