# ClusterAutoscalerUnschedulablePods

## Meaning

The cluster autoscaler is unable to scale up and is alerting that there are
unschedulable pods because of this condition.

<details>
<summary>Full context</summary>

* The autoscaler is unable to create new machines due to replica limits on the
  MachineAutoscalers.
* The autoscaler is unable to create new machines due to maximum node, CPU, or
  RAM limits on the ClusterAutoscaler.
* Kubernetes is waiting for new nodes to become ready before scheduling pods to
  them.

</details>


## Impact

We cannot schedule pods and the autoscaler doesn't have any scaling rules to fix this

## Diagnosis

- Look at the limits on the different k8s node groups.
- Look at the node states

## Mitigation

In many cases this alert is normal and expected depending on the configuration
of the autoscaler. You should check the replica limits in the autoscaler
resources to ensure they are large enough. You should also check the maximum
totals nodes, CPU, and RAM limits in the autoscaler resource to ensure
they are valid.

In rare cases it is possible that the AWS is taking longer than 20
minutes to create new nodes.
