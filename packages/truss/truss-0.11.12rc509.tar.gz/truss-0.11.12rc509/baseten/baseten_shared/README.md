# baseten_shared

Shared code between different baseten services. e.g. between Django/Celery and
Operator.

## Version upgrade

This is not a published package, so versioning is not strictly needed. 

Local dev envs might have a prebuild copy of `baseten_shared` in their
`.venvs`.  As devs merge in from `master`/`main`, they can end running
an older copy. If the `version` in `pyproject.toml` has changed, `uv`
should detect it and rebuild reliably.

Services using `baseten_shared` _should_ specify the
[package as editable](https://docs.astral.sh/uv/concepts/projects/dependencies/#editable-dependencies)
in their pyproject;

```toml
[tool.uv.sources]
baseten_shared = { path = "../baseten_shared", editable=true }
```

Deployments use the checked out source code and will always rebuild
since their venvs are fresh.

## How to make sure changes to baseten_shared are picked up

We use baseten_shared in other projects in monorepo via local path in poetry.
Updates are not picked up automatically in this scenario, especially on github
action runners. The issue is that a lot of these environments use poetry.lock to
detect changes to poetry environment. For local poetry packages, modifying the
code does not result in poetry.lock of the package using it. It has to be done
manually like so:

```bash
cd backend
uv run python manage.py export_schema
```

This will update the corresponding `poetry.lock` and result in new code being
picked up.

While this is the surest way of getting changes picked everywhere, it can be
slow and thus cumbersome when developing locally, where you want to make many
change to baseten_shared. To pickup changes quickly for local dev the following
works:

`poetry run pip install -e ./baseten_shared`
