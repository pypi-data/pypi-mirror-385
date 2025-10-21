# InvokeWorkletRateLimitingTooHigh

## Meaning

Too many worklet invocation API calls from the same ip address. 

<details>
<summary>Full context</summary>

We rate-limit worklet invocation calls by ip address. This error indicates that
someone is breaching this limit. It may be a real user overstepping their limit
or this could be a malicious actor.

</details>

## Impact

It could be a real customer, whose worklet invocation calls may be failing.

## Diagnosis

Use logs on grafana to identify the organization of the worklet that's hitting
the rate-limit. One can look at worklet run logs. One can also run a query on
the baseten postgres database to identify this. Once that organization is
identified we may want to contact them and let them know why they may be seeing
their worklet calls fail.

## Mitigation

Nothing specific to do, but possibly our rate-limit could be too low that we may
need to increase. 
