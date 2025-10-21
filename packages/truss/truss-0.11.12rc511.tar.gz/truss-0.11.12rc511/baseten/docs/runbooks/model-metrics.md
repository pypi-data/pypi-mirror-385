# Model metrics 📈

_(and how to debug them)_

We interface with Victoria Metrics to query for model metrics and display these results to users in the Metrics tab. We break these metrics down per model version for users.

You can see the exact queries we use to query Victoria Metrics for the charts in these two files:

- [range_model_metrics.py](../../backend/oracles/schema/metrics/queries/range_model_metrics.py)
- [instant_model_metrics.py](../../backend/oracles/schema/metrics/queries/instant_model_metrics.py)

The general API to communicate with Victoria Metrics via django lives here: `backend/oracles/monitoring/`.

> Note: We switched away from Prometheus to instead use Victoria Metrics (VM) for our metrics storage. However, VM is prometheus-compatible and more or less uses the prometheus API, so you may see references to Prometheus in the codebase when in fact the queries are powered by VM.

## Metric forwarding

Most model metrics originate in a workload plane, from either the model pod, beefeater, or a metric exporter like kube-state-metrics. Select metrics, including the model metrics, are then forwarded to the centralized control plane via a dedicated vmagent. So before adding or modifying metric queries, make sure the metrics you're looking for are being forwarded to the control plane. If they're not, you need to first edit the configs here:

- https://github.com/basetenlabs/baseten-deployment/blob/main/multi-cluster/workload-plane-gcp/k8s-modules/shared/local-vmagent-remotewrite-config.tf
- https://github.com/basetenlabs/baseten-deployment/blob/main/multi-cluster/workload-plane-aws/k8s-modules/shared/local-vmagent-remotewrite-config.tf

## Debugging

_I want to play around with the metrics from a model version in staging or production locally, how do I do that?_

You'll need to have access to staging or production clusters locally (or in codespaces) in order to view metrics locally.

### Connecting to Control Plane
It is likely that the metrics you want to play around with are already being exported to the Control Plane, in which case you should connect to the Control Plane cluster via Rancher and follow the instructions below to port-forward from there. Otherwise if your metrics aren't available you may need to connect to the workload plane clusters directly via Rancher. (Note: this means if you want those metrics in the CP you'll need to add logic to forward those metrics from the WP to the CP)

**Note:** Should just use Rancher to connect to the individual clusters if possible, rather than the below.

### Connecting to an AWS cluster

Follow the instructions to set up the AWS CLI and `aws-vault` [here](../local-dev/AWS-&-Terraform-Setup.md), through the "Connecting to the EKS cluster" section. Make sure to use `--backend=file` for the codespace environment.

### Connecting to a GCP cluster

Follow the instructions to set up the GCP CLI and exec into a cluster [here](/docs/how-to/connect-to-gcp-clusters.md), you'll likely need to use the [Debian/Ubuntu instructions](https://cloud.google.com/sdk/docs/install#deb) for the codespace environment.

Then, run this command to port-forward Victoria Metrics:

```sh
kubectl port-forward svc/vmselect-victoria-metrics-k8s-stack -n monitoring 8481
```

### Then hardcode a couple values in the codebase

In `get_query_spec` inside [`base_metrics_query.py`](../../backend/oracles/schema/metrics/queries/base_metrics_query.py), hardcode the values for `namespace` and `model_version_id` to the values for a model version in production.

Check the queries you're testing in [`range_model_metrics.py`](../../backend/oracles/schema/metrics/queries/range_model_metrics.py) or [`instant_model_metrics.py`](../../backend/oracles/schema/metrics/queries/instant_model_metrics.py) to if there are additional values you need to hardcode (ex: `model_id`).

Now you'll just need to deploy a custom model locally to see the metrics you've exported from staging or production.

_FYI the model you deploy doesn't need to be deployed sucessfully! We just need access to a model page with a Health tab in the UI to be able to see the metrics we just exported._

To see GPU metrics (even if you don't have a GPU model deployed locally), open [Metrics.tsx](frontend/pages/Model/Metrics/Metrics.tsx) and comment out the check for `!!version.currentDeployment?.gpuCount` so that `<GpuMemoryTabs />` renders unconditionally.

Enjoy your metrics :) 🔮

## Automated testing

We have a limited set of [metrics integration tests](/docs/testing/metrics-integration-tests.md) we use to validate our model metrics. Please see the doc for more details.
