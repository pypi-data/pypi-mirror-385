# Cluster Ops Runbook

## Common Tasks
#### Scale cluster
There are two parts to scaling the cluster.
1. Increase number of replicas for appropriate service
2. Provide resources for the new replicas

To determine existing cluster nodes:
```
kubectl get nodes
```

The following script can be used to do both. Currently it only supports increasing number of django and celery worker replicas but more will be added.
```
# From baseten repo git root in poetry shell
python scripts/scale_k8s_cluster.py --cluster=[] --nodes-count=[] --django-replicas=[] --celery-replicas=[]

# e.g.
python scripts/scale_k8s_cluster.py --cluster=demov2 --nodes-count=4 --django-replicas=2 --celery-replicas=2
```
Node counts and replica counts can be increase individually as well.
```
# Increase node count only
python scripts/scale_k8s_cluster.py --cluster=demov2 --nodes-count=4

# Increase django replica count only
# Increase node count only
python scripts/scale_k8s_cluster.py --cluster=demov2 --django-replicas=2
```
More help available with --help option.

#### Access helm values
```helm get values baseten -n baseten```

To include secrets:
```helm get values baseten -n baseten -a```

#### Update a helm value
```
helm upgrade baseten ./helm/baseten -n baseten --reuse-values --set key=value
```

#### View pods with nodes they're running on
`kubectl get pod -o=custom-columns=NAME:.metadata.name,STATUS:.status.phase,NODE:.spec.nodeName`

#### View deployments with actual pods
As we deploy pynode services using knative we end up with lots of deployments, most of which are for old releases and have no pods. This command makes it easy to view the deployments we care about ie the ones with deployed pods.

```kubectl get deployments --sort-by='spec.replicas'```

#### Get names of ips hitting baseten the most
Run [this query](https://us-west-2.console.aws.amazon.com/athena/home?force&region=us-west-2#query/history/86630eef-3b70-464c-9753-508f4c1ada32) on athena to get the ip addresses with most requests in past hour.

Note that if you're using it the first time you will need to set an s3 bucket for the output location. Feel free to use this bucket:
`baseten-athena-query-results`.

#### Get pod resource requests
```
kubectl get pods -o=jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[0].resources.requests}{"\n"}{end}'
```
This only gets resource requests for the first container, which is usually the one that is ours, others are usually the auto-injected sidecars.

#### Commands useful for debugging resource allocation
##### Get resource requests on pods.
```
kgp -o jsonpath='{range .items[*]}{.spec.nodeName}{"\t"}{.metadata.name}{"\t"}{range .spec.containers[*]}{.name}{":"}{.resources.requests}{"\t"}{end}{"\n"}{end}' | column -t | sort
```
##### Get resources available on nodes
Add this to your .bash_profile
```
function kgnr {
  local CPU="CPU:status.allocatable.cpu"
  local MEMORY="MEMORY:status.allocatable.memory"
  local GPU="GPU:status.allocatable.nvidia\.com/gpu"
  local NAME="NAME:metadata.name"
  local NODEGROUP_NAME="NodeName:.metadata.labels.alpha\.eksctl\.io/nodegroup-name"
  kubectl get nodes -o custom-columns="$NAME,$CPU,$MEMORY,$GPU,$NODEGROUP_NAME"
}
```
Then call `kgnr`.

It also provides the nodegroup a node belongs to which can be handy when trying to scale the cluster manually.

#### RDS error logs

List error logs from cli
```
aws rds describe-db-log-files --db-instance-identifier baseten-db-demov2 | jq '.DescribeDBLogFiles[] .LogFileName'
```

Download them from the log file names above
```
for f in `cat file_with_output_of_above`; do aws rds download-db-log-file-portion --db-instance-identifier baseten-db-demov2 --starting-token 0 --output text --log-file-name $f >> error.log; done
```
