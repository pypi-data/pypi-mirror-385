# Baseten dynamo trtllm

Code under src is mostly copied from https://github.com/ai-dynamo/dynamo/tree/main/examples/tensorrt_llm

# Running standalone

In this dir, run the dynamo routing 
```bash 
PRIMARY_DYNAMO_GPUS=0 make docker_run_standalone 
```

```bash
uv pip install . --group test --group dev 
uv run python -m pytest
```

Both commands above, including teardown are packaged as single command.
```
PRIMARY_DYNAMO_GPUS=0 ./bin/pytest_standalone.sh
```

## Running llama / dsv3
```
export PRIMARY_DYNAMO_GPUS=0,1,2,3,4,5,6,7
DYNAMO_CONFIG=llama3 make docker_compose_up
```

# Pre-commit

Install the pre-commit hooks by running `poetry run pre-commit install`
