# Celery Queues we use

We have three celery queues as of this writing.
1. default (actually called 'celery' in the code)
1. build
1. deploy-build


# Default queue
The default queue is used for short lived tasks. We expect a very large number of tasks and a high throughput.

This mostly means all tasks that don't involve building a docker image. They involve
user facing and non user facing actions. 

Example tasks:
- Collecting udm metrics (non user facing)
- Logging worklet run (user facing, low priority)
- Deploying a model (user facing, high priority)

We want execution on this queue to be very quick, with a minimal delay.

## Scaling:

Since we expect a high number of tasks, and want to keep a high throughput and
 low delay. We set scaling to have a quick reactivity and scale to high numbers. 
 
We keep a small number of minimum workers but that's because we expect a 
small number to be more than sufficient due to the short lived nature of tasks. 
Scale up quickly doesn't mean that we scale up at a very small number of tasks,
the tasks are pretty short lived here. It means we scale up at a number of tasks
that would ordinarily take only single digit seconds to execute.


# Build queue
The build queue is used for long running tasks that involve user facing docker image building. We expect a low number of tasks that get executed with a minimal delay.

Example tasks:
- Upding pynode requirements, python or system
- Warmup resulting in pynode deploy to disable scale to zero

## Scaling

These tasks are quite infrequent but since they are user facing we want them to
be picked up quickly. We also scale up to high number if needed. We keep a large
minimum number of workers and we also scale up quickly.

# Deploy build queue
The "deploy build" queue is Baseten deploy tasks, tasks initiated by us and not the user.
These tasks are not user facing, so we have a lot of flexibility and can optimize for cost. 

Example tasks:
- Baseten deploy involving code change in pynode (eg: baseten_internal code change)
- Deploys related to orgs being marked dormant and thus scaled to zero

## Scaling

We want to control the pynode rollout to avoid resource usage spikes due to 
zero scaled pynodes coming up for a short time during deploys.

For this queue we go with being scaled to zero by default and going only up to a
small number of workers.

