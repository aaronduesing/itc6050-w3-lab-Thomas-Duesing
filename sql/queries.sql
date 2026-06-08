--1. 
EXPLAIN ANALYZE
SELECT
  date_trunc('month', order_date) AS month,
  COUNT(order_id) AS orders,
  SUM(total) AS revenue
FROM orders
GROUP BY month
ORDER BY month DESC;
--2.
EXPLAIN ANALYZE
SELECT
  p.name AS product_name,
  SUM(o.quantity) AS total_qty,
  SUM(o.quantity * o.unit_price) AS revenue
FROM order_item o
JOIN product p
  ON o.product_id = p.product_id
GROUP BY p.name
ORDER BY revenue DESC
LIMIT 10;
--3.
EXPLAIN ANALYZE
SELECT
  status,
  COUNT(order_id) AS order_count,
  AVG(total) AS avg_total,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY total) AS median_total
FROM orders
GROUP BY status;
--4
EXPLAIN ANALYZE
SELECT
  c.customer_id,
  c.first_name,
  c.last_name,
  c.email,
  MAX(o.order_date) AS last_order_date,
  (NOW() - MAX(o.order_date)) AS days_dormant
FROM customer AS c
LEFT JOIN orders AS o
  ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.first_name, c.last_name, c.email
HAVING MAX(o.order_date) IS NULL
   OR MAX(o.order_date) < NOW() - INTERVAL '90 days'
ORDER BY last_order_date;
--5
EXPLAIN ANALYZE
WITH customer_spend AS (
  SELECT
    c.customer_id,
    c.email,
    SUM(o.total) AS lifetime_spend
  FROM customer c
  LEFT JOIN orders o
    ON c.customer_id = o.customer_id
  GROUP BY c.customer_id, c.email
)

SELECT
  RANK() OVER (ORDER BY lifetime_spend DESC) AS rank,
  email,
  lifetime_spend,
  lifetime_spend
    - LAG(lifetime_spend) OVER (ORDER BY lifetime_spend DESC)
    AS gap_to_previous
FROM customer_spend
ORDER BY rank
LIMIT 20;