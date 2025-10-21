# Predict internal monitoring

Models can be invoked through the python code in python nodes in worklets. This is a special path 
that's different from other flows such as calling model directly through the external api or
through the model node in worklet. This code path is used by two important use cases, Patreon transcription
and Riffusion. Patreon transcription is by far the most important as it is much larger scale and serves
an important purpose for Patreon. Outage to this path was one of the worst we've seen so far in terms of
customer impact, which goes to show how important this is.

So, whenever we roll out changes that can affect this flow we need to verify that these critical flows don't
break. This page serves to document this testing.

The Patron model in question is available [here](https://app.baseten.co/models/WB5WeRP/versions/w5d6v73). One
should monitor the graphs there.

Please monitor [this beefeater chart](https://grafana.baseten.co/explore?orgId=1&left=%7B%22datasource%22:%22P4169E866C3094E38%22,%22queries%22:%5B%7B%22refId%22:%22A%22,%22expr%22:%22round%28sum%28rate%28http_requests_total%7Bcontainer%3D%5C%22baseten-beefeater%5C%22,%20path%3D%5C%22%2Fmodels%2FWB5WeRP%2Fpredict_internal%5C%22%7D%5B1m%5D%29%29%20by%20%28path%29,%200.001%29%22,%22range%22:true,%22datasource%22:%7B%22type%22:%22prometheus%22,%22uid%22:%22P4169E866C3094E38%22%7D,%22editorMode%22:%22code%22%7D%5D,%22range%22:%7B%22from%22:%22now-1h%22,%22to%22:%22now%22%7D%7D) to make sure these predict_internal requests do not drop.
