# Workload Optimize - Accumulator & Uploader

This guide explains how to set up and run the **Accumulator** and **Uploader** services using **Redpanda (Kafka)**

---

## **Prerequisites**

Ensure you have the following installed:

- **Go 1.23+**
- **Redpanda (Kafka alternative)** → `brew install redpanda kaf`
- **Docker** -> used for running Redpanda

---

## **Step 1: Start Redpanda (Kafka)**

Redpanda is a Kafka-compatible event streaming platform.

```sh
brew install redpanda-data/tap/redpanda
brew install kaf
rpk container start -n 3  # Start a 3-node Redpanda cluster
Verify Redpanda is running:
rpk cluster health
```

## **Step 2: Start the Accumulator**

- The Accumulator collects records from FluentBit and deduplicates them before sending them to Kafka.

```sh
go run cmd/accumulator/main.go --configPath ././config/accumulator/
```

## **Step 3: Start Uploader**

- The Uploader reads records from Kafka and uploads them to S3 (S3 uploader needs to be implemented).

```sh
go run cmd/uploader/main.go --configPath ././config/uploader
```

## **Step 4: Send test payload**

- Send json nl delimited payload to Accumulator running on port 8080.

```json lines
{
  "image": "aws-us-west-2-vh3.registry.staging.baseten.co/aws/baseten/baseten-custom-model:ccd12f99ef567fb405cf545fd1c8510a56eda116669ae87b8ca4e4f833aad3f2",
  "path": "usr/local/lib/python3.10/dist-packages/pyarrow/__pycache__/_compute_docstrings.cpython-310.pyc",
  "manifestDigest": "sha256:1de4ec3046bbb6715d65a4c7ae9c0dd346673160c7c50a5a621f4e926f95c940",
  "layerIndex": 27
}
{
  "image": "index.docker.io/baseten/b10cp@sha256:1a24ba919abaad297e0e4d3a29bab7d488ead9c1d5f5cf117242651d60de494a",
  "path": "usr/local/lib/python3.10/dist-packages/transformers/models/phobert/__pycache__/__init__.cpython-310.pyc",
  "manifestDigest": "sha256:bars",
  "layerIndex": 12
}
```

```sh
curl -d @payload.json http://127.0.0.1:8080/records
```

## Debugging / Troubleshooting

[kaf](https://github.com/birdayz/kaf) config file located in `~/.kaf/config.yaml`

```yaml
- name: local
  brokers:
    - 127.0.0.1:57277
```

```sh
# List all topics:

rpk topic list

kaf -c local consume workload-optimize_test-plane_stargzoptimizerecord -f
```
