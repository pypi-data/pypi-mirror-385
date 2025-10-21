# BasetenDjangoHigh5xxErrorRate

## Meaning

This alert indicates that Baseten django app is returning 5xx http error codes.
These indicate unexpected behavior in django app functioning, they shouldn't
happen under normal operation.

<details>
<summary>Full context</summary>

These errors would normally cause a sentry, and more details about the specific errors can be found there. These are critical issues, each type of error would need investigating even if the errors stop happening for a while.

</details>

## Impact

Since these are unexpected errors the user is likely either seeing errors or not seeing their actions take effect. Either way it's a bad user experience. Impact would depend on what percentage and which user requests are getting the 5xx.

## Diagnosis

Use sentry to gather more details about the error. Use logs and charts in grafana to debug.

## Mitigation
If the suspect functionality can be turned off with a feature flag then consider
that. If it's deploy related then reverting the deploy may be an option. If
revert is not easy then a fix would need to be deployed. 
