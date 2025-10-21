# Migrating oracles between WPs

Users may automatically migrate their oracles when changing instance types. Every time the oracle resources are updated (`update_resource` mutation), we redetermine which WP to deploy the oracle to (See `org_wp_for_gpu_type()`). If it’s different than the WP of the previous `OracleDeploymentSpec`, this initiates a migration.

## Manually migrating oracles

There are cases where we want to migrate the oracles ourselves, without user involvement. For example, we might want to load balance A100 capacity across AWS and GCP, or customers might have requirements that necessitate them to be in one WP over another. Although the implementation is largely the same as the user-facing migration, the steps are a little different.

1. In the billip constance page, update `ACCELERATOR_TYPE_DEFAULT_WORKLOAD_PLANES` or `ORGANIZATION_ACCELERATOR_TYPE_WORKLOAD_PLANE_OVERRIDES` to change the GPU type → WP assignment either globally or for one organization.
2. Go to the [Oracles list view](http://localhost:9090/billip/oracles/oracle/) in Billip and find the oracles impacted by the constance change. Check the boxes next to these oracles, select "Migrate oracles between workload planes" from the "Action" dropdown, and click "Go".
3. The next page will display the oracles needing migration. Under each oracle, the versions needing migration are shown. Click "Migrate" to initiate the migration.
4. Monitor the migration until it is complete:
   1. Each the versions should enter and leave the migrating state.
   2. As the new deployment scaled up, you should see the "New replica count" increase to match the "Old replica count".
   3. Once the migration is done, the "Old replica count" should go to zero.

## Rolling back a failed migration

Although it hasn’t happened to a customer model yet (🤞), there’s a small chance that the OVD will fail to come up in the new workload plane. For cases where the model is serving continuous, real customer traffic, we need to be able to revert to the previous workload plane with zero downtime.

Follow the same steps above for manually migrating oracles, except instead of importing and calling `migrate_oracle_to_desired_workload_plane`, call instead `rollback_workload_plane_migration(oracle)`. This will reuse any OVDs that are still live from before the migration was initiated. This should work for both user and billip-initiated migrations, and any other changes to the deployment spec like a new instance type will be undone.
