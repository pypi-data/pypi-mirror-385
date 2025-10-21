# Alerts & Service-Level Objectives

Monitoring a very large system is challenging for a couple of reasons:

- The sheer number of components being analyzed
- The need to maintain a reasonably low maintenance burden on the engineers responsible for the system

It’s important that decisions about monitoring be made with long-term goals in mind. Every page that happens today distracts a human from improving the system for tomorrow, so there is often a case for taking a short-term hit to availability or performance in order to improve the long-term outlook for the system.

## Indicators SLIs (service level indicators)

An **SLI** is a service level indicator: a carefully defined quantitative measure of some aspect of the level of service that is provided.

eg: 
- Error rate
- Request latency
- System throughput

A **metric** is one kind of indicator. But you can get indicators from **traces** and other measurement tools.

Ideally, the SLI directly measures a service level of interest, but sometimes only a proxy is available because the desired measure may be hard to obtain or interpret. For example, client-side latency is often the more user-relevant metric, but it might only be possible to measure latency at the server.


## Objectives - SLOs (service level objectives)

An SLO is a service level objective: a target value or range of values for a service level that is measured by an SLI.

eg:
- I want the *average request latency* to be *under 100ms*

*The definition of an alert, is one kind of objective.*

Choosing an appropriate SLO is complex. To begin with, you don’t always get to choose its value! For incoming HTTP requests from the outside world to your service, the queries per second (QPS) metric is essentially determined by the desires of your users, and you can’t really set an SLO for that.

On the other hand, you can say that you want the average latency per request to be under 100 milliseconds, and setting such a goal could in turn motivate you to write your frontend with low-latency behaviors of various kinds or to buy certain kinds of low-latency equipment.

### Error budgets

