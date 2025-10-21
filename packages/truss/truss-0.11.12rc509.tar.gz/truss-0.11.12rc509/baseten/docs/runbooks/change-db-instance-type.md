# Change DB instance type in AWS Aurora

AWS Aurora offers many utility to allow for almost seemless instance type update in a database cluster.

## Requirements
- DB must be a Aurora DB cluster
- Cluster must have 1 writer instance and at least 1 reader instance
- At least 1 reader instance must have the same `failover priority` as the writer instance

## How To
1. For minimal down and better DB failover, change the `CONN_MAX_AGE` setting to 0 and deploy to production
1. Modify reader instance type
1. Wait for the reader instance to become available again
1. Start a `failover` on the cluster from AWS console
1. Wait for the `failover` to complete.
    - Make sure the writer instance is now the instance with new instance type
1. Modify other instance's instance type
1. Modify the instance_class in terraform
1. Run `terraform plan` to validate what terraform will do
    - It should show that there is nothing to change on the database
1. If `CONN_MAX_AGE` was modified, set it back to it's original value (60)
1. Deploy to prod to apply terraform and config changes
