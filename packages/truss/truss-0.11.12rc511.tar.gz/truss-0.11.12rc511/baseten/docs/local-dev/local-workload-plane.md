# Running a separate workload plane locally

## Create the cluster

This is an **experimental** dev setup. It allows you to create a secondary minikube cluster that runs the workload plane. This is useful for testing scenarios that require multiple workload planes, like the migration of an oracle between workload planes.

Prerequisite

- Install `istioctl`. See [documentation](https://istio.io/latest/docs/setup/additional-setup/download-istio-release/) for instructions

Start by running:

```sh
./local_workload_plane_setup
```

This will create a cluster named "baseten-local-wp". To modify your shell to use the new cluster, run:

```
export KUBECONFIG=~/.kube/local-wp.config
minikube update-context -p baseten-local-wp
minikube profile baseten-local-wp
```

Then, if you run:

```sh
kubectl get pods -A
```

You should see a fairly empty cluster, without postgres or tekton. To reuse this configuration and access `baseten-local-wp` for separate shells, just run `export KUBECONFIG=~/.kube/local-wp.config`.

## Start the operator

Start django, webpack and the operator as you would normally, making sure you have the default `baseten-local` kube context in the respective shells. Then inside a shell with `baseten-local-wp`, start another operator on port 9001:

```sh
poetry run python core/server.py --reload --port 9001
```

## Set up the WorkloadPlane in Django

Get minikube IP:

```sh
minikube ip -p baseten-local-wp
```

Get istio ingress port:

```sh
kubectl -n istio-system get service istio-ingressgateway -o 'jsonpath={.spec.ports[?(@.name=="http2")].nodePort}'
```

Add workload plane to Django here: http://localhost:8000/billip/oracles/workloadplane/add/

- **Name:** baseten-local-wp
- **Endpoint:** http://localhost:9001
- **Loki endpoint:** `http://<MINIKUBE_IP>:<ISTIO_PORT>` based on minikube ip and istio ingress port found above
- **Region:** local
- **Platform:** CLUSTER_LOCAL

## Beefeater inference request proxying

If models are deployed to the `baseten-local-wp` workload plane, you will need a beefeater running for that workload plane.

```
# Make sure minikube and kubectl are using the right profile and context in your shell
minikube profile baseten-local-wp
k config use-context baseten-local-wp

# Start a second beefeater
cd go/beefeater && make run-cs-wp2
```

This will inference requests sent to `localhost:9090` (the beefeater started by `run_everything.sh`) to proxy requests to the second beefeater and reach models on deployed on the `baseten-local-wp` workload plane.

## Copy built model image

One of the big issues is that model build images are pushed to the control plane's container registry, which isn't connected to the separate WP's registry. To get around this, first build a model like you would normally. Get the image ref, a long hexadecimal string, from the build logs. It's the first sha, not the one preceeded by `@sha256:`.

Open port forwarding to each cluster's registry, making sure each shell has the correct kube context:

```sh
# baseten-local
k port-forward -n kube-system svc/registry 1111:80
# baseten-local-wp
k port-forward -n kube-system svc/registry 1112:80
```

Install [oras](https://oras.land/docs/installation) - a tool for working across OCI registries.

Use the copy command to copy the image from the CP to the WP:

```sh
oras cp \
  "localhost:1111/baseten/baseten-custom-model:<image_ref>" \
  "localhost:1112/baseten/baseten-custom-model:<image_ref>" \
  --from-plain-http \
  --to-plain-http
```

Then you can deploy the model in the new WP.

## On starting codespace

```
minikube start -p baseten-local-wp --keep-context
```
