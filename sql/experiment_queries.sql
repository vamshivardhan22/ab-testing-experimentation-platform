-- A/B testing SQL examples for the Marketing A/B dataset.

SELECT
  variant,
  COUNT(*) AS users,
  ROUND(100.0 * AVG(converted), 2) AS conversion_rate,
  ROUND(AVG(total_ads), 2) AS avg_ads_seen,
  ROUND(MIN(total_ads), 2) AS min_ads_seen,
  ROUND(MAX(total_ads), 2) AS max_ads_seen
FROM experiment
GROUP BY variant;

SELECT
  most_ads_day,
  variant,
  COUNT(*) AS users,
  ROUND(100.0 * AVG(converted), 2) AS conversion_rate
FROM experiment
GROUP BY most_ads_day, variant
ORDER BY most_ads_day, variant;

SELECT
  most_ads_hour,
  variant,
  COUNT(*) AS users,
  ROUND(100.0 * AVG(converted), 2) AS conversion_rate
FROM experiment
GROUP BY most_ads_hour, variant
ORDER BY most_ads_hour, variant;
