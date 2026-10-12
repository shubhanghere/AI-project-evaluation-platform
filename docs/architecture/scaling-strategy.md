# Scaling strategy

Capacity estimates and assumptions are in the main report. Average input rate is 0.000347/s at 30/day and 0.1157/s at 10,000/day. At 8.5 minutes mean evaluation, Little's Law implies about 59 concurrent evaluations at average target rate; peak and retries add headroom. Scale worker task count based on oldest queue age/backlog while respecting provider concurrency and token budgets. Keep the API stateless; tune pooling and indexes before partitioning.
