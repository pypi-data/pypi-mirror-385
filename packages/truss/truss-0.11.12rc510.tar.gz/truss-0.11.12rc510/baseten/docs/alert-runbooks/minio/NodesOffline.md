### NodesOffline

**Alert**: `NodesOffline`

**Trigger**: Node(s) have been offline for more than 5 minutes.

**Severity**: Critical

#### Runbook Steps:
1. **Check Logs**: Inspect the MinIO StatefulSet logs for the offline nodes to understand the cause.
2. **Check Node Status**: Use `kubectl get nodes` to check if the nodes are down or experiencing issues.
3. **Check Pod Status**: Use `kubectl get pods -n baseten-fs` to check if the pods are not in running state.
3. **Escalate**: If the issue persists, escalate to the infrastructure team.
