# To build & push this image, from this directory
#
#   Make sure you do `docker login` with the basetenservice service account
#   Then run:
#   - docker buildx build . -t baseten/buildkit:v6 --platform=linux/amd64 -f buildkit.Dockerfile  --push
#

FROM moby/buildkit:v0.12.2

RUN apk --no-cache add curl bash python3 py3-pip
RUN pip3 install --no-cache-dir awscli
RUN curl -sSL https://sdk.cloud.google.com | sh
RUN wget -q https://amazon-ecr-credential-helper-releases.s3.us-east-2.amazonaws.com/0.7.0/linux-amd64/docker-credential-ecr-login -O /bin/docker-credential-ecr-login
RUN chmod a+x /bin/docker-credential-ecr-login
ENV PATH="/root/google-cloud-sdk/bin:${PATH}"

# Install Depot CLI
RUN curl -L https://depot.dev/install-cli.sh | sh -s 2.100.0
ENV PATH="/root/.depot/bin:${PATH}"
