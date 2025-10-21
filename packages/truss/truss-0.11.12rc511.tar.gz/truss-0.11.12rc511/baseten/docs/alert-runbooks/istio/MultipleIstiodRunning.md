# MultipleIstiodRunning

## Meaning

There are currently multiple versions of istiod running, are we currently
upgrading istio?

<details>
<summary>Full context</summary>

This can happen if:
- A bad manipulation was done (eg: running istioctl and installing a new version on the cluster)
- we are running a planned upgraded of istiod

</details>

## Impact

Misbehavior of the service mesh and network communication errors

## Diagnosis

Make sure we are not currently upgrading on purpose

## Mitigation

- Silence this alert if we are really upgrading
- Carefully cleanup the wrong istio version. **This can have critical impact if not done properly. Use caution and make sure you know what you are doing**
