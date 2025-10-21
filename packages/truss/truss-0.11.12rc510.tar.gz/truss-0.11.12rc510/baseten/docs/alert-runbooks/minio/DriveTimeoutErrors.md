### DriveTimeoutErrors

**Alert**: `DriveTimeoutErrors`

**Trigger**: More than 5 drive timeout errors in the past 5 minutes.

**Severity**: Critical

#### Runbook Steps:
1. **Inspect Logs**: Check MinIO logs for any disk timeout errors. Inspect EBS or GKE Volume logs to see if there are any alerts or failures.
2. **Check Disk Health**: Shell into the minio nodes and inspect individual disk by using `df` and `iostat` to check disk health. To install `iostat` use `yum install sysstat` or `apt-get install sysstat`
3. **Add More Storage**: Scale the storage by adding more disks or increasing capacity. Easiest is to add more nodes. Default is to run a cluster of 5 nodes.
4. **Escalate**: If the issue persists, escalate to the infrastructure team.

