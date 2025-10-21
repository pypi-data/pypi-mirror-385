# DaemonSetMemoryRequest

## Meaning

The total memory request of all daemonset pods on a node has increased. It can cause oracle instance type to no longer schedule or schedule on the wrong node type.

<details>
<summary>Full context</summary>

This can happen if:
- A new daemonset was added to the infrastructure
- An existing daemonset now requests more memory

</details>

## Impact

It can cause oracle instance type to no longer schedule or schedule on the wrong node type.

## Diagnosis

Look at the changes to the infrastructure or ask in the #infra channel on slack if those changed are expected.

## Mitigation

- Open a PR similar to [this one](https://github.com/basetenlabs/baseten/pull/5603) to reduce the amount of memory that the GPU instance types are requesting
- Test in dev or staging that the new memory request for the instance types are using the expected node type
- Change the alert threshold for this alert ([DaemonSetMemoryRequest](https://github.com/basetenlabs/baseten/blob/master/terraform/modules/kube-prometheus-stack/prometheus-stack.tf#L)) to the new value show in [this grafana dashboard](https://grafana.baseten.co/goto/zV56w_J4z?orgId=1)
