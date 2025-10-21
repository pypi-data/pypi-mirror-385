# What is Github Codespaces?
A codespace is a container in the cloud with the set up needed for developing baseten.

# What does the Baseten Github Codespaces set up look like?
It's a linux environment with python, node and other tools and libraries already installed. It has a local minikube cluster to run pynodes, models and other components. The django app and node server will need to run directly on the host machine (they're not on minikube). Overall, it closely mimics the dev environment on the laptop.

# How do I use it for the first time?

**IMPORTANT:** Codespaces does not have access to GPUs. For that, you will need to use the [development environment](https://github.com/basetenlabs/baseten/blob/master/docs/local-dev/Dev-deployment.md).

1. Create a new codespace on the [baseten repo homepage](https://github.com/basetenlabs/baseten/), and open it in vscode app on your desktop. (**Do not use the browser-based vscode view on Github for UI or anything that requires port-forwarding,** that will not work.) **Please pick 8 cores for resources; with 4 or less cores it's really slow and will likely fail**.
2. Wait for the codespace to launch and a post-setup command to execute.
  The whole process can take 15-25 mins. Image building, poetry install, node install, building pynode image, setting up minikube cluster, it all takes time.

3. Start running the application:
```sh
bin/run_everything.sh
```

4. Access the application at `http://127.0.0.1:8000`. Vscode should have automatically forward port 8000 locally, but as mentioned earlier, you should ensure you're using the desktop app with the codespaces extension and _not_ the browser view launched by Github.

Both username and password are `baseten`. If login fails, ensure that the codespace post create command finished successfully, and potentially run `bin/codespace_post_create.sh` manually. Note that first load is usually very slow due to nodejs compilation.

Codespace might automatically stop after a few mins of inactivity, but can easily be resumed.

# How do I use it when I already have a codespace?
You can simply resume your codespace. minikube is automatically started on resuming the codespace session. You would just need to start your django and node servers again (instructions above).

# How do I run my cypress tests with codespace?
There are two ways to run tests for code on codespace.
1. You can run cypress directly on your laptop (mac osx). Cypress looks to hit
   port 8000 on localhost which django on Codespace would already have been
   forwarded to. This is useful if you want to see cypress tests run visually.
2. You can run cypress tests directly on codespace with instructions below. This
   is useful if all you want to do is run the test. It's not great if you want
   to debug a failing test, for which being able to view visually is better.

## How to run cypress tests on codespace?

You can use regular cypress set up steps, such as creating the cypress
test users, starting django with specific env vars etc, as described in Cypress
tests wiki. And then:
```
npx cypress run [spec path]

# For example
npx cypress run --spec cypress/e2e/datasource/data_source_create_spec.ts
```


# For `bin/start_servers_codespace` where are my django and node logs?
`bin/start_servers_codespace` is a helper script to start django and node
servers in one place. In practice we haven't found it to be very useful, it's
not that much more complex to start django and node servers in separate terminal
tabs. But if you prefer using it then here is where you can find the logs for
the servers it starts.
`bin/start_servers_codespace` start 3 servers
1. Main django server --> `Logs in django_main.log`
2. Node server  -->  `logs in node.log`
3. A django server for callbacks from pynode --> `logs in django_callback.log`

`start_servers_codespace` is just a shortcut to launching the three processes.
You need to keep it running. Killing this process will kill the three underlying
processes. At the cost of occupying a terminal tab, it makes it really easy to
kill and restart these processes.

tip: You can open the log files directly in vscode.

# How do I customize my dot environment?
Github codespaces allows using a public dot repository.
https://docs.github.com/en/codespaces/customizing-your-codespace/personalizing-codespaces-for-your-account#dotfiles

In a nutshell, you could:
1. Create a public dot files repo
 - [Pankaj's dotfiles repo](https://github.com/pankajroark/dotfiles)
 - [P-A's dotfiles repo](https://github.com/pastjean/dotfiles)
 - [Nikhil's dotfiles repo](https://github.com/nnarayen/dotfiles)
2. Enable dotfiles in github codespace settings.
3. Cmd + Shift + p -> Rebuild container (THIS IS SLOW)

Codespaces sees the bootstrap.sh (or [others](https://docs.github.com/en/codespaces/setting-your-user-preferences/personalizing-github-codespaces-for-your-account#dotfiles)) file in the dot_files repo and executes it. That script in Pankaj's dotfiles repo adds sourcing of appropriate rc files into the .bashrc file in the codespace.

To try things out you can always [clone](https://stackoverflow.com/a/78333830) your dotfiles repo in the codespace and run the bootstrap.sh script manually.

# How can I access metrics locally?

If you'd like view prometheus metrics you've created, start the backend with the following command:

```sh
EXPOSE_METRICS=1 poetry run python manage.py runserver --noreload
```

You can then see the value of all metrics by running:

```sh
curl -s localhost:8001
```

# Troubleshooting

## Why is minikube postgres not available on minikube host?
On resuming a codespace it takes some time for minikube to start up and for postgres node to start up. This can take 1-2 minutes. You can run the command `minikube status` to make sure that minikube has come up. You should see something like:
```
baseten-local
type: Control Plane
host: Running
kubelet: Running
apiserver: Running
kubeconfig: Configured
```

Next thing needed is for postgres to be up. You can check if it's up by running:
```kubectl get pods -n baseten```
You should see a single postgres pod. Make sure that it's in running state.

## Codespace has run out of disk space
This can happen due to pynode or model deploys. These deploys create docker images, which can run into Gbs. You can remove images to free up space.
```
minikube ssh
docker image ls
```

Then use `docker rmi [image name]` to delete any images.

If need further space then you could do the more drastic but effective.
```
docker system prune -a
```

## localhost:8000 isn't responding
Try going to the ports list and removing ports `3000` and `8000`, then adding them again.

## Baseten front application fails to load
Sometimes Baseten application fails to load for weird reasons, failure to download various js files, graphql failures etc, and there doesn't seem to be anything wrong in django or node logs.
In such cases stopping the codespace and starting it back up seems to be the only thing that works consistently.

`Cmd + Shift + p` --> 'Codespaces: Stop current codespace'

`Cmd + Shift + p` --> 'Codespaces: Connect to codespace'

## postgres just disappeared
Unfortunately, sometimes when codespace is resumed the postgres setup on minikube and all pynodes just disappear. This needs to be debugged. But until then, the fix is to `Cmd + Shift + p` --> 'Codespaces: Rebuild container'. This will take ~15 mins.
A slightly faster but more manual solution is to run this:
```
bin/local_cluster_setup

export POSTGRES_HOST=$(minikube ip)
export POSTGRES_PORT=$(kubectl get service -n baseten baseten-postgres-np -o jsonpath={.spec.ports[0].nodePort})
export CREATE_DB_POSTGRES_USER=postgres
export PGPASSWORD=postgres

bin/create_dev_db
```

## Infinite wait connecting to codespace
Unfortunately, sometimes when trying to connect to codespace one keeps waiting indefinitely. This happens both from VS Code as well as from the browser. Ultimately, you would get a message saying that it would be best to restart codespace. Instead of waiting this long you could stop and start the codespace manually from the github UI.
<img width="1470" alt="image" src="https://user-images.githubusercontent.com/664454/155626024-1916cab9-5193-4b23-95b1-d1a6abff23d8.png">

# Gotchas
* Do not run `runserver_plus` to run django. With runserver_plus the callbacks from pynode to django don't work.

## Tips for using codespaces for integration testing
Codespace set up is now tested automatically. The github action for this is here:
https://github.com/basetenlabs/baseten/blob/master/.github/workflows/codespace.yml#L27

The test involves spinning up a fully functioning Codespace with minikube on it and a pynode deployed on it as well. This is a great base for writing
integration tests on top of. The way to do it would be to write an integration test as a pytest and then invoke that pytest on the running container.
Something like this at the end of https://github.com/basetenlabs/baseten/blob/master/.github/workflows/codespace.yml should so:
`npx devcontainer exec --workspace-folder . poetry run pytest /path/to/test`

The test currently runs on any PR that touches .devcontainer or helm folder in the baseten repo, but a separate workflow can be created based on `https://github.com/basetenlabs/baseten/blob/master/.github/workflows/codespace.yml` to be run on appropriate triggers.
