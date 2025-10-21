# MCM

MCM (or multi-cluster models) is a system for managing multi-cluster deployments, including autoscaling, scheduling, and state management across workload planes.

## Project structure

The MCM codebase consists of several components, each with their own main packages under the `cmd` directory. The main components are:

- [ATC](./services/v1/atc/README.md): The ATC (air traffic control) service provides the main API for interacting with MCM and pushes out deployment and routing changes to the Workload Planes.
- [Autoscaler](./services/v1/mcs/README.md): The autoscaler determines the global desired scale for each deployment.
- [Scheduler](./services/v1/mcs/README.md): The scheduler determines how to schedule deployments across the various workoad plane compute resources.
- [GNS](./services/v1/gns/README.md): The GNS (global notifier service) manages and consumes from write-ahead log (WAL) slots on the DB and publishes change events via Kafka.
- [LSM](./cmd/lsm): The LSM (local state manager) runs in each workload plane, listened for kubernetes resource changes, and publishes them to Kafka for the GSM to consume.
  - LSM is the only MCM component that runs in the workload plane. All others run in the control plane.
- [GSM](./cmd/gsm/): The GSM (global state manager) consumes events from the LSM and stores the current state in the MCM database. The two services in tandem provide us with a global view of the state of all workload planes.

The logic for each service lives under the `services` directory. The `state` directory contains the [gorm](https://gorm.io/docs/models.html) DB models and helpers. The `shared` directory contains shared utilities.

Check out the [IcePanel system diagram](https://s.icepanel.io/9Z9IPaVrUJYVHE/V0zV) (shared credentials in 1Password) to understand how all the components fit together.

## Local development

MCM uses [skaffold](https://skaffold.dev/) to deploy MCM components as well as other dependencies to the local minikube cluster. Skaffold will build the necessary docker images and release helm charts according to [skaffold.yaml](../../skaffold.yaml).

Follow the [dev-setup instructions](../../docs/local-dev/Dev-setup.md) if you haven't already. If you're using codespaces, most of the work should be done automatically. If not using codespaces, see [local dev setup instructions](../../docs/local-dev/Local-Development.md) for installing the required tools.

Install dependencies by running `docker/codespace/library-scripts/go-build-tools.sh`.

To build and deploy the local environment, navigate to the **root** of the repository (not the current folder) and run `skaffold run`. You should re-run this whenever you need to build and deploy changes to the MCM codebase.

#### Deploying models locally
Enable the relevant MCM-related [org flags for your organization via billip](http://localhost:8000/billip/users/organizationflag/), this is likely `ORG_ENABLE_DEPLOY_TO_MCM_FOR_CPU`.

Run django / beefeater / celery locally using `bin/run_everything.sh` and deploy models as you would using 
`truss push ...` and `truss chains push ...`

### Code formatting and linting

In general, this project follows go best practices. We use `gofmt` for code formatting and `golangci-lint` for linting. See [Effective Go](https://go.dev/doc/effective_go) for best practices.

- Use `make format` to format the code.
- Use `make lint` to perform linting using Buf (see below section on protobuf) and golangci-lint.

### VS Code integration

When developing in VS Code, you can use the official Go extension (`golang.go`), providing language features like IntelliSense, formatting, and test detection. For the best results, use the "Add folder to workspace" command to add this folder (./go/mcm) to your workspace.

You can debug individual unit tests through the testing panel and the `Go: Run/Test Current File` to debug a single test file or main file.

## Tests

We have extensive unit tests for the MCM codebase. Run unit tests with `make test`. You can also call `go test` directly to run tests for a specific package or file.

We use [Mockery](https://vektra.github.io/mockery/latest/) to generate interface mocks as specified in [.mockery.yaml](./.mockery.yaml). We then inject these mocks as dependencies in our unit tests to isolate certain behaviors and simplify test complexity. To regenerate mocks, run `make generate`.

### Integration tests

We also have integration tests, which test the interactions between various components by running against MCM deployed in the minikube environment. To run integration tests, use `./bin/run_mcm_integration_test.sh`. To run the tests from a clean environment, you can use `make integration`.

The integration tests are run on every pull request by the [MCM integration tests](.github/workflows/mcm-integration-tests.yml) GitHub action.

### Kafka tests

Some of our tests rely on a running Kafka cluster, like to test the producer/consumer patterns. To locate these tests, seach the code for calls to `kafkatest.IsBrokerRunning()`.

For these tests, we run redpanda inside docker compose. See [docker-compose.yml](./docker-compose.yml). To start the Kafka cluster, run `make local-infra-start`. To stop the Kafka cluster, run `make local-infra-stop`.

## Protobuf

We use [protobuf](https://protobuf.dev/) and [gRPC](https://grpc.io/) to standardize communication both between the MCM components and for the [ATC API](./services/v1/atc/README.md) used by Django. All protobuf defintions reside under the [mcm_protos](./mcm_protos/) directory.

You can run protobuf generation with `make generate` and lint the protobuf files with `make lint`. We use [buf](https://buf.build/) for protobuf build and linting. See `buf.gen.yaml` and `buf.yaml` for configuration. To support the Django gRPC client, we also generate [Python bindings](../../backend/mcm_protos/) for the protobuf messages.

## Database migrations

We use [atlas](https://atlasgo.io/docs/) to manage database migrations. Atlas generates SQL migrations based on the [GORM](https://gorm.io/docs/models.html) models defined in the codebase. All migrations are listed under the [migrations](./migrations) folder.

To generate migrations:

- Ensure that all model structures are defined in the modelsv1 and atcmodelsv1 packages. These structures should use GORM annotations to define schema details like table names, column types, and constraints.
- When adding a new model, be sure to include it in [schemagen](cmd/schemagen/main.go). This command converts the gorm annotations into a schema that atlas can use.
- Use `make migrate` to generate migrations.

### Writing manual migrations

Some tasks, like modifying permissions or replication settings, require writing manual migrations. To do this:

- Run `atlas migrate new`
- Edit the generated migration file in the `migrations` directory.
- Run `atlas migrate hash` to update the `atlas.sum` file.

### Migration ordering
We use the [linear execution order (default)](https://atlasgo.io/versioned/apply#execution-order) for migration files. Atlas expects a linear history and fails if it encounters files that were added out of order. The order is specified in the atlas.sum file. By convention 
we should make the file name that will follow the same order. Need to be careful not to change the order when merging PRs.

When migration file gets out of order, the migration job will fail with an error like this:
`Error: migration file 20250404194953.sql was added out of order. See: https://atlasgo.io/versioned/apply#non-linear-error`

If migrations are non-linear on your feature branch, you can resolve the error by following these steps:
1. Remove the migration file (`go/mcm/migrations/<timestamp>.sql).
2. Run `atlas migrate hash` to update the `atlas.sum` file.
3. Run `make migrate` to regenerate the migration file.

## Deployment and packaging

The MCM source code is built into a Docker image and deployed to our clusters via helm. See:

- [Dockerfile](./Dockerfile) for the Docker image build.
- [mcm-cp](../../helm/charts/mcm-cp/Chart.yaml) - Chart for the MCM control plane components.
- [mcm-wp](../../helm/charts/mcm-cp/Chart.yaml) - Chart for the MCM workload plane components.
- [Go Build Test Push](.github/workflows/golang.yml) GitHub action - Performs validation and build on all go projects in the repository, including MCM.

## What next?

Read the documentation for each component:

- [ATC](./services/v1/atc/README.md)
  - [ATCtl](cmd/atctl/README.md) - Command line client for the ATC
- [Autoscaler/Scheduler](./services/v1/mcs/README.md)
- [GNS](./services/v1/gns/README.md)

For more information on the MCM architecture and design, see the original [tech spec](https://www.notion.so/ml-infra/MCM-22f9bcef259e4105be6705edf5c97204?pvs=4).
