# Node Warmer

DaemonSet for pre-downloading models to warm up Kubernetes nodes.

## Usage

```bash
# Build and push to Docker Hub
make build-push

# Build with custom tag
IMAGE_TAG=v1.0.0 make build-push
```

## Configuration

- **HF Token**: `HUGGING_FACE_HUB_TOKEN` env var
- **Models**: YAML config at `/config/models.yaml`
- **Cache**: HuggingFace cache at `/root/.cache/huggingface`

## Docker Hub

Image: `baseten/node-warmer:latest` 
