# Deploying Baseten

## Deploying staging

Staging is automatically deployed when you update the `master` branch.

Here is the process:

1. Merge to master triggers: [./github/workflows/auto-deploy-staging.yml]
2. This updates the staging branch to point to the same commit as master
3. An update to `staging` branch triggers [.github/workflows/deploy-app-n-infra-staging.yml] which is the deployment build

## Deploying Production

We now use the CDLI to deploy to production:

1. Make sure you have the CDLI tool set up as described in the [CDLI README](/go/cdli/README.md)

2. To deploy the latest version from staging to production, run:
   ```bash
   # For everything under Django group
   ./cdli.sh promote-group django

   # For everything under operator group
   ./cdli.sh promote-group operator
   
   # For the Baseten application (django, frontend, workers)
   ./cdli.sh promote image/baseten/baseten-app
   
   # For the Baseten Helm chart
   ./cdli.sh promote chart/baseten
   ```

3. Alternatively, if you need to deploy a specific version:
   ```bash
   # For the Baseten application
   ./cdli.sh deploy image/baseten/baseten-app [version]
   
   # For the Baseten Helm chart
   ./cdli.sh deploy chart/baseten [version]
   ```
   
4. Review and merge the PR created by the CDLI tool
   1. Wait for tests to pass
   2. Get a review from another engineer
   3. Merge the PR

## Monitoring Deployment
1. Find your deployment in Github Actions [here](https://github.com/basetenlabs/baseten/actions/workflows/deploy-app-n-infra-production.yml)
2. Keep an eye on the [grafana On-Call dashboard](https://grafana.baseten.co/d/VNNj9w2Vz-vm/on-call-dashboard?orgId=1)
3. Monitor the #alerts-production-sentry channel in Slack to identify any new errors that might be popping up.

## Helm charts

Baseten is packaged as a [helm](https://helm.sh/) chart, located in [/helm/charts/baseten](/helm/charts/baseten/). In order to install Baseten on a new cluster, the values in `values.yaml` need to be specified. Then one can execute

```
cd helm
helm install baseten ./baseten -n baseten
```

There are many components to the application, but once installed, the only thing that will change regularly is the docker image that runs the backend.
