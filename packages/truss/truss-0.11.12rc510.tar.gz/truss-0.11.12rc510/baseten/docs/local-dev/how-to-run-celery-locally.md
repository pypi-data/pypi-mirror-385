# How to run celery locally 

## Requirements
You will need an instance of Redis. There are two ways:

### Redis running as a Brew service (for MacOS)

```sh
brew install redis
brew services start redis
```

### Redis running inside Minikube (for codespaces)
Redis is installed on codespace and runs by default.

## Usage
By default, in the development environment Django runs celery tasks eagerly, meaning synchronously in-thread. While this is good enough for most testing and development, sometimes it's necessary to run celery in a distributed, asynchronous fashion to better match the in-cluster behavior.

To start **celery** in a separate worker:

1. Change the value of `CELERY_TASK_ALWAYS_EAGER` to `False` in `local_base.py`

2. Run the following command from the backend directory:
    ```sh
    USE_GEVENT=True poetry run python manage.py celery  --queue queue_name --concurrency 3
    ```
    - `[queue_name]` can be one of `celery`, `build` or `deploy-build`. If all tasks need to run, repeat step 2 to start one worker on each queue. The celery workers do not yet support live reload. They must be restarted when the code changes

### Running periodic tasks
Running periodic tasks requires celery beat. Start celery beat from the root of the baseten project like so:
```
cd backend
poetry run celery -A baseten beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```
