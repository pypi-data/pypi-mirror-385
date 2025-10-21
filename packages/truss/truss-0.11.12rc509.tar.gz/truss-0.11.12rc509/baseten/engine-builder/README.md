# engine-builder
This application provides the general framework for optimizing a model for a downstream deployment on Baseten infra. Practically, this takes the shape of building a TRT-LLM engine given a user provided build config, and uploading build artifacts to remote storage to be fetched by the runtime machine. The structure of the project is as follows:

```sh
├── builder
│   └── models
│       └── trt_llm
│           └── model_utils
├── secrets
└── tests
    └── configs 
```
## builder
This directory contains checkpoint conversion and engine building logic for a set of supported model architectures and build configuration

### builder.models
This directory contains the specifications for the checkpoint conversion and engine build for models as a Builder class – inheriting from the `GenericModelBuilder` ABC. At the time of writing, the only implemented builder class is the `TRTLLMEngineBuilder` with support for Llama architectures (including Mistral), Deepseek, and Whisper.

### builder.upload
This module contains the implementation for uploading the build job artifacts and a [BasetenPointer manifest](https://www.notion.so/ml-infra/LMS-Bptr-resolver-approach-e6094f3e7b4148758aed7d281071b2cb?pvs=4) to cloud storage. Namely, we upload the TRT-LLM engines and a manifest file to S3. This manifest is added to the serving image built in the downstream [container image build](https://github.com/basetenlabs/baseten/blob/d78206f85f7350f7b2ba7d5df188841c7354c72e/backend/deployment/tekton/build_tekton_configs/model_build_pipeline_run.yaml.jinja#L123-L156) and is ultimately referenced to [pull the engines ](https://github.com/basetenlabs/truss/blob/84ef60848693bdcda3239def24a8f57fde07490b/truss/templates/shared/lazy_data_resolver.py#L14) on the runtime machine. 

## Build configuration
The supported build configuration options come from types in the [Truss library](https://github.com/basetenlabs/truss/blob/main/truss/config/trt_llm.py). Please introspect the `TRTLLMQuantizationType` and `TrussTRTLLMPluginConfiguration` for more detailed usage. Most of these configurations are mapped directly to their upstream TRT-LLM analogs.

The interface for the build configuration is governed by the Truss library – which is a pinned dependency in the `engine-builder` project.


## dev setup
Get a GPU machine to work on – one way is by following this runbook: https://github.com/basetenlabs/benchmarks/tree/main/gpu-dev/runbooks/a100-dev-env.
Once you have a pod, to test locally:
```sh
# Clone the baseten repo, this requires setting up github auth and using the corresponding protocol for cloning (HTTPS / SSH)
git clone git@github.com:basetenlabs/baseten.git
cd engine-builder

# ASDF (only need to do once)
export ASDF_BRANCH="v0.10.2"
git clone https://github.com/asdf-vm/asdf.git $HOME/.asdf --branch ${ASDF_BRANCH}
# Add running of asdf.sh to .bashrc/.zshrc, but only if script exists and
# it was not already added to the rc file.
MAYBE_RUN_ASDF="
if [ -f \$HOME/.asdf/asdf.sh ]; then
    . \$HOME/.asdf/asdf.sh;
fi
"
if ! grep -q "${MAYBE_RUN_ASDF}" $HOME/.bashrc; then
    echo "${MAYBE_RUN_ASDF}" >> $HOME/.bashrc
fi
if ! grep -q "${MAYBE_RUN_ASDF}" $HOME/.zshrc; then
    echo "${MAYBE_RUN_ASDF}" >> $HOME/.zshrc
fi

export PATH=$HOME/.asdf/bin:$HOME/.asdf/shims:$PATH 
asdf plugin add python 
asdf plugin add poetry
# END ASDF

# From `engine-builder` as the project root use the following make target to setup your environment for development
make setup

# Specify location to build engine, engine is created at ${APP_HOME}/engines
make run

# Specify a configuration to build engine with
make run CONFIG_FILE=/path/to/config_yaml

# There exists a sample config for testing speculative decoding builds
make run CONFIG_FILE=./tests/test_config.yaml

# Run tests with
make test_unit
CUDA_VISIBLE_DEVICES=$GPU_ID make test_integration
```

**Note: TRT-LLM 0.13.0 has an improper pin on transformers, so we use pip to override the transformers version in Docker, we should be able to remove this in future releases. See the Dockerfile for details**

For containerized testing – use docker from `baseten` root:
```sh
# from baseten root
IMAGE_TAG=$(poetry version -C engine-builder/ | cut -d ' ' -f 2)
docker buildx build --network host -t baseten/trtllm-engine-builder:$IMAGE_TAG -f engine-builder/Dockerfile --output oci-mediatypes=true,compression=estargz,force-compression=true,type=image .
docker run -it --gpus all -v "$(pwd)"/engine-builder/tests:/app/tests  -v "$(pwd)"/engine-builder/secrets:/secrets baseten/trtllm-engine-builder:$IMAGE_TAG /bin/bash
# From inside the running container
export CUDA_VISIBLE_DEVICES="0,1"
python3 -m builder.main --config /app/tests/test_config.yaml

# once above is finished, continue to push your built image
docker push baseten/trtllm-engine-builder:$IMAGE_TAG 
docker tag baseten/trtllm-engine-builder:$IMAGE_TAG baseten/trtllm-engine-builder:$IMAGE_TAG.integration
docker push baseten/trtllm-engine-builder:$IMAGE_TAG.integration
```

Keep in mind that some builder flows can only be validated on specific hardware (e.g. FP8 quantization on Grace-Hopper architectures). In this case, create a pod for testing your built images after developing on A100 boxes.

An example pod spec for H100:2 is as follows:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: h100-engine-builder-justin
  namespace: baseten-trt-dev
spec:
  imagePullSecrets:
    - name: docker-registry
  containers:
  - name: container
    image: baseten/trtllm-engine-builder:0.16.0.post4
    command: ["sleep", "infinity"]
    resources:
      limits:
        nvidia.com/gpu: 2
  nodeSelector:
    baseten.co-gpu-type: nvidia-h100-80gb
    nvidia.com/gpu.product: NVIDIA-H100-80GB-HBM3
```
which can be applied:
```sh
kubectl apply -f PATH_TO_POD_SPEC
```

## Contribution guide
TRT-LLM is a rapidly evolving package that regularly introduces new features and API breaks. Historically, the most reliable way to implement feature support for new models, quantization formats, and additional features is to run through the `TensorRT-LLM/examples` for walkthroughs of how exactly to build engines that leverage particular features. It is important to check out the commit that correlates to the builder `tensorrt_llm` python package is pinned to.

For example, when using `tensorrt_llm-0.12.0.dev2024072301` make sure to check out the view of the repository at 07/23/2024 to ensure compatibility by referencing the [commits to the `main` branch](https://github.com/NVIDIA/TensorRT-LLM/commits/main/)

```sh
git clone git@github.com:NVIDIA/TensorRT-LLM.git
cd TensorRT-LLM
git checkout 0d5ffae9a79d70e45c7e03e52756476dd6645560 # commit from 07/23/2024
```

From there, reproduce the scripts by referencing the model README (e.g. `examples/llama/README.md`) that are used to generate said engine and trace through and replicate the process in this application. For example, to implement AWQ quantization for models in the Llama family, one should reference the [`README`](https://github.com/NVIDIA/TensorRT-LLM/blob/main/examples/llama/README.md#groupwise-quantization-awqgptq).

### Truss changes
When making changes to the build configuration interface, one must make changes in Truss, publish a package version, and change the pin in the engine builder project to be able to use the new interface. For testing a dev version of truss – you can simply specify a git branch or sha as the version to pin in the builder pyproject.toml. Documentation for how to release Truss can be found in [Notion](https://www.notion.so/ml-infra/Release-Truss-Versions-bc78f4e5b62b4f4389bc46748db955db?pvs=4).

### TRT-LLM version upgrades
TRT-LLM version upgrades are unfortunately not a painless process. Upgrades can potentially require updating the parent image, underlying tensorrt versions, and updating stale code. When making changes to the utilized TRT-LLM version, ensure that the associated tensorrt_libs, tensorrt_bindings, and tensorrt version are pinned as well, by referring to the [tensor-llm repo requirements.txt](https://github.com/NVIDIA/TensorRT-LLM/blob/main/requirements.txt). Additionally, make sure that [quantization requirements](https://github.com/NVIDIA/TensorRT-LLM/blob/main/examples/quantization/requirements.txt) are also kept in sync. Check the comments in pyproject.toml for more details.

### Changing the engine builder image
After building and pushing the docker container image to dockerhub.
1. Test that the new builder image works, by modifying the [dynamic constance config](https://app.baseten.co/billip/constance/config/):
    - Update `ORGANIZATION_TRT_LLM_BUILDER_IMAGE_OVERRIDES` mapping for the test org and validate a deploy for a model that uses the builder flow.
    - After testing the changes, update the `TRT_LLM_BUILDER_IMAGE_URI` in [constance](https://app.baseten.co/billip/constance/config/) to propagate the change globally for that environment.
        - Make sure to make a follow up change to `TRT_LLM_BUILDER_IMAGE_URI` in `backend/baseten/settings/base.py` to persist the upgrade in code. 
        
        **Once the deploy with the settings change lands, make sure to go back and reset to default in constance**
