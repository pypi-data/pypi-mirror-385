# Cross-service Integration testing guide

We have extensive backend unit tests. We also have integrations tests amongst
components of the django app. We have cypress tests for testing frontend
interaction with django (but not beyond).

Now, we also have the ability to test integrations between django and backing
services such as pynodes and models. This guide is about writing those
integration tests.

## Set up

These integration tests are currently located
[here](/backend/oracles/tests/integration/test_deploy.py). They are run in
the same environment as codespace.

This means:

- All the python and npm packages are installed
- Database migrations are run
- minikube is started up
- The baseten user account is created and corresponding pynode is bought up

Django is started up at the start of test session and killed at the end. The
session is shared by all the tests, bringing django up and down for each test
would been slow. A special django command is used to get api-key for the baseten
user. All other interactions with django are done using that api-key.

These tests are run on master every 30 mins and failures are reported over email
and slack.

## How to develop new tests

Great thing about using the codespace setup is that it's very easy to develop
these tests. You can write and test new tests on the codespace environment,
getting very close to the working state, and then test them with the github
action.

0. Start up your codespace
1. Make any changes needed to the integration tests file
   [at](/backend/oracles/tests/integration/test_deploy.py)
2. Run the tests locally, and make sure they pass

```sh
uv run pytest -c backend/oracles/tests/integration/pytest.ini backend/oracles/tests/integration/test_deploy.py
```

3. Push changes to your branch and trigger the `Integration Tests` workflow
   [manually on your
   branch](https://github.com/basetenlabs/baseten/actions/workflows/integration-tests.yml).
   Click on the `Run workflow` drop down and pick your branch to do that.
4. Get your PR reviewed, merge to master etc, and make sure the next
   `Integration Tests` [workflow
   run](<(https://github.com/basetenlabs/baseten/actions/workflows/integration-tests.yml)>)
   succeeds (they run every 30 mins on master currently).

## Gotchas

1. Make sure the local django server is not running, integration test starts a
   django server on the same port and would likely fail.
1. Local environment doesn't have all the k8s components as deployed
   environments. Notable missing pieces:
   - Victoria metrics, Custom knative fork, kube event watcher
1. Django does not run on k8s
   - Among other things, it means that django logs won't show up in Loki.
1. Same django server is used for all the tests. Any in-memory state can affect
   other tests, so should be cleared up.
1. Any db changes affect all the other tests, so be sure to clean those up.
   Delete any applications, worklets, models that are created during the test at
   the end of test.
1. Due to the high cost of codespace environment spin up, these tests are on the
   expensive side; they will no way replace the need for unit tests. But they
   should help augment our testing to cover the service interactions and
   deployments that we can't currently test. We won't be able to cover all edge
   cases here but should try to cover all the important ones.

## Conclusion

These are early days for these integrations tests. We'll likely learn and
streamline a lot of things in due time. But having this ability should be a big
boon overall and avoid us a lot of manual testing. We should grow coverage of
these tests and try to cover all the important scenarios. All big changes
affecting multiple services should ideally have integration tests. While
integration tests tend to be flaky, these tests are likely a lot less flaky
compared to say cypress tests, because the backend apis are typically more well
behaved than the frontend UI, where rendering can be problematic.
