# Long running tasks
 
# Background
Goal of long running tasks is to support user code that takes quite a bit of time, up to a few hours. For such tasks, latency becomes a low priority and reliability becomes a higher priority. This document describes the current implementation which is a compromise. Please refer to this doc for more background and a more solid design:
https://coda.io/d/BaseTen_dnHt_bP59MQ/Async-Broker-Design-Doc_suLtA#_luK0q

The current implementation is based on https://coda.io/d/BaseTen_dnHt_bP59MQ/Async-Broker-in-Django-Design_su_MT#_luoJ_ 

We went with the current design to ship something reasonable quickly. 
This document focuses on the implementation mechanics and alludes to code.


# Design
## High Level
Note that this design only affects the async flow. Async flow can be achieved by invoking a worklet in async manner, either by supplying the async flag in the request or by marking the worklet as async, in which case all invocations are automatically considered async.

In the async flow, Pynodes don't return the result of code execution as a response to the initial request. Instead, they return an acknowlegement and return the execution result in a separte callback to django. In this way, all http requests finish quickly.

## Mechanics
Lets walk through a worklet invocation to look at the mechanics.
When a worklet is invoked in async mode, it creates a worklet run, creates a celery task for worklet execution and quickly returns the worklet run id in response. The celery task executes the worklet invocation code (invoke_worklet_version). It executes nodes in the graph until reaching a python node. Through this execution the async mode flag is available to all nodes in the provided context. The python node recognizes the async flow using the same context flag and executes the async flow.

In the async flow, the python node makes a request to the pynode service's async endpoint. It also creates an instance of AsyncPynodeTask to keep track of this invocation. pynode service puts the request in an in-memory queue and returns an ack that includes uid of the pod that accepted the request. This pod uid is unique in the lifetime of a k8s cluster and uniquely identifies this pod. The python node on the django side takes the uid, puts that into the AsyncPynodeTask, and sets the state to accepted.

In the pynode service, multiple workers read from the in-memory queue. One of the workers ultimately picks up the request and executes it. When done it calls back django with the output. It includes task id in the response as a header. The endpoint it calls back is /worklet_run/{worklet_run_id}/continue. Effectively this continues a suspended worklet run. WorkletRun has all the needed information to continue the execution, such as workflow version, worklet version and the node_version to continue at.

The worklet_run continue endpoint invokes the worklet using invoke_worklet_version but supplies a continuation action, indicating that it's the continuation of an existing worklet. Worlet_run already knows where the execution was suspended, the python node. Execution resumes there. The python node is invoked with the output and env provided by the pynode service. The python node returns a success response and alongise it the supplied output and env as it's own output and env. Rest of the worklet then executes normally, until another python node is encountered. The same flow repeats for every pynode.

Note that the worklet continuation mechanism used here, which was originally created for view nodes, works with nested worklets. So the python nodes in all nested worklets would execute async as well. This makes sense, as otherwise it would be hard to reuse a worklet that can only work async, in another worklet.

## Reque
Since the long running tasks are, well, long running the chances of failure are much higher. eg a pynode may die for many reasons or may get replaced due to deploys. Any of the rpcs in the async flow can fail. It's important to make sure that long running tasks get executed and for this simple retries don't suffice. To retry we run a special cronjob that identifies tasks that look like are lost and retries them.

It retries the following:
1. Any tasks that have been in accepted state for more than ACCEPTED_TASK_CONSIDERED_LOST_PERIOD_MINS mins.
2. Any tasks whose pod (identified by uid) is no longer alive on k8s
3. Any tasks that have been requed in the past but have remained in that state for REQUEUED_TASK_CONSIDERED_LOST_PERIOD_MINS mins. In a good case they would have been accepted by now.
4. Any tasks in failed_retryable state. In these cases the request to send async task to pynode failed.

For (2), the requeue task hits k8s to get the currently running pods to check if the pod uid on the AsyncPynodeTask is among them.

Regarding (4), when the initial request to pynode is made, any errors returned by pynode response explicitly (ie status === 'failed' in the response json) are considered final. All other errors, e.g. errors due to inability to call pynode, or an error status code returned from pynode, are considered retryable.

The reque cron job uses select for update to effectively take a lock, so that no two cronjobs run at the same time. We run these cronjobs every two minutes right now. For whatever reason, if the next cronjob starts up before the previous one is finished then the next job would wait for the previous one to finish due to this lock.
