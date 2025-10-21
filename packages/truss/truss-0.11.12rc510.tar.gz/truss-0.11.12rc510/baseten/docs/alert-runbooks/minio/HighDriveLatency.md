### HighDriveLatency

**Alert**: `HighDriveLatency`

**Trigger**: Drive latency exceeds 1 second over the past 5 minutes.

**Severity**: Critical

#### Runbook Steps:
1. **Check Drive Health**: Use `iostat` or similar tools to monitor disk I/O performance.
2. **Check Disk Usage**: High disk usage may cause latency; use MinIO or system tools to check. `df` and `du` can give mount and utilization information.

