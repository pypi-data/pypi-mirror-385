# Daemon Node Warmer

DaemonSet that pre-downloads models on GPU nodes to reduce cold start times.

## Quick Start

Note: to run the following commands you need these pre-reqs:

1. `helm plugin install https://github.com/databus23/helm-diff`
2. `brew install helm` (for MacOS)
3. `brew install rancher-cli`

```bash
# Development
make dev_install_nodewarmer HF_TOKEN=your_token

# Production  
make prod_install_nodewarmer HF_TOKEN=your_token
```

## Testing/Preview

Preview rendered manifests without deploying:

```bash
# Development manifest (with dev overrides)
helm template test-release . \
  --set hfToken=demo123 \
  --set imageProxy=dev-registry/ \
  --set checkIntervalSeconds=30 \
  --set configReadRetryDelaySeconds=10

# Production manifest
helm template prod-release . \
  --set hfToken=your_token \
  --set imageProxy=prod-registry/
```

## Configuration

### Configuration
- `values.yaml` - Default configuration
- Use `--set` flags or custom values files for environment-specific overrides

### Key Options
```yaml
# Global settings
nodeHostPath: /mnt/stateful_partition/kube-ephemeral-ssd
cachePath: dynamo_cache-b8c557a4-6e3b-4f56-86f9-f4a5e6b51/huggingface

checkIntervalSeconds: 3600          # Config check interval
minFreeSpaceGB: 20                  # Minimum free space
models:                             # Models to download
  model-name: {}
  model-with-filter:
    gpu_compatible: ["ALL"]
```

## Features

- **Single Purpose**: Install to enable, uninstall to disable - no complex toggles
- **GPU Targeting**: Runs only on GPU nodes, excludes special types
- **Disk Management**: Monitors space, stops downloads when low
- **Dynamic Config**: Updates when ConfigMap changes
- **Fault Tolerant**: Handles failures, resumes downloads
- **Configurable Cache**: Customizable host path for model storage

## Components

The chart creates:
- **DaemonSet** - Main workload
- **ServiceAccount + RBAC** - Node read permissions  
- **ConfigMap** - Model configuration
- **Secret** - HuggingFace token (from `hfToken` value)

## Implementation

- Code: `/mp/ci/node-warmer/node-warmer.py`
- Image: `baseten/model-api-nodewarmer`
- Cache: `/root/.cache/huggingface` (hostPath) 
