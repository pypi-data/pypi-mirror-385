# Docker

We use 2 places to host docker images
- AWS Container repository, only private stuff, only the CI & django app pushes to it
- Docker hub https://hub.docker.com/orgs/baseten, private and public images, CI and Humans have access to it

## Login

1. Create a docker hub account (if you don't already have one) - [Docker hub](https://hub.docker.com/)
2. Login to that docker account on your computer `docker login -u <username>` or using the desktop application
3. Give your docker user name to #infra team and they'll add you to our dockerhub organization https://hub.docker.com/orgs/baseten It can be found

eg: `docker login -u pastjean`

## Building and pushing an image


Multiplatform (2 parallel builds):  `docker buildx build --platform=linux/amd64,linux/arm64 <context> -t baseten/<name>:<version>`

AMD only (some python libraries don't support arm): `docker buildx build --platform=linux/amd64 <context> -t baseten/<name>:<version>`

- `context`: is the directory where the docker content is run from
- `-f <dockerfile location>`: directory where the dockerfile is, default: current directory
- `-t <tag>`: the tag to tag your image, format: `[hub url]/[org]/<repository>:<versiontag>`
- `--platform=<comma separated platform list>`: the platforms to build for, default: your current host platform (eg: m1 laptops is linux/arm64)
- `--push`  pushes the image to the remote hub

Example for scaffolds: `docker buildx build --platform=linux/amd64 . -t baseten/scaffolds:pa-build --push`

Will build and push the image to "docker hub" baseten org in the repository scaffolds.

## Resources

- [Docker blog - How to Rapidly Build Multi-Architecture Images with Buildx](https://www.docker.com/blog/how-to-rapidly-build-multi-architecture-images-with-buildx/)
