# PynodeHigh4xxErrorRate

## Meaning

pynode is returning too many 4xx responses to requests.

<details>
<summary>Full context</summary>

pynode is only called through Django, so this clearly indicates a
misconfiguration where django is hitting a missing endpoint on pynode. This
should be quickly corrected.

</details>

## Impact

High. It means that Django is hitting a missing endpoint on pynode. This is most
likely user facing. Users' worklet invocations or query invocations may be
failing.

## Diagnosis

Look at pynode logs to check what paths django is trying to hit that are causing these 404s. 

## Mitigation

If this is deploy related then revert the deploy immeditely. If revert is not
possible or easy then quickly deploy django and celery with a fix, correcting the
pynode path being hit.
