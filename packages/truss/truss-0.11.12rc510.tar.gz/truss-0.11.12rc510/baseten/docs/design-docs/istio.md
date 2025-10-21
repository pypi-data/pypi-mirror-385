# Istio

[Istio](https://istio.io/) extends Kubernetes to establish a programmable, application-aware network using the powerful Envoy service proxy. Working with both Kubernetes and traditional workloads, Istio brings standard, universal traffic management, telemetry, and security to complex deployments.

We use istio for:
- Knative networking
- General service mesh and network management
- Some security
- Open telemetry

## Installation

Istio is installed through multiple helm releases:

- Istio base (CRDs, service accounts)
- Istiod (a single instance)
- Istio-cni (the cni daemonset plugin which istiod connects to)
- Gateway (ingress and egress controller)
  - ingress-gateway
  - cluster-local-gateway

## Revision and tags

Hierarchy:

`Tag -> Revision -> istiod instance`

How to apply:

Set a label: `istio.io/rev = (tag|revision)` on (priority highest to lowest):


- Workload (pod)
- Service account
- Namespace

If not set then the `default` tag is gonna be used if the resources have the label istio-injection=enabled

## Upgrading Istio

1. Upgrade istiod and set a new revision matching the version (eg `version=1.11.4` -> `revision=1-11-4` assing a tag that also matches this revision, eg: `revisionTags: ["canary"]`
2. Deploy the new resources and ensure istio is running, and the `MutatingWebhookConfiguration` and `ValidatingWebhookConfiguration` are up
3. Assign some workloads (by changing the label) and validate they are working correctly
4. If all is working properly, assing `revisionTags: ["default"]` to the new istiod
5. Deploy
6. Slowly rotate workloads to use the new "default"
