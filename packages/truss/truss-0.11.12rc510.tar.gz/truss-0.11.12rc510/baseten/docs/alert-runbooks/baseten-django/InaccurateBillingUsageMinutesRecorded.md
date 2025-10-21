# InaccurateBillingUsageMinutesRecorded

## Meaning

This alert indicates that more or less than 60 minutes of usage was recorded for the smoke test organization in this environment. This smoke test organization is meant to have exactly 60 minutes of usage recorded every hour.

<details>
<summary>Full context</summary>

This error could indicate a fault in the billing queries we use to query VictoriaMetrics for usage every hour.

</details>

## Impact

An inaccurate amount of usage (minutes) recorded for the smoke test org for one hour is a strong indicator that the usage records created for other organizations in the same hour were impacted. The quantity of minutes recorded in each usage record created recently should be investigated.

## Diagnosis

Using dashboards in grafana, the same metric that created this alert, and the metrics that we use to query for usage, we can come to a conclusion as to whether the hour when this alert was triggered is indicative of an inaccurate quantity of usage reported in usage records created. Scraping intervals, kube-state-metrics pods, and the state of VictoriaMetrics should also be considered.

Useful grafana dashboards:
* [Billing usage record creation](https://grafana.baseten.co/d/a3db3c2b-831c-4287-b182-bd1e4e91734f)
* [create_stripe_usage_record celery task details](https://grafana.baseten.co/d/fb9bbbad-9c23-4ae9-89e7-b9f3532dc96a/celery-task-details?var-task=create_stripe_usage_records&orgId=1)

## Mitigation

In instances where usage records were not created at all, we can backfill those usage records using usage metrics from the past. To backfill usage records, run the `backfill_stripe_usage_records` command documented [here](https://github.com/basetenlabs/baseten/blob/master/docs/runbooks/backfill-missing-stripe-usage-records.md)
