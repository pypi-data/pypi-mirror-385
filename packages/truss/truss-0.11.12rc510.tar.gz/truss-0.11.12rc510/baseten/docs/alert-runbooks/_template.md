# NodeFilesystemSpaceFillingUp

## Meaning

This alert is based on an extrapolation of the space used in a file system. It fires if both the current usage is above a certain threshold _and_ the extrapolation predicts to run out of space in a certain time. This is a warning-level alert if that time is less than 24h. It's a critical alert if that time is less than 4h.

<details>
<summary>Full context</summary>

Here is where you can optionally describe some more details about the alert. The "meaning" is the short version for an on-call engineer to quickly read through. The "details" are for learning about the bigger picture or the finer details.

> NOTE: The blank lines above and below the text inside this `<details>` tag are [required to use markdown inside of html tags][1]

</details>

## Impact

A filesystem running completely full is obviously very bad for any process in need to write to the filesystem. But even before a filesystem runs completely full, performance is usually degrading.

## Diagnosis

Study the recent trends of filesystem usage on a dashboard. Sometimes a periodic pattern of writing and cleaning up can trick the linear prediction into a false alert.

Use the usual OS tools to investigate what directories are the worst and/or recent offenders.

Is this some irregular condition, e.g. a process fails to clean up behind itself, or is this organic growth?

## Mitigation

<Insert site specific measures, for example to grow a persistent volume.>


[1]: https://github.github.com/gfm/#html-block
