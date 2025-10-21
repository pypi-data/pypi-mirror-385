# GraphQLRateLimitingTooHigh

## Meaning

Too many graphql calls are being made from the same ip address. 

<details>
<summary>Full context</summary>

Graphql calls are made from the Baseten frontend and is triggered via manual
interactions. As such there can't natually be a high rate of these calls. This
could be a malicious actor.

</details>

## Impact

No direct impact, the rate limit prevented impact. But one should alert about
malicious actors if this happens.

## Diagnosis

Analyze AWS loadbalancer logs to identify the offending ip address. It may be a
known malicious ip address. If it seems malicious then we may want to blacklist
that ip address.

## Mitigation

No specific mitigation but be alert for malicious activity.
