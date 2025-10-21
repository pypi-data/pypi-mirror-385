# Baseten Embeddings Inference Runtime (BEI-Runtime)

Baseten Embeddings Inference is a fork of text-embeddings-inference, originally developed by Huggingface. 

It contains of two portions:
- https://github.com/basetenlabs/bei - "router" containing the Dockerfile + Rust (hyper, tokio, PyO3) stack. It performs queueing, request validation, batching, and a Backend PyO3 interface, fullfilling the backend trait.
- this project "trt_tei_runtime", which is a python package that is deployed inside the python side BEI code, performing the TensorRT. This repo also contains the only tests for the runtime and engine-builder.

### BEI-Router:
- Development is done here https://github.com/basetenlabs/bei
    - adding a custom PyO3; called "bei" backend https://github.com/basetenlabs/bei/pull/12 . It uses Rust -> python bindings
    - adding a custom gRCP; called "python" backend https://github.com/basetenlabs/bei/tree/baseten/backends/python
- BEI performs dynamic batching within Rust. 

### trt_tei_runtime
- python libary using plain tensorrt 10.7 bindings
- works with GPTAttention (Causal/Bidirectional, variable window len, feasible) or BertAttention (never uses KV Caches)

## Docs
### Install, Development, Testing

All tests require GPU and make use of the engine-builder test. 
All models must have snapshot tests + All models running in prod need a covering case.

```bash
# installs asdf
make setup 
# run slow and fast unit tests
make test_unit
make test_integration
```

### Release Python Package

Currently, the release is `manually` distributed via `./dist/*.whl`, the wheel is copied over to https://github.com/basetenlabs/bei manually. 
Keep any .whl tracked in git immutable, and always commit git + source code together.

```bash
make wheel && git add* && git commit -m "new release"
```

## Building a new docker release candidate (BEI-Router with trt_tei_runtime backend)

See command and docs in [BEI-Router](https://github.com/basetenlabs/bei) with `trt_tei_runtime` backend

## Cycle / validate a release

For embedding models:
```bash
make run_embed # starts the docker server, building `./release_matrix_cfg/builder_config_embed.yaml`
# unit test, latency and throughput tests
make benchmark_embed
```

For reranker models:
```bash
make run_reranker # starts the docker server, building `./release_matrix_cfg/builder_config_rerank.yaml`
# unit test, latency and throughput tests
make benchmark_embed
```