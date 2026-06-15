-- A/B testing SQL examples

SELECT
  variant,
  COUNT(*) AS visitors,
  ROUND(100.0 * AVG(clicked), 2) AS ctr,
  ROUND(100.0 * AVG(converted), 2) AS conversion_rate,
  ROUND(SUM(revenue), 2) AS revenue,
  ROUND(AVG(revenue), 2) AS revenue_per_visitor
FROM experiment
GROUP BY variant;

SELECT
  traffic_source,
  variant,
  COUNT(*) AS visitors,
  ROUND(100.0 * AVG(converted), 2) AS conversion_rate
FROM experiment
GROUP BY traffic_source, variant
ORDER BY traffic_source, variant;
