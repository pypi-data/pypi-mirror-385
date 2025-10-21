# Briton

Details about Briton can be found at https://www.notion.so/ml-infra/Briton-c406c2470b5b4d57ad827ff533779e4f

At a high level, Briton serves trtllm engines via GRPC.

## How to

All common actions should be wired via make. Please refer to [Makefile](Makefile) for details.

Some important ones are listed below.

Briton functionality is closely tied to TensorRT-LLM version. We track this via
the git commit on [TensorRT-LLM repo](https://github.com/NVIDIA/TensorRT-LLM).
This is defined in the Makefile as the `TENSORRT_LLM_GIT_COMMIT` variable. This
variable can be and should be overridden correctly. Export this variable to use
this value in your session. Most briton images already export this variable for
convenience.

e.g.
`export TENSORRT_LLM_GIT_COMMIT=06c0e9b1ec38f981d023a223b212b312cfb62417`

### Bash prompt

It's good to have the TENSORRT_LLM_GIT_COMMIT indicated in bash prompt as this
environment variable is so important. Here's an example prompt:

```sh -> ~/.bashrc
update_prompt() {
    RESET="\[\033[0m\]"           # Reset color
    RED="\[\033[0;31m\]"          # Red
    GREEN="\[\033[0;32m\]"        # Green
    YELLOW="\[\033[0;33m\]"       # Yellow
    BLUE="\[\033[0;34m\]"         # Blue
    PURPLE="\[\033[0;35m\]"       # Purple
    CYAN="\[\033[0;36m\]"         # Cyan
    WHITE="\[\033[1;37m\]"        # White

    # Define the prompt ${TENSORRT_LLM_GIT_COMMIT:0:4} is the important part.
    # It includes first 4 chars of the commit in prompt.
    PS1="$GREEN\u$YELLOW@$RED\h $CYAN\w ${TENSORRT_LLM_GIT_COMMIT:0:4} $RESET\$ "
}

PROMPT_COMMAND=update_prompt
```

### make auto complete

Autocomplete for make is really useful. Put this into ~/.bashrc to install it for bash.

```sh -> ~/.bashrc
complete -W "\`grep -oE '^[a-zA-Z0-9_.-]+:([^=]|$)' ?akefile | sed 's/[^a-zA-Z0-9_.-]*$//'\`" make
```

### Build

`make build`

### Lint

`make lint`

### Run server

`make run_server`

Builds and runs the Briton server locally.

`make run_server_tp2`

To run server with a tensor parallelism 2 model.

### Image builders

`docker_build_*` target are for building various images. These images will be described shortly.
These target, and some others, require docker to be available.

### Testing

There are a lot of testing flows:

#### Unit tests

`make test`

#### server-client flow

`make test_server_client_flow`

Starts up the Briton server, then sends one request to it via a client.

#### run_python_client

`make run_python_client`

Runs a python client to send a request to Briton

#### run_truss_spec_dec

`make run_truss_spec_dec`

Builds a truss serving container for speculative decoding and runs in docker.
This assumes that one has ran `make run` in `engine-builder` directory to create engines to `briton/spec-dec-data-dir`

#### Load testing

There are 3 ways of testing with load.

##### C++

`make run_client`

or, to specify concurrency etc.

`make && ./build/client [options]`

Runs a C++ grpc client to send load to local Briton server. Allows sending a
bunch of concurrent requests. See `build/client -h` for options.

##### Python

`make run_python_load_client`

Similar to the C++ client above, sends a bunch of concurrent requests. Involves,
detokenization, so this is close to the truss server experience.

TODO(pankaj) Support concurrency and other options for the python client.

##### k6

`make load`

This load test seems to have worse performance than C++ or python clients.
Likely k6 is unable to send enough load and is the bottleneck. Needs more
digging, but for prefer the other two clients.

#### Truss testing

`make run_truss`

Runs a truss server locally on docker and invokes a single request. Useful for testing
the truss flow.

This can take a while, but is the most end-to-end flow here.

## Logging

We use grpc logging mechanism. Set log level via environment variable.
`export GRPC_VERBOSITY=debug`

Note that trtllm log level can be separate controlled.
`export TLLM_LOG_LEVEL=TRACE`
This will print all functions that are executed and can be very verbose.

## Tracer

Briton includes a low-overhead tracing system to help debug and analyze performance.

### Usage

To enable the tracer:

1. Set the environment variable:
   - `BRITON_TRACER_OUT`: Path for the final trace output file (e.g., `/shared/trace.bin`)

2. Run Briton/truss as you normally would.

3. Convert the binary trace output to CSV format for analysis:
   ```
   trace_to_csv /path/to/trace.bin /path/to/trace.csv
   ```

Example output:
```
StepId,Timestamp,RequestId,ThreadId
...
SEND_RESPONSE_start,1741390793694378687,22952008,17164424297733380889
SEND_RESPONSE_end,1741390793694383667,22952008,17164424297733380889
LOGITS_POST_PROCESSOR_start,1741390793695747164,22952007,17164424297733380889
APPLY_MASK_start,1741390793695750916,,17164424297733380889
APPLY_MASK_end,1741390793695767764,,17164424297733380889
LOGITS_POST_PROCESSOR_end,1741390793695768121,22952007,17164424297733380889
LOGITS_POST_PROCESSOR_start,1741390793695768411,22952009,17164424297733380889
APPLY_MASK_start,1741390793695772436,,17164424297733380889
APPLY_MASK_end,1741390793695779871,,17164424297733380889
...
```

The tracer is designed with minimal performance impact, making it suitable for use in production environments when debugging performance issues.

## Development flow

There are two ways of developing Briton.
1. Environment where docker is available
  - e.g. Raw GCP or AWS instance
2. Docker is not available
  - e.g. a Pod on k8s cluster

Second one is the preferred way now. Please follow https://github.com/basetenlabs/benchmarks/tree/main/gpu-dev/runbooks/a100-dev-env
Then follow the following steps:
1. Clone baseten repo
2. cd briton
3. make run_devel_container
4. Once inside the devel container, start docker
```sh
service docker start
```

Devel container has docker installed, it just needs to be started.

### With docker

- Clone baseten repo at /root/shared/baseten
- Start up a development container:
`make run_devel_container`

- SSH into the development container and work there.
`docker exec -it briton_dev_${TENSORRT_LLM_GIT_COMMIT}`

The development container should have all the needed tools. To check that
everything is solid:

```sh
cd /shared/baseten/briton
# test uses gated llama3.1 repository, so authenticate with huggingface
huggingface-cli login
make test_server_client_flow
```

You probably want to set up vscode tunnel etc.
If you find yourself needed to install anything then consider adding it to [devel image](docker/devel.Dockerfile).

If you get an error indicating that the devel image doesn't exist then you can build it:
`make docker_build_devel`

### Without docker

- You'd want to make sure apppriate devel image is available on dockerhub. e.g.
  `baseten/briton-devel:06c0e9b1ec38f981d023a223b212b312cfb62417`
- Start a pod with that image and ssh into it
- Develop here, noting that any commands requiring docker won't work here.
  - While this will be a bit limited you should be able to develop Briton for the most part.

### Summary of Other Useful Common Commands

#### Outside the Docker container
```bash
# change directory to briton
cd briton

export TENSORRT_LLM_GIT_COMMIT=v0.13.0
export TENSORRT_LLM_SRC_OPEN_GIT_COMMIT=4fd8a10

# run truss_model
make run_truss

# run truss_model tp 2
make run_truss_tp2

# british server dev setup
make run_devel_container_bg

# tail truss_model log
docker logs -f truss_model

# grep log (e.g. excllude INFO)
docker logs -f truss_model | grep -v INFO
```

#### Inside the briton_dev Docker container
```bash
docker exec -it $(docker ps | grep briton_dev | awk '{print $1}') /bin/bash

cd /shared/baseten/briton

# build server
make build

# ln compile_commands.json
# use clangd for sematic indexing
ln -s build/compile_commands.json .
```

#### Inside the truss_model Docker container
```bash
docker exec -it $(docker ps | grep truss_model | awk '{print $1}') /bin/bash

# setup baseten eval
cd /shared/baseten/briton/baseten_eval
pip3 install poetry
poetry install

# run eval
poetry run eval --config example_configs/llama3_8b_gsm8k_config.yaml
poetry run eval --config example_configs/llama3_8b_mmlu_config.yaml
poetry run eval --config example_configs/llama3_8b_mmlu_pro_config.yaml
poetry run eval --config example_configs/llama3_8b_bench_serving_config.yaml

# ln Briton
# After any modifications and compilations in briton_dev, truss_model will be automatically updated
rm -rf $(which Briton)
ln -s /shared/baseten/briton/build/Briton /usr/local/briton/bin/Briton

# restart
ps aux | grep main.py | grep -v grep | awk '{print $2}' | xargs kill -9
ps aux | grep Briton | grep -v grep | awk '{print $2}' | xargs kill -9
```

```bash
vim /app/main.py
```
