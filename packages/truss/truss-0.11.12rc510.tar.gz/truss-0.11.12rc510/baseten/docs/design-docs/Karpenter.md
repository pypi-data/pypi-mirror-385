# Karpenter controller

## Intro

Karpenter is a Kubernetes controller that takes care of EC2 instances provisioning.

From [Karpenter website](https://karpenter.sh/):

> Karpenter automatically launches just the right compute resources to handle
> your cluster's applications. It is designed to let you take full advantage of
> the cloud with fast and simple compute provisioning for Kubernetes clusters.

## How to use it

The main goal is to let Karpenter chose the best node configuration for
resources defined in a Kubernetes deployment. We still need to give it general
rules of what we want. Those rules are defined a *Provisioner* manifest. There
is 3 types of provisioners configured:

- memory: for memory optimized nodes
- cpu: for CPU optimized nodes
- gpu: for GPU optimized nodes

To specify the provisioner that we want we use the *nodeSelector* or an
affinity rule. Here an example of a *Deployment* using a *nodeSelector* using
the GPU provisioner:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: dep-test
  namespace: default
spec:
  replicas: 1
  selector:
    matchLabels:
      app.kubernetes.io/instance: dep-test
      app.kubernetes.io/name: dep-test
  template:
    metadata:
      labels:
        app.kubernetes.io/instance: dep-test
        app.kubernetes.io/name: dep-test
    spec:
      nodeSelector:
        "baseten.co/karpenter-provisioner": gpu
      containers:
        - name: nginx
          image: nginx
          ports:
            - containerPort: 80
          volumeMounts:
            - name: workdir
              mountPath: /usr/share/nginx/html
          resources:
            limits:
              memory: '1Gi'
              cpu: '800m'
              nvidia.com/gpu: "1"
            requests:
              memory: '100Mi'
              cpu: '100m'
              nvidia.com/gpu: "1"
```

If for whatever reason a specific node type must be provisioned the label
*node.kubernetes.io/instance-type* can be used. This will force Karpenter to
provision this type of node for the workload. For example:

```yaml
      ...
      nodeSelector:
        "baseten.co/karpenter-provisioner": gpu
        "node.kubernetes.io/instance-type": g5.xlarge
      ...
```

It really important to configure resource requests for each workload to
explicitly tell Karpenter how to best provisioned each nodes. Specifying
*nvidia.com/gpu* if also very important because Karpenter is going to use the
right AMI with GPU support when this resource request/limit is set.

When using the *gpu* provisioner we also need to configure the *toleration*.
Here example of what it looks like:

```yaml
      ...
      tolerations:
      - key: nvidia.com/gpu
        operator: Exists
        effect: NoSchedule
      ...
```

## How it works

Karpenter help provision dynamically nodes into a cluster. One important aspect
of this is that essential services in particular Karpenter must run on a node
group outside of Karpenter.

### Scheduling

Karpenter monitors the cluster for unschedulable pods. When Kerpenter find
unschedulable pods it checks the pod/deployment definition for values like
resource requests, replicas, hpa, topology spread, affinity/anti-affinity rules
to determine how much resources is needed. It will try it's best to schedule
pods onto existing nodes that have enough resources left to run the workload.
If new nodes are needed it will check the *Provisioners* defined in the
cluster. Those *Provisioners* are rule to help Karpenter decides whitch type of
nodes are the best fit for the resources needed.

Karpenter needs to run alongside the cluster autoscaler and don't touch nodes
that don't belongs to itself. It's important that the *nodeSelector* chosen to
select a *Provisioner* are not the same as those used by the defined cluster
node groups.

### Deprovisoning

Node deprovisioning occurs after the configured delay in each provisioners. For
this to happen the node must not run any workload that are not daemonsets. An
annotation is added to the node to track this delay. If no workload occurs
after that delay the node is deprovisoned.

## provisioners

The [*Provisioner*](https://karpenter.sh/v0.19.3/provisioner/) resource is how Karpenter knows what type of nodes it needs
to provision when new pods must be scheduled. Currently we have 3 provisioners.
Provisioner definitions must be exclusive. That's why the label
*baseten.co/karpenter-provisioner* is used. This label insure that it's unique
and help drive the right type of node to use.

For each provisioner a AWS template is defined. The manifest used is
*awsnodetemplate*. This manifest controls the type and and size of disks
required to launch the instance, the AMI template to use, the AMI type and
more. See the
[doc](https://karpenter.sh/v0.19.3/aws/provisioning/#awsnodetemplate) for more
details if needed.

### CPU

The CPU provisioner will chose the best fit for the resources specified in the
workload. It's geared towards instance types that are optimized for CPU usage.
Please see the
[manifest](../../terraform/modules/baseten-backend/karpenter/provisioner-cpu.yaml)
for node types that can be provisionned by this provisioner.

### memory

The memory provisioner will chose the best fit for the resources specified in
the workload. It's geared towards instance types that are optimized for memory
usage. Please see the
[manifest](../../terraform/modules/baseten-backend/karpenter/provisioner-memory.yaml)
for node types that can be provisionned by this provisioner.

### GPU

The GPU provisioner will chose the best fit for the resources specified in
the workload. It's geared towards instance types that are optimized for GPU
usage. Please see the
[manifest](../../terraform/modules/baseten-backend/karpenter/provisioner-gpu.yaml)
for node types that can be provisionned by this provisioner.

At the moment specifying request limits for GPU usage is quite limited. We can
specify the number of GPU we want but not the memory. We me have to add
specific Karpenter provisioners to be able to better choose instance types.

To specify a specific node type the *nodeSelector*
*node.kubernetes.io/instance-type* can be added alongside the
*baseten.co/karpenter-provisioner* label like this:

```yaml
      ...
      nodeSelector:
        "baseten.co/karpenter-provisioner": gpu
        "node.kubernetes.io/instance-type": g5.xlarge
      ...
```


## Debugging

To output nodes provisionned with Karpenter with their instance type and capacity
(spot, "on-demand"):

```bash
kubectl get nodes --label-columns node.kubernetes.io/instance-type,karpenter.sh/capacity-type -l karpenter.sh/provisioner-name
```

