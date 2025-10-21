# mcm-cp

![Version: 0.8.36](https://img.shields.io/badge/Version-0.8.36-informational?style=flat-square) ![Type: application](https://img.shields.io/badge/Type-application-informational?style=flat-square) ![AppVersion: 0.0.6](https://img.shields.io/badge/AppVersion-0.0.6-informational?style=flat-square)

Chart to create the Baseten MCM Service and subcomponents for the Control Plane

## Values

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| atc.aws.keyId | string | `nil` |  |
| atc.aws.region | string | `"us-west-2"` |  |
| atc.aws.secretAccessKey | string | `nil` |  |
| atc.consumerPoolConcurrency | int | `3` |  |
| atc.consumerPoolJitterDurationFactor | float | `1.5` |  |
| atc.consumerPoolJitterDurationMilliseconds | int | `1000` |  |
| atc.deploymentName | string | `"baseten-mcm-atc"` |  |
| atc.django.baseUrl | string | `"http://baseten-django.baseten:8000"` |  |
| atc.django.secretKey | string | `"atc-django-api-key"` |  |
| atc.django.secretName | string | `"atc-django-api-key"` |  |
| atc.django.secretsDir | string | `"/etc/django"` |  |
| atc.enabled | bool | `true` |  |
| atc.grpcPort | int | `51002` |  |
| atc.mode | string | `"cluster"` |  |
| atc.modelLoadingTimeoutHours | int | `8` |  |
| atc.operatorReconcileIntervalSeconds | int | `60` |  |
| atc.operatorReconcileTimeoutSeconds | int | `60` |  |
| atc.operatorTLSEnabled | bool | `true` |  |
| atc.periodicMetricsIntervalSeconds | int | `30` |  |
| atc.periodicMetricsTimeoutSeconds | int | `30` |  |
| atc.replicas | int | `1` |  |
| atc.resources.cpu | string | `"0.5"` |  |
| atc.resources.memory | string | `"100Mi"` |  |
| atc.terminationGracePeriodSeconds | int | `30` |  |
| atc.tls.enabled | bool | `true` |  |
| atc.tls.secretName | string | `"atc-tls-client"` |  |
| atc.tls.secretsDir | string | `"/etc/atc/secrets"` |  |
| autoscaler.deploymentName | string | `"baseten-mcm-autoscaler"` |  |
| autoscaler.enabled | bool | `true` |  |
| autoscaler.grpcPort | int | `8080` |  |
| autoscaler.metricsPort | int | `9090` |  |
| autoscaler.replicas | int | `1` |  |
| autoscaler.resources.cpu | string | `"0.5"` |  |
| autoscaler.resources.memory | string | `"100Mi"` |  |
| autoscaler.serviceAccountName | string | `"baseten-mcm-autoscaler"` |  |
| autoscaler.terminationGracePeriodSeconds | int | `30` |  |
| database.secretName | string | `"dsn"` |  |
| database.secretsDir | string | `"/etc/pguser"` |  |
| defaults.metricsPort | int | `9090` | Default metrics port |
| gns.deploymentName | string | `"baseten-mcm-gns"` |  |
| gns.deploymentStrategy | string | `"Recreate"` | k8s deployment strategy see [Docs Recreate](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/#recreate-deployment) |
| gns.deprecatedSlots[0] | string | `"mcm_monoslot"` |  |
| gns.enabled | bool | `true` |  |
| gns.grpcPort | int | `51005` | gRPC port |
| gns.metricsPort | string | `""` | Optional metricsPort for the gns service, defaults to defaults.metricsPort |
| gns.replicas | int | `1` |  |
| gns.resources.cpu | string | `"0.5"` |  |
| gns.resources.memory | string | `"100Mi"` |  |
| gns.slotConsumers[0].name | string | `"mcm_pods_slot"` |  |
| gns.slotConsumers[0].podName | string | `"gns-pods-slot"` |  |
| gns.slotConsumers[0].tables[0] | string | `"pods"` |  |
| gns.slotConsumers[10].name | string | `"mcm_org_resource_cap_slot"` |  |
| gns.slotConsumers[10].podName | string | `"gns-org-resource-cap-slot"` |  |
| gns.slotConsumers[10].tables[0] | string | `"org_resource_caps"` |  |
| gns.slotConsumers[1].name | string | `"mcm_nodes_slot"` |  |
| gns.slotConsumers[1].podName | string | `"gns-nodes-slot"` |  |
| gns.slotConsumers[1].tables[0] | string | `"nodes"` |  |
| gns.slotConsumers[2].name | string | `"mcm_local_deployments_slot"` |  |
| gns.slotConsumers[2].podName | string | `"gns-local-deployments-slot"` |  |
| gns.slotConsumers[2].tables[0] | string | `"local_deployments"` |  |
| gns.slotConsumers[3].name | string | `"mcm_local_model_scalers_slot"` |  |
| gns.slotConsumers[3].podName | string | `"gns-local-model-scalers-slot"` |  |
| gns.slotConsumers[3].tables[0] | string | `"local_model_scalers"` |  |
| gns.slotConsumers[4].name | string | `"mcm_deployment_scales_slot"` |  |
| gns.slotConsumers[4].podName | string | `"gns-deployment-scales-slot"` |  |
| gns.slotConsumers[4].tables[0] | string | `"deployment_scales"` |  |
| gns.slotConsumers[5].name | string | `"mcm_deployment_schedules_slot"` |  |
| gns.slotConsumers[5].podName | string | `"gns-deployment-schedules-slot"` |  |
| gns.slotConsumers[5].tables[0] | string | `"deployment_schedules"` |  |
| gns.slotConsumers[6].name | string | `"mcm_rule_sets_slot"` |  |
| gns.slotConsumers[6].podName | string | `"gns-rule-sets-slot"` |  |
| gns.slotConsumers[6].tables[0] | string | `"rule_sets"` |  |
| gns.slotConsumers[7].name | string | `"mcm_deployments_slot"` |  |
| gns.slotConsumers[7].podName | string | `"gns-deployments-slot"` |  |
| gns.slotConsumers[7].tables[0] | string | `"deployments"` |  |
| gns.slotConsumers[8].name | string | `"mcm_route_tables_slot"` |  |
| gns.slotConsumers[8].podName | string | `"gns-route-tables-slot"` |  |
| gns.slotConsumers[8].tables[0] | string | `"route_tables"` |  |
| gns.slotConsumers[9].name | string | `"mcm_ksvc_service_slot"` |  |
| gns.slotConsumers[9].podName | string | `"gns-ksvc-service-slot"` |  |
| gns.slotConsumers[9].tables[0] | string | `"ksvc_services"` |  |
| gns.terminationGracePeriodSeconds | int | `60` |  |
| gsm.deploymentName | string | `"baseten-mcm-gsm"` |  |
| gsm.enabled | bool | `true` |  |
| gsm.replicas | int | `1` |  |
| gsm.resources.cpu | string | `"0.5"` |  |
| gsm.resources.memory | string | `"100Mi"` |  |
| gsm.terminationGracePeriodSeconds | int | `30` |  |
| imagePullSecrets | string | `"dockerregistrykey"` |  |
| imageTag | string | `nil` |  |
| kafka.brokers.secretName | string | `"kafka-brokers"` |  |
| kafka.brokers.secretsDir | string | `"/etc/kafka-brokers"` |  |
| kafka.cpevents.topicReplicationFactor | int | `3` |  |
| kafka.eventhub.topicReplicationFactor | int | `3` |  |
| kafka.mcsevents.topicReplicationFactor | int | `3` |  |
| kafka.routetableevents.topicReplicationFactor | int | `3` |  |
| kafka.tls.caSecretName | string | `"baseten-root-ca"` |  |
| kafka.tls.enabled | bool | `true` |  |
| kafka.tls.secretName | string | `"redpanda-tls-cert"` |  |
| kafka.tls.secretsDir | string | `"/etc/kafka/secrets"` |  |
| logLevel | string | `"debug"` |  |
| migration.baseline | string | `""` |  |
| migration.enabled | bool | `true` |  |
| migration.fromBaseline | bool | `false` |  |
| namespace | string | `"baseten"` |  |
| redis.secretName | string | `"redis-url"` |  |
| redis.secretsDir | string | `"/etc/redis"` |  |
| redisSentinel.secretName | string | `"redis-sentinel"` |  |
| redisSentinel.secretsDir | string | `"/etc/redis-sentinel"` |  |
| scheduler.deploymentName | string | `"baseten-mcm-scheduler"` |  |
| scheduler.enabled | bool | `true` |  |
| scheduler.grpcPort | int | `8080` |  |
| scheduler.metricsPort | int | `9090` |  |
| scheduler.replicas | int | `1` |  |
| scheduler.resources.cpu | string | `"0.5"` |  |
| scheduler.resources.memory | string | `"100Mi"` |  |
| scheduler.serviceAccountName | string | `"baseten-mcm-scheduler"` |  |
| scheduler.terminationGracePeriodSeconds | int | `30` |  |
| serviceMonitorsEnabled | bool | `true` |  |
| workloadPlanes.secretName | string | `"workload-planes"` |  |
| workloadPlanes.secretsDir | string | `"/etc/workload-planes"` |  |
| workloadPlanesDir | string | `"/etc/workload-planes"` |  |
| workloadPlanesSecretName | string | `"workload-planes"` |  |

----------------------------------------------
Autogenerated from chart metadata using [helm-docs v1.14.2](https://github.com/norwoodj/helm-docs/releases/v1.14.2)
