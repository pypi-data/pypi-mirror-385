# Provides development environment for Briton.
# Includes grpc, protobuf, cmake and other utilities that are needed
# for developing Briton, but not for serving.
#
# It's ok for this image to be a bit larger as this is only used for
# development and not serving.
# Building grpc is a bit time consuming.
# TODO(pankaj) Consider moving grpc build to a separate stage and copy
# over the binaries, to avoid building it for every trtllm version.
#
# Publish this as baseten/briton-devel:${TENSORRT_LLM_GIT_COMMIT} as follows
# docker build -t baseten/briton-devel:${TENSORRT_LLM_GIT_COMMIT} -f devel.Dockerfile .
# docker push baseten/briton-devel:${TENSORRT_LLM_GIT_COMMIT}

ARG TENSORRT_LLM_GIT_COMMIT
FROM baseten/briton-base:${TENSORRT_LLM_GIT_COMMIT}

RUN : 🚀🚀🚀🚀🚀🚀  Building Briton Development-Min Docker Image  🚀🚀🚀🚀🚀🚀

RUN apt update \
 && apt install -y wget cmake build-essential autoconf libtool pkg-config ninja-build lld \
 && rm -rf /var/lib/apt/lists/* \
 && apt-get clean

# Install grpc
RUN git clone --recurse-submodules -j$(nproc) -b v1.62.0 --depth 1 --shallow-submodules https://github.com/grpc/grpc \
  && cd grpc \
  && mkdir -p cmake/build \
  && cd cmake/build \
  && cmake -DgRPC_INSTALL=ON -DgRPC_BUILD_TESTS=OFF ../.. \
  && make -j$(nproc) \
  && make install \
  && cd ../../.. \
  && rm -rf grpc

# rust
RUN apt update \
 && apt install -y wget curl clang-format tmux htop jq iftop lsof libssl-dev libpq-dev \
 && rm -rf /var/lib/apt/lists/* \
 && apt-get clean
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"
RUN rustc --version && cargo --version
