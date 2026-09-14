-- Test
SELECT *
FROM traffic
LIMIT 10;

-- Number of records
SELECT COUNT(*) AS total_records
FROM traffic;

-- Annual traffic totals
SELECT
    strftime('%Y', date_time) AS year,
    SUM(traffic_volume) AS total_traffic
FROM traffic
GROUP BY year
ORDER BY year;

-- Mean traffic volume

SELECT
    AVG(traffic_volume) AS mean_traffic
FROM traffic;

-- Median traffic volume

SELECT
    AVG(traffic_volume) AS median_traffic
FROM (
    SELECT
        traffic_volume
    FROM traffic
    ORDER BY traffic_volume
    LIMIT 2 - (SELECT COUNT(*) FROM traffic) % 2
    OFFSET (SELECT (COUNT(*) - 1) / 2 FROM traffic)
);

-- Standard deviation of traffic volume

SELECT
    SQRT(
        AVG(
            (traffic_volume -
             (SELECT AVG(traffic_volume) FROM traffic))
            *
            (traffic_volume -
             (SELECT AVG(traffic_volume) FROM traffic))
        )
    ) AS standard_deviation
FROM traffic;

-- Variance of traffic volume

SELECT
    AVG(
        (traffic_volume -
         (SELECT AVG(traffic_volume) FROM traffic))
        *
        (traffic_volume -
         (SELECT AVG(traffic_volume) FROM traffic))
    ) AS variance
FROM traffic;

-- Minimum, maximum and range of traffic volume

SELECT
    MIN(traffic_volume) AS minimum_traffic,
    MAX(traffic_volume) AS maximum_traffic,
    MAX(traffic_volume) - MIN(traffic_volume) AS traffic_range
FROM traffic;

-- Pearson correlation between temperature and traffic volume

WITH stats AS (
    SELECT
        AVG(temp) AS mean_temp,
        AVG(traffic_volume) AS mean_traffic
    FROM traffic
),
correlation AS (
    SELECT
        SUM(
            (temp - stats.mean_temp) *
            (traffic_volume - stats.mean_traffic)
        ) AS numerator,

        SQRT(
            SUM(
                (temp - stats.mean_temp) *
                (temp - stats.mean_temp)
            ) *
            SUM(
                (traffic_volume - stats.mean_traffic) *
                (traffic_volume - stats.mean_traffic)
            )
        ) AS denominator
    FROM traffic, stats
)
SELECT
    numerator / denominator AS pearson_correlation
FROM correlation;

-- Probability of high congestion
-- A = traffic_volume > 5500

SELECT
    AVG(
        CASE
            WHEN traffic_volume > 5500 THEN 1.0
            ELSE 0.0
        END
    ) AS probability_high_congestion
FROM traffic;

-- Conditional probability:
-- P(Clear weather | High congestion)

SELECT
    AVG(
        CASE
            WHEN weather_main = 'Clear'
                 AND traffic_volume > 5500
            THEN 1.0
            ELSE 0.0
        END
    )
    /
    AVG(
        CASE
            WHEN traffic_volume > 5500
            THEN 1.0
            ELSE 0.0
        END
    ) AS probability_clear_given_high_congestion
FROM traffic;

-- Probability of clear weather

SELECT
    AVG(
        CASE
            WHEN weather_main = 'Clear'
            THEN 1.0
            ELSE 0.0
        END
    ) AS probability_clear
FROM traffic;

-- Joint probability:
-- P(High Congestion AND Clear Weather)

SELECT
    AVG(
        CASE
            WHEN traffic_volume > 5500
                 AND weather_main = 'Clear'
            THEN 1.0
            ELSE 0.0
        END
    ) AS probability_high_and_clear
FROM traffic;

-- Independence test:
-- Compare observed P(A and B) with P(A) * P(B)

WITH probabilities AS (
    SELECT
        AVG(
            CASE
                WHEN traffic_volume > 5500
                THEN 1.0
                ELSE 0.0
            END
        ) AS p_high,

        AVG(
            CASE
                WHEN weather_main = 'Clear'
                THEN 1.0
                ELSE 0.0
            END
        ) AS p_clear
    FROM traffic
)
SELECT
    p_high * p_clear AS expected_if_independent
FROM probabilities;

-- Odds ratio:
-- High congestion vs clear/non-clear weather

WITH counts AS (
    SELECT
        SUM(
            CASE
                WHEN weather_main = 'Clear'
                     AND traffic_volume > 5500
                THEN 1 ELSE 0
            END
        ) AS a,

        SUM(
            CASE
                WHEN weather_main = 'Clear'
                     AND traffic_volume <= 5500
                THEN 1 ELSE 0
            END
        ) AS b,

        SUM(
            CASE
                WHEN weather_main != 'Clear'
                     AND traffic_volume > 5500
                THEN 1 ELSE 0
            END
        ) AS c,

        SUM(
            CASE
                WHEN weather_main != 'Clear'
                     AND traffic_volume <= 5500
                THEN 1 ELSE 0
            END
        ) AS d
    FROM traffic
)
SELECT
    a,
    b,
    c,
    d,
    (CAST(a AS REAL) * d) /
    (CAST(b AS REAL) * c) AS odds_ratio
FROM counts;


-- Inspect available holiday labels

SELECT DISTINCT holiday
FROM traffic
ORDER BY holiday;


-- Inspect New Year's Day and Labor Day observations

SELECT
    date_time,
    holiday,
    temp,
    traffic_volume
FROM traffic
WHERE holiday IN ('New Years Day', 'Labor Day')
ORDER BY date_time;

-- Holiday temperature analysis for 2015-2017

SELECT
    strftime('%Y', date_time) AS year,
    holiday,
    COUNT(*) AS observations,
    AVG(temp) AS average_temperature,
    MIN(temp) AS minimum_temperature,
    MAX(temp) AS maximum_temperature
FROM traffic
WHERE holiday IN ('New Years Day', 'Labor Day')
  AND strftime('%Y', date_time) BETWEEN '2015' AND '2017'
GROUP BY
    year,
    holiday
ORDER BY
    year,
    holiday;

-- Holiday temperatures in Kelvin and Celsius

SELECT
    strftime('%Y', date_time) AS year,
    holiday,
    COUNT(*) AS observations,
    AVG(temp) AS average_temperature_kelvin,
    AVG(temp) - 273.15 AS average_temperature_celsius
FROM traffic
WHERE holiday IN ('New Years Day', 'Labor Day')
  AND strftime('%Y', date_time) BETWEEN '2015' AND '2017'
GROUP BY
    year,
    holiday
ORDER BY
    year,
    holiday;