

# Workload Plane Health Check

## Introduction

The Workload Plane Health Check is a system that continuously monitors the health and accessibility of our workload planes. This system ensures that our infrastructure remains operational and capable of handling user workloads efficiently.

### How It Works

1. **Periodic Checks**: The system uses a Celery beat scheduler to trigger health checks at regular intervals. (60 seconds)

2. **Per-Workload Plane Testing**: For each workload plane:
   - A dedicated smoke test user is utilized.
   - A test `/predict` and `/async_predict` request is sent to a specific "health-check-model" oracle.
   - The response is evaluated to determine the health status. You can find a guide for each status bellow.

3. **Caching**: Results are cached for 2 minutes.

4. **Metric Reporting**: Health statuses are exposed as Prometheus metrics, each workload plane would have a status.

See [here](/docs/testing/workload-plane-health-checks.md) for more details on local testing and implementation.


## Overview

This runbook is designed to help on-call engineers diagnose and resolve issues related to workload plane health. It covers the implementation details, monitoring approach, and step-by-step troubleshooting guidelines for various failure scenarios.


### NO_USER Status

**Meaning**: The smoke test email for the workload plane doesn't correspond to a user in the system.

**Impact**: The health check cannot be performed, potentially masking other issues with the workload plane.

**Diagnosis**:
1. Verify the smoke test user exists for the workload plane using billip (format: `admin__smoke_test_{workload_plane_name}`).

**Mitigation**:
1. Investigate why the production smoke test in github action isn't creating the user automatically. The github workflow can be run manually.

### NO_ORACLE Status

**Meaning**: The "health-check-model" oracle is not found for the organization.

**Impact**: The health check cannot be performed, indicating a potential issue with database.

**Diagnosis**:
1. Check the state of the model by impersonating the workload plane user with Billip.
2. Review logs related to model deployment and the production smoke test.

**Mitigation**:
1. If the oracle doesn't exist, trigger a manual deployment of the health check model.

### FAILED Status

**Meaning**: The health check request to the oracle failed.

**Impact**: The workload plane may be experiencing issues that could affect user workloads.

**Diagnosis**:
1. Impersonate the workload plane user using Billip.
2. Verify the logs in the model itself.
3. Check for any network issues or oracle accessibility problems.

**Mitigation**:
1. Address any network or accessibility issues identified.
2. If the oracle is malfunctioning, consider redeploying it.

### NO_VALUE Status

**Meaning**: The test wasn't run.

**Impact**: The test didn't run which is not great, but this doesn't mean that workload planes have an issue.

**Diagnosis**:
1. Look for any sentry alerts that may help debug why the test didn't run.
2. This could be an issue with celery worker or celery-beat.

**Mitigation**:
1. Find the right person in core-product and have them debug/fix.
