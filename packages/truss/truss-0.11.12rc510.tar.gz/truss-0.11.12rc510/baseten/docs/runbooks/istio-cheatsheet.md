# Useful commands

## Hitting envoy admin endpoints
istio-proxy sidecar consists of two processes, pilot-agent and envoy. pilot-agent
communicates with istiod to get the latest configs and passes them onto envoy.
Envoy has a bunch of helpful [admin endpoints](https://www.envoyproxy.io/docs/envoy/latest/operations/admin),
pilot-agent provides access to them. 

To list all available admin endpoints:
```
kubectl exec [podname] -c istio-proxy -- pilot-agent request GET /help
```

## Dump envoy config for a pod with injected istio-proxy sidecar.
```
kubectl exec [podname] -c istio-proxy -- pilot-agent request GET /config_dump
```

## Change istio-proxy logging level
```
kubectl exec [podname] -c istio-proxy -- pilot-agent request POST /logging?level=debug
```

The end point allows [changing logging level of particular logger as well](https://www.envoyproxy.io/docs/envoy/latest/operations/admin#post--logging).

## Spin up a pod with common dns debugging utils
```
kubectl run -it --rm --restart=Never --image=infoblox/dnstools:latest dnstools
```

Avoid spinning up pods in namespaces that touch Baseten in any way. Create a separate namespace and spin up the pod there. 

## dig command to get dns details including ttl
```
dig +ttlid +noall +answer knative-local-gateway.istio-system.svc.cluster.local
```
Would print something like:
```
knative-local-gateway.istio-system.svc.cluster.local. 18 IN A 10.100.75.179
```
The second entry is the ttl remaining. 


