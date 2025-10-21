ARG UBUNTU_VERSION=24.04
ARG CUDA_VERSION=12.9.0
ARG TENSORRT_LLM_GIT_COMMIT

FROM nvidia/cuda:${CUDA_VERSION}-devel-ubuntu${UBUNTU_VERSION}

ARG TENSORRT_LLM_GIT_COMMIT
ENV TENSORRT_LLM_GIT_COMMIT=${TENSORRT_LLM_GIT_COMMIT}

RUN : 🚀🚀🚀🚀🚀🚀  Building Briton Engine Builder Docker Image  🚀🚀🚀🚀🚀🚀

RUN apt-get update && apt-get install -y \
  python3 python3-dev python3-venv wget git libopenmpi-dev

RUN python3 -m venv /venv && \
  . /venv/bin/activate && \
  pip install --upgrade pip

ENV PATH="/venv/bin:$PATH"
ENV VIRTUAL_ENV="/venv"

RUN VERSION=$(wget -qO - https://raw.githubusercontent.com/NVIDIA/TensorRT-LLM/${TENSORRT_LLM_GIT_COMMIT}/tensorrt_llm/version.py | grep __version__ | awk '{print $NF}' | sed 's/^"\(.*\)"$/\1/') \
  && pip install --extra-index-url https://pypi.nvidia.com/ tensorrt_llm==$VERSION hf_transfer

RUN mkdir -p /app \
  && cd /app \
  && git clone https://github.com/NVIDIA/TensorRT-LLM.git \
  && cd TensorRT-LLM \
  && git checkout ${TENSORRT_LLM_GIT_COMMIT}
