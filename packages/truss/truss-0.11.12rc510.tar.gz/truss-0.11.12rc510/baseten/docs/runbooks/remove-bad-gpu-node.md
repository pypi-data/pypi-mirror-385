# Removing bad GPU nodes

## Description

We've observed that some GPU nodes come up but during initialization they fail to return a non-zero status code from `nvidia-smi`. This halts the initialization and causes the node to be unusable. This document describes how to remove such nodes.

## Steps

1. Find the node name

```bash
kubectl get pods -n gpu-operator -o wide | grep Init
```

You should see the node name.

2. Remove the node

```bash
kubectl delete node <node-name>
```

Karpenter handles removing the node from the cluster and deleting the underlying instance.


