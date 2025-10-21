# CDLI (Continuous Deployment CLI)
## Requirements
- gh (authenticated)
- git (authenticated)

### Local Setup
In local setup, you must install `proto`, which is a tool that manages Baseten's go tooling

```bash
cd $BASETEN_MONOREPO # go to root of monorepo
bash <(curl -fsSL https://moonrepo.dev/install/proto.sh)
proto install
```

### Codespace
`gh` needs to be authenticated and have access to the flux cd repository. On codespace, the best is to relogin with `gh auth login` after clearing the `GITHUB_TOKEN` environment variable with `unset GITHUB_TOKEN`.
## Overview
CDLI is a command-line interface tool designed to manage and automate deployments across different environments (production, staging, dev) using FluxCD. It provides seamless artifact promotion and deployment management while maintaining a clear audit trail through Git commits and pull requests.

## Features
- List artifacts and their current versions across environments
- Deploy specific versions of artifacts to production
- Promote artifacts from staging to production
- Automated PR creation with detailed deployment information
- Git-based version control and tracking

## Usage
In the cdli directory
```bash
chmod +x cdli.sh
./cdli.sh artifacts
```

## How to Use

### Configuration

The tool uses two configuration files:

1. **Main configuration** (`~/.b10/config`):
```yaml
fluxcd_directory: "~/.b10/repo/flux-cd/"
fluxcd_repository: "https://github.com/basetenlabs/flux-cd"
baseten_directory: "~/.b10/repo/baseten/"
baseten_repository: "https://github.com/basetenlabs/baseten"
```

2. **Artifact groups configuration** (`artifact-groups.yaml` in the cdli directory):
```yaml
artifacts:
  image/django:
    scopes: [frontend, django]
    groups: [django]
  chart/django:
    scopes: [frontend, django]
    groups: [django]
```

### Commands

1. **List Artifacts**
   ```bash
   ./cdli.sh artifacts
   ```
   Shows all artifacts across environments with their current versions and commit information.

2. **Deploy Specific Version**
   ```bash
   ./cdli.sh deploy [artifact-name] [version] [--scope <scope>]
   # example: ./cdli.sh deploy image/baseten/workload-optimize master-12434343-20250410210554 --scope workload-optimize
   ```
   Create a PR to deploy a specific version of an artifact to production.

3. **Promote from Staging**
   ```bash
   ./cdli.sh  promote [artifacts]
   # example: ./cdli.sh promote image/baseten/async-service --scope async-service
   # example with multiple artifacts: ./cdli.sh promote image/baseten/async-service image/baseten/workload-optimize --scope async-service workload-optimize
   ```
   Create a PR to promote an artifact from staging to production environment.

4. **List Artifact Groups**
   ```bash
   ./cdli.sh groups
   ```
   Shows all configured artifact groups and their associated artifacts.

5. **Promote Artifact Group**
   ```bash
   ./cdli.sh promote-group [group-name]
   # example: ./cdli.sh promote-group django
   ```
   Promote all artifacts in a group from staging to production using the combined scopes from all artifacts in the group.

### Debug Mode
Add `-d` or `--debug` flag to any command for verbose output:
```bash
cdli -d artifacts


### List artifacts version
- Artifacts image are stored in [dockerhub](https://login.docker.com). Use credentials stored in 1password to connect.
- Artifacts chart are stored in [harbor](https://registry.infra.basetensors.com). Use credentials stored in 1password to connect.

## How It Works

### Architecture Overview

1. **Repository Management**
   - The tool maintains local copies of two repositories:
     - FluxCD configuration repository
     - Main application repository
   - Repositories are automatically cloned and updated as needed

2. **Artifact Discovery**
   - Scans YAML files in the FluxCD repository
   - Identifies artifacts through special comments:
     ```yaml
     image: repository/image:tag #{"#b10_image": "service-name", "#b10_env": "production"}
     ```
    - For chart, the artifact name should be directory name.

3. **Deployment Process**
   1. Creates a new branch in the FluxCD repository
   2. Updates the relevant YAML files with new versions
   3. Commits changes with detailed information
   4. Creates a pull request with:
      - Previous and new version details
      - Commit information
      - Deployment environment
      - Change summary

4. **Version Tracking**
   - Extracts commit information from the main repository
   - Shows when changes were made and by whom
   - Provides humanized timestamps for better readability

The tool follows GitOps principles, ensuring that all changes are tracked, reviewable, and reversible through standard Git workflows.

### UI deployment
We build manually and deploy.
`docker build -t baseten/cdli:0.0.11 .` && `docker push baseten/cdli:0.0.11`
Change image in `deployment.yaml` and deploy to `basetensors`
