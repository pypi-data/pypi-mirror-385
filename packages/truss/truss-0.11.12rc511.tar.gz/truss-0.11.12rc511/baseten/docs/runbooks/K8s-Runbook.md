# K8s Runbook

## Aliases

We have a number of common aliases and functions that are useful for interacting with k8s clusters. These are defined in [bin/baseten_aliases.sh](../../bin/baseten_aliases.sh) and can be installed to your user profile via [bin/install_aliases.sh](../../bin/install_aliases.sh).

## Namespaces

```sh
# get a single organization namespace
kubectl get ns -l organization.baseten.co=baseten -o yaml
# get organization namespaces
kubectl get ns -l organization.baseten.co
# get stuff in a single namespace
kubectl get isvc,pods -n org-gpqvbql
```

<a href="https://www.loom.com/share/e3692bcd02bd4a6895d13247cc0e745a">
    <p>Namespaces split quick tour - Watch Video</p>
    <img style="max-width:300px;" src="https://cdn.loom.com/sessions/thumbnails/e3692bcd02bd4a6895d13247cc0e745a-with-play.gif">
  </a>

## Port-forwarding a k8s-service to your local computer

In order to communicate with an application running on a port in a resource within some cluster from your local machine, you can port-forward:

```sh
kubectl port-forward <podname> <your-port>:<pod-port>
# or
kubectl port-forward svc/<svc-name> <your-port>:<svc-port>
```

If you want to connect to a service/replicaset/deployment you can do so

```sh
kubectl port-forward svc/<servicename> <your-port>:<svc-port>
```

### Flower

```sh
kubectl port-forward svc/flower-service 5555:5555
```

### Prometheus

To connect to victoriametrics to run queries:

```sh
kubectl port-forward svc/vmselect-vmcluster -n monitoring 8481 &
```

Then you should be able to query the Victoria Metrics server from localhost:

```sh
 curl "http://127.0.0.1:8481/select/1/prometheus/api/v1/query?query=up"
# Results in: {"status":"success","data":{"resultType":"vector","result":[{"met....
```
