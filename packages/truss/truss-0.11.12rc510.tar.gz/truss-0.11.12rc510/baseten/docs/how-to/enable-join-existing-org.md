# Enabling join existing

### Assuming we're trying to enable the join existing organization feature _in production_, do the following:

1. Make sure you're logged into the production admin/superuser account on app.baseten.co
2. Find the same organization [here](https://app.baseten.co/billip/users/organization/) and set `join_existing_setting` to `ENABLED`.
    * Optionally, set `domain`. If `domain` is left empty, it will default to the domain of the org's email (e.g. for email `foo@bar.com`, defaults to `bar.com`).
    * Note that `domain` must be unique across all organizations.
