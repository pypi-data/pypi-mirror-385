# Changing Maximum Deployed Models Limit

Go into shell plus for the right environment

```sh
kshp ()
{
    kubectl exec -it -n baseten $(kubectl get pods -n baseten -l app=celery-worker -o name | awk -F/ '{ print $2 }' | head -n 1) -- poetry run python manage.py shell_plus
}

>>> org = Organization.objects.get(pk='[put org id here]')
>>> org.metadata.maximum_deployed_model_versions = 10 # or the value that you want
>>> org.metadata.save()
```
