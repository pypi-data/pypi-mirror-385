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
FROM baseten/trtllm-wheel:${TENSORRT_LLM_GIT_COMMIT} as wheel
FROM baseten/briton-devel-min:${TENSORRT_LLM_GIT_COMMIT}
############################################################
# Install python3.10 (for truss compatibility) and dependencies
############################################################
# TODO(mahmoud): move this to base.Dockerfile when upgrading trtllm.
RUN --mount=type=bind,source=docker/common,target=/common \
    /bin/bash -c "cd /common && ./install_deps.sh"

RUN : 🚀🚀🚀🚀🚀🚀  Building Briton Development Docker Image  🚀🚀🚀🚀🚀🚀

# General utilities are here separately so we can keep adding to them
# without having to build grpc above to save time.
RUN apt update \
 && apt install -y wget curl clang-format tmux htop jq iftop lsof nano \
 && rm -rf /var/lib/apt/lists/* \
 && apt-get clean

# Install docker
RUN apt update \
  && apt install -y ca-certificates gnupg lsb-release \
  && mkdir -p /etc/apt/keyrings \
  && curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg \
  && echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null \
  && apt update \
  && apt install -y docker-ce-cli docker-ce containerd.io \
  && apt install -y nvidia-container-toolkit \
  && rm -rf /var/lib/apt/lists/* \
  && sed -i 's/^\(\s*\)ulimit/\1echo omitted: ulimit/' /etc/init.d/docker \
  && ulimit -n 65536 \
  && echo '{"data-root": "/persistent/var/lib/docker"}' > /etc/docker/daemon.json \
  && apt-get clean

# Install k6
RUN wget -q https://github.com/grafana/k6/releases/download/v0.47.0/k6-v0.47.0-linux-amd64.tar.gz \
  && mkdir -p /tmp/k6_holder \
  && tar -xvf k6-v0.47.0-linux-amd64.tar.gz -C /tmp/k6_holder --strip-components=1 \
  && mkdir -p /usr/bin \
  && cp /tmp/k6_holder/k6 /usr/bin/

RUN export PIP_BREAK_SYSTEM_PACKAGES=1 && pip install transformers hf_transfer cpplint

ENV HF_HUB_ENABLE_HF_TRANSFER=true

RUN cd /root \
  && curl -Lk 'https://code.visualstudio.com/sha/download?build=stable&os=cli-alpine-x64' --output vscode_cli.tar.gz \
  && tar -xf vscode_cli.tar.gz

# gptManagerBenchmark
COPY --from=wheel /src/tensorrt_llm/cpp/build/benchmarks/gptManagerBenchmark /usr/local/briton/bin/gptManagerBenchmark
ENV PATH=$PATH:/usr/local/briton/bin

# INSTALL PYTHON POETRY. Use the .tool-versions in the briton directory.
ARG ASDF_BRANCH="v0.10.2"
RUN echo "ASDF_BRANCH: $ASDF_BRANCH"
ENV HOME=/root
WORKDIR /root

# Copy all of the the setup and shell config files.
COPY docker/dev_env_setup/ $HOME/
# Copy the asdf config files to the home directory for the initial setup.
COPY .tool-versions $HOME/

# Python dependencies.
RUN apt update \
 && apt install -y libbz2-dev libncursesw5-dev libffi-dev liblzma-dev libreadline-dev libsqlite3-dev \
 && rm -rf /var/lib/apt/lists/* \
 && apt-get clean

### Install ASDF to ease installation of Poetry.
RUN git clone https://github.com/asdf-vm/asdf.git $HOME/.asdf --branch ${ASDF_BRANCH} \
 && echo '. $HOME/.environment' | tee -a $HOME/.bashrc >> $HOME/.zshrc \
 && echo '. $HOME/.aliases' | tee -a $HOME/.bashrc >> $HOME/.zshrc \
 && export PATH=$HOME/.asdf/bin:$HOME/.asdf/shims:$PATH \
 && asdf plugin add python \
 && asdf plugin add poetry \
 && cd $HOME \
 && asdf install python \
 && asdf install
ENV PATH=$HOME/.asdf/bin:$HOME/.asdf/shims:$PATH

# Do the rest of the setup using a script.
RUN /bin/bash $HOME/dev_env_setup.sh
