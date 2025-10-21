# AsyncServiceHighPushLatency

**NOTE: This runbook is a WIP**

The `AsyncServiceHighPushLatency` alert is triggered when the P99 latency to 
push a request to the async queue exceeds a certain threshold over a certain 
amount of time.

## Impact

High push latency results in slower response times from `/async_predict` and 
lower enqueue throughput.

## Diagnosis

In load tests, we have observed high push latency in these scenarios:
* Heavy read traffic (e.g. > 200 requests / sec to the `GET /async_request` 
endpoint)
* Heavy write traffic (e.g. > 200 requests / sec to the `POST /async_predict` 
endpoint)

We currently don't have tracing inside the async request service, so 
unfortunately there's some guesswork involved in determining bottlenecks.

Possible mitigations:
* Assuming the bottleneck is at the DB level:
  * Increase [async service connection pool size](https://github.com/basetenlabs/baseten/blob/90fd990188132f714e5a36114565b5b953885c8c/async-request-service/core/settings/base.py#L26-L27)
  * Move read queries to read replica

## Useful resources
* [Async service Grafana dashboard](https://grafana.baseten.co/d/b4ce6885-f15b-463d-b9cc-da14bb2297fe/async-detailed?orgId=1&refresh=30s)
