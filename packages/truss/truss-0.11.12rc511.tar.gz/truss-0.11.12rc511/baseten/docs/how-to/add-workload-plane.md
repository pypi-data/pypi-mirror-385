# How to add a new workload plane

Use shell_plus into the appropriate environment and execute something like this:

```py
baseten_user = User.objects.filter(is_canonical_baseten_user=True).last()
org = baseten_user.organization
platform = WorkloadPlane.CloudPlatform.AWS.value
WorkloadPlane.objects.create(
  name='us-west-2-prod-1',
  endpoint='https://us-west-2-prod-1-op-9v5e4zaj1n.baseten.co',
  loki_endpoint='https://us-west-2-prod-1-loki-vjfsqgpbth.baseten.co',
  vm_endpoint='https://us-west-2-prod-1-vmselect-fy07i26e7d.baseten.co/select/0/prometheus',
  region='us-west-2',
  platform=platform,
  owner=org,
)
```

Make sure to use the right values for the WP in the snippet above.

There's also a constance and django command based mechanism but in practice shell_plus seems much
simpler, so let's use that. We'll streamline this due time.
