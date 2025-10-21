# A100 GPU Count Decreased

The number of A100 GPUs on the cluster decreased.

## Impact

The A100s are typically paid upfront. When the GPUs are not available, we are paying for resources that cannot be utilized. Also, the customers who need to serve models on A100s won't be able to acquire the resource and thus we will lose revenues.

## Root cause
We still don't fully understand the root cause. It looks like the node was rebooted for some reason and also worth to note there is a gap in the /var/log/messages file before the node was rebooted.

## Verify Node status
Make sure to run `kubectl get node -l nvidia.com/gpu.product=NVIDIA-A100-SXM4-80GB` and all nodes should report status `Ready`. The alert can be marked as resolved at this point.

## Fix the NotReady status - AWS
You will need to get a shell on the node in order to fix the `NotReady` status.
- Log on https://aws.amazon.com with your credentials and assume the production admin role.
- Goto EC2 -> Instances, find and click on the node
- Click on the `Connect` button on the top right
- Click on the yellow `Connect` button under `Session Manager` tab. You should have a new browser tab with a shell prompt now
- Run `sudo su -` from the shell
- Verify `kubelet` status by running `systemctl status kubectl`
- Start the `kubelet` service if it is not in `active (running)` status by running `systemctl start kubelet`
- If the service cannot be started, check the logs. One problem experienced before was that there was a left over file proventing `containerd` from starting. Delete the `/var/lib/containerd` symlink and run `systemctl start containerd`, then `systemctl start kubelet` fixed the problem.

If kubelet is running and the node still shows `NotReady`, you will have to look at `/var/log/messages` and figure out the root cause.
