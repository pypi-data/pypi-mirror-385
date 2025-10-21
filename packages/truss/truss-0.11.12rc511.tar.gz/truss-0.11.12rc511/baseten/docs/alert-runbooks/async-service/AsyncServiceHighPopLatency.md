# AsyncServiceHighPopLatency

**NOTE: This runbook is a WIP**

The `AsyncServiceHighPopLatency` alert is triggered when the P99 latency to pop 
a request from the async queue exceeds a certain threshold over a certain 
amount of time.

## Impact

High pop latency results in additional end-to-end latency in processing 
inference requests. Although async use cases tend to be less latency sensitive 
than sync, this is still undesirable for users.

## Diagnosis

This could be caused by:
* DB level load
  * Unoptimized pop query (e.g. query doesn't perform index scan)

We currently don't have tracing inside the async request service, so 
unfortunately there's some guesswork involved in determining bottlenecks.

## Useful resources
* [Async service Grafana dashboard](https://grafana.baseten.co/d/b4ce6885-f15b-463d-b9cc-da14bb2297fe/async-detailed?orgId=1&refresh=30s)

