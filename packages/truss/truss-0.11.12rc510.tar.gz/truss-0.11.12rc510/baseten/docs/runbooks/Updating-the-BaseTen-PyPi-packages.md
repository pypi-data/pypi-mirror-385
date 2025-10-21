# Updating the Baseten Pypi packages

We currently publish the following packages in PyPI

* `baseten` from https://github.com/basetenlabs/baseten_client
* `truss` from https://github.com/basetenlabs/truss

To publish the package; 
* Ensure that you have merged an increment to the semantic version of the package in `pyproject.toml`. [Here](https://github.com/basetenlabs/baseten_client/pull/139/files) is an example.

### For baseten_client

In the root of the project directory (e.g. `baseten_client`):
* Checkout master and stash any local changes.
* `poetry publish --build`
* Use your PyPi account to publish. Preferably use a [token](https://pypi.org/help/#apitoken) over username/password auth.


### For Truss

Follow steps in contributing.md in the Truss repository
