#calico #networking

# Calico Network Policies

Calico allows us to set fine grained network policies that enforce which network traffic is allowed or denied.

## Description

Our primary use case is to isolate customer workloads from things they shouldn't be able to reach, as well as protecting them from external traffic that shouldn't be able to reach them. Our policies effectively whitelist and blacklist certain traffic, everything that does not match a policy is **by default denied**.

Policies are applied in order (lowest first), so if a policy A with order 100 says X, and policy B with order 200 which has some conflict with A, then A takes precedent. Policies are ultimately enforced via iptables rules.

## Debugging

Currently all denied traffic (and some external traffic) is logged by calico for customer workloads. This allows us to detect threats within the system. It also allows us to debug network denial issues. The Calico logs tail iptables log events, filtering for traffic matching a calico rule. To view all the logs either use grafana or run

```
kubectl logs -l app=calico-logs -n calico-logs --max-log-requests <number greater than the number of nodes> -f
```

A typical log line looks like

```
Apr 19 04:52:19 ip-192-168-74-5 kernel: calico-packet: IN=eth0 OUT=eni8d48114818c MAC=0a:a3:01:06:e0:c5:0a:3d:c7:6e:53:91:08:00 **SRC=192.168.22.247 DST=192.168.94.122** LEN=60 TOS=0x00 PREC=0x00 TTL=253 ID=52641 DF PROTO=TCP SPT=59070 **DPT=8012** WINDOW=62727 RES=0x00 SYN URGP=0
```

In bold above are the source, destination and port. Internal traffic will match something like 192.168.*.* on both source and destination. Any log lines of this type are either **malicous or bugs** caused by poorly configured policies. Match the ip addresses with pods by grepping for them, eg if the ip address is `192.168.22.247` then:

```
kubectl get pods -A -o wide | grep 192.168.22.247
```

This will tell you what pods are involved and help with debugging.


## Panic button

If traffic is failing and cannot be debugged, and it is crucial to get back running immediately, you can write a network policy that will bring you to safety. Ideally write one which you know will solve your particular issue, but the following should get you out of almost any problem involving customer related traffic:

```yaml
apiVersion: projectcalico.org/v3
kind: GlobalNetworkPolicy
metadata:
  name: allow-all
spec:
  namespaceSelector: baseten.co/organization == 'true'
  order: 100
  types:
  - Ingress
  - Egress
  ingress:
  - action: Allow
  egress:
  - action: Allow
```

Dump the above into a file, eg `calico-panic.yaml` and apply it to the cluster directly:

```
kubectl apply -f calico-panic.yaml
```

This will allow all traffic to pass through uninhibited due to the low order of the policy.
