# Django Celery Runbook

## Logs

[Prod](https://grafana.baseten.co/d/liz0yRCZz/loki-dashboard-quick-search?var-namespace=baseten&var-workload=baseten-django&var-search=&orgId=1)

## k8s spec

- [django-deployment](/helm/charts/baseten/templates/baseten-app/baseten-django-deployment.yaml)
- [celery-deployment](/helm/charts/baseten/templates/baseten-app/celery-deployment.yaml)

## Common Tasks

#### Deployment history with git sha
From baseten git root
```
poetry run python scripts/deploy_history.py
```

#### Manually deploy pynode service
1. ssh into django pod
tip: Add this to ~/.bash_profile for a simple command

```sh
ksshdj ()
{
    kssh $(kubectl get pods -n baseten -l app=baseten-django -o name | awk -F/ '{ print $2 }')
}
```

2. Run `poetry run python manage.py ensure_pynode_deployed`


#### Updating dynamic settings
We've just introduced dynamic settings for the django app, setting that are picked up at runtime and don't need a deploy. These settings are defined in a config map and can be updated as follows:

```sh
kubectl -n baseten edit cm baseten-django-dynamic-setting
```

Settings are under data, eg ratelimitEnabled here:

```yaml
data:
  ratelimitEnabled: "false"
```

The only safeguard we have in place is that if the key is found missing or malformed than we'll fall back to the default, which in this case is to apply rate limit. So be careful when making changes to this file. 
Deleting the configmap will stop django app from coming up and next helm upgrade will not be able to restore the file as it's only created at install, not upgrade. So, don't delete it.
