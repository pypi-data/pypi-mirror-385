# Nodewarmer Testing & Operations

## Prerequisites

```bash
export HF_TOKEN="your_huggingface_token"
export KUBECONFIG="path_to_your_kubeconfig"
```

## 1. Local Testing

```bash
make test-all           # Run all tests (quiet)
VERBOSE=1 make test-all # Run all tests (verbose)
```

### How Tests Work
The tests are Python-based using pytest and automatically handle the full lifecycle: create a test namespace, deploy the nodewarmer DaemonSet with specific model configurations, wait for pods to be ready, monitor download progress and symlink creation, validate that the correct revisions are downloaded and symlinks point to expected targets, copy logs for debugging, upgrade configurations for multi-step tests (promotion/rollback), and finally clean up all resources including cache and namespace to ensure test isolation.

### What Tests Run:
- **test-simple**: Tests implicit mode (downloads latest, current=latest)
- **test-revision-promotion**: Tests promoting from old revision to new revision
- **test-rollback**: Tests rolling back current revision to previous revision  
- **test-latest-promotion**: Tests promoting current revision to actual latest

## 2. Deploy Nodewarmer to Cluster

### Basic Deployment
```bash
# From helm/charts/daemon-nodewarmer/
helm upgrade --install nodewarmer . \
  --set hfToken=$HF_TOKEN \
  -n nodewarmer --create-namespace
```

### With Custom Models
```bash
# Edit values.yaml to add your models:
models:
  your-org/your-model:
    gpu_compatible: ["H100", "A100"]
    
# Deploy
helm upgrade --install nodewarmer . \
  --set hfToken=$HF_TOKEN \
  -n nodewarmer --create-namespace
```

### Check Status
```bash
kubectl get pods -n nodewarmer
kubectl logs -n nodewarmer -l app.kubernetes.io/name=daemon-nodewarmer
```

## 3. Promote Revisions

### Set Specific Revision
```bash
# Edit values.yaml:
models:
  your-org/your-model:
    gpu_compatible: ["H100"]
    previous: "old_commit_hash" # Or "INTENTIONAL_NO_PREVIOUS" for first deployment if you want to be explciit
    current: "new_commit_hash"

# Apply changes
helm upgrade nodewarmer . \
  --set hfToken=$HF_TOKEN \
  -n nodewarmer
```

### Promote to Latest
```bash
# Option 1: Remove explicit revisions (implicit mode)
models:
  your-org/your-model:
    gpu_compatible: ["H100"]
    # No previous/current = downloads latest

# Option 2: Set current to latest hash explicitly
models:
  your-org/your-model:
    gpu_compatible: ["H100"]
    previous: "old_commit_hash"
    current: "latest_commit_hash"

helm upgrade nodewarmer . \
  --set hfToken=$HF_TOKEN \
  -n nodewarmer
```

## 4. Rollback Revisions

```bash
# Swap current and previous in values.yaml:
models:
  your-org/your-model:
    gpu_compatible: ["H100"]
    previous: "new_commit_hash"     # Was current
    current: "old_commit_hash"      # Was previous

# Apply rollback
helm upgrade nodewarmer . \
  --set hfToken=$HF_TOKEN \
  -n nodewarmer
```

## Troubleshooting

### Check Nodewarmer Status
```bash
kubectl get pods -n nodewarmer -o wide
kubectl describe pods -n nodewarmer
```

### View Logs
```bash
kubectl logs -n nodewarmer -l app.kubernetes.io/name=daemon-nodewarmer -f
```

### Check Symlinks
```bash
POD=$(kubectl get pods -n nodewarmer -l app.kubernetes.io/name=daemon-nodewarmer -o jsonpath='{.items[0].metadata.name}')
kubectl exec $POD -n nodewarmer -c model-downloader -- ls -la /root/.cache/huggingface/hub/models--your--model/
```

### Clean Up
```bash
make clean  # Clean test resources
helm uninstall nodewarmer -n nodewarmer  # Remove nodewarmer
```
