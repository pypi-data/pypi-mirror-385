# Cluster Access Bot

The Cluster Access Bot is a Go microservice that handles cluster access requests for Baseten engineers. It has the following features:

- A Slack bot that can be used to request cluster access and posts when access sessions start and end
- Integration with Racher's cluster role template bindings to grant access
- Collection of audit logs for each access session, stored in a Google Drive shared drive. The audit logs can then be shared with customers to meet audit requirements.

## Architecture

The Cluster Access Bot follows a microservice architecture pattern with several key components working together to provide secure, auditable cluster access management:

### Core Components

**HTTP Server (`internal/http/`)**: Provides REST endpoints for health checks and Slack webhook integration. The server handles incoming Slack slash commands (`/access`) and modal submissions, with signature verification for security. It exposes `/healthz` and `/readyz` endpoints for Kubernetes health monitoring.

**Slack Integration (`internal/slack/`)**: Manages all Slack bot interactions including modal dialogs for access requests, posting access notifications, and thread-based communication. The client handles user authentication, cluster selection, and reason collection through interactive Slack modals.

**Rancher Integration (`internal/rancher/`)**:

- **Kubernetes Client (`kube/`)**: Wraps Kubernetes dynamic client with Rancher-specific resource handling for ClusterRoleTemplateBindings (CRTBs), clusters, users, and user attributes. Provides CRUD operations and informer-based event watching.
- **Access Controller (`access/`)**: Orchestrates access session creation by validating user permissions, checking cluster availability, and creating CRTBs with appropriate role templates and TTL labels.
- **Informer Controller (`informer/`)**: Implements Kubernetes informer pattern with leader election to watch CRTB changes and trigger Slack notifications for access grants and revocations.

**Leader Election (`internal/leader/`)**: Ensures only one instance processes CRTB events in multi-replica deployments using Kubernetes Lease resources. Provides callbacks for leadership transitions and graceful worker shutdown.

**Audit Logging (`internal/auditlog/`)**: Captures comprehensive audit trails by querying Loki for Rancher audit logs during access sessions. Creates timestamped log archives with metadata and uploads them to Google Drive for customer compliance requirements.

### Data Flow

1. **Access Request**: User triggers `/access` command in Slack → HTTP server validates signature → Slack client presents modal for cluster/reason selection
2. **Access Grant**: Access controller validates user permissions → Creates CRTB with TTL labels → Rancher grants cluster access
3. **Event Processing**: Informer detects CRTB creation → Posts Slack notification with access details → Marks CRTB as processed
4. **Access Revocation**: TTL controller removes expired CRTBs → Informer detects deletion → Posts Slack notification
5. **Audit Capture**: On CRTB deletion, audit controller queries Loki logs → Creates zip archive → Uploads to Google Drive → Posts link in Slack thread

### High Availability & Scalability

The bot implements leader election to ensure only one instance processes events while allowing multiple replicas for fault tolerance.

### Security & Compliance

All Slack interactions are signature-verified. User access is validated against Okta groups through Rancher user attributes. Audit logs are automatically captured and stored in Google Drive with comprehensive metadata for compliance reporting. The bot only processes private clusters and ignores system-generated CRTBs.

## Mocks

To generate test mocks, run:

```sh
make mockery
```

## Deployment

The Cluster Access Bot is deployed to the basetensors cluster (where Rancher runs) via a helm release managed by [Terraform](https://github.com/basetenlabs/baseten-deployment/blob/main/baseten-infra/cluster-access-bot/main.tf). It can be applied using Atlantis.

Chart and image versions must be bumped manually.

View service logs: https://grafana.infra.basetensors.com/goto/CTE8pn6Hg?orgId=1

## References

- [Runbook](https://www.notion.so/ml-infra/Grant-PWP-access-27091d24727380f0ab82d4e6cf8e2e63)
- [Helm chart](../../helm/charts/cluster-access-bot/Chart.yaml)
- [TF project](https://github.com/basetenlabs/baseten-deployment/blob/main/baseten-infra/cluster-access-bot/main.tf)
- [Slack bot configuration](https://api.slack.com/apps/A09GSBZ1YRL/general)
- [Slack bot manifest](app_manifest.yaml)
