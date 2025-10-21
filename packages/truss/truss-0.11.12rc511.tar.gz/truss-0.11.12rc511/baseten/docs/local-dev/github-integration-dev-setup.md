# Github App Development Setup
For the github integration, we use a [Github App](https://docs.github.com/en/developers/apps/getting-started-with-apps/about-apps). While being pretty easy to work with, they require a bit of setup to allow github to send events to a local server.

The process is well explained on this page: https://docs.github.com/en/developers/apps/getting-started-with-apps/setting-up-your-development-environment-to-create-a-github-app.

Note that _step 5_ is optional, but it is a good read if you are new to github apps.

## Smee.io (step 1)

Smee.io is the tool recommended by github to expose your local server. The steps to install it are described in [step 1](https://docs.github.com/en/developers/apps/getting-started-with-apps/setting-up-your-development-environment-to-create-a-github-app#step-1-start-a-new-smee-channel).

You will need to modify the command used to start smee a bit
1. Be sure to use the url of your channel
2. The `--path` option must point to the configured route in `urls.py`. It is `/integrations/github`
3. The local server for the django app uses port 8000

```
smee --url <your smee url> --path /integrations/github --port 8000
```

## Creating the github app (step 2)
For development purpose, we each create a github app in our personal github account (i.e. not in the baseten org). This way, each individual app can point to a different smee.io channel.

### Permissions
When creating the app, you will need to set the following permissions in github:
- Administration - Read & Write
- Content - Read & Write

`Administration` is used to create the baseten_apps repository and `Content` is used to clone, commit and push to the repository.

### Callback URL
In the `Identifying and authorizing users` section, you will need to check the `Request user authorization (OAuth) during installation` checkbox and configure the callback URL. Set the callback URL to `http://localhost:8000/integrations/github/callback`


## Save private key and app id (step 3)
We don't use a private key in the github integration, so this step can be skipped. We do use a `client secret` though, so you can generate one here and save it (it will only be available to see on creation)

To generate the client, click the `Generate a new client secret` button in the `Client Secret` section of the github app setting.

*Note*: Client secret and private key are not the same thing. Make sure you generate a `Client Secret`. It is a string that should look like this: `2a3182f69f8cb3c8b98acb0cdf52d4e79a14f66b`

## Set your environment (step 4)
In your poetry shell (or just in your terminal if you don't use a poetry shell):

```
export GITHUB_APP_IDENTIFIER="insert app identifier"
export GITHUB_WEBHOOK_SECRET="insert webhook secret here"
export GITHUB_CLIENT_ID="insert your client id here"
export GITHUB_CLIENT_SECRET="insert client secret here"
```

## Installing the app in github (step 7)
As for step 4, we install the app on our personal github accounts (and not in the baseten org)

## Running the Django app locally with the git integration
There are some race conditions that happen when the celery tasks are executed in the same process as the Django server, so we need to run celery outside of this process. To do that, you will need to change the `CELERY_TASK_ALWAYS_EAGER` in local_base.py to `False` and start the celery workers in another terminal. There are more details on how to run celery workers locally in those there: [How to run celery locally](/docs/local-dev/how-to-run-celery-locally.md)

You will need to run 2 celery workers because the tasks involved during the installation and push process run on 2 different celery queues:
- The `handle_github_installation_webhook_events`, `create_github_repository` and `push_workflow_to_git` run on the `celery` queue.
- the `deploy_release_to_prod` task run on the `build` queue.

How to start the workers:
```
# worker for the "celery" queue
python manage.py celery

# worker for the "build" queue
python manage.py celery --queue build
```

For a faster feedback loop, you can comment out the part of the `deploy_release_to_prod` that builds and deploys the pynode (building a pynode can take some time in local). The following lines in workflows/tasks.py can be commented out
```
    if should_deploy_pynode:
        ensure_pynode_deployed_on_deploy_queue.apply(
            args=[org.pk.hashid, DeploymentEnvEnum.PRODUCTION.value]
        )
```

## Enabling git sync in an organization
There are a couple of flag controlling the git sync feature that need to be enabled in order for the Django app to push to GitHub:
- In bilip, update the git sync flag by upgrading License to Starter/Business or customize license.
- On the workflow that you want to sync to git, the `is_synced_to_git` flag
