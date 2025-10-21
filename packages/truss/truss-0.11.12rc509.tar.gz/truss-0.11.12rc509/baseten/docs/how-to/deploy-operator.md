# How to deploy operator

## Operator overview

Operator is a Gateway service to our workload planes. Django in the control
plane cluster talks to Operator to deploy models and few other control plane
activities. Operator is a Python FastApi based service. 

## How to deploy

- Make changes to the Operator code as usual and get it into baseten master
  branch.
- Deploy Baseten

## Post deployment verification

There are few ways to check the deployments

### Slack
- Staging deployment will post messages to cd-staging channel
- Production deployment will post messages to cd-production  channel

### Kubectl
- Verify pods are restarted,  and the tag should be the commit sha from the merge
  `kubectl -n baseten get  pods -l app=baseten-wp-operator`
  `kubectl -n baseten get deploy baseten-wp-operator -o jsonpath='{.spec.template.spec.containers[0].image}' && echo`
- Verify Flux reconcile is done. 
  `kubectl -n baseten describe helmrelease baseten-wp-operator`

### How to test one-off on dev
You will need to build the image using whatever means.
`kubectl edit deploy baseten-wp-operator` and find/replace the image tag then save.   
