# RequestQPSTooHigh

## Meaning

Coredns qps is too high.

<details>
<summary>Full context</summary>

Coredns, even normally, gets pretty high qps because almost every request
requires dns resolution first. But this alert indicates that the qps is
abnormally high. This is unlikely due to any customer related usage. This is
most likely due to a misconfiguration somewhere.

</details>

## Impact

High qps in itself is not an issue, but it may be a pre-cursor to other issues
and may be the cause.

## Diagnosis

Look for the timing of the qps spike and try to find correlation with deploys of infrasctructure changes.

## Mitigation

In short term, number of coredns replicas can be increased to effectively
handle high qps. For full mitigation, the misconfiguration would need to be
identified and fixed.
