# Scale to zero design -- 2022-03-24
Our current scale to zero design is centered on the idea of dormancy of Orgs. 
Dormancy in turn is based on the idea of activity. If an organization doesn't
see any activity for a long time then it's marked dormant and scale to zero is
enabled for both the pynode and all the models of that org. As soon as there
is any activity the org is marked active and scale to zero is disabled.
Specific details will likely change over time, but the general design will 
probably stay longer.


# Activity
Activity is any kind of interaction with Baseten. It could be an organization's 
creators logging into Baseten to build their apps, operators interacting with 
views, invocation of worklets or models. We capture a selected set of actions 
and send an activity signal (called warmup signal in code). Such signals 
ultimately update the last_activity_at value for the org.

# Dormancy
Dormancy is assessed based on activity. Currently, an org is considered dormant
if the last activity was more than 24 hrs ago.

# scale_to_zero_allowed
Scale to zero is only done for an app if **scale_to_zero_allowed** flag is set
for it. We keep this flag off for some of the important organizations, such as 
admin and some customers.

# Scale to zero
Scale to zero is applied when org turns dormant and if scale to zero is allowed
on the org. When scale to zero is done, knative scale to zero settings are 
applied to pynodes and all models of that org. As soon as the first activity
happens, reverse of the same settings is applied to disable scale to zero for
both pynode and models of the org.

To disable scale to zero for an org:
```
# Start shell_plus
kubectl exec -it -n baseten $(kubectl get pods -n baseten -l app=celery-worker -o name | awk -F/ '{ print $2 }' | head -n 1) -- poetry run python manage.py shell_plus

[1] org.metadata.scale_to_zero_allowed = False
>>> org.metadata.save()
```

# Mechanics

## Activity handling
Activity is communicated as django signals. There may be a lot of activity so
signal handlers apply rate limits to reduce chatter; in our design we only need
an approximate sense of activity. Any activity updates last_activity_at of the
org. If the org were dormant, then it's immediately marked active and, on this
dormancy switch, actions are taken to disable scale to zero for pynode and models.

## Dormancy detection
A cronjob runs every hour and, for each org, checks for lack of activity in last
24 hours based on last_activity_at. If no activity has taken place then the org
is marked dormant. On this dormancy switch, actions are taken to enable scale to
zero for pynode and models.

## Pynode scale to zero mechanism
Pynodes are knative services. For enabling scale to zero, knative minScale property
is set to zero. This is done by modifying the service, which creates a new revision.
For disabling scale to zero, the minScale setting is set to 1. Scale to zero
settings are pretty aggressive, pynode pod would go away in around a minute of
not receiving any requests.

## Model scale to zero mechanism
Models are kserve entities; kserve internally creates/manages a knative
service, which in turn uses podautoscalers to manage scaling. For models we
directly patch the podautoscalers. TODO(Alex) explain the reasoning for this.

## Pynode Deploy implications
We end up redeploying all pynodes whenever we modify the Baseten specific code in
them. Upon a deploy, pynodes maintain their scale to zero settings. If scale to
zero is enabled then they just come up as usual and stay up. If scale to zero is 
enabled, they come up for a minute and then scale back down if there is no
activity. This means that all pynodes come up during such a deploy, even if they
were scaled to zero. This can create resource spike for a brief period, but 
since pynodes scale back down quickly this isn't expected to be too bad.

## Model deploy implications
(TODO) pankaj: Update this section after implementing application of scale to zero
settings for models on deployment.
