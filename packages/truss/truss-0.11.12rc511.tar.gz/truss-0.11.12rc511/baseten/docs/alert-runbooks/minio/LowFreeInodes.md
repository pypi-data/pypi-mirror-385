### LowFreeInodes

**Alert**: `LowFreeInodes`

**Trigger**: Free inodes are below 1000.

**Severity**: Critical

#### Runbook Steps:
1. **Check Inode Usage**: Shell into the stateful set pods and use `df -i` or similar tools to check inode usage on the affected node/pod.
2. **Check Small Files**: Identify small files consuming inodes. JuiceFS creates a minimum file size of 8MB. Clearing out files is an involved process, because we don't want to accidentally corrupt user data. 
3. **Increase Inodes**: Add more disks or nodes to the cluster to increase the number of available inodes.
4. **Monitor Inode Growth**: Set up monitoring for inode usage trends to avoid future issues. Minio Metric - `minio_node_drive_free_inodes`.
