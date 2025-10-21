# BasetenDjangoHigh4xxErrorRate

## Meaning

This alert indicates that Baseten django app is returning 4xx http error codes,
that indicate client errors. This could be an issue in Baseten frontend.

<details>
<summary>Full context</summary>

While this errors don't necessarily mean that there is something wrong with the
Django app, they may indicate an issue in the Baseten frontend or in the way an
important client is hitting baseten via API, e.g. to invoke models or worklets.

</details>

## Impact

Depending on the error code it may have veriety of impacts. e.g. 404s might mean
certain frontend functionality is broken.

## Diagnosis

One should further look into which 4xx error code has spiked and try to see if
change correlates with an event such as a deploy.

## Mitigation

If it's deploy related then reverting the deploy may be an option. If revert is
not easy then a fix in the frontend may be needed. If it's a bad client then we
could communicate to them the right way of hitting our API.
