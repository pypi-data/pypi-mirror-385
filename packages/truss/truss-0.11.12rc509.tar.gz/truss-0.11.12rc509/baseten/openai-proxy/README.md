# Summary

A FastAPI proxy that implements the OpenAI API, and proxies requests to a
Baseten model of your choice.


See test.py for an example of how to use this.

# Local Testing

A note about the OpenAI proxy as it stands today is that it by default hits Baseten production. This
is is going to be the easiest way to test your changes.

1. Deploy an openai-compatible model to your Baseten account. (Search the https://github.com/basetenlabs/truss-examples repo for models)
2. Run `poetry install` to setup dependencies
3. Run `make run` to run the bridge server locally.

The server runs on port 8080 by default (you can do this on codespaces or locally).

See the [./test.py] file for an example testing snippet. Note to sub out the model id for the id of your deployed model.

# Deploying new versions to production

Once you've tested your changes and merged into master, you can build a new new docker image using:


1. you will have to be auth'd to dockerhub for this to work (using `docker login` -- credentials are in 1password).
1. `$ make docker-build`
1. Once it is pushed, you can update the tags in terraform. See terraform/environments/production/app.tf as an example. You'll have to
update all of the other environments too. 
1. Create a PR with the updated tags. This will deploy the updated image for all environments, with one exception
  1. For production, you'll need to update the source of truth in Flux (as of 2024-06-26, we are in the middle of a migration) as well. You can see an exmaple here
https://github.com/basetenlabs/flux-cd/pull/106. Without this, the Bridge won't update in GCP

# Testing on dev or other environments

Note that if you need to test on dev first, you can update the tags for just the dev environment in terraform/environments/development/app.tf
first.
