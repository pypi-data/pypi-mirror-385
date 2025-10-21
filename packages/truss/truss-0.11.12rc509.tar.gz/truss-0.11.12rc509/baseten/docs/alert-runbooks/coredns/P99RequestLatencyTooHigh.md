# P99RequestLatencyTooHigh

## Meaning

Coredns p99 latency is very high, dns resolution could be slow or failing
occassionally.

<details>
<summary>Full context</summary>

dns resolution is foundational to networking in any infrastructure, we use
coredns for it. p99 latency being high means that at least one in hundred dns
resolutions are happening very slowly.

</details>

## Impact

High. All kinds of requests may be failing across the cluster, some of them may
be user facing. p99 latency for almost all requests in the cluster are likely
affected, because dns resolution is usually the first step to making requests.

## Diagnosis

There are two most likely causes: coredns being overloaded or ineffective
caching. Check cache hit rate and tune settings as needed. Make sure coredns
pods are not running out of resources. Watch out for cpu throttling, that's a
strong sign that coredns is underprovisioned for cpu.

## Mitigation

Increasing number of coredns replicas may help. Tuning coredns cache settings
can also be done quickly, coredns cache settings are in the `coredns` configmap
in kube-system namespace. They take effect immediately after the configmap is
modified.

Can also consider increasing per pod coredns resources.
