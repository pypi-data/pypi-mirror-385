# LogReadLatencyTooHigh

## Meaning

Latency is high for read call to Loki.

<details>
<summary>Full context</summary>

We use Loki for aggregating and querying both internal and user logs. This alert
means that reading logs from Loki, typically by running LogQL queries, is slow.

</details>

## Impact

Medium: Logs may load slowly in the Logs tab in Baseten application. There are
separate Loki setups for user-facing and baseten internal. Check which one the
alert is for. User-facing is much more critical.

Low: Internal debugging may be affected due to slow querying of logs in grafana.

## Diagnosis

Loki provides a lot of prometheus metrics, use them through grafana to debug.
Loki collects logs for itself as well, they can be accessed through grafana as
well. If Loki is in a bad state, and log querying is not working via grafana
then directly look at Loki read statefulset pod logs via kubectl.

Watch out for any frontend changes that would cause logs to be queried more
frequently.

[Loki internal dashboard](https://grafana.baseten.co/d/AItSVYU7k/loki-baseten?orgId=1&refresh=10s)
[Loki customer dashboard](https://grafana.baseten.co/d/bs5IVYU7z/loki-user?orgId=1&refresh=10s)


## Mitigation

Loki read can be scaled by increasing number of replicas in the loki-read
stateful set, that might help. Increasing resource request for individual pods
is another option. 

For example, to update loki-read

```
kubectl edit statefulset loki-read -n logging
# Update spec.replicas (preferred)
# Or update resource requests in the embedded pod template in the stateful set
```
