# AsyncServiceZeroProcessingRequests

The `AsyncServiceZeroProcessingRequests` alert is triggered when the async processor is processing zero requests for a certain period of time when there are requests queued up. 

## Impact

No processing requests when requests are queued up indicates that a critical flow (the async processor) is down, users are likely seeing async requests expire in the queue instead of being processed. These expired requests are not retried in the async service.

## Diagnosis

### Debugging guide
Use logs and dashboards in the links below for the async request service and processor to debug. Check #alerts-production-sentry in slack for any related errors.

Questions to guide debugging and root cause analysis:
* Is there any cpu or memory pressure on the async service or processor?
* Do errors come from the async service or processor?
* Are we seeing any errors related to the async service's DB?
* Can we isolate the issues to a particular Workload Plane or is it affecting all Workload Planes?
* Are related services like Beefeater and Django healthy?

### Previous incidents

[7/21/25's async inference outage incident report](https://www.notion.so/ml-infra/No-async-requests-processed-for-15m-in-us-central-1-prod-1-24291d2472738075b254ed88f24c0d95?source=copy_link)


## Useful resources
* [Async service Grafana dashboard](https://grafana.baseten.co/d/b4ce6885-f15b-463d-b9cc-da14bb2297fe/async-detailed?orgId=1&refresh=30s)
