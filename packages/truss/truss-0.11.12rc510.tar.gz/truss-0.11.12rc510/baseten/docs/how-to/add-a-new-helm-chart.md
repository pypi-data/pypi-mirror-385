# How to add new helm chart for a service

## Create chart

Create the chart under `helm/charts/<service>`. 

There's no set best-practice currently (2025Q3). Reusing an existing one like `api-gateway` is fine. 

For reference, here's [the PR](https://github.com/basetenlabs/baseten/commit/3fc15ba4464e3c2f199dff0dbea10db3871c9d97#diff-f18b69384a86b4ecd7109fbb54de4e4a2d19b0a96e78314ada80d2b6f96c398b) for `api-gateway`s helm chart.

* `Chart.yaml`
  * Most charts manually keep a changelog in the chart
  * Most charts keep the appversion at `0.0.1`
* `values.yaml`
  * A lot of services use [norwoodj/helmdocs](https://github.com/norwoodj/helm-docs) to document values.
  * Comment your `values.yaml` using it's format is nice.
* `templates/*.yaml`
  * Create the usual set of yamls as needed, `deployment.yaml`, `service.yaml` etc.

While writing it, use `helm template` and `helm lint` to test. 

## Testing

You can apply the generated chart to eg. minikube or `development` cluster for further testing.

#### Lint

```shell
# Lint your chart
$ helm lint helm/charts/alyx-lb
engine.go:206: [INFO] Missing required value: ingress.host is required
engine.go:206: [INFO] Missing required value: ingress.host is required
==> Linting helm/charts/alyx-lb
[INFO] Chart.yaml: icon is recommended

1 chart(s) linted, 0 chart(s) failed
```

#### Template

```shell
# Run template
$ helm template alyx-lb1 helm/charts/alyx-lb --values some-sample-values.yaml --namespace my-test-ns > helmlrease.yaml
```

#### Apply

```shell
# Pick your cluster, this will vary by how you've decided to manage cluster
$ kubectl set context wp-gcp-us-central1-dev/minikube

# Create a test namespace
❯ kubectl create namespace my-test-ns
namespace/my-test-ns created

# Apply to cluster
$ kubectl apply -f helmlrease.yaml
configmap/alyx-lb1-config created
service/alyx-lb1 created
deployment.apps/alyx-lb1 created
ingress.networking.k8s.io/alyx-lb1-ingress created
servicemonitor.monitoring.coreos.com/alyx-lb1-service-monitor created

# Explore with k9s...

# Nuke it
$ kubectl delete namespace my-test-ns
namespace "my-test-ns" deleted
```

## Releasing

* Add to the [github action workflow](https://github.com/basetenlabs/baseten/blob/6a8878870e4df0b69db878635be9a8602fa4b74a/.github/workflows/helm-chart-pipeline.yaml#L61-L77). 
* [Deploy to development cluster](/docs/local-dev/Dev-deployment.md). In the [branch workflows](https://github.com/basetenlabs/baseten/actions?query=branch%3Adevelopment), the job named _"Helm Chart Pipeline"_ releases the chart. It looks like [this](https://github.com/basetenlabs/baseten/actions/runs/17305799264/job/49128305746#step:8:143)
* Released charts can be checked in [registry.basetensors.com](https://registry.infra.basetensors.com/harbor/projects/3/repositories)

## flux-cd deployment in development/staging

Refer to [flux-cd's README](https://github.com/basetenlabs/flux-cd/blob/main/README.md).
