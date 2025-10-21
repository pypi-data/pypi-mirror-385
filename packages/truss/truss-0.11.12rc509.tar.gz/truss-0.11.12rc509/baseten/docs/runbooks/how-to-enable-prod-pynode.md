# How to enable prod pynode (dual env feature)

At the time of writing this, there are 2 gates to enabling the production pynode for an organization: a feature flag and a flag in OrgMetadata. Once those 2 flags are enabled, the production pynode will be deployed when creating a Release or when rotating the pynodes on deploy. For v0 of the dual env feature, it will also be rotated when a new pynode requirement is created.

Note that those gates are not blocking the creation of a `Release`, only the production pynode deployment.

## Feature Flag
The feature flag is called `DUAL_ENVIRONMENTS_FLAG`. It must be enabled for the organization for which you want to deploy a production pynode. To enabled, go to the `feature flags` page in Django admin panel.

See the [feature flag documentation](/docs/how-to/Feature-Flags.md) for more details.

## License
To enable the `dual_envs_is_enabled` flag on the License object, go to Billip and either:
  (1) Change the license to be customizable and set the flag
  (2) Upgrade to starter/business tier

## Run Django Admin command to set up prod environment

Locate the org in the Billip organizations list (/billip/users/organization/), and run one of the following two commands:
- **Enable draft environment** - Creates initial releases for all applications and deploys the production pynode
- **Enable draft environment and sync UDM data** - Does everything for "Enable draft environment" and additionally copies all UDM data from the draft environment to the new production environment
