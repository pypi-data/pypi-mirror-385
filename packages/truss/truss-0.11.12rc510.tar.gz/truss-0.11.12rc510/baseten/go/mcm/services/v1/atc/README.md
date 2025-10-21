# ATC service

## Design

The ATC (Air Traffic Control) service provides several functions as part of MCM:

- Management API - main model serving interface to application layer (i.e. Django) as well as provide observability into the system
- Controllers - push out model deployment, routing, and serving configurations to the workload planes. Responsible for eventual consistency between this centralized state and the state of the workload planes.

## Management API

The Management API is composed of a set of gRPC services, one per resource type. The implementations of the services live in subdirectories of the current directory. See `deployment`, `instancetype`, and `namespace`.

The management API supports a command-line client, [atclt](../../../cmd/atctl/README.md).

### API design

The ATC gRPC services follow resource-oriented design patterns as specified by Google's open source [API Improvement Proposals](https://google.aip.dev/general), or AIPs. Resource-oriented design is a generalization of RESTful design, relying on strict gRPC resource definitions and CRUD operations over those definitions. These patterns are very similar to those of the kubernetes API.

Conforming to these standard patterns has the following benefits:

- Strong contracts between the client and server, leading to more predictable behavior and less implicit coupling between layers
- Clear separation of ownership and concerns between client and server
- Compatibility with declarative programming patterns like upsert semantics and reconciliation loops, ensuring that the system converges to the desired state
- Consistency across services, permitting the use of shared helpers (see grpcutils) and utilities (like atctl)
- The Google AIPs are battle-tested and well-documented

If you're implementing a new service, making changes to an existing service, or integrating with a service, take some time to familiarize yourself the AIPs, particularly:

- [121. Resource Oriented Design](https://google.aip.dev/121)
- [122. Resource names](https://google.aip.dev/122)
- [123. Resource types](https://google.aip.dev/123)
- [124. Resource association](https://google.aip.dev/124)
- [129. Server-Modified Values and Defaults](https://google.aip.dev/129)
- [130. Methods](https://google.aip.dev/130)
- [131. Standard methods: Get](https://google.aip.dev/131)
- [132. Standard methods: List](https://google.aip.dev/132)
- [133. Standard methods: Create](https://google.aip.dev/133)
- [134. Standard methods: Update](https://google.aip.dev/134)
- [135. Standard methods: Delete](https://google.aip.dev/135)
- [157. Partial responses](https://google.aip.dev/157)
- [158. Pagination](https://google.aip.dev/158)
- [203. Field behavior documentation](https://google.aip.dev/203)

The API should adhere to the following principles and best practices:

- Follow the Google AIPs to the extent possible, especially the ones listed above which are well established in the codebase.
  - If you need some novel behavior that doesn't fit within existing ATC patterns, check first if there's a relevant AIP that you can follow. Check with the team (like in the Slack `#team-infra` channel) if you're unsure.
- Services should return results very quickly, whether for create, update, delete, or list. These methods should only rely on the MCM postgres DB state.
  - 🙅 DON'T: make calls to external services like the operator or perform side-effects as part of service methods. Side effects, like propagation of changes, should happen asynchronously.
- If it's necessary to deviate significantly from the AIPs, do this as part of a separate gRPC service (which can run in the same server) rather than mixing patterns within a service.
  - For an example, see [ATCPatchService](../../../mcm_protos/v1/atc_patch.proto).
- Use `OUTPUT_ONLY` fields as a way of attaching additional related information to resources.
  - For an example, see the "Extended view fields" in the [Deployment](../../../mcm_protos/v1/atc_deployment.proto) resource.
- For more advanced use cases, leverage reflection via protoreflect to acess static information about the resource and service definitions.
  - As an example, [IsFieldUpdateable()](grpcutils/updatemask.go) reads the field annotations to determine whether a resource field may be updated.
  - [ATCtl](../../../cmd/atctl/README.md) makes extensive use of reflection to generalize CRUD operations across different resource types.

#### API linter

We use the Google API linter (see `protoc-gen-gapi-lint` plugin in `buf.gen.yaml`) to check AIP compliance in the proto definitions. Each AIP-compliant API must be listed as an `allowed-files` in the `buf.gen.yaml` file. The `.api-linter.yaml` config disables certain linter rules that aren't relevant to our use case.

While the API linter does a good job of enforcing the AIPs at the proto definition level, it can't enforce the correct behavior of the service implementations. This is where we rely on code reviews, unit tests, and a proper understanding of the AIPs.

### Service implementation

Each service consists of the following major components:

- A proto definition file, including both the resource and the service - for example [atc_deployment.proto](../../../mcm_protos/v1/atc_deployment.proto) contains both the `Deployment` resource, `ATCDeploymentService`, and all the related request and response messages.
- A service implementation - for example [deployment.ServiceImpl](deployment/service.go)
- A backing GORM model - for example [atcmodels.Deployment](../../../state/models/v1/atc/deployment.go)

The database model file contains the two-way binding between fields in the resource and fields in the DB model:

- `ToProto()` converts the GORM model to its proto
- The `NewX()` function (e.g. `NewDeployment()`) creates a new GORM model from a proto
- In the model struct declaration, the `fromProtoField` custom tag is used to determine which fields to update in the DB model during Update method calls. See [updatemask.go](./grpcutils/updatemask.go) for more information.

The [grpcutils](./grpcutils/) package provides common utilities that implement gRPC and AIP patterns, including list pagination and handling update masks.

### Django integration

The baseten Django application calls the ATC API to deploy and manage models. See:

- [mcm_model_deployer.py](../../../../../backend/oracles/model_deployer/mcm/mcm_model_deployer.py) - Integrates between Django `OracleVersionDeployment` and ATC `Deployment` resources.
- [mcm_namespace_deployer.py](../../../../../backend/oracles/model_deployer/mcm/mcm_namespace_deployer.py) - Integrates between Django `Organization` and ATC `Namespace` resources.
- [client.py](../../../../../backend/oracles/model_deployer/mcm/client.py) - Manages connections to the ATC API.

The ATC also has a [Django notifier](../../../services/v1/atc/django/notifier.go) that calls into the Django API to notify it of deployment state and workload plane mapping changes.

## Controllers

The ATC has the following controllers:

1. [Operator deployer](./operator/deployer/deployer.go) - Uses control plane state (ATC Deployment, Deployment Schedule, etc) to create and manage model deployment resources in each workload plane via the operator API.
2. [Route table controller](./routing/routing.go) - Manages the route table for each deployment.
3. [State machine controller](./statemachine/statemachine.go) - Derives the current state and sub-states for each deployment.

## Service architecture

The ATC runs by default in "cluster" mode, which splits the ATC functionality across two kubernetes deployments:

- The `baseten-mcm-atc` deployment is responsible for serving the gRPC API and consuming change events via Kafka. It is primarily event-driven. This deployment can scale horizontally via multiple replicas and should maintain high-availability.
- `baseten-mcm-atc-reconciler` - This deployment runs the periodic reconciler, ensuring the operator deployer and route table controller are in sync with the ATC state. This deployment should run with a single replica.

See [atc.yaml](../../../../../helm/charts/mcm-cp/templates/atc.yaml) in the mcm-cp Helm chart for more details.

## References

- [ATC Milestone 1 Spec](https://www.notion.so/ml-infra/ATC-Milestone-1-Spec-76165d462bac42d6bcfa771130ac3045?pvs=4) - historical doc
- [Google Cloud Resource-Oriented Design guide](https://cloud.google.com/apis/design/) - General guide on resource-oriented design from Google Cloud