In a nutshell, an [error budget](https://landing.google.com/sre/workbook/chapters/alerting-on-slos/#low-traffic-services-and-error-budget-alerting) is the amount of error that your service can accumulate over a certain period of time before your users start being unhappy. You can think of it as the pain tolerance for your users, but applied to a certain dimension of your service: availability, latency, and so forth.

In order to adopt an error budget-based approach to Site Reliability Engineering, you need to reach a state where the following hold true:

There are SLOs that all stakeholders in the organization have approved as being fit for the product.
The people responsible for ensuring that the service meets its SLO have agreed that it is possible to meet this SLO under normal circumstances.
The organization has committed to using the error budget for decision making and prioritizing. This commitment is formalized in an error budget policy.
There is a process in place for refining the SLO.
Otherwise, you won’t be able to adopt an error budget–based approach to reliability. SLO compliance will simply be another KPI (key performance indicator) or reporting metric, rather than a decision-making tool.

## Alerts

We alert based on some objectives. There are some simple rules to follow when defining alerts:

### Keep a safety margin
  Make sure the threshold gives some leverage for people to have time to fix the problem before it affects customer

### As Simple as Possible, No Simpler

- Alerts on different latency thresholds, at different percentiles, on all kinds of different metrics
- Extra code to detect and expose possible causes
- Associated dashboards for each of these possible causes

The sources of potential complexity are never-ending. Like all software systems, monitoring can become so complex that it’s fragile, complicated to change, and a maintenance burden.

Therefore, design your monitoring system with an eye toward simplicity. In choosing what to monitor, keep the following guidelines in mind:

- The rules that catch real incidents most often should be as simple, predictable, and reliable as possible.
- Signals that are collected, but not exposed in any prebaked dashboard nor used by any alert, are candidates for removal.

## The Four Golden Signals

The four golden signals of monitoring are latency, traffic, errors, and saturation. If you can only measure four metrics of your user-facing system, focus on these four.

### Latency

The time it takes to service a request. It’s important to distinguish between the latency of successful requests and the latency of failed requests. For example, an HTTP 500 error triggered due to loss of connection to a database or other critical backend might be served very quickly; however, as an HTTP 500 error indicates a failed request, factoring 500s into your overall latency might result in misleading calculations. On the other hand, a slow error is even worse than a fast error! Therefore, it’s important to track error latency, as opposed to just filtering out errors.

### Traffic

A measure of how much demand is being placed on your system, measured in a high-level system-specific metric. For a web service, this measurement is usually HTTP requests per second, perhaps broken out by the nature of the requests (e.g., static versus dynamic content). For an audio streaming system, this measurement might focus on network I/O rate or concurrent sessions. For a key-value storage system, this measurement might be transactions and retrievals per second.

### Errors

The rate of requests that fail, either explicitly (e.g., HTTP 500s), implicitly (for example, an HTTP 200 success response, but coupled with the wrong content), or by policy (for example, "If you committed to one-second response times, any request over one second is an error"). Where protocol response codes are insufficient to express all failure conditions, secondary (internal) protocols may be necessary to track partial failure modes. Monitoring these cases can be drastically different: catching HTTP 500s at your load balancer can do a decent job of catching all completely failed requests, while only end-to-end system tests can detect that you’re serving the wrong content.

### Saturation

How "full" your service is. A measure of your system fraction, emphasizing the resources that are most constrained (e.g., in a memory-constrained system, show memory; in an I/O-constrained system, show I/O). Note that many systems degrade in performance before they achieve 100% utilization, so having a utilization target is essential.

In complex systems, saturation can be supplemented with higher-level load measurement: can your service properly handle double the traffic, handle only 10% more traffic, or handle even less traffic than it currently receives? For very simple services that have no parameters that alter the complexity of the request (e.g., "Give me a nonce" or "I need a globally unique monotonic integer") that rarely change configuration, a static value from a load test might be adequate. As discussed in the previous paragraph, however, most services need to use indirect signals like CPU utilization or network bandwidth that have a known upper bound. Latency increases are often a leading indicator of saturation. Measuring your 99th percentile response time over some small window (e.g., one minute) can give a very early signal of saturation.

Finally, saturation is also concerned with predictions of impending saturation, such as "It looks like your database will fill its hard drive in 4 hours."

If you measure all four golden signals and page a human when one signal is problematic (or, in the case of saturation, nearly problematic), your service will be at least decently covered by monitoring.

## How do you create an alert

At baseten we create a `PrometheusRule`, which defines alerts on kubernetes and the prometheus stack.

This section is annotated with `#` comments to allow easy comprehension.

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  labels:
    app: kube-prometheus-stack
    app.kubernetes.io/instance: prometheus-stack
    release: prometheus-stack
  # The name of the Prometheus rule 
  name: celery-flower-prometheus-rules

  # The namespace of the rule, you want that rule to live close to it's metric and
  # to the software defining it.
  namespace: baseten
spec:
  # You can define multiple groups
  groups:
  - name: celery-tasks
    rules:
    # You Can define multiple alerts, here's one example
    # We name our alert `TaskConsumptionRateTooLow`
    - alert: TaskConsumptionRateTooLow
      # Here's the prometheus expression to calculate the alert  
      expr: (sum(increase(flower_events_total{type="task-sent"} [1m])) - sum(increase(flower_events_total{type="task-started"} [1m]))) > 1
      # For how long do you want the expression to be "true" before triggering an alert
      for: 5m
      labels:
        # Severities of the alert
        severity: warning
        context: celery-task
      annotations:
        summary: Task Consumption Rate Too Low.
        description: Number of tasks in the queue is increasing faster than tasks are being executed.
        runbook_url: "https://github.com/basetenlabs/baseten/tree/master/docs/runbooks/celery/TaskConsumptionRateTooLow.md"
```

### Expression
  
path: `spec.groups[*].rules[*].expr`

This is the prometheus formula used to calculate the alert

### For

path: `spec.groups[*].rules[*].for`

For how long does the expression need to be true before triggering an alert

### Severity

path: `spec.groups[*].rules[*].labels.severity:`

Posible values:
- `critical`: an urgent pager
- `error`: a pager
- `warning`: a slack message

### Summary

path: `spec.groups[*].rules[*].labels.annotations.summary`

Summarize the alert in under 80 chars, this is the title in pager and slack

### Description

path: `spec.groups[*].rules[*].labels.annotations.description`

Describe the alert in detail, what is happening

### Runbook Link:

path: `spec.groups[*].rules[*].labels.annotations.runbook_url`

Copy /docs/runbooks/_template.md and create a runbook describing the alert,
what to look for and how to fix it.

### Dashboard Link

path: `spec.groups[*].rules[*].labels.annotations.dashboard_url`

Create a dashboard related to the alert which is gonna help us fix it


## Resources

- [Site reliability engineering - Service level objectives chapter](https://sre.google/sre-book/service-level-objectives/)
- [Alerting on SLOs](https://sre.google/workbook/alerting-on-slos/)
- [Practical Alerting on time series data](https://sre.google/sre-book/practical-alerting/)
- [Prometheus Alerting Rule Documentation](https://prometheus.io/docs/prometheus/latest/configuration/alerting_rules/)
