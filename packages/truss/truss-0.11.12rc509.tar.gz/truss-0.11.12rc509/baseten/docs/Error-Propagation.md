# Error Handling and Propagation System

## Overview

This document outlines the error handling and propagation system implemented to distinguish between userspace and basetenspace incidents. The system aims to improve incident alerting, identification, and resolution by providing more precise error information.

## Key Components

1. Baseten Error Convention
2. Error Propagation Mechanism
3. Error Configuration and Management

## 1. Baseten Error Convention

### Structure

The Baseten error convention uses a five-digit code:
- First two digits: Source ID
- Last three digits: Error code

Example: `01501`
- `01`: Source ID (e.g., Beefeater)
- `501`: Specific error code

## 2. Error Propagation Mechanism

Errors are propagated using response headers. The edge server decodes the header and logs the request in the metrics system.

### Process

1. If the status code is 5xx or 4xx, check for the `X-BASETEN-ERROR-SOURCE` header.
2. Use the configuration to interpret the error code and act accordingly.

## 3. Error Configuration and Management

### Source IDs

| Source | ID |
|---------|------|
| Beefeater | 01 |
| Knative Activator | 02 |
| Knative Queue | 03 |
| Truss Server | 04 |


### Error groups

| Error Group| Name | Description
|------------|------------| - |
| 5**| Unexpected error | An error originating from a baseten internal component. |
| 6**| Downstream error | An error originanting from a downstream component that is "re-raised". |
| 7**| Client error | An error originanting from incorrect usage of the client. |

Note: if we have have seamless error propagation, the only errors left as "downstream" errors are
failures from user-land code, e.g. the `predict` method failing.


### Predefined Errors

| Error Name | Service ID | Error Code | Description |
|------------|------------|------------|-------------|
| BeefeaterInternalError | 01 | 500 | Unexpected Error |
| BeefeaterDownstreamError | 01 | 600 | Downstream error |
| BeefeaterUnknownError | 01 | 500 | Unknown error code |
| KnativeQueueDownstreamError | 03 | 600 | Downstream error |

### Error Lookup

The system includes a function to find errors based on the source and code. If no matching error is found, it returns the BeefeaterUnknownError.
