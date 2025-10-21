# LogWriteLatencyTooHigh

## Meaning

Writing logs to Loki is slow.

<details>
<summary>Full context</summary>

We use Loki to aggregate and query logs. Promtail tails k8s pod logs and writes
them to Loki. This alerts means that the write latency is too high. Writes
should normally be very quick.

</details>

## Impact

If write latency continues to be high then promtail may start lagging and that
increases the chance of losing some logs entirely.

## Diagnosis

Analyze Loki prometheus metrics via grafana to analyze if loki-write instances
are overloaded. Watch out for any recent infrastructure related changes that may
affect networking. See if number of writes has spiked.

[Loki internal dashboard](https://grafana.baseten.co/d/AItSVYU7k/loki-baseten?orgId=1&refresh=10s)
[Loki customer dashboard](https://grafana.baseten.co/d/bs5IVYU7z/loki-user?orgId=1&refresh=10s)

## Mitigation

Increasing number of replicas for loki-write stateful set might help. Increasing
pod resources for the same statefulset may also help.

```
kubectl edit statefulset loki-write -n logging
# Update spec.replicas (preferred)
# Or update resource requests in the embedded pod template in the statefulset
```
