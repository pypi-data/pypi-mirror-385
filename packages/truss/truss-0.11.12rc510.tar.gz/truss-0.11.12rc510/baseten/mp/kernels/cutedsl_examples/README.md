# CuTeDSL examples

This repo contains example of Python CuTeDSL usage. Idea is to have simple,
specific and isolated examples that are easy resources to lookup when we need to
use these features/techniques in real world complex examples. These will also be
great learning resources for beginners.


## How to use

```sh
uv sync
uv run python src/test_tma_copy.py
```

### Run with container

When upgrading cuda version etc it may be easier to test in a container
(updating image as needed). 

ssh into container and execute examples from /workspace/src (mounted)

```sh
make run_image
docker exec -it cdsl bash
# On the container
python src/test_tma_copy.py
```