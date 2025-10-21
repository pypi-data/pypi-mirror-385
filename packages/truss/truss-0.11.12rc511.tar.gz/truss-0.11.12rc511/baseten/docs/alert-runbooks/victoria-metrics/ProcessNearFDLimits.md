# ProcessNearFDLimits

## Meaning

Exhausting OS file descriptors limit can cause severe degradation of the process. Consider to increase the limit as fast as possible

<details>
<summary>Full context</summary>

VM pods all have unlimited FD configured. This really should not happen.

</details>

## Impact

When there is no file descriptor can be used, nothing would work on the affected container.

## Diagnosis
Log on to the pod and check output of `ulimit -a`

## Mitigation

Try to restart the affected component. Make sure only restart the affected Deployment or StatefulSet
```kubectl -n monitoring get deployment
kubectl -n monitoring rollout restart deploy <deployment-name-from-above>

kubectl -n monitoring get sts
kubectl -n monitoring rollout restart sts <statefulset-name-from-above>
```
