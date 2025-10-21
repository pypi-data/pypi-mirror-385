# Model scale to zero turned off

## Notes for when we want to enable model scale to zero again
We turned off model scale to zero on Production on 20220401. This document goes
into the reasons for doing this and leave some context for when we need to turn
it back on.


## Post-mortem of user issue that ultimately caused us to turn off model scale to zero
### What happened
A user complained about all requests to their model failing for a few hours.

### Whys

#### Why did the requests fail?
User's model had been scaled to zero. Even on requests it didn't come back up.

#### Why was model scaled to zero?
At that point we didn't have warm up signals on directly invoking model through
django. It was planned to be done in a follow up. This was not considered a
blocker for the roll out because:
- It was thought not to be a common case. I (Pankaj) mistakenly thought that
  most folks will call the model via a worklet.
- The model is expected to come up on demand on requests. This is one of the
  main features of knative, there's so much machinery around it.

#### Why didn't the model come up on requests?
We don't know this for sure. It could be due to the way we're doing scale to
zero for models, which is by directly modifying the podautoscaler created by
knative, rather than specifying the settings at Knative service level, like we
do for pynodes. It was considered safe because the mechanism worked well in
local testing and staging testing. This testing was limited though, where we
scaled the service down and back up in quick succession. It may not catch issues
where the service has been scaled down to zero for a long time. 


#### Why didn't we catch the issue ourselves? Why didn't we know about it immeditely?
This needs to be looked into, but clearly we either didn't have the right alerts
in place or the alerts did not catch this particular issue.

## Current state
Model scale to zero has been disabled in Production through the waffle flag:
MODEL_SCALE_TO_ZERO_ALLOW_FLAG
All existing models that were scaled to zero have been bought back up.


## Mitigations
- We have a warmup signal in place for when model is invoked directly (without a
worklet). This would make sure that model scale to zero would be disabled on the
first request. If the issue -- existing model not coming up on request when
scale to zero is enabled -- happens again, then there's a possibility that the
first request would fail, but retries should likely work. The warm up signal also
makes sure that for the previous scenario model would not be scaled to zero.
- Model scale to zero is disabled


## Things to check before enabling model scale to zero
- More thorough testing of first request on a model that's scaled to zero.
- Make sure there are alerts in place for any model call failues due to no model
pods being available.
- It should be enabled by someone keenly familiar with all the model invocation
  paths.
- Another concern with enabling model scale to zero has been around potential
  variability in startup times for models as compared to pynodes. We analyzed
  and found that of the existing models only the HuggingFace models were taking
  very long to come back up. We didn't expect it to be common for users to
  deploy HuggingFace models directly. Even a model that's more than a GB in size
  comes back up within a minute unless it had to download a lot of stuff on
  startup. e.g. pynode itself is 1.3 GB in size and comes back up in around a
  min. When we enable model scale to zero again we should double check that
  model startup times continue to be under a minute for most cases.
