# Baseten REST API
**🚧This feature is still under development! Direct questions to #core-product in slack 🚧**

This document aligns how we've implemented REST API endpoints for certain Baseten management actions (ex. creating a secret).

## Architecture 
At a high level, our REST API takes on the following structure:

![image](https://github.com/basetenlabs/baseten/assets/20553087/272e6eda-0602-4de9-bdda-20b3d4101ad4)

## How to create a REST API endpoint
Create a directory in `backend/rest_api` with a `views.py` file or edit an existing one.

Subclass from `RestApiView` to ensure auth permissions are set properly.

Ensure a method is created in your class that matches one of these HTTP methods (case matters!): [`get`, `post`, `patch`, `delete`, `put`] and that the `@auth` and `@rest_api_spec` decorators are specified for each of the methods you define. 
Without the `@rest_api_spec` decorator, the view will not have any of the validation or error handling guarantees and will not show up in the generated OpenAPI spec.

## Error Handling
We've added handlers for 403 and 404 errors (`handler403` and `handler404`) in [urls.py](backend/rest_api/urls.py). These handlers allow us to return helpful JSON responses to the requester for PermissionDenied and Http404 errors.

All other errors (400s, 500s) are handled by the `@raises_rest_api_error` decorator in [utils.py](backend/rest_api/utils.py)

## OpenAPI Spec generation
To update our current OpenAPI spec, which lives at [openapi_v1_spec.json](backend/rest_api/openapi_v1_spec.json), run the following django command:
```
poetry run python manage.py generate_openapi_spec
```
And this will update our OpenAPI JSON spec. **All updates to REST API endpoints need this command to be run manually to properly update our OpenAPI spec.**


## Local development
Ensure that your `/etc/hosts` file includes this mapping of localhost to `api.localhost`:
```
127.0.0.1     api.localhost
```
This should automatically be added in codespaces but may get reset if your codespace restarts. *This entry will need to be added to your local `/etc/hosts` file if developing locally and not on codespaces*

You can invoke an endpoint locally like so:

* Listing all secrets
  ```
  curl 'api.localhost:8000/v1/secrets' -H "Authorization: Api-Key $BASETEN_API_KEY"
  ```
* Upserting a secret
  ```
  curl -X 'POST' 'api.localhost:8000/v1/secrets' \
    -d '{"name": "test", "value": "new_value"}' \
    -H "Authorization: Api-Key $BASETEN_API_KEY"
  ```
