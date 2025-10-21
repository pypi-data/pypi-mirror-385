# Workload Plane Health Checks

These health checks run every minute in each workload plane to ensure that sync inference and async inference are functioning as expected. The health checks are triggered by a periodic Celery beat task configured [here](/backend/oracles/migrations/0294_auto_20240613_1626.py).

The django command defined [here](/backend/common/management/commands/create_workload_planes_health_check_oracle.py) runs as part of the hourly smoke tests defined in `.github/workflows/production-smoke-test.yml`. This django command ensures that a health check oracle exists for each workload plane in the current environment.

Every minute, the `update_workload_plane_continuous_healthcheck` celery task is called by the periodic task. This task runs `workload_plane_health_check` on each defined WorkloadPlane in the current environment. This health check consists of the following steps:
1. Ensuring the smoke test organization and deployed health check model exists
2. Running a sync inference request on the model using `/predict` and verifying its response
3. Running an async inference request on the model using `/async_predict`
    - Checking that the `/smoke_test_webhook` endpoint is called with the expected payload
    - Checking that the `/async_request` endpoint reports the expected statuses

See the [Workload Plane Health Check runbook](/docs/alert-runbooks/baseten-django/WorkloadPlaneHealthNotOk.md) for more details on diagnosing and resolving issues related to workload plane health.


### Testing locally
* Run Django, Operator, Beefeater, Async Processor, Async Service locally

* Run `poetry run python manage.py create_workload_planes_health_check_oracle` after modifying the following in `backend/common/management/commands/create_workload_planes_health_check_oracle.py`:
  * Set `BASETEN_API_TOKEN` to be the `api_key` for the `default` workload plane listed when visiting http://localhost:9090/smoke_test_config
  * Set `BASETEN_API_HOST = "http://localhost:9090"`

* Run the `update_workload_plane_continuous_healthcheck()` in `shell_plus` after modifying the following in `backend/common/observability/metrics/workload_plane_continuous_health.py`:
  * Set `hostname = "http://localhost:9090"`
  * Set `"webhook_endpoint": "http://0.0.0.0:8000/smoke_test_webhook"` in the `/async_predict` call
  * Add a `"Host": f"model-{oracle.id}.api.dev.baseten.co"` header in the `/async_predict` and `/async_request` calls
