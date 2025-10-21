# Pynode development

Developing for pynode can get very tedious due to the long time it takes to try out changes. The docker build is the slowest part and can take a few minutes, which totally kills productivity and development experience. Long term it would be best to be able to develop pynode locally, similar to django, for now, there are a few ways to avoid waiting on docker builds to try things out.

## Packages needed

`apt install -y procps vim curl lsof`

You can put these in system packages of your settings.

## Reload new code in pynode
In most cases you would want to reload changes in the main pynode flask server itself, so that django can see those changes and one can test changes end-to-end.
1. Make changes to pynode code locally using local IDE and other tools
2. `bin/sync_code_and_refresh_pynode [pynode podname]` to sync changes to pynode and refresh

Gunicorn would start a new process that will have the new code.

## Develop against secondary flask app
1. Make changes to pynode code locally using local IDE and other tools
2. `bin/sync_files_to_pynode` to sync changes to pynode
3. run a secondary flask app on another port on pynode
`PORT=8081 python app.py`
One can then hit this flask server manually with curl to test.
The app once started loads code changes automatically, this is the main advantage of this flow: that reloads are easy.

## Running tests

To run the pytests for the pynode code locally, do _not_ use `poetry`. Instead,
call `pytest` directly in a Virtual Env.

```
$ cd docker/pynode
$ python -m venv ~/.pynode_env 
$ source ~/.pynode_env/bin/activate
$ pip install -r requirements.txt
$ pytest
```
