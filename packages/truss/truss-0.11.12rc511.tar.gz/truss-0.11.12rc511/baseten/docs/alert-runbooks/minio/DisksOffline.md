### DisksOffline

**Alert**: `DisksOffline`

**Trigger**: Disk(s) offline for more than 5 minutes.

**Severity**: Critical

#### Runbook Steps:
1. **Check Logs**: Inspect the MinIO StatefulSet logs for the offline nodes to understand the cause.
2. **Check Pod Status**: Use `kubectl get pods -n baseten-fs` to check if the pods are not in running state.
3. **Disk Health**: Look at [Minio Dashboard](https://grafana.baseten.co/d/TgmJnqnnk/minio-dashboard?orgId=1) in Grafana to see if any Disks are reporting outage.
4. **Replace Faulty Disk**: If a disk is found to have issues, this would involve restarting the pod and potentially replacing the PV. Escalate to the infrastructure team. This should be a very rare condition.

