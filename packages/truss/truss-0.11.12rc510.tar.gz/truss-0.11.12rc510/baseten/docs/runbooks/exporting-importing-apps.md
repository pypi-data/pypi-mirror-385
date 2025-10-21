# Exporting/importing apps
We have apis for exporting applications and also for importing them back. We also have an explicit api for exporting starter applications.
This is a complex feature, we haven't decided to ship that externally yet, but the same underlying mechanism is used in importing
starter apps and cloning resources.

You can export applications from one environment say prod and import them into another environment say
staging. You can also export and import applications across accounts. 

There are a bunch of caveats, e.g. we don't support exporting models but references to model zoo models
are fine, UDM tables are only created if they don't exist and never updated, and so on. But for the most
part it's very useful for testing, most applications export/import fine.

# How to

## Export a starter application
Hit the export api to download the starter application's resources yaml locally to `backend/workflows/nux/` where all the other exported starter apps live!
```
curl -X POST https://app.baseten.co/internal_export_starter_app/${STARTER_APP_ID} -H "Authorization: Api-Key ${YOUR_API_KEY}" -d '{ "udm_class_typenames": ["Hi"], "query_names": ["another_hi_query", "hi query"] }' > backend/workflows/nux/starter_app_{model zoo name}.yaml
```
Once you specify a `udm_class_typename`, all objects that exist in that table will also be exported over.

## Export any resource
Hit the export api to download application resources yaml locally to `/tmp/app` (or another file of your choice).
You can export from any of: `https://app.baseten.co`, `https://app.staging.baseten.co`, and `http://127.0.0.1:8000`
```
curl -X POST https://app.baseten.co/export_resource/application/${APP_ID} -H "Authorization: Api-Key ${YOUR_API_KEY}" -d '{ "export_dependency_types": ["strong", "weak"] }' > /tmp/app
```

## Import
Import application resources file, the one you stored above at `/tmp/app`
You can import to any of: `https://app.baseten.co`, `https://app.staging.baseten.co`, and `http://127.0.0.1:8000`
```
curl -X POST http://127.0.0.1:8000/import_resource_bundle -H "Authorization: Api-Key ${YOUR_API_KEY}" --data-binary "@/tmp/app"
```

You should see a json message with success field as true. Something like:
```
{"success": true, "imported_resource_ids": [["APPLICATION", "ZBAbw0W"], ["WORKLET", "8qjyvP5"], ["NODE", "v0Vxb8q"], ["NODE", "VBlzydP"], 
["NODE", "XP9WKlB"], ["NODE", "pP8L3rP"], ["NODE", "ZBA4xpq"], ["NODE", "VqK2XdP"], ["NODE", "DBOlGJ0"], ["WORKLET", "MPXZ7Bp"], 
["NODE", "7qQWdD0"], ["NODE", "mP7N8a0"], ["NODE", "rqWV3nP"], ["ORACLE", "VqKzYPo"], ["NODE", "pqvbxbq"], ["NODE", "1BbrpgB"], 
["WORKLET", "eP3awBJ"], ["NODE", "V0NE1xB"], ["WORKLET", "301jOPX"], ["NODE", "rBL1yK0"], ["WORKLET", "oBoWzBd"], ["NODE", "Xq6AkKP"], 
["WORKLET", "yPxRAB2"], ["NODE", "VBno3m0"], ["NODE", "ZBMZxx0"], ["QUERY", "M0kjABb"], ["QUERY", "NBE4Zqa"], ["QUERY", "pBDgAqb"], 
["QUERY", "8qZr6qg"], ["VIEW", "a0z8KqN"], ["QUERY", "nBrR8BD"], ["VIEW", "Rqgd4BV"], ["VIEW", "Q04Xr0d"], ["CODEBASE", "VqKzYPo"], 
["CODEFILE", "yqe9gqL"], ["CODEFILE", "2BYmaBG"], ["CODEFILE", "EqwEb0a"], ["CODEFILE", "b0d94Pn"], ["UDMCLASS", "mP7wOPp"], 
["UDMCLASS", "rqWrxPv"], ["UDMCLASS", "dyqeZBL"], ["UDMCLASS", "pqv9YPl"], ["UDMCLASS", "1BbAkq4"], ["QUERY", "gPG1MB4"], 
["QUERY", "20aj9P6"], ["QUERY", "b0dpE0n"], ["QUERY", "yqeeDqL"], ["QUERY", "2BYr20G"], ["QUERY", "Eqw960a"], ["QUERY", "8qjrEq5"], 
["QUERY", "MPX3Z0p"]]}
```

That's it!

## Contribute to the model zoo

1. Try to [export any resource](#Export-any-resource) and save the output to `backend/workflows/nux/starter_app_{model zoo name}.yaml`; be sure to export the starter app from the same account where the model is hosted (i.e. the prod admin account). That output may include irrelevant UDM elements from that account, which you can safely delete.

2. Make sure that the Oracle in `backend/workflows/nux/starter_app_{model zoo name}.yaml` specifies that it is part of the model zoo, e.g.:
```
---
apiVersion: 1.0.0
metadata:
  id: <model_id>
  name: Wav2vec Speech Transcription
spec:
  '@type': type.googleapis.com/resources.Oracle
  modelPlatformType: MODEL_ZOO
  modelZooModel:
    modelZooName: <model zoo name>
```

3. Add the model to `workflows.nux.services.STARTER_APP_YAMLS`:
```py
STARTER_APP_YAMLS = {
    ...
    "invoice_parser": "starter_app_invoice_parser.yaml",
    "dummy_model": "starter_app_dummy_model.yaml",
}
```
