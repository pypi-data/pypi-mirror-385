# Kube analytics export

This directory contains functionality to export specific kube metrics data from Prometheus (VictoriaMetrics) to Google BigQuery for cost and utilization analysis.

## How it works

- The `record_kube_metrics` celery task is run as a periodic task to export aggregated data every hour.
- From there, subtasks export the pod and node-level metrics independently:
  - We make several queries to the Prometheus API (see `fetch_pod_metrics` and `fetch_node_metrics`) to get different columns of data.
    - Note: while other queries Django makes to Prometheus are filtered by pod or namespace, these queries cover all relevant pods and nodes across all clusters. From testing, there don't appear to be any performance or scaling issues. In the future, we could shard queries by cluster name, namespace, etc. to improve performance.
  - Each query result is converted to a pandas DataFrame.
  - The DataFrames are then merged together for each pod or node
  - The merged results are ingested to separate tables in BigQuery (see `ingest_data_frame_to_bigquery`)
    - Note: the ingestion process is idempotent, so if the task gets duplicated, it will not result in duplicate data in BigQuery.

## Integration tests

The prometheus queries along with the data wrangling logic are covered by [metric integration tests](../../../docs/testing/metrics-integration-tests.md) defined under [test_analytics_metrics.py](../tests/queries/metrics_integration/test_analytics_metrics.py).

## Testing locally

Beyond the metric integration tests, you can test the queries against cloud cluster (e.g. dev, staging) data following the instructions [here](../../../docs/runbooks/model-metrics.md). Be sure to forward VictoriaMetrics in the control plane. You can then call `fetch_pod_metrics()` and `fetch_node_metrics()` from `shell_plus` and inspect the resulting DataFrames.

### Testing the BigQuery ingestion

Testing ingesting data into BigQuery should only be necessary to debug issues with the ingestion process.

**Prerequisite**: BigQuery access to the `baseten-data` project in GCP.

```sh
# Install the gcloud SDK and authenticate with your Google Cloud account.
brew install --cask google-cloud-sdk
gcloud init

# Set the project to the baseten-data project
gcloud config set project baseten-data

# Install application-default auth
gcloud auth application-default login
```

Then, create a new dataset in BigQuery for testing: (substitute `<yourname>` with your name)

```sh
bq mk --location=us-west1 <yourname>_test
```

In `backend/baseten/settings/base.py`, update the `BIGQUERY_DATASET` setting to `<yourname>_test`":

```py
BIGQUERY_ANALYTICS_DATASET_ID = "baseten-data.<yourname>_test"
```

You can then call `ingest_data_frame_to_bigquery()` from `shell_plus` to test the ingestion process.
