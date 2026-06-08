1. In Q3, what's the difference between AVG() and PERCENTILE_CONT(0.5)? Which is more
honest for skewed data, and why?
Average is sum/count and median finds the middle value. Median is better for skewed data cause skews also skew the average in the skew's favor.

2. In Q5, why did we need a window function instead of just ORDER BY ... DESC LIMIT 20?

Just creating an ORDER BY query would return only the top results, but not analye rank or compare between customers.


Concept check: 
1. When would you choose orders (referenced) over orders_embedded?
Mostly for joining, scalability, and independant access to each column, since the data is normalized.
2. When would you choose orders_embedded over orders?
Mostly for when you want to pull up the entire order, when I do not need to use joins, and not compare rows wihin orders.

Q1 — Monthly revenue trend
| Aspect          | SQL (Postgres) | MongoDB |
| --------------- | -------------- | ------- |
| Lines of code   | 8              | 17      |
| Wall time (ms)  | 278.3          | 189.8   |
| Subjective ease | ★★★★★       | ★       |

Q2 — Top 10 products by revenue
| Aspect          | SQL (Postgres) | MongoDB |
| --------------- | -------------- | ------- |
| Lines of code   | 11             | 24      |
| Wall time (ms)  | 399.1          | 463.3   |
| Subjective ease | ★★★★★       | ★       |

Q3 — Order stats by status (count, avg, median)
| Aspect          | SQL (Postgres) | MongoDB |
| --------------- | -------------- | ------- |
| Lines of code   | 8              | 25      |
| Wall time (ms)  | 163.6          | 145.2   |
| Subjective ease | ★★★★★       | ★       |

Q4 — Dormant customers (90+ days)
| Aspect          | SQL (Postgres) | MongoDB |
| --------------- | -------------- | ------- |
| Lines of code   | 15             | 43      |
| Wall time (ms)  | 83.4           | 332.3   |
| Subjective ease | ★★★          | ★       |

Q5 — Top customers by lifetime spend
| Aspect          | SQL (Postgres) | MongoDB |
| --------------- | -------------- | ------- |
| Lines of code   | 22             | 53      |
| Wall time (ms)  | 117.1          | 726.9   |
| Subjective ease | ★★★★★       | ★       |


🎯 Concept check (in your README, in addition to the per-query notes):
1. Which query was hardest in MongoDB? Why?
Q5 because although it is the same concept as SL, building the pipeline is more complex than in SQL becasue you are combining multiple operations. The logic takes a bit more to process.
2. Which was hardest in SQL? Why?
Also Q5 because although the syntax and structure are quite simple, it requires a level of logical reasoning to know which order to process first and then carry that level to the next window.
3. Did the embedded orders_embedded collection make any query notably easier than working from referenced orders?
Embedded made Q2 easier since you can unwind the array and group by product_id. This would have required an extra join statement using the references orders.
