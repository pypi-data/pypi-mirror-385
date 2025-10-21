# Alyx Load Balancer

HTTP reverse proxy load balancer written in Go that supports both traditional primary-secondary failover and advanced multi-cluster load balancing with consistent hashing, TPM-based rebalancing, and user affinity for Dynamo based prediction workloads.

## Features

### Multi-Cluster Mode (Cursor mode)
- **Consistent Assignment**: Users consistently route to the same cluster for KV cache affinity
- **TPM-Based Rebalancing**: Load balancing based on Tokens Per Minute metrics
- **Dynamic Capacity**: Cluster capacity fetched from clients
- **Health-Aware Routing**: Automatic failover when clusters become unhealthy
- **User ID Header Support**: Configurable header for user identification
- **Redis Coordination**: Optional Redis Sentinel support for multi-instance coordination
- **Dynamic Configuration**: Add/remove clusters without restart

### Traditional Primary-Secondary Mode (Xyla mode)
- **Active-passive failover** between two backends
- **Periodic health checks** with configurable interval and threshold
- **Force failover** to secondary (evacuate primary)

### Core Features
- **Connection reuse** via shared HTTP transport
- **Safe request retry handling** (supports HTTP/2 GOAWAY via GetBody)
- **Prometheus metrics** for monitoring and observability
- **Dynamic configuration reloading** without restart

## Configuration

### Multi-Cluster Mode (Cursor mode)

For AI prediction workloads requiring KV cache affinity and intelligent load balancing:

```yaml
#
# Enable multi-cluster mode
#
multiClusterMode: 
  enabled: true
  # User ID header for consistent routing
  userIDHeader: "user-id"
  # TPM-based rebalancing settings
  tpmUpdateIntervalSeconds: 30
  # Cluster configurations for multiClusterMode
  clusters:
    - name: "cluster1"
      endpoint: "https://cluster1.example.com"
      healthCheck: "https://cluster1.example.com/health"
      hostHeader: "cluster1.example.com"

    - name: "cluster2"
      endpoint: "https://cluster2.example.com"
      healthCheck: "https://cluster2.example.com/health"
      hostHeader: "cluster2.example.com"

    - name: "cluster3"
      endpoint: "https://cluster3.example.com"
      healthCheck: "https://cluster3.example.com/health"
      hostHeader: "cluster3.example.com"

  # Balance algorithm knobs
  balanceAlgorithm:
    overloadedCapacityRatio: 0.95

  # Redis configuration for multi-cluster coordination
  redis:
    enabled: true
    sentinelAddresses: 
      - "redis-sentinel-1:26379"
      - "redis-sentinel-2:26379"
      - "redis-sentinel-3:26379"
    masterName: "mymaster"
    db: 0

# Health check settings
healthCheckIntervalSeconds: 5
healthCheckFailThreshold: 3

# Server addresses
listenAddress: ":8080"
metricsListenAddress: ":9090"

#
# Primary/secondary still required for backwards compatibility
#
primary:
  endpoint: "https://primary.example.com"
  healthCheck: "https://primary.example.com/health"
  hostHeader: "primary.example.com"

secondary:
  endpoint: "https://secondary.example.com"
  healthCheck: "https://secondary.example.com/health"
  hostHeader: "secondary.example.com"

evacuatePrimary: false
```

### Traditional Primary-Secondary Mode

For simple active-passive failover scenarios:

```yaml
# Disable multi-cluster mode (default)
multiClusterMode: 
  enabled: false

primary:
  endpoint: "https://gcp-us-central1-qlq.api.baseten.co"
  healthCheck: "https://gcp-us-central1-qlq.api.baseten.co/health/deep"
  hostHeader: "model-zq8mmvyw.api.baseten.co"

secondary:
  endpoint: "https://gcp-us-east4-juw.api.baseten.co"
  healthCheck: "https://gcp-us-east4-juw.api.baseten.co/health/deep"
  hostHeader: "model-e3moo29q.api.baseten.co"

healthCheckIntervalSeconds: 5
healthCheckFailThreshold: 12  # 12 * 5 seconds = 60 seconds
listenAddress: ":8080"
evacuatePrimary: false  # Set to true to force traffic to secondary if healthy
```

