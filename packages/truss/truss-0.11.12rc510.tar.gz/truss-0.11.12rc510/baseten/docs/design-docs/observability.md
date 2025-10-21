# Observability stack

## Overview
This document contains the infrastructure setup and monitoring details for our services. Below is a comprehensive guide on the various aspects of our monitoring, metrics collection, logging, health checks, and alerting systems.

## Metrics

### Storage and Collection
- **VictoriaMetrics**: We use VictoriaMetrics to store and serve metrics. It has a Prometheus-compatible API, so most Python services use a Prometheus client library to expose metrics. Golang services use the victoriametrics client library.
- **Non-Compatible Metrics**: Some metrics (inference time, end-to-end request time, and time in async queue) are collected using `vmhistograms`, which are not compatible with Prometheus.
  - For more information on `vmhistograms`, refer to [this post by VictoriaMetrics](https://valyala.medium.com/improving-histogram-usability-for-prometheus-and-grafana-bc7e5df0e350).

### Cloud Metrics
- We also have some metrics in CloudWatch (AWS) and the equivalent in GCP. These are gathered automatically by the cloud provider but are not used extensively.

## Health Checks
- We use **Route53 health checks** to monitor the state of a couple of websites:
  - `app.baseten.co`
  - `baseten.co`
  - `docs.baseten.co`

## Logs

### Collection
- **FluentBit**: Logs are gathered by FluentBit and pushed to Loki.
  - There is a FluentBit daemonset that creates a pod on each node in the clusters.

### Deployment
- **Loki**: There is one Loki deployment per Workload Plane.

## User Interface

### Grafana
- We have two Grafana instances to look at logs and metrics:
  - `grafana.baseten.co`: Mostly contains legacy control plane logs and metrics (e.g., Django, Celery, Pynodes, and some models).
  - `grafana.baseten.co`: Contains logs and metrics for all Workload Planes (WPs). You can change the data source to point to the Loki/VictoriaMetrics deployments from the WP you want to examine.

## Alerting

### AlertManager
- We use **AlertManager** for alerting.
  - Alerts are defined in the repository, and there is documentation about how to add new ones.
  - Some alerts are still defined in the legacy Terraform, but we are transitioning to the Terraform setup in `baseten-tf-modules`.

### Notifications
- Alerts are sent to `#alerts-production` or PagerDuty, depending on the severity:
  - Critical alerts result in a PagerDuty notification.
  - Non-critical alerts are sent to Slack.

### Sentry
- We also use **Sentry** for error tracking. Errors are forwarded to `#alerts-production-sentry`.

## Tracing

### OpenTelemetry
- We have some tracing integration using **OpenTelemetry** clients and SDKs to collect traces and store them in Honeycomb.
  - Sampling is done at the Kubernetes cluster level, so not all traces make it to Honeycomb. However, all error traces should be captured.

