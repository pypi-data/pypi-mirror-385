# OracleVersionNotScalingDown

## Meaning

This alert means that an oracle version is not scaling to zero after receiving no requests for a certain amount of time.

<details>
<summary>Full context</summary>

We first observed an issue in August 2023 with knative not scaling down a model even after a long period (several hours) with no requests being sent to the model. The purpose of this alert is to track and guard against this issue impacting customers now and in the future.

The alert looks for model versions that meet the following conditions:

- In an active state
- Have scale to zero enabled (`min_replicas=0`)
- Have at least one replica running
- Have not received a request in: `scaling_window_seconds + idle_time_seconds + 15 minutes` (scaling window + scale to zero delay + 15 minutes extra buffer)

This alert and the underlying metric instrumentation may be removed if and when we are confident that the issue has been resolved. The root issue investigation is tracked by [this Linear](https://linear.app/baseten/issue/BT-8634/model-doesnt-scale-to-zero-sometimes-when-it-should).

</details>

## Impact

Many customer models rely on scale to zero to save resources and money when a model is not being actively called. If a model fails to scale down, this can result in unwarranted model costs for the customer.

## Diagnosis

Given the oracle version id and org name from the alert, you should double check through the Baseten UI (impersonating the user) that the model is not scaled to zero and has not received inference requests in the last interval of the scaling window + scale to zero delay. You can find both these quantities in the manage resources dialog.

## Mitigation

Deactivate and reactivate the model. This will cause the model to scale up to one replica but it should scale down properly on its own (double check that it does after the expected period of time). Note that it may take 5-10 minutes for the alert to clear after the model has scaled down.

## References

- [Django logic used to generate alert](../../../backend/common/observability/metrics/oracles_not_scaling_down.py)
- [BT-8634 : Model doesn't scale to zero sometimes when it should](https://linear.app/baseten/issue/BT-8634/model-doesnt-scale-to-zero-sometimes-when-it-should) - Tracking investigating root cause
- [Slack thread for 1st occurence](https://basetenlabs.slack.com/archives/C02K3QNBVCJ/p1692107472434139)
- [Slack thread for 2nd occurence](https://basetenlabs.slack.com/archives/C02K3QNBVCJ/p1693958017764139)
