# Deploy to Development Environment

0. Post in #dev-environment to let the team know you'll be taking it over. 
1. Make sure you have a feature branch for your work
2. `git checkout development` to check out the development branch
3. `git pull` to pull in recent changes to the branch  
4. `git merge --no-ff -m "merge" <my-feature-branch-name>` to pull in your branch's changes
5. `git push origin development` to push to dev!
6. FluxCD will pick up the changes to dev, typically after a few minutes.
7. Visit https://app.dev.baseten.co to test your branch

Visit the GHA page, [Deploy Development action](https://github.com/basetenlabs/baseten/actions/workflows/deploy-app-n-infra-development.yml) to see how your deployment is doing.

You can also validate whether your changes were picked up by [comparing master...development](https://github.com/basetenlabs/baseten/compare/master...development).

You may verify whether your change has been picked up by checking the image tag of the pod, which has the format: `{environment}-{commit}-{timestamp}`. For example, for `baseten-django`:
```
kubectl -n baseten get deploy baseten-django -o jsonpath="{.spec.template.spec.containers[?(@.name=='baseten-django')].image}"
# will show something like baseten/baseten-app:development-fb805772-20240715224455
```
Here, `fb805772` is the **merge** commit sha that corresponds to the image.

## Wipe development branch
Sometimes the development branch gets to a state where it is hard to merge with or in a bad merged state. It may be easier to wipe the development branch and overriding from the master branch.
1. Force push from master and wipe development: `git push -f origin master:development`
2. After that you can then do the steps in prior section on merging your private branch changes over.

The are some deployment logic that are triggered by checks of current and previous HEAD to identify relevant changes. It is recommended that you push from master first before merging with a private branch.

## Manual patching
If you see an older container image on your component, you might have to apply a manual patch. Here is an example for baseten-wp-operator. Install `flux` locally if you don't already have it.

1. Log in to the relevant workload plane (say, dev-wp-us-west-2) on Kubernetes. Use [Rancher](https://rancher.infra.basetensors.com/) to get the relevant config file.
2. Go to the [relevant kustomization patch file](https://github.com/basetenlabs/flux-cd/blob/main/workload-plane/dev/baseten-wp-operator-patch.yaml).
3. Paste the contents of the file to a local copy, say `wp-operator-patch.yaml`.
4. Apply the patch:
```sh
# Verify running older image
kubectl -n baseten get deployment baseten-wp-operator -o jsonpath="{.spec.template.spec.containers[].image}"
# could show something like: baseten/baseten-wp-operator:development-2844fdcf-20250701170357

# Apply patch
kubectl -n baseten apply -f wp-operator-patch.yaml
# helmrelease.helm.toolkit.fluxcd.io/baseten-wp-operator configured
flux reconcile helmrelease baseten-wp-operator -n baseten
# ► annotating HelmRelease baseten-wp-operator in baseten namespace
# ✔ HelmRelease annotated
# ◎ waiting for HelmRelease reconciliation
# ✔ applied revision 0.0.0-20250606201912-0.1.24-6e316701

# Verify new image
kubectl -n baseten get deployment baseten-wp-operator -o jsonpath="{.spec.template.spec.containers[].image}"
# could show something like:
baseten/baseten-wp-operator:development-90ff4b15-20250702200106
```

## Troubleshooting
The following commands are useful to get the state of continuous deployment:
```
flux get all -n baseten
flux get kustomizations -A
```
Note any columns with `READY` set to `False`. Also note any unmet dependencies. Talk to @sre team on Slack if you see anything suspicious.
