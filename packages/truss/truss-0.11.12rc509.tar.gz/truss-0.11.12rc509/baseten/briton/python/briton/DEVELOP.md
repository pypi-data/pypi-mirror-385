# Developing for Briton

## Running tests

```
poetry run ./test.sh
```

To skip the GPU tests:

```
poetry run pytest -m "not gpu"
```

### On MacOS

You may need to first install the `xz` packages, and then reinstall python.

```
brew install xz
pyenv install 3.11.9  # for python 3.11
```

## Formatting code

```
poetry run ./format.sh
```

## Manually publishing to PyPi

Before running this, please increment the version appropriately in pyproject.toml.

Find the `basetenbot` credentials in 1Password, which can be used to sign into PyPi
and generate a token. This token can be saved in your `.pypirc` as follow:

```
[distutils]
  index-servers =
    pypi

[pypi]
  username = __token__
  password = # either a user-scoped token or a project-scoped token you want to set as the default
```

Or entered into the CLI when prompted by `twine upload` below:

```
rm -rf dist
poetry build
poetry run twine upload dist/*
```
