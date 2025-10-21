# FluxCD
FluxCD is installed in each of the k8s clusters. It monitors changes on different sources, pulls and applies to the cluster when a change is detected.

Grafana dashboards in the [FluxCD](https://grafana.baseten.co/dashboards/f/fds8obkpnbvnkd/fluxcd) can help tracking down the problems.
- [Flux Cluster Stats](https://grafana.baseten.co/d/flux-cluster/flux-cluster-stats?orgId=1&refresh=30s) shows the state of all resources.
- [Flux Control Plane](https://grafana.baseten.co/d/flux-control-plane/flux-control-plane?orgId=1&refresh=10s) shows the state of Flux controllers
- [Flux Logs](https://grafana.baseten.co/d/flux-logs/flux-logs?orgId=1&refresh=10s) can be used to pull the logs

<details cli>
  <summary>Interacting with FluxCD</summary>

  ### CLI
  FluxCD has a CLI `flux` can be installed using `brew install fluxcd/tap/flux`.

  ### Helper
  When FluxCD CLI queries the API, it uses specific versions of the resource so the resource will not show up if the CLI and resource are on different version. To address this problem, `flxenv` is recommended to manage the CLI. `flxenv` can be installed using `pip install flxenv`. More details [here](https://github.com/nachrivcost/flxenv)

  ### Connect to API
  Switch kubectl context to the targeted cluster, `flux` works just like `kubectl` that talks to the k8s API.
</details>

<details>
  <summary>FluxCDResourceNotReady</summary>

  This means the mentioned resource has been in a non ready state for a period of time. This error typically is caused by errors introduced in the code.

  `flux -n <namespace> get <customresource_kind> <name>` shows the message of the failure.
</details>

<details>
  <summary>FluxCDResourceSuspended</summary>

  Because FluxCD reconciles all the resources on a configured interval, it is often needed to suspend the reconciliation when debugging/troubleshooting. The resource reconciliation should be resumed after the session.

  Run `flux -n <namespace> resume <customresource_kind> <name>` to resume the reconciliation
</details>
