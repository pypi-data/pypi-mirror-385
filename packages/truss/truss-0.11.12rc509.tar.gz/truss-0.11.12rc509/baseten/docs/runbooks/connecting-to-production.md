# Connecting Directly to Staging or Production

There may be more than a few occassions in which you need to run commands directly against the production or staging instance of Baseten. This could be due to bad code, bad migrations, or some other form of hotfixing. It's alright. It happens.

Fortunately, it _is_ possible to SSH directly into our production nodes. Doing so is a multi-step process.

## 1. Setup AWS locally

You can follow [this guide](./AWS-&-Terraform-Setup.md) to set up the tools you'll need, such as [AWS Vault](https://github.com/99designs/aws-vault) and the [AWS CLI](https://aws.amazon.com/cli/). Once everything is configured, assuming you have successfully configured [role switching](./AWS-&-Terraform-Setup.md#set-up-role-switch-in-consoleawsamazoncom), you'll want to spawn a subshell under a role that will have the correct permissions:

```sh
# Staging
$ aws-vault exec staging-admin

# Production
$ aws-vault exec prod-admin
```

## 2. Switch the Cluster Context

While assuming a production or staging role in the AWS console, you should be able to view either the production or staging Kubernetes cluster via [the dashboard](https://us-west-2.console.aws.amazon.com/eks/home?region=us-west-2). Clicking into the cluster resource, you should be able to nab it's Amazon Resource Name (ARN).

As of this writing, our ARNs are as follows:

- **Staging:** `arn:aws:eks:us-west-2:094050715936:cluster/staging-cluster`
- **Production:** `arn:aws:eks:us-west-2:836885557665:cluster/production`

Back on the command-line, you'll want to inform `kubectl` that it should use the correct cluster context when running commands:

```sh
$ kubectl config use-context <ARN>
```

**Note: If you have not finished the commands in the [the AWS setup guide](./AWS-&-Terraform-Setup.md), this will not work.**

### Connecting to Stability

After completing [the AWS setup guide](./AWS-&-Terraform-Setup.md), you should use this ARN to connect to the Stability cluster.
Ensure that you have run the correct `aws-vault` command (ie: `$ aws-vault exec stability`) with your Stability profile name
first.

- **Stability Cluster:** `arn:aws:eks:us-west-2:556147119599:cluster/stabilityai-cluster`

## 3. SSH into a production pod

Once your `kubectl` context is set, next you'll want to use `kubectl` to view the list of running pods inside the Kubernetes cluster. Specifically, you'll want to find celery workers. [Celery](<(https://github.com/celery/celery)>) is the distributed task queue we use to run async tasks in our clusters. You can use either the command below, or its shorthand form if you've configured Kubernetes aliases via the [runbook](/docs/runbooks/K8s-Runbook.md#bash-tips).

```sh
$ kubectl get pods -A | grep celery

# Of, if you are using the runbook:
$ kgp -A | grep celery
```

Celery pods typically look something like ` celery-worker-6478b4fcd7-kq4vs`. Once you've found one, you can SSH into it via `kubectl`'s `exec` command:

```sh
$ kubectl exec -it -n baseten celery-worker-6478b4fcd7-kq4vs -- /bin/bash

# Or, if you are using the runbook:
$ ksh celery-worker-6478b4fcd7-kq4vs
```

## 4. Run your commands

Once you're inside the pod, you'll notice the directory contents are the same as this monorepo's [backend](/backend) folder. From there, you can run whichever commands you need.

```sh
# To run a Python shell
$ poetry run ./manage.py shell_plus

# To run a Postgres shell
$ poetry run ./manage.py dbshell
```

There you have it! Good luck fixing whatever broke 💪
