# Helm and Helmfile

We use helm to manage a lot of our core k8s infra. Baseten essentially gets installed as a helm chart. Initially, we added almost everything to this one chart, including resource definitions for frameworks such as knative and kfserving. Over time we've realized that it would be much easier to manage disparate components as separate charts. Especially for external charts, most of which come as standalone charts. For maintainability and simplicity, it's much better to keep install them as they come, and only configure them for our usecase, rather than dump the resource definitions into the Baseten chart.

With multiple helm charts comes the issue of managing them. We often want to install third party charts into separate namespaces. Also, it's best to define secret values, such as AWS creds, once and reuse them for the various charts, rather than have to pass them to each one separately. It would also be great to keep the helm values in code rather than have to set them manually for each environment. Helmfile helps with all of these.

helmfile is essentially a helm chart generator. It converts the helmfile specification, typically defined in a file called helmfile.yaml, into a set of helm charts and deploys them. The cluster is not aware of helmfile at all, the cluster only sees helm.

Our helmfile is located at https://github.com/basetenlabs/baseten/blob/master/helm/helmfile/helmfile.yaml.

# helmfile configuration

## Repositories

A simple list of helm repositories that gets installed on the cluster, so that we don't have to remember to do it manually on every new cluster.

## Environments

Values and secrets can be defined at helmfile level, separately for each environment. We'll cover the details of secrets mechanism later but essentially the environment values and secrets are both available under `.Values` for use in configuring helm chart installations.

## Releases

These are the configured helm charts to install on the cluster. We specify the chart to install, the namespace the install it in and the values to override. The values can be specified as templates, where the per environment values and secrets can be used. These values override any values defined inside the helm chart and are essentially the way to configuring the helm chart.

# Deployments

Deployments boil down to running a command that looks like

```
helmfile -e [environment name] sync
```

helmfile generates helm charts for the specific environment and applies them to the cluster.

Most common change is the updating of the baseten image tag, which is applied as a helm value for the baseten chart. The ci job builds a new image, uploads it to the docker registry, stores the new image tag in an environment variable and runs the above command. Our helmfile setup picks up the image tag value from the environment variable to use for Baseten helm chart. When the new imageTag is thus applied it results in re-deployment of the components that use it, eg the django and celery components.

# Useful commands

```
helmfile -e [environment name] diff

# eg
helmfile -e production diff
```

`diff` command allows viewing the changes that will be applied without applying them.

```
helmfile -e [environment name] sync
```

`sync` command applies the new configuration.

```
helmfile -e [environment name] apply
```

`apply` is a shortcut for `diff + sync`

### Dev Usage

To apply changes in dev:

```
cd helm/helmfile
helmfile -e local sync
```

# Dev setup

./Dev-setup#helm-and-helmfile
