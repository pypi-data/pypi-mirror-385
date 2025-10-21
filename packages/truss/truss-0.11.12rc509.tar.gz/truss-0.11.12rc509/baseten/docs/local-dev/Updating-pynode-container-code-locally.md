# Updating pynode container code locally

Keep the following django command running continuously in the background for pynode container code to be updated continuously

```sh
poetry run python manage.py sync_pycode --username=[your-username]
```

Note that this is not user code in pynode, that one comes from db dynamically any way, this is for the flask wrapper and other surrounding code that runs on pynode container. This command checks for any changes in corresponding files and deploys them automatically as they change.
