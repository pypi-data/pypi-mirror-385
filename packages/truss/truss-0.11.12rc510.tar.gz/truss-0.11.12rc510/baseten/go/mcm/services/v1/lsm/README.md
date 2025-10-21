

## Checkpoints
Per resource type checkpoints (k8s resourceVersion) are written to Redis. For performance reasons we read checkpoints from memory cache (when present) and only write to Redis.

The checkpoint hash key: `lsm-{resourceName}`
The checkpoint field: `checkpoint`
Where resource name is: `pods, nodes, deployments, podautoscalers`

To reset checkpoint. Stop the LSM deployment first (prevent checkpoint writes) and then manually delete hash key from redis.

<code>
hget lsm-pods checkpoint
hdel lsm-deployments checkpoint
</code>

