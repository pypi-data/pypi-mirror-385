# Unified model logs

## Motivation

User-facing model logs come from several sources:

- The tekton job that builds the model image
- The running model's container
- The kube-pod-lifecycle-watcher that listens for model termination
- Django for deployment and other lifecycle logs
- GPU User build job pods

Prior to unified model logs, each of these logs were written into loki separately, in differing formats, and with lots of non-user-facing metadata attached as labels. This put the onus on Django to query each of these source separately across different streams and stitch them together into a single log stream for the user. Furthermore, the unnecessary labels goes against Loki's [best practices](https://grafana.com/docs/loki/latest/best-practices/) and significantly hurts read performance.

The idea behind unified model logs is to write a single pre-processed, pre-filtered log stream (meaning a single set of unique labels) for each model version so that querying logs from the Baseten application is as simple as querying from this single stream. This reduces the number of synchronous, serial Loki requests from 4 to 1 while also reducing the number of streams Loki has to query from S3 to find all matching logs.

## Log format

- Labels - All logs have exactly the following labels, no more, no less
  - `model_version_id`
  - `namespace`
  - `unified_model_logs: '1'`: Used to distinguish these logs with other logs with a `model_version_id` label
  - `job`: Indicates the log collector service. This should always be set `fluent-bit` and therefore have no effect on cardinality.
- JSON message payload
  - `levelname: 'DEBUG' | 'INFO' | 'WARNING' | 'ERROR'`\*
  - `replica: string!`
  - `source: 'build' | 'deploy' | 'model_container' | 'kube-pod-lifecycle-watcher' | ...`
    - Not currently exposed to the user, but may be useful for debugging or for filtering by stage in the future
  - `message: string!`
  - `exc_info: string` - stacktrace information for errors

For example, a log line might have labels:

```json
{
  "namespace": "org-50a9bc6b456e47aa88e0d81e622ea315",
  "unified_model_logs": "1",
  "model_version_id": "x5qe2qo",
  "job": "fluent-bit"
}
```

and a message payload:

```json
{"levelname":"INFO","message":"172.17.0.6:0 - \\"POST /v1/models/model%3Apredict_binary HTTP/1.1\\" 200","replica":"q7rg5"}
```

Metadata like level that applies only to a subset of logs should be attached as JSON fields in the message payload, not as labels. Note that this is a bit of a performance trade-off since it means Loki can't index these fields, but in following with Loki [best practices](https://grafana.com/docs/loki/latest/best-practices/#use-dynamic-labels-sparingly), this type of filtering should be fairly fast and is worth the performance gains to log loading more generally.

We should exercise caution about adding new labels over time. One situation where this might be necessary in the future is if we want to display logs across all versions of a model. In this case, we would want to add a `model_id` label, but because there's only one `model_id` for a given `model_version_id`, this would not affect the total number of streams and thus should have minimal impact on performance.

## Implementation

Logs are ingested from two sources:

- Django logs are written directly by Django into Loki. See log_model_deploy in `backend/oracles/model_deployer/deploy_model.py`
- Fluentbit is used to scrape logs from pods for each of the other sources. The fluentbit config is duplicated across two locations:
  - For in-cluster deployments:
    - `terraform/modules/fluentbit/fluentbit-values.tf`
    - `terraform/modules/fluentbit/fluentbit.lua`
  - For minikube deployments:
    - `helm/helmfile/fluent-bit.yaml.gotmpl`
    - `k8s/local/configmap_fluentbit-lua.yaml`
