# Preemption V1

Preemption in MCM is complicated because we do not have full control on pod-node placements i.e. which pod to remove and where to place the new pod. Pod-node placement is deferred to k8s scheduler when we scale up or down the k8s deployment.

## How do we select the node and victims (preemptees)?
The normal scheduler cycle phase allocates from available resources only.
The preemption phase will attempt to use non-available resources:
* Terminating pods
* Surplus pods i.e. when deployment has more assigned pods than the commit in the WP. This usually happens during scale down. We can expect the pod to transition to a terminating state.
* Committed pods

We attempt to match preemption request to resources that are least intrusive. The types of victim
in order of preference:
1. Force delete pods. We need to wait for the pod to be deleted from the system. Last step for a pod's resource to be freed.
2. Terminating pods. We need to take action to force delete the pod.
3. Surplus pods (does not map to commit). We need to wait for the pod to transition to terminating state.
4. Normal pods (maps to commit). We need to preempt a deployment (scale down).

We break ties based on the following order:
1. Priority of the pod
2. Prefer pods in WP with lower Preemptor's WP score.
3. Prefer recent creation timestamp
4. Prefer the higher lexical order pod name

If this pod corresponds to the deployment's last replica in a WP then we will not select this pod. This is
because of ksvc's limitation where scaling down to zero may take a long time (scale down delay applies) and
so the pod might take a very long time to be freed. Better to avoid matching to this resource.

We do not use the deployment priority of the pod as the primary differentiator because of the lifecycle transitions. 
The following is the lifecycle transition of a preempted resource:
1. Victim's deployment is scaled down. The pod is still around until action is executed. During this time it becomes a surplus pod.
2. Once the scale down action is executed, the pod transitions to a terminating state (k8s action).
3. Scheduler will mark the terminating pod for force delete in the next cycle
4. Force delete action is taken (via Operator) and k8s deletes the pod. This frees up the resource on the node.
5. Scheduler sees the available resource on the node on the next cycle and allocate it to the highest priority
deployment.

The victim preferences will attempt to use the pods that are later in the lifecycle. This will maximize the likelihood that the next scheduler cycle will choose the same victims. It will also minimize disruptive actions e.g. preempt another pod or force delete another pod. 

Another reason is because of the multi-GPU scenario. Multi-GPU scenario could have multiple victim pods with different priorities. These victims will transition at different times and could cause the same node to have 
difference lowest/highest victim prioriy across cycles. It can lead to unstable preemption behavior across cycles.

## Selecting preemptors
For the preemption phase, we will always attempt to allocate resources to the highest priority deployments first.
This phase does not scale up preemptor deployments. The goal is to scale down preemptee deployments and force delete 
terminating pods to free up resources. Once the resources are truly freed up, the deployments will be able to scale up.

Reminder here that we do not have control over which pods are actually preempted (exception is the force delete scenario). The algorithm will find a potential solution that would work and scale down the victim deployment with the expectations that it would eventually work out.

Important criteria to consider with the implementation:
* Needs to be stable across scheduler cycles i.e. same input should result in same preemption outcome.
* Prefer selecting the same preemptor and preemptees across cycle, even when some input changes (e.g. a pod transitions to terminating state).
* Avoid fluctations where we preempt in one cycle and add back resource in another.

To improve stability of the algorithm, we made the following implementation decision (compromises) for V1:
1. The Deployment priority is static throughout this phase. This makes the algorithm stable and prevents circuler loops where deployments preempts each other.
2. Deployment are not able to preempt resources from deployment of the same priorituy level or pods that were allocated from prior preemption in the same cycle.
3. When a deployment resource has been preempted, we will remove the deployment from further allocations. This forces the preempt action to be taken (victim's schedule change). This avoids the case when preemptee finds resource in another node resulting in no schedule changes (no action taken). Because we don't have control of pod-node placements, we need to force action for preemption to be effective. Once deployment is not a preemptee anymore (in next cycles), it is then eligible for being a preemptor.

For the single-GPU scenario. the algorithm is straighforward and we will always choose the node with the lowest priority victim to preempt. The preemptee should not lead to another preemption.

For the multi-GPU scenario, the algorithm is more complex because the victims are not necessarily the lowest priority in the node. It is the lowest priority with the required GPU resources. The preemptee in this case could lead to another preemption. Because we do not know which pod will be preempted, it is best to avoid/minimize propagating preemption decisions.