# 🌓 Moon Monorepo

[Moon](https://moonrepo.dev/docs) is a fast task runner for monorepos, used for CI, local development, and build artifact generation. It allows you to describe "tasks" easily and handles the complexity of managing dependencies and execution across multiple projects.

Benefits:
* Compatible with native tooling for go, python, C++, etc.
* Allows common tasks to be shared across projects (e.g. tasks for `go mod tidy`, `golangci-lint`, etc. are automatically created for all go projects).
* Executes actions in parallel and in topological order.
* Only runs affected projects in CI.
* Caches artifacts to avoid redundant builds, tests, linting, etc.
* In combination with docker bake, supports common base images that can be shared across projects.

## Installation

We install and manage moon using proto. Install moon using `proto install moon`.

If you do not have proto installed, run the following command in the root of the monorepo to install proto and all proto tools:
```bash
bash <(curl -fsSL https://moonrepo.dev/install/proto.sh)
proto install
```

## Setting up moon projects

Moon projects are declared in `.moon/workspace.yml`. Each project just needs a `moon.yml` file at the root of the project directory, which defines its tasks.

For more details, see [the docs](https://moonrepo.dev/docs/create-project).

## Running tasks

To run a task:
```
moon run <project>:<task>
```
Example:
```
moon run workload-optimize:test
```
Moon handles caching, dependencies, and consistent execution across environments.

## Managing tools

We use proto as our toolchain. Proto has native support for [several common tools](https://moonrepo.dev/docs/proto/tools), and also supports custom tools via [plugins](https://moonrepo.dev/docs/proto/plugins).

See `.prototools` and `.proto/plugins` for examples of proto plugins.

## Why moon?

### vs Bazel / Pants

Moon is simpler--it's a glorified task runner that's easy to understand and adopt. Bazel and Pants require significant knowledge investment and change how we work.

Moon works on existing 'native' monorepo solutions:
* Go projects use Go workspace
* Python projects use uv workspace

It does not require special IDE tooling and Moon projects remain valid Go / Python projects.

### Docker Bake Integration

Moon integrates with Docker bake for image dependency and code reuse:
1. Moon builds base images
2. Moon builds artifacts  
3. Same commands work locally, in CI, in codespaces, and in Docker
