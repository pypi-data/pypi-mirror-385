# AsyncServiceHigh5xxErrorRate

The `AsyncServiceHigh5xxErrorRate` alert is triggered when the async service returns 5xx error codes at a high rate from either the `/async_predict` or `/async_request` endpoints.

## Impact

High 5xx error rates indicate a critical flow (the async service) is down -- users likely cannot create async inference requests using the `/async_predict` endpoint, and since we currently don't support buffering failed requests, those requests are lost. It is also possible that we cannot get the status of requests using the `/async_request` endpoint.

## Diagnosis

### Debugging guide
Use logs and dashboards in the links below for the async request service and processor to debug. Check #alerts-production-sentry in slack for any related errors.

Questions to guide debugging and root cause analysis:
* Which endpoints are returning 5xx errors? `/async_predict`? `/async_request`? Both?
* Can we isolate the issues to a particular Workload Plane or is it affecting all Workload Planes?
* Do errors come from the async service or processor?
* Are we seeing any errors related to the async service's DB?
* Are related services like Beefeater and Django healthy?

### Previous incidents

From [7/30/24's async inference outage incident report](https://www.notion.so/ml-infra/Async-inference-outage-in-us-east-4-98505aeafdb34ef7a0d259b0140e7905?pvs=4) one possible root cause of receiving `5xx` errors from `/async_predict` is that async service or processor is connected to the wrong replica (in this case the read replica), which can be remediated by performing a `kubectl rollout restart` on the affected async deployment (service or processor or both).


## Useful resources
* [Async service production runbook](https://www.notion.so/ml-infra/WIP-Production-runbook-2059b9ba8a6a4a9898357349ea3283e9?pvs=4) - includes links to logs in Grafana, useful k8s commands, and debugging tips
* [Async service Grafana dashboard](https://grafana.baseten.co/d/b4ce6885-f15b-463d-b9cc-da14bb2297fe/async-detailed?orgId=1&refresh=30s)

## Mitigation
If the issue is cluster-specific (e.g. not due to a global resource constraint or a bug in Baseten code / model code), the issue can be mitigated by migrating the deployment. See [here](https://www.notion.so/ml-infra/Core-Product-Oncall-Runbook-1e591d24727380979752f4d577881224?source=copy_link#24291d24727380a89680cc0ba0218642)
