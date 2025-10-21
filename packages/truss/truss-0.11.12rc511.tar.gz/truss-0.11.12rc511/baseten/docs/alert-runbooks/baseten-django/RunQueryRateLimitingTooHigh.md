# RunQueryRateLimitingTooHigh

## Meaning

Too many run query api calls from the same ip address.

<details>
<summary>Full context</summary>

Run query calls are made when user tries out a query in Baseten application.
It's very unlikely that a real user would be trying out lots of queries very
quickly, this is most likely a malicious actor.

</details>

## Impact

No impact, just watch out for malicious activity.

## Diagnosis

Analyze AWS loadbalancer logs to identify the offending ip address. It may be a
known malicious ip address. If it seems malicious then consider blacklisting
that ip address.

## Mitigation

No specific mitigation but be alert for malicious activity.
