# Model Redeployment (IMPORTANT: Possibly out-of-date)

As of this writing (July 20201) this is a fairly involved process

## Job Template

This is located in `k8s/jobs/deploy-model-job.yaml` - you need to alter this for each perspective environment and deploy.

An easy way to do this is running a dry run of a `helm` command from the `helm/` directory and copying attributes from there. A la:
```
helm upgrade baseten ./baseten -n baseten --reuse-values --dry-run > ~/Documents/helm_staging.yaml # assuming you're pointing at stage!
```

## Managing Job

After you've filled out the job template, with `kubectl` pointing at the correct cluster run the command:
```
kubectl apply -f deploy-model-job.yaml -n baseten
```

It will attempt 3 times to complete the model flips; if that is not enough for some reason delete the job and try again
```
kubectl delete job -n baseten baseten-ensure-models-deployed
kubectl apply -f deploy-model-job.yaml -n baseten
```
