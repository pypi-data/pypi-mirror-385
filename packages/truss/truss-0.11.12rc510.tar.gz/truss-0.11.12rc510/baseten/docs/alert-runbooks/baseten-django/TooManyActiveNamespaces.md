# TooManyActiveNamespaces

## Meaning

There are more than the [kubernetes-recommended](https://github.com/kubernetes/community/blob/master/sig-scalability/configs-and-limits/thresholds.md) amount of namespaces (10000) in the production cluster.

<details>
<summary>Full context</summary>

We delete namespaces when an organization has not been active for more than 2 weeks.
This means that more than 10,000 organizations have been active.

</details>

## Impact

_Likely ok_, we've had 14,000+ namespaces in the cluster previously. Still a cause for concern because **this is uncharted Kubernetes territory**.

## Diagnosis

Check out the organization information dashboard in production and see if there truly is an uptick in active organizations. 
Check the logs and the #user-events channel to make sure organizations are still being routinely hibernated after 2 weeks of inactivity.
Make sure pynodes are still scaling down to zero after an hour of inactivity.

## Mitigation

Consider a more aggressive hibernation period and hibernate more organizations.
