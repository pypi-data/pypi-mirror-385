# PynodeHight5xxErrorRate

## Meaning

Too many requests to pynode are getting 5xx http status code.

<details>
<summary>Full context</summary>

Pynode is failing to process some requests and the failures are unexpected. This is likely an issue that needs to be fixed in Baseten code in pynode.

</details>

## Impact

High. User worklets or queries may be failing.

## Diagnosis

Look at pynode logs via grafana to debug.
- Pynode logs: https://grafana.baseten.co/d/liz0yRCZz/logs-loki-user?orgId=1
    - This dashboard requires a specifc customer namespace to be selected. To see all namespaces, use [this "explore" panel](https://grafana.baseten.co/goto/W81Q6Lwnk?orgId=1)
- Django logs: https://grafana.baseten.co/d/sadlil-loki-apps-dashboard/logs-loki-internal?orgId=1&var-app=baseten-django&var-container=baseten-django
- Celery logs: https://grafana.baseten.co/d/sadlil-loki-apps-dashboard/logs-loki-internal?orgId=1&var-app=celery-worker&var-container=celery-worker

## Mitigation

If the issue is correlated with a deploy then revert the deploy. If a revert is complicated or not possible (because of db migrations for example) identify  and fix the issue in code and deploy pynodes.
