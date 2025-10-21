# How to change an org's pynode specs

At times we need to add some oomph to an org's pynode (e.g. more cpu/mem, more replicasets, etc). To do so you have to add an entry for the given org [here](https://app.baseten.co/billip/workflows/pynodedeploymentspec/).

Then you have to flip the pynode:

1. ssh into a celery pod
tip: Add this to ~/.bash_profile for a simple command

```sh
ksshdj ()
{
    kssh $(kubectl get pods -n baseten -l app=celery-worker -o name | awk -F/ '{ print $2 }')
}
```

2. Run `poetry run python manage.py ensure_pynode_deployed --org-name THE_NAME_OF_THE_ORG`. Find the `name` of the org on the org's billip page.
