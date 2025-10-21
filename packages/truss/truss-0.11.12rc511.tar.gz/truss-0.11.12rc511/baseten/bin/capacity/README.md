# Capacity Scripts

## Safe Defrag Script
**Note**: This script does everything short of actually draining/deleting the node. That is still a manual step to keep a human in the loop.

This script safely defrags a node. It will also report out if it is safe to defrag/bring down if left to run.

How this script works
- Figure out all of the relevant pods on the node, report out what's running and what GPU types before proceeding
- Get the initial scale (from the knative podautoscaler), the initial replicas (from the replicaset) and the number of pods for that model we want to take action on.
- Cordon the node.
- Orphan the pods.
  - Orphaning the pods consists of removing the `ownerReferences` and the `pod-template-hash` label. This causes the pod to become invisible to the ReplicaSet, triggering the ReplicaSet to scale another replica up. However, the pod is still visible to knative as an available backend. This ends up overprovisioning the model by `n`+`m` model pods where `m` is the number of model pods for that model we orphaned.
- Wait to see if we've overprovisined by enough pods to allow for safe drain/delete.
  - There's 2 conditions which can trigger this
    - `current_kpa_scale >= initial_replicas + overprovision_count` - catches conditions where we are running a static # of replicas and if we've scaled up.
    - `current_kpa_scale >= current_replicas + overprovision_count` - catches conditions where the model has scaled down while we're running our script
- Report out that the node can be safely defragged

Example output:
```
[AWS:production] cmcgrath@baseten:~/Documents/Work/Baseten$ python3 defrag.py -n gke-us-central1-prod-dws-h100-1c-mega-fd11a600-csnq

Found pods to defrag:
	org-9edb01c1dffe4d95bb2cec51ce3d9ebe/bt-deployment-qvr7e9w-00001-deployment-547cc9b97f-pgtn2
		- 1x nvidia-h100-80gb GPUs
		- STATUS=[Running] REPLICAS=3 KPA_SCALE=3

Proceed with defrag? (y/n): y
Node gke-us-central1-prod-dws-h100-1c-mega-fd11a600-csnq has been cordoned (marked unschedulable).
Pod org-9edb01c1dffe4d95bb2cec51ce3d9ebe/bt-deployment-qvr7e9w-00001-deployment-547cc9b97f-pgtn2 orphaned
---
Revision bt-deployment-qvr7e9w-00001 - 1 extra needed - current_scale=3 replicas=3 initial_scale=3

...

---
Revision bt-deployment-qvr7e9w-00001 - 1 extra needed - current_scale=3 replicas=3 initial_scale=3
---
Revision bt-deployment-qvr7e9w-00001 - 1 extra needed - current_scale=4 replicas=3 initial_scale=3
Safe to defrag/remove node
```
