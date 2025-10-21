# Needs to be run with baseten as the context
# Needs both briton-base and briton-devel images to be built for this
# TENSORRT_LLM_GIT_COMMIT.
#
# cd baseten/briton
# Publish this as baseten/briton-server:${TENSORRT_LLM_GIT_COMMIT} as follows
# docker build -t baseten/briton-server:${TENSORRT_LLM_GIT_COMMIT} -f docker/devel.Dockerfile .
# docker push baseten/briton-server:${TENSORRT_LLM_GIT_COMMIT}

ARG TENSORRT_LLM_GIT_COMMIT
FROM baseten/briton-devel-min:${TENSORRT_LLM_GIT_COMMIT} as devel
############################################################
# Install python3.10 (for truss compatibility) and dependencies
############################################################
# TODO(mahmoud): move this to base.Dockerfile when upgrading trtllm.
RUN --mount=type=bind,source=docker/common,target=/common \
    /bin/bash -c "cd /common && ./install_deps.sh"

RUN : 🚀🚀🚀🚀🚀🚀  Building Briton Server Docker Image  🚀🚀🚀🚀🚀🚀

############################################################
# Build C++ Briton
############################################################
ENV LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu/:/usr/local/briton/libs/:/usr/local/lib:$LD_LIBRARY_PATH
ENV LD_LIBRARY_PATH=/usr/local/cuda-12.5/compat/:$LD_LIBRARY_PATH
COPY . /briton
RUN cd /briton && make clean && make build

FROM baseten/briton-base:${TENSORRT_LLM_GIT_COMMIT}
############################################################
# Install python3.10 (for truss compatibility) and dependencies
############################################################
# TODO(mahmoud): move this to base.Dockerfile when upgrading trtllm.
RUN --mount=type=bind,source=docker/common,target=/common \
    /bin/bash -c "cd /common && ./install_deps.sh"

COPY --from=devel /briton/build/Briton /usr/local/briton/bin/Briton
COPY --from=devel /briton/build/lib*.so /usr/local/briton/libs/
COPY --from=devel /briton/build/trace_aggregator /usr/local/briton/bin/trace_aggregator

# put the hot_reload library in the bin directory so it can be found easily by python for LD_PRELOAD
RUN ln -s /usr/local/briton/libs/libhot_reload.so /usr/local/briton/bin/libhot_reload.so

ENV PATH=/usr/local/briton/bin/:$PATH

# Install openssh server
RUN apt-get update && apt-get install -y --no-install-recommends \
    openssh-server \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /var/run/sshd

# Create venv and make default
ENV VIRTUAL_ENV=/usr/local/briton/venv
RUN python3.10 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"


############################################################
# Install Briton python package
############################################################
COPY --from=devel /briton/python/briton /tmp/pybriton
RUN pip install poetry && \
    cd /tmp/pybriton && \
    poetry build && \
    pip install dist/*.whl && \
    rm -rf /tmp/pybriton


############################################################
# Install C++ extension
############################################################
COPY --from=devel /briton/build/briton_bind.cpython-*.so $VIRTUAL_ENV/lib/python3.10/site-packages/briton/
