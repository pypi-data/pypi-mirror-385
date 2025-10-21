### LowStorageAvailability

**Alert**: `LowStorageAvailability`

**Trigger**: Available storage drops below 10 GB.

**Severity**: Critical

#### Runbook Steps:
1. **Review Storage Usage**: Check which nodes are consuming excessive storage.
2. **Add More Storage**: Scale the storage by adding more disks or increasing capacity. Easiest is to add more nodes. Default is to run a cluster of 5 nodes.
3. **Rebalance Cluster**: Ensure that MinIO automatically redistributes data across new storage. Once a new node is added, it distributes to a new node gradually to prevent network flood.
4. **Reduce Replication Factor**: Reducing replication factor can free up diskspace.
5. **Escalate**: If the issue persists, escalate to the infrastructure team.

