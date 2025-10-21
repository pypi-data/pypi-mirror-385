# baseten-vmrule

This chart contains the Victoria Metrics alerting rules for Baseten clusters.

Rules should be grouped by component or subsystem. Each rule manifest can be enabled or disabled depending on the cluster type and environment.

## Versions

### 0.1.14

WorkloadPlaneHealthNotOk: Increase time window to 5m and use max instead of sum.

### 0.1.x

Version `0.1.0` copies all built-in rules from `victoria-metrics-k8s-stack` chart.

In the `baseten-deployment` repo, we will disable all vmrules when install VictoriaMetrics and kustomize the rules with different threshold and/or severity in the `flux-cd` repo.

`ruleSets` and alerts for each `rule` need to be disabled explicitly by setting `disabled: true`

## 0.0.x

Disabled few rules in `victoria-metrics-k8s-stack` and moved them here, added few Baseten specific rules (GPU resources etc)

## ChangeLog
- 0.0.0 -  2025-08-29 18:30:00 -0400 - Add snapshotter alert
- 0.1.56 - 2025-08-25 18:30:00 -0400 - Update BeefeaterRedisConnectionLimitReached expr to filter for just Beefeater redis
- 0.1.55 - 2025-08-12 17:30:00 -0400 - Restrict GPUTempTooHigh alert to h100s only
- 0.1.54 - 2025-08-12 00:30:00 -0400 - see baseten PR #12829
- 0.1.53 - 2025-08-05 12:00:00 -0400 - Update GPUTempTooHigh alert to all and alert on call
- 0.1.52 - 2025-07-31 13:00:00 -0400 - Fix NodeMissingAllocatableGpus query to include namespace
- 0.1.51 - 2025-07-28 10:00:00 -0400 - Fix DeleteSlowReplica query to include namespace
- 0.1.50 - 2025-07-24 11:29:00 -0400 - Fix GPUTempTooHigh alert expression
- 0.1.49 - 2025-07-23 09:54:24 -0400 - Fix NodeMissingAllocatableGpus alert and add a critical version
- 0.1.48 - 2025-07-18 19:00:00 -0400 - Add alert for GPUTempTooHigh
- 0.1.47 - 2025-07-18 14:45:00 -0400 - DeleteSlowReplica - enable Robusta action to delete
- 0.1.46 - 2025-07-16 17:43:00 -0400 - Add CustomerModels alert group for slow replicas
- 0.1.45 - 2025-07-15 13:00:00 -0700 - Add alert for node missing allocatable GPUs
- 0.1.44 - 2025-07-09 12:56:48 -0400 - Add robusta action for alert BasetenFSFillingUpSoon
- 0.1.43 - 2025-07-07 20:16:00 -0400 - Add sum by to limit model-api alert labels, fix alert expr
- 0.1.42 - 2025-06-23 14:29:00 -0400 - Add alert for BasetenKubeProxyUnableToSyncIptablesRules
- 0.1.41 - 2025-06-17 11:19:07 -0700 - Reduce false alarms for MinIO nodes offline alert.
- 0.1.40 - 2025-06-11 00:19:01 -0400 - Decrease sensitivity of some dynamo alerts.
- 0.1.37 - 2025-05-28 11:00:00 PST - Remove $_interval from expr 
- 0.1.36 - 2025-05-23 11:00:00 PST - Change BasetenKubeStorageObjectsCritical to use max instead of sum.
- 0.1.32 - 2025-05-05 00:00:00 PST - Disable OracleVersionNotScalingDown alert.
- 0.1.30 - 2025-04-15 00:00:00 PST - Fix: Remove JuiceFS PVC alerts from general, add to minio group by ns
- 0.1.29 - 2025-04-15 00:00:00 PST - Remove JuiceFS PVC alerts from general, add to minio group by ns
- 0.1.28 - 2025-04-02 00:00:00 PST - Add Redis AOF write failed alert
- 0.1.27 - 2025-04-01 00:00:00 PST - Add GPU device error alert
- 0.1.25 - 2025-03-16 00:00:00 PST - Update redpanda resource alert
- 0.1.20 - 2025-01-15 00:00:00 PST - Change redpand related alert rules
- 0.1.19 - 2024-11-13 00:00:00 PST -
- 0.1.17 - 2024-10-07 00:00:00 PST - Improve BasetenKubeStorageObjects alerts.
- 0.1.16 - 2024-09-25 00:00:00 PST - Increase threshold for StorageObjects alert. Exclude events resource.
- 0.1.15 - 2024-09-23 00:00:00 PST - Add new baseten-kube-resources vmrules
- 0.1.11 - 2024-08-14 08:11:00 PST - Change BasetenBeefeaterHigh4xx5xxErrorRate to warning
- 0.1.10 - 2024-08-05 09:00:13 PST - Fix order-of-operations error in Django billing smoke tests
- 0.1.9 - 2024-08-05 09:00:13 PST - Add Django billing smoke tests
- 0.1.8 - 2024-07-31 08:30:00 PST - Add async VMRule for high 5xx error rate
- 0.1.7 - 2024-07-26 06:25:00 PST - Update alertmanager namespace, add k8s API error alerts, add FluxCD alerts
- 0.1.6 - 2024-07-26 06:25:00 PST - Update bridge alerting rules
- 0.1.5 - 2024-07-23 12:37:00 PST - Fix default values for Kubernetes app rules
- 0.1.4 - 2024-07-22 15:27:00 PST - Add Minio VMRule for storage
- 0.1.3 - 2024-07-16 15:29:00 PST - Make async VMRule thresholds configurable
- 0.1.2 - 2024-07-16 13:42:00 PST - Add async VMRule for high pop latency
- 0.1.1 - 2024-07-16 13:00:00 PST - Bump chart version to trigger prod deploy