### Field Descriptions

#### Multi-Cluster Fields

| Field                                                            | Type     | Description                                                                       |
|------------------------------------------------------------------|----------|-----------------------------------------------------------------------------------|
| `multiClusterMode.enabled`                                       | bool     | Enable multi-cluster load balancing (default: false)                              |
| `multiClusterMode.userIDHeader`                                  | string   | Header name for user ID extraction (default: "user-id")                           |
| `multiClusterMode.tpmUpdateIntervalSeconds`                      | int      | Interval for TPM data fetching (in seconds, default: 30)                          |
| `multiClusterMode.balanceAlgorithm.overloadedCapacityRatio`      | float    | Pick another cluster if over this capacity threshold, see below (default: 0.95)   |
| `multiClusterMode.balanceAlgorithm.clusterWeightSmoothingFactor` | float    | Smoothening for `leastloaded` algorithm, see [here](#picking-an-availble-cluster) |
| `multiClusterMode.clusters[].name`                               | string   | Unique name for the cluster                                                       |
| `multiClusterMode.clusters[].endpoint`                           | string   | Main endpoint URL for the cluster                                                 |
| `multiClusterMode.clusters[].healthCheck`                        | string   | Health check endpoint for the cluster                                             |
| `multiClusterMode.clusters[].hostHeader`                         | string   | Host header to set for cluster requests                                           |
| `multiClusterMode.redis.enabled`                                 | bool     | Enable Redis for multi-cluster coordination (default: false)                      |
| `multiClusterMode.redis.sentinelAddresses`                       | []string | Redis Sentinel addresses for high availability                                    |
| `multiClusterMode.redis.masterName`                              | string   | Redis master name for Sentinel configuration                                      |
| `multiClusterMode.redis.db`                                      | int      | Redis database number (default: 0)                                                |
| `multiClusterMode.redis.userClusterMappingTTLMinutes`            | int      | TTL for cluster assignment in minutes (default: 15)                               |

##### Multi-Cluster Balancer Algorithm fields

`overloadedCapacityRatio`

If a model's cluster assignment is currently over this capacity threshold, we'll attempt to find a new one.

In order to reduce the impact of consumption differences at very low numbers, we add a smoothing factor relative
to the cluster's capacity. Imagine A and B both with 2000 capacity:

#### Traditional Fields (primary/secondary failover mode)

| Field                         | Type   | Description                                         |
|-------------------------------|--------|-----------------------------------------------------|
| `primary.endpoint`            | string | URL of the primary backend                          |
| `primary.healthCheck`         | string | Health check URL for the primary backend            |
| `primary.hostHeader`          | string | Host header to set for primary backend              |
| `secondary.*`                 |        | Same fields as `primary` for the secondary backend  |
| `evacuatePrimary`             | bool   | Force traffic to secondary backend if healthy       |

#### Common Fields

| Field                         | Type   | Description                                         |
|-------------------------------|--------|-----------------------------------------------------|
| `healthCheckIntervalSeconds`  | int    | Interval between health checks (in seconds)         |
| `healthCheckFailThreshold`    | int    | Number of failures before switching to secondary    |
| `metricsListenAddress`        | string | Address for Prometheus metrics (default: ":9090")   |
| `listenAddress`               | string | Address to bind the proxy server (default `:8080`)  |
| `logLevel`                    | string | Zerolog log level (default: "info")                 |


## Dynamic Configuration Reloading

alyx-lb now supports dynamic configuration reloading using [Viper](https://github.com/spf13/viper). When the configuration file changes, the load balancer will automatically reload the configuration without requiring a restart. The primary usecase is to allow toggling `evacuatePrimary` dynamically.

### Updating Configuration

Alyx Load Balancer should work with kubernetes ConfigMaps for dynamic configuration management.

To update the configuration at runtime, pause flux before and edit the config.

```shell
# Suspend flux
flux suspend kustomization alyx-lb

# Edit the ConfigMap to toggle evacuatePrimary
kubectl edit configmap alyx-lb-config --namespace=beefeater

# Eventually resume flux, *it'll overwrite the configmap again*
flux resume kustomization alyx-lb
```


## Running

### Production Deployment

```bash
go build -o alyx-lb
./alyx-lb config.yaml
```

The server will start on the configured `listenAddress` and begin proxying requests and performing health checks.

## Architecture

__NOTE: the architecture has undergone a lot of changes leading up to 2025/09/22, and more may come. Check source code for ground truth.__

### Multi-Cluster Mode Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│  Client Request │    │   Load Balancer  │    │   Clusters      │
│   + user-id     │───▶│   (:8080)        │───▶│                 │
│   + model       │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │      Redis       │
                       └──────────────────┘
                                │
                                ▼
                  ┌────────────────────────┐
                  │                        │    ┌──────────────────┐
                  │   Deep Health Manager  │͔◁──▶│ Cluster Health   │┐
                  │                        │    └──────────────────┘|┐ 
                  └────────────────────────┘     └──────────────────┘|
                                                  └──────────────────┘
                        
                   
```

### Key Components

1. **Client Request**: Arrives with user-id (optiona) and model (required).
2. **Load Balancer**: Checks redis for existing cluster assignment, calls Health Manager as necessary.
3. **Redis**: Routes users to consistent clusters for KV cache affinity. 
4. **Deep Health Manager**: On redis miss, pulls health information from clusters' deepth health endpoints.
5. **Cluster health**: Deep health endpoints in clusters, provide model names, health, consumption and capacity. Regularly polled by deep health manager.

### Routing algorithm outlined

__NOTE: the algorithm has undergone a lot of changes leading up to 2025/09/22, and more may come. Check source code for ground truth.__

#### Request Flow

1. `ExtractMetadataFromRequest`: look up user-id and model name in request.
2. If no user id route to _an available cluster_ (see [here](#picking-an-availble-cluster)).
3. `ValidateClusterAssignment`: check the cluster and model health, check if the model is overloaded.
4. _If cluster and model is healthy_: 
   1. Reset TTL (`userClusterMappingTTLMinutes`) for assignment in redis.
   2. Route to assigned cluster.
5. _Else_: pick _an available cluster_ (see [here](#picking-an-availble-cluster)).
   1. Set TTL (`userClusterMappingTTLMinutes`) for assigment in redis.
   2. Route to assigned cluster.

**_route to available cluster_, see below for how this picked**

#### Cluster health monitoring

At a configurable (`healthCheckIntervalSeconds`) interval, the configured cluster's healtchecks (`multiClusterMode.clusters[].healthCheck`) are polled.

The health check status code indicates whether the cluster as a whole is considered healthy

| Code     | Healty |
|----------|--------|
| 200      | yes    |
| *        | no     |

The health check body response is json and indicates the models available, their health and consumption

| Field                                | Type      | Meaning
|--------------------------------------|-----------|------------------------------------------------------------------------------|
| `timestamp`                          | timestamp | _not used_                                                                   |
| `models[].name`                      | string    | Model identifying name, used to lookup models from request metadata.         |
| `models[].payload.healthy`           | bool      | Model health, `false` means this cluster cannot currently serve this model.  |
| `models[].payload.capacity`          | float     | Model capacity, an opaque number.                                            |
| `models[].payload.consumption`       | float     | Model consumption, an opaque number that should be <= `capacity`.            |

#### Picking an availble cluster

When picking an available cluster:
1. Skip ineligible clusters
   1. If cluster is unhealthy.
   2. If model is unhealthy.
   3. If model is overloaded
      1. `(consumption / capacity) > overloadedCapacityRatio`.
2. Compute each cluster's `weight` as;
   1. `(capacity + capacity * clusterWeightSmoothingFactor) / (consumption + capacity * clusterWeightSmoothingFactor)`
3. Pick using randomly distributed weight

Some defintions

`overloadedCapacityRatio`

If a model's cluster assignment is currently over this capacity threshold, we'll attempt to find a new one.

`clusterWeightSmoothingFactor`

In order to reduce the impact of consumption differences at very low numbers, we add a smoothing factor relative
to the cluster's capacity. Imagine A and B both with 2000 capacity:

Without smoothing:
- A reports 1 consumption, B reports 2
- A cluster weight is 2000, B is 1000. 
- A will receive 2x the traffic as B, even though they're both effectively empty.

With smoothing:
- A reports 1 consumption, B reports 2
- A cluster weight is (2000 + 100) / (1 + 100) = 20.7, B is (2000 + 100) / (2 + 100) = 20.5. 
- A will receive 0.1% more traffic, which feels correct.

   
## Metrics

Alyx Load Balancer exposes Prometheus metrics for monitoring and observability. Metrics are available at the configured `metricsListenAddress` (default `:9090`).

### Core Metrics

| Metric Name | Type | Description |
|-------------|------|-------------|
| `alyx_lb_http_requests_total{code,target}` | Counter | Total HTTP requests by status code and target |
| `alyx_lb_http_request_duration_seconds{method,code}` | Histogram | HTTP request duration |
| `alyx_lb_backend_healthy{target}` | Gauge | Backend health status (1=healthy, 0=unhealthy) |
| `alyx_lb_health_checks_total{target,result}` | Counter | Health check attempts by result |
| `alyx_lb_health_check_duration_seconds{target,result}` | Histogram | Health check duration |
| `alyx_lb_failover_events_total{to}` | Counter | Failover events between primary/secondary |

### Multi-Cluster & Rebalancing Metrics

| Metric Name | Type | Description |
|-------------|------|-------------|
| `alyx_lb_rebalance_events_total{reason}` | Counter | Rebalancing events by reason (`tpm_imbalance`, `cluster_unhealthy`) |
| `alyx_lb_user_mapping_changes_total` | Counter | Total user mapping changes from consistent hash |
| `alyx_lb_routing_deviations_total{reason}` | Counter | Routing deviations by reason (`rebalance`, `optimal_cluster`) |
| `alyx_lb_tpm_imbalance_ratio` | Gauge | Current TPM imbalance ratio across clusters |
| `alyx_lb_cluster_tpm_total{cluster_name}` | Gauge | Total TPM for each cluster |
| `alyx_lb_cluster_worker_count{cluster_name}` | Gauge | Worker count for each cluster |
| `alyx_lb_cluster_tpm_per_worker{cluster_name}` | Gauge | TPM per worker for each cluster |



### Example Metrics Output

```
# HELP alyx_lb_rebalance_events_total Total rebalancing events
# TYPE alyx_lb_rebalance_events_total counter
alyx_lb_rebalance_events_total{reason="tpm_imbalance"} 5
alyx_lb_rebalance_events_total{reason="cluster_unhealthy"} 12

# HELP alyx_lb_user_mapping_changes_total Total user mapping changes
# TYPE alyx_lb_user_mapping_changes_total counter
alyx_lb_user_mapping_changes_total 17

# HELP alyx_lb_tpm_imbalance_ratio Current TPM imbalance ratio
# TYPE alyx_lb_tpm_imbalance_ratio gauge
alyx_lb_tpm_imbalance_ratio 0.15

# HELP alyx_lb_cluster_tpm_per_worker TPM per worker for each cluster
# TYPE alyx_lb_cluster_tpm_per_worker gauge
alyx_lb_cluster_tpm_per_worker{cluster_name="cluster1"} 1250.5
alyx_lb_cluster_tpm_per_worker{cluster_name="cluster2"} 980.2
alyx_lb_cluster_tpm_per_worker{cluster_name="cluster3"} 1100.8
```

### Dashboards

* [Production grafana](https://grafana.baseten.co/d/30215330-347a-44b1-90e7-b86250565995/alyx-lb-cursor?orgId=1&from=now-15m&to=now&timezone=browser&var-datasource=P013DF5682D46C395&refresh=5s])
* [Dev](https://grafana.mc-dev.baseten.co/d/30215330-347a-44b1-90e7-b86250565995/alyx-lb-cursor?orgId=1&from=now-1h&to=now&timezone=browser&var-datasource=eeusem7g0grnkc&var-service=&var-model=$__all&refresh=5s&query=Alex)

## Logging

Logs are emitted to standard output in Google Cloud Logging-compatible JSON format:

```json
{
  "message": "Primary failed health checks. Switching to secondary.",
  "severity": "WARNING",
  "component": "proxy"
}
```

### Severity Levels

- `INFO`: General status messages
- `WARNING`: Health-based routing changes
- `ERROR`: Proxy or health check errors
- `CRITICAL`: Startup or fatal system errors

### Dashboards

* [Production logs](https://grafana.baseten.co/explore?schemaVersion=1&panes=%7B%22jd1%22%3A%7B%22datasource%22%3A%22P9CFF06760211CEA7%22%2C%22queries%22%3A%5B%7B%22refId%22%3A%22A%22%2C%22expr%22%3A%22%7Bcontainer%3D%5C%22alyx-lb%5C%22%7D+%7C%3D+%60logging+current+cluster+state%60%5Cn%7C+json%5Cn%7C+unpack%5Cn%7C+line_format+%60aws-uw2-prod-2%3A+capacity%3A+%7B%7B.aws_uw2_prod_2_modelState_cursor_dsv3_agent_0819_capacity%7D%7D+%7C+consumption%3A+%7B%7B.aws_uw2_prod_2_modelState_cursor_dsv3_agent_0819_consumption%7D%7D%5Cnaws-ue2-prod-1%3A+capacity%3A+%7B%7B.aws_ue2_prod_1_modelState_cursor_dsv3_agent_0819_capacity%7D%7D+%7C+consumption%3A+%7B%7B.aws_ue2_prod_1_modelState_cursor_dsv3_agent_0819_consumption%7D%7D%5Cnaws-ue1-prod-2%3A+capacity%3A+%7B%7B.aws_ue1_prod_2_modelState_cursor_dsv3_agent_0819_capacity%7D%7D+%7C+consumption%3A+%7B%7B.aws_ue1_prod_2_modelState_cursor_dsv3_agent_0819_consumption%7D%7D%60%22%2C%22queryType%22%3A%22range%22%2C%22datasource%22%3A%7B%22type%22%3A%22loki%22%2C%22uid%22%3A%22P9CFF06760211CEA7%22%7D%2C%22editorMode%22%3A%22code%22%2C%22direction%22%3A%22backward%22%7D%5D%2C%22range%22%3A%7B%22from%22%3A%22now-1h%22%2C%22to%22%3A%22now%22%7D%7D%7D&orgId=1)
* [Production error logs](https://grafana.baseten.co/explore?schemaVersion=1&panes=%7B%22f1i%22:%7B%22datasource%22:%22P9CFF06760211CEA7%22,%22queries%22:%5B%7B%22refId%22:%22A%22,%22expr%22:%22%7Bapp%3D%5C%22alyx-cursor%5C%22%7D%7C%3D%20%60error%60%22,%22queryType%22:%22range%22,%22datasource%22:%7B%22type%22:%22loki%22,%22uid%22:%22P9CFF06760211CEA7%22%7D,%22editorMode%22:%22code%22,%22direction%22:%22forward%22%7D%5D,%22range%22:%7B%22from%22:%22now-3h%22,%22to%22:%22now%22%7D,%22panelsState%22:%7B%22logs%22:%7B%22columns%22:%7B%220%22:%22Time%22,%221%22:%22Line%22%7D,%22visualisationType%22:%22logs%22,%22labelFieldName%22:%22labels%22%7D%7D%7D%7D&orgId=1)


## Behavior

- On startup, the primary backend is used by default.
- If health checks for the primary fail for `healthCheckFailThreshold` consecutive intervals, traffic is routed to the secondary backend.
- If the primary recovers, traffic is switched back automatically.
- All HTTP traffic is forwarded with the correct `Host` header set for the destination.
- Configuration changes are automatically detected and applied without restart.
- The `evacuatePrimary` flag allows manual control over traffic routing.

## Notes

- Requests with bodies are safely re-buffered to support retries under HTTP/2.
- The reverse proxy uses a shared HTTP transport for connection reuse.
- Only `GET` requests are used for health checking.
