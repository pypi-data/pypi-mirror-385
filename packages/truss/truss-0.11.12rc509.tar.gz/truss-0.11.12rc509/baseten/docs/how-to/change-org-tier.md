# How to change an org's license tier

Org license tiers allow us to control various aspects of how an organization's workspace operates. There are currently two license tiers:

1. The Startup tier - This is the default for new signups and should be used by self-serve customers.
2. The Pro tier (identified as the `BUSINESS` tier in code) - This should be used by our enterprise, high value, or high touch customers. The Pro tier offers the following features:
   1. Higher limits on the number of models that can be deployed
   2. Exemption from billing protections such as the $50 charging threshold and automatic deactivation
   3. Support for invoicing (rather than automatic charging)

## Upgrading an org to the Pro tier

To upgrade a Starter tier org to the Pro tier, you will need to do the following:

1. Search for the org in [Billip](http://app.baseten.co/billip/users/organization/). Check the box next to the org's name.
2. From the Action dropdown, select "Upgrade to Pro tier".
3. You should be redirected to the upgrade form.
4. _Note:_ You can enable the "Join existing org by email" feature for new signups by setting `join_existing_setting` to `ENABLED`. See the [Enable join existing guide](/docs/how-to/enable-join-existing-org.md) for details
5. Click "Save" to upgrade the organization.

If you need to change these settings later (like the "Collection method"), you can repeat the same steps above for the same org later.

## Downgrading an org to the Startup tier

To downgrade a Pro tier org to the Startup tier, you will need to do the following:

1. Search for the org in [Billip](http://app.baseten.co/billip/users/organization/). Check the box next to the org's name.
2. From the Action dropdown, select "Downgrade to Startup tier".
3. You will be asked to confirm the downgrade. To ensure that the organization will be in good standing after the downgrade, check that either:
   1. The org has a positive credit balance
   2. The org has a payment method on file and none of their invoices are overdue (You can see this on the billing tab in the workspace settings UI)
4. Click "Save" to downgrade the organization.
