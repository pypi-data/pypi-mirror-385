# Debugging loki performance

## Loki is slow to query

Loki queries timeout after 30 seconds, which generally is enough time for the queries in baseten to return a result. If loki is slow to query, it is likely that the loki instance is overloaded in some way. It has been observed that intermittently poor performing queries correlate with [high memory load](https://grafana.baseten.co/d/a164a7f0339f99e89cea5cb47e9be617/kubernetes-compute-resources-workload?orgId=1&var-datasource=default&var-cluster=&var-namespace=logging&var-type=statefulset&var-workload=loki-gateway&from=now-1h&to=now&refresh=10s) on one of the loki-read pods in the loki-read statefulset. If this is the case, the loki-read pod should be restarted to clear the memory load.

