# This dockerfile is used to create an environment where briton c++ code can be
# executed to run inference using a TensorRT-LLM engine.
#
# This dockerfile depends on baseten/trtllm-wheel:${TENSORRT_LLM_GIT_COMMIT}-${TENSORRT_LLM_SRC_OPEN_GIT_COMMIT}
#
# For any trtllm commit, branch or tag, this needs to be built using `Build TRT-LLM wheel`
# github action on this github repo. That job needs to be run on a self
# hosted runner with at least 64 cores or it will take many hours and may fail.
#
# These images should be created once for specific TensorRT-LLM version and
# pushed to dockerhub and used from there.
#
# The image with tag should be of the form:
# baseten/briton-base:${TENSORRT_LLM_GIT_COMMIT} e.g.
# baseten/briton-base:5fa9436e17c2f9aeace070f49aa645d2577f676b
#
# TODO(pankaj) Infer CUDA_VERSION automatically based on TENSORRT_LLM_GIT_COMMIT
# Values of these arguements should be picked up as follows:
# 1. Start with TENSORRT_LLM_GIT_COMMIT
# 2. Pick up CUDA_VERSION from CUDA_VER value in install_tensorrt.sh file in the
#    trtllm repo
#
# To build and push:
# docker build -t baseten/briton-base:${TENSORRT_LLM_GIT_COMMIT} . -f base.Dockerfile
# docker push baseten/briton-base:${TENSORRT_LLM_GIT_COMMIT}

ARG UBUNTU_VERSION=24.04
ARG CUDA_VERSION=12.9.0
ARG TENSORRT_LLM_GIT_COMMIT

FROM baseten/trtllm-wheel:${TENSORRT_LLM_GIT_COMMIT} as base

FROM nvidia/cuda:${CUDA_VERSION}-devel-ubuntu${UBUNTU_VERSION}

RUN : 🚀🚀🚀🚀🚀🚀  Building Briton Base Docker Image  🚀🚀🚀🚀🚀🚀

RUN : Remove compat folder to avoid conflicts with host GPU drivers
RUN rm -rf /usr/local/cuda-12.9/compat
ENV NVIDIA_DISABLE_REQUIRE=true

ARG TENSORRT_LLM_GIT_COMMIT

# libs
COPY --from=base /src/tensorrt_llm/tensorrt_llm/libs/* /usr/local/briton/libs/
# [IMPORTANT] The rename is needed
RUN ln -s /usr/local/briton/libs/libnvinfer_plugin_tensorrt_llm.so /usr/local/briton/libs/libnvinfer_plugin_tensorrt_llm.so.10

# includes
COPY --from=base /src/tensorrt_llm/cpp/tensorrt_llm /usr/local/briton/TensorRT-LLM/cpp/tensorrt_llm
COPY --from=base /src/tensorrt_llm/cpp/include /usr/local/briton/TensorRT-LLM/cpp/include
COPY --from=base /usr/local/tensorrt/include /usr/local/briton/tensorrt/include

RUN apt update \
  && apt install -y curl git git-lfs vim wget openmpi-bin libopenmpi-dev python3-pip binutils-dev \
  && rm -rf /var/lib/apt/lists/* \
  && apt-get clean

# As of v0.20.0.rc0, the cuda repos in the base image conflict with those in the install_tensorrt.sh script
RUN rm -f /etc/apt/sources.list.d/cuda*.list \
    && rm -f /etc/apt/trusted.gpg.d/cuda*.gpg \
    && rm -f /usr/share/keyrings/cuda*.gpg

# Install TensorRT
RUN rm -rf /usr/local/tensorrt || true
RUN curl -o /tmp/install_tensorrt.sh -L https://raw.githubusercontent.com/NVIDIA/TensorRT-LLM/${TENSORRT_LLM_GIT_COMMIT}/docker/common/install_tensorrt.sh \
  && chmod +x /tmp/install_tensorrt.sh \
  && export ENV=${ENV:-/etc/shinit_v2} \
  && export PIP_BREAK_SYSTEM_PACKAGES=1 \
  && /tmp/install_tensorrt.sh

ENV LD_LIBRARY_PATH=/usr/local/tensorrt/lib:$LD_LIBRARY_PATH


# Set LD_LIBRARY_PATH
ENV LD_LIBRARY_PATH=/usr/local/briton/libs/:/usr/lib/x86_64-linux-gnu/:$LD_LIBRARY_PATH
ENV TENSORRT_LLM_GIT_COMMIT=$TENSORRT_LLM_GIT_COMMIT
