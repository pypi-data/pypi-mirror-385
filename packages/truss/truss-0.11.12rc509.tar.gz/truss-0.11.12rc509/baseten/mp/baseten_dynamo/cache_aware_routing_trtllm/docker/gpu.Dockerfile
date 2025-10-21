# [Baseten] Copied and modified from https://github.com/ai-dynamo/dynamo/blob/main/container/Dockerfile.tensorrt_llm
# Mainly to reduce number of layers to allow us to build on top.
ARG DYNAMO_IMAGE_BASE
ARG TRTLLM_BASE_IMAGE

FROM ${TRTLLM_BASE_IMAGE} AS irl_build
WORKDIR /workspace
COPY irl /workspace/irl
RUN pip install --no-cache-dir scikit-build-core nanobind
RUN --mount=type=cache,target=/workspace/irl/build pip install --no-cache-dir -v --no-build-isolation /workspace/irl

FROM ${TRTLLM_BASE_IMAGE} AS build

USER root

# Install utilities
RUN apt update -y && apt install -y git wget curl nvtop tmux vim

# [Baseten] We only need the nats and etcd clients, but to keep thing simple we
# install the server version to avoid changing too much away from the original
# Dockerfile in dynamo repo. nats
RUN wget --tries=3 --waitretry=5 https://github.com/nats-io/nats-server/releases/download/v2.10.24/nats-server-v2.10.24-amd64.deb && \
    dpkg -i nats-server-v2.10.24-amd64.deb && rm nats-server-v2.10.24-amd64.deb
# etcd
ENV ETCD_VERSION="v3.5.18"
RUN wget https://github.com/etcd-io/etcd/releases/download/$ETCD_VERSION/etcd-$ETCD_VERSION-linux-amd64.tar.gz -O /tmp/etcd.tar.gz && \
    mkdir -p /usr/local/bin/etcd && \
    tar -xvf /tmp/etcd.tar.gz -C /usr/local/bin/etcd --strip-components=1 && \
    rm /tmp/etcd.tar.gz
ENV PATH=/usr/local/bin/etcd/:$PATH

RUN pip install partial-json-parser openai jsonschema hf_xet truss-transfer==0.0.36 truss==0.11.12 blobfile xgrammar==0.1.23 openai-harmony==0.0.4
RUN pip install triton==3.3.1 --force-reinstall

COPY --from=irl_build /usr/local/lib/python3.12/dist-packages/irl_ext/ /usr/local/lib/python3.12/dist-packages/irl_ext/

COPY src /workspace/trtllm

RUN patch -d /usr/local/lib/python3.12/dist-packages/tensorrt_llm/ -p2 --input=/workspace/trtllm/trtllm.patch
RUN patch -d /usr/local/lib/python3.12/dist-packages/tensorrt_llm/ -p2 --input=/workspace/trtllm/trtllm_dsv3.patch
RUN patch -d /usr/local/lib/python3.12/dist-packages/tensorrt_llm/ -p2 --input=/workspace/trtllm/mla.patch
RUN cat /workspace/trtllm/irl.snippet >> /usr/local/lib/python3.12/dist-packages/tensorrt_llm/__init__.py


# [Baseten] Instead of building on top of this image, we only copy the necessary
# files, because this image is already at max allowed docker layers, making it
# impossible to build on top of it.
FROM ${DYNAMO_IMAGE_BASE} AS dynamo_image_base

FROM build AS dev_1
# DYNAMO_01
WORKDIR /workspace
COPY --from=dynamo_image_base /workspace/dist /workspace/dist
COPY --from=dynamo_image_base /workspace/lib /workspace/lib
COPY --from=dynamo_image_base /workspace/target /workspace/target

RUN mkdir -p /opt/dynamo/bindings/wheels && \
    mkdir -p /opt/dynamo/bindings/lib && \
    cp /workspace/dist/ai_dynamo_runtime*cp312*.whl /opt/dynamo/bindings/wheels/. && \
    cp /workspace/target/release/libdynamo_llm_capi.so /opt/dynamo/bindings/lib/. && \
    cp -r /workspace/lib/bindings/c/include /opt/dynamo/bindings/.

RUN pip install dist/ai_dynamo_runtime*cp312*.whl  && \
    pip install dist/ai_dynamo*any.whl


ENV DYNAMO_HOME=/workspace
ENV DYN_DISABLE_AUTO_GPU_ALLOCATION=1
WORKDIR /workspace/trtllm

# need to be in the last stage:
FROM build as dev_4
COPY --from=dynamo_image_base /opt/dynamo/wheelhouse /opt/dynamo/wheelhouse
RUN pip install /opt/dynamo/wheelhouse/ai_dynamo_runtime*cp312*.whl  && \
    pip install /opt/dynamo/wheelhouse/ai_dynamo*any.whl

COPY tests /workspace/tests
COPY bin /workspace/bin
ENV DYNAMO_HOME=/workspace
ENV PYTHONPATH=/workspace/trtllm:$PYTHONPATH
WORKDIR /workspace/trtllm
