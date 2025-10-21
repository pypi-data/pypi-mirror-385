# GPU Node Test

When testing new GPU nodes across different clusters—each with its own software
stack—this folder provides everything you need for quick validation.

## How to check a gpu node

```sh
export NODE_NAME=PUT_NODE_NAME_HERE
#e.g. b200-node-d64dfac39c22
make check_node
```

Alternatively, just update `REPLACE_WITH_NODE_NAME` in the `job.yaml` here and
`kubectl apply -f job.yaml`.

The key piece is the Docker image, which will run a test workload across all 8
GPUs on the node.

After you're done:
`kubectl delete job h100-gpu-job`
