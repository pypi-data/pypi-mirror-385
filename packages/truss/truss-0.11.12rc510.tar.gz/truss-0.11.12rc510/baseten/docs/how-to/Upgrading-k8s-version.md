# Upgrading K8s

1. Upgrade the eks cluster version in the terraform files. And deploy the terraform. This will update the cluster control plane.
2. Upgrade the nodes. In the AWS console, go into the EKS cluster, select compute and you will see the node groups, you need to click "upgrade now" on the node groups. Some nodes won't upgrade, they are often nodes with only daemonsets remaining (aka they can be killed without downtime). Monitor the upgrade and make sure it goes through.

> Monitor the upgrade and make sure it goes through.

That means: Make sure all the nodes rotate, if they don't validate that they don't have a critical workload. If only daemonsets are running on it, or workloads which have redundancy, you can kill the node. 

In parallel of step 2, you can upgrade: 

- Manually upgrade coredns
  Find the new imagename matching the cluster version here: https://docs.aws.amazon.com/eks/latest/userguide/managing-coredns.html

  To update `kubectl edit deploy -n kube-system coredns`

- Manually upgrade kube-proxy
  Find the new imagename matching the cluster version here: https://docs.aws.amazon.com/eks/latest/userguide/managing-kube-proxy.html

  To update `kubectl edit ds -n kube-system kube-proxy`
