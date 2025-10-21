# Backfill missing Stripe usage records
When Prometheus is down, we run the risk of missing hours worth of Stripe usage records since we rely on Prometheus to calculate model usage. [See an example of the impacts of Prometheus downtime here](https://basetenlabs.slack.com/archives/C02K3QNBVCJ/p1672787712961599.). In order to be able to backfill for these hours, we can use a django command.

## Find missing Stripe usage records
```
from datetime import timedelta
from django_context_crum import set_current_user
org = Organization.objects.get(email='email@address.com')
set_current_user(org.impersonation_user)

start = org.stripe_usage_records.order_by("timestamp").first().timestamp
end = org.stripe_usage_records.order_by("timestamp").last().timestamp
delta = end - start
delta_hours = delta.days * 24 + delta.seconds // 3600
hourly_range = set(start + timedelta(hours=x) for x in range(0, delta_hours + 1))
timestamps = set(org.stripe_usage_records.values_list('timestamp', flat=True))

missing_stripe_usage_record_timestamps = hourly_range - timestamps

# If missing_stripe_usage_record_timestamps is empty, there are no missing records. If not, then those timestamps are the ones we are missing.
```

## Backfill using the django command

### To backfill for **all missing** usage records
`python manage.py backfill_missing_stripe_usage_records --all-orgs --all-missing`

### To backfill for all provisioned orgs
`python manage.py backfill_missing_stripe_usage_records --all-orgs --timestamp "2023-01-10 08:00:00+00:00"`

### To backfill for **some** provisioned orgs
`python manage.py backfill_missing_stripe_usage_records --orgs baseten another sam--stripe--baseten-co --timestamp "2023-01-10 08:00:00+00:00"`

### To backfill for hours in a time range
`python manage.py backfill_missing_stripe_usage_records --orgs baseten --start "2023-01-10 08:00:00+00:00" --end "2023-01-10 20:00:00+00:00"`

### To backfill for a specific hour
`python manage.py backfill_missing_stripe_usage_records --all-orgs --timestamp "2023-01-10 08:00:00+00:00"`
