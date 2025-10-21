# TooManyRestarts

## Meaning

Job mentioned in the description has restarted more than twice in the last 15 minutes. It might be crashlooping.

<details>
<summary>Full context</summary>

This can happen if:
- Pod is OOM killed soon after it is started.

</details>

## Impact

The impact varies based on the affected components.
- VMAlert - Alerts might get delayed or missed (if it was self resolved)
- VMAgent - Slight chance of lossing metrics. VMAgent restarts really quick.
- VMInsert - If all pods are down at the same time for extended time period, VMAgent may run out of disk space on local cache and thus may drop metrics
- VMSelect - If all pods are down at the same time, no queries can be served.
- VMStorage - If all pods are down at the same time, no queries can be served and may drop metrics if VMAgent ran out of disk cache

## Diagnosis
Use the following steps to determine the cause.
- Run `kubectl -n monitoring get pods <pod-name> -o json | jq '.status.containerStatuses[].lastState'` on mentioned pod. If the pod was OOM killed, you should see the information there.
- Run `kubectl -n monitoring logs -f <pod-name>` and monitor the logs

## Mitigation

- If the restart was caused by OOM and not stopping, try to increase the memory requests and limits for the component. Make sure a PR is created to persist the changes
- If the restart was caused by program errors, consider rolling back to older version of image or upgrading to newer version if a particular fix is included to address this bug.
