# Investigating inference issues

This runbook list common places and components to look at when a user is reporting an inference issue.

### 1- Gather the required information
You need the following:
- model id
- model version id
- namespace
- workload plane where the model is running.

All this information can be found in billip. I strongly recommend using the `cmd+k` navigation to find the information

### 2- Check the #alert-production and #alert-production-sentry channels
Look for any alerts and errors that could guide you to the issues. Some alerts to look for are:
- Crashloop alerts on pods in the `istio-ingress`, `knative-serving`, `beefeater` and `baseten` namespaces
- High percentage of 4xx and 5xx in `Django` or `Beefeater`
- Authentication sentries

This list is no exhaustive. Other alerts and sentries could lead to the issues.

### 3- Check the state of the `cluster-local-gateway` pods in the `istio-ingress` namespace
Make sure that:
- pods are running and haven't restarted or started recently
```
kubectl get pods -n istio-ingress -o wide

# if pods are not in a healthy state
kubectl describe pod [pod name] -n istio-ingress
```

### 4- Check the state of the `knative-serving` namespace's pods
The `activator` pods are on the inference path. It's the one you'll want to make sure is healthy. Make sure that:
- pods are running and haven't restarted or started recently
```
kubectl get pods -n knative-serving -o wide

# if pods are not in a healthy state
kubectl describe pod [pod name] -n knative-serving
```

### 5- Check the state of the `beefeater` pods
Make sure that:
- pods are running and haven't restarted or started recently
```
kubectl get pods -n beefeater -o wide

# if pods are not in a healthy state
kubectl describe pod [pod name] -n beefeater
```
**Beefeather health dashboard**: https://grafana.baseten.co/d/b996cd32-740c-4a18-82ef-f6649a8a492c/beefeater-dashboard?orgId=1. Make sure to select the data source corresponding to the workload plane you are investigating

Logs for beefeater are available in grafana. For example, to see the error logs in beefeater: https://grafana.baseten.co/goto/WzOpJZPSg?orgId=1


### 6- Check the health of the model pods
If all above seems healthy, it might be an issue with the single model. Check the pods in the org's namespace:
```
kubectl get pods -n [org namespace] -o wide
```
You can also check this dashboard in Grafana for a particular model's health: https://grafana.baseten.co/d/a8dbbf05-1590-441f-994c-2905d18311b2/customer-models-overview-v2?orgId=1. Look for:
- Increase in traffic
- Increase in response time
- Increase in error rate

For example, and increase in traffic coupled with a plateau of number of replica could mean that the model can't handle the traffic it is getting with its current `max_replica` value.
