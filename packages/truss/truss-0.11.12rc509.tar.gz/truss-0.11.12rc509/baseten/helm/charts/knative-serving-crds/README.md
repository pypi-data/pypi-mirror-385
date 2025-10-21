Knative Serving CRDs
=====================

This helm chart contains knative serving custom resource definitions. The reason this is not included 
with the knative chart is to allow upgrading the CRDs. Helm by default doesn't upgrade the CRDs if they
are in the crds folder. This way we can upgrade the CRDs and knative serving without downtime and we can
control the order.
