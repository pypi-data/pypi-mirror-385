# Auto update pynode container code locally

This is useful when making any changes to the flask server wrapper code that executes on the py node container. This django command keeps checking for local changes for relevant files and on identifying a difference creates a new docker image and deploys that to py node service.

Usage:
```
poetry run python manage.py sync_pycode --username=[username]
```

ps: Make sure that minikube profile is baseten-local
```
kubectl config current-context
```
should be `baseten-local`
