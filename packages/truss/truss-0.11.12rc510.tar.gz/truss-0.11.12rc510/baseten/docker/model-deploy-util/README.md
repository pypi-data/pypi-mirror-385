# model-deploy-util

This image contains utilities used as part of the model build pipeline.

It is build by the moon monorepo tooling, under the `backend` project. See [backend/moon.yml](../../backend/moon.yml). We use the backend project because the build depends on files in backend, and we want the image to be rebuilt in response to those files changing. In the future, these shared dependencies should be moved to a separate python library project to decouple `model-deploy-util` from the backend.

Build and deployment follows our standard CI/CD workflow, with builds managed by the moon_release pipeline and version bumps managed by FluxCD & CDLI.

For instructions on testing changes locally, see the "How to test locally" in [dockerfiles.md](../../docs/how-to/dockerfiles.md).
