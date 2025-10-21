# Model API Shadow Proxy (WIP)

This is a proxy that receives requests from the model API gateway and can shadow traffic to arbitrary endpoints.

Incoming requests have the body matching the openAI API spec.

## Overview

A high-performance FastAPI server that receives OpenAI API conformant traffic, immediately returns 202 responses, and asynchronously forwards filtered traffic to configured backends.

## Architecture

### Request Flow
```
Incoming Request → Immediate 202 Response
                ↓
Configuration Check → Filter → Queue for Processing
                                ↓
                      Background Task → Forward to Backend(s) → Collect Metrics
```

## Configuration

### Global Settings

- `timeout_seconds`: Request timeout for backend calls (default: 30)
- `debug_logging`: Enable debug logging (default: false)
- `max_request_size_mb`: Maximum request size in MB (default: 10)
- `num_workers`: Number of background workers for processing requests (default: 1, range: 1-100)

**Note**: Increasing `num_workers` can significantly improve throughput by allowing parallel processing of queued requests.

# How to run

```
docker build -t shadow-proxy .
docker run -it -p 8080:8080 -v $(pwd)/config.yaml:/app/config/config.yaml shadow-proxy
```