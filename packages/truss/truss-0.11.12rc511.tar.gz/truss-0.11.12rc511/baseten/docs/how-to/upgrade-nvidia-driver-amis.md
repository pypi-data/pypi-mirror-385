# Upgrading NVIDIA Driver AMIs

This document provides instructions on how to use the [amazon-eks-gpu-ami](https://github.com/basetenlabs/amazon-eks-gpu-ami) repository to build a new Amazon Machine Image (AMI) using Packer.

## Steps

1. Clone the [amazon-eks-gpu-ami repo](https://github.com/basetenlabs/amazon-eks-gpu-ami)
2. Authenticate into the production cluster.
3. Ensure that all the values in `gpu.pkrvars.hcl` are what you want them to be
   1. for new workload planes, make sure to bump the k8s version to 1.27 or the approriate version for that workload plane.
4. Initialize packer project using `packer init -upgrade .`
5. Kick off a packer build using `packer build -var-file=gpu.pkrvars.hcl .`
6. Wait for the job to finish. It takes about 45 minutes until the AMI is ready.
7. The image is created in basetensors account (741854743076) in us-west-2 and shared with `arn:aws:organizations::836885557665:organization/o-bxg9i5qp82`


You can now use the AMI ID to modify the aws node template of interest. See the [gpu node template](../../terraform/modules/baseten-backend/karpenter/template-gpu.yaml) for an example.
