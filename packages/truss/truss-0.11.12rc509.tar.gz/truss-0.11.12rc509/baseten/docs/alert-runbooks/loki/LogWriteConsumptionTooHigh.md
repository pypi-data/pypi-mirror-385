# LogWriteConsumptionTooHigh

## Meaning

Too many log messages are being written.

<details>
<summary>Full context</summary>

We use Loki to aggregate and query logs. This alert means that too many logs are
being written to Loki.

</details>

## Impact

High number of writes may blow up storage used by Loki (on s3) and overload,
loki write service. While Loki reads and writes are decoupled, via separte
statefulsets, there may still be some cross-impact. e.g. fresh logs are
kept and queried directly from ingester. Too many labels may affect index
caching on reads. Queries on high cardinality data may be slow and may affect
overall throughput on reads.

## Diagnosis

Try to find what's causing the large number of writes.
[LogQL](https://grafana.com/docs/loki/latest/logql/) supports aggregations which
could be useful in finding this; these queries can be run through grafana. You
can also look at Loki prometheus metrics via grafana to find interesting
patterns such as which log level the writes have spiked the most on. 

Watch out for log level being set to debug for workloads. Some components such
as coredns can generate humoungous amounts of logs very quickly at debug level.
This should be either avoided or done for very short periods.

Example logql query to find pynode pod that's logging the most:
```
rate({app="pynode"}[1m])
```

## Mitigation

Try to find the source of spike in writes and stop it. e.g. turn down log levels
if needed.
