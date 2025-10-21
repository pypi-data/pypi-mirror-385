# InaccurateBillingUsageRecordsCreated

## Meaning

This alert indicates that more or less than one `StripeUsageRecord` was created for the smoke test organization in this environment. This smoke test organization is meant to have exactly one usage record created every hour.

<details>
<summary>Full context</summary>

This error could indicate a fault in celery, VictoriaMetrics, or another part of the usage record creation flow.

</details>

## Impact

An inaccurate amount of usage records created for the smoke test org for one hour is a strong indicator that the usage records created for other organizations in the same hour were impacted. The number of usage records created as a whole should be investigated.

## Diagnosis

Using dashboards in grafana and the same metric that created this alert, we can come to a conclusion as to the number of usage records created in previous hours and whether the hour when this alert triggered is indicative of an inaccurate amount of usage records created. Logs for the `create_stripe_usage_records` celery task should also be investigated. This task runs once every hour at the 5 minute mark.

Useful grafana dashboards:
* [Billing usage record creation](https://grafana.baseten.co/d/a3db3c2b-831c-4287-b182-bd1e4e91734f)
* [create_stripe_usage_record celery task details](https://grafana.baseten.co/d/fb9bbbad-9c23-4ae9-89e7-b9f3532dc96a/celery-task-details?var-task=create_stripe_usage_records&orgId=1)

## Mitigation

In instances where usage records were not created at all, we can backfill those usage records using usage metrics from the past. To backfill usage records, run the `backfill_stripe_usage_records` command documented [here](https://github.com/basetenlabs/baseten/blob/master/docs/runbooks/backfill-missing-stripe-usage-records.md)
