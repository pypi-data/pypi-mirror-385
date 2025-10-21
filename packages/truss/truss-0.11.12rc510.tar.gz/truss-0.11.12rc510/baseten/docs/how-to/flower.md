# Flower

[Flower](https://github.com/mher/flower) is a tool that monitors celery status.

Repository: https://github.com/mher/flower

# Build flower image

```sh
git clone https://github.com/mher/flower
cd flower
docker buildx build --platform=linux/amd64,linux/arm64 . -t baseten/flower --push
```

# Access Flower hosted on K8s to monitor celery

1. Port forward flower port to localmachine

```sh
kubectl -n baseten port-forward svc/celery-flower 5555:5555
```

2. Access flower on http://localhost:5555
