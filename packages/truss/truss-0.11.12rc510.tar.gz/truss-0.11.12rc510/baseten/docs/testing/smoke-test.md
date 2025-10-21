# Smoke Test Documentation

## Overview
This smoke test is an automated integration test designed to verify the end-to-end functionality of our model deployment system using Truss and Baseten. It runs **hourly** in production to ensure system health and catch potential issues early.

## Components:
1. Python Test Script (test_smoke.py)
2. [GitHub Actions Workflow](/.github/workflows/production-smoke-test.yml)

## When It Runs:
* Automatically every hour (triggered by cron job)
* Manually via workflow dispatch

## What It Does:

### 1. Workload Plane Setup:
   * Fetches workload plane configurations from https://app.baseten.co/smoke_test_config
   * Uses these configurations for matrix testing across different workload plane environments. We don't have the option to have multiple workload planes per user; that's why we need multiple accounts.
### 2. For each workload plane:
   * Creates a unique model name with timestamp
   * Writes Baseten credentials to ~/.trussrc
   * Deploys a test model using Truss CLI
   * Verifies model deployment status
   * Performs a prediction using the deployed model
   * Checks prediction results
   * Performs an async prediction using the deployed model
   * Checks that the async prediction succeeded
   * Queries logs from the deployed model
   * Verifies presence of expected log messages (e.g., "Entrypoint initialization", "Build succeeded")

### 3. Cleanup:
   * Deletes the test model after successful verification

## Key Points for On-Call:
1. Monitor Slack for failure notifications
2. Check GitHub Actions logs for detailed error information
3. Failures may indicate issues with:
   * Truss deployment process
   * Baseten API
   * Prediction endpoint
   * Async inference service
   * Logging system

## Troubleshooting Ideas:
1. Review the GitHub Actions logs for the specific workload plane that failed
2. Check Baseten API status and functionality
3. Verify Truss CLI operations manually if necessary
4. Inspect model logs for unexpected errors or behaviors
5. Use Billip to connect to each workload plane organization. Search for "smoke" in the email and hijack
