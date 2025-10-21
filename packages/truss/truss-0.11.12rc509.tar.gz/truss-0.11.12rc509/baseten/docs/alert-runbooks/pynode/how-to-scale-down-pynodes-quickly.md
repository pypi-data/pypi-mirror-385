# How to scale down pynodes quickly

Some orgs have more activity than others. We try to reduce resources devoted to
dormant (inactive) orgs [(design)](/docs/design-docs/scale-to-zero.md). Orgs with no activity within `org_domancy_period` are
considered dormant.

`org_dormancy_period` is a dynamic setting, i.e. it can be modified without
needing a deploy. This can be used to not only tune this setting over time, but
also to reduce resource needs of the cluster if needed.

## How to reduce number of running pynodes by reducing `org_domancy_period`

There are essentially two steps:

1. Update baseten-django-dynamic-settings
2. Manually invoke `set_org_dormancy_task` celery task

First one updates the setting. Second one scales down pynodes based on this
setting immediately. If you skip the second step then the pynode scale down will
still take effect but at the start of next hour (when set_org_dormancy_task runs
via celery cronjob).

### Update `baseten-django-dynamic-settings`

```bash
k edit cm -n baseten baseten-django-dynamic-settings
```

Update or add the setting `orgDormancyPeriodSecs`. Default is `86400` i.e. one
day. Make sure that the period part in `orgWarmupRatelimitStr` is equal to or
smaller than org dormancy period. Othewise the org can go dormant even if
there's activity because the rate limit will not allow the warm up messages to
go through.

For example, to set it to 2 hr and warm up rate limit to twice per hour (some
information omitted).

```yaml
apiVersion: v1
data:
  orgDormancyPeriodSecs: "7200"
  orgWarmupRatelimitStr: "2/hour"
  ratelimitEnabled: "false"
kind: ConfigMap
metadata:
  name: baseten-django-dynamic-settings
  namespace: baseten
```

### Run `set_org_dormancy_task` manually

```bash
# Run shell plus
kubectl exec -it -n baseten $(kubectl get pods -n baseten -l app=celery-worker -o name | awk -F/ '{ print $2 }' | head -n 1) \
-- poetry run python manage.py shell_plus
```

```python
In [1]: from workflows.tasks import set_org_dormancy_task
In [2]: set_org_dormancy_task()
```
