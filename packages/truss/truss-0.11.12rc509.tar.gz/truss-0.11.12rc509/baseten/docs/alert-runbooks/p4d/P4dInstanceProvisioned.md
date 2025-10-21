# P4dInstanceProvisioned

## Meaning

An instance of the `p4d` family was provisioned, most likely a `p4d.24xlarge`. Those nodes are very expensive and should not be provisioned in the baseten owned environment.

<details>
<summary>Full context</summary>

This can happen if:
- An error happened during the provisinoning of an oracle
- An oracle was configured to use the `a100` gpu type
- A manual deployment in k8s using the karpenter `gpu` provisioner and not specifying the gpu type caused a `p4d.24xlarge` to be provisioned

</details>

## Impact

The `p4d` instances are very expensive and will cost a lot of money to baseten

## Diagnosis

Find the node in k8s that is running on a `p4d` instance. Look at what workload is running on it and find who deployed this workload. Check with this person why they need a `p4d`

## Mitigation

- Modify the workload requesting the `a100` gpu typ to use something else
- Once the workloads other than daemonsets are off the node, cordon, drain and delete the node

