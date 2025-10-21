# Cypress tests

We use [Cypress](https://www.cypress.io/) to write end-to-end integration tests. Typically we mark relevant components with the `data-cy` property to identify them easily in Cypress tests.

## Best practices for writing tests

The Cypress docs provide a lot of useful information and battle-tested [best practices](https://docs.cypress.io/guides/references/best-practices#Unnecessary-Waiting). Here are some other tips to writing reliable and maintainable tests:

- Write custom Cypress commands (see commands.js) for any common command or set of commands. [Don't repeat yourself!](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself). This makes test code more readable and maintainable.
- Avoid using waits whenever possible since they can unnecessarily slow down tests and are prone to intermittent failure. See [Unnecessary waiting](https://docs.cypress.io/guides/references/best-practices#Unnecessary-Waiting).
- If you're adding a test in response to a specific regression, make sure to run the test without the product code fix to make sure the test fails.

## How to set up Cypress to run integration tests locally

Create special test users by running: `poetry run python manage.py create_cypress_user`

## To run Cypress:

### On your local computer

First make sure you have a Poetry environment set up for the `baseten` repo (refer to [this doc](../local-dev/Local-Development.md)). Then `cd` into `baseten/cypress` and run the following commands:

```bash
# Only needs to be run once or any time you need to apply new DB migrations.
make init

# Only needs to be run if the frontend code was changed and needs to be rebuilt for Cypress tests.
make rebuild

# Needs to run every time you want to run Cypress tests locally. Restarting this process will reset the test data.
make django
```

And open Cypress:

```
npx cypress open
```

This would launch the Cypress test runner. Tests should be listed on the left hand side. Click on
the one you want to run.

This should launch a browser window where the test is run.

### On Codespaces

Before running Cypress tests, make sure to run the following commands:

```bash
# Only once before running Cypress tests on a new Codespace.
poetry run manage.py create_cypress_user

# Django needs to be running for Cypress to work.
poetry run manage.py runserver
```

Currently it's not recommended to run Cypress tests on a Codespace since there's no tooling for resetting the Postgres data.

Note that `npx cypress open` will not work on Github Codespaces. However, you can still run
Cypress tests using `npx cypress run`, which still gives you access to videos of test runs.

## Mocking response data

Read more about how to define test fixtures [here](../../cypress/e2e/typed-fixtures/README.md).

## To investigate failing builds due to Cypress

Look at [this video](https://www.loom.com/share/5fc5dc66f14a49eb95e642d93f235424) to see how to use Cypress to find failure information such as the stack, video, and screenshot of the failed test.

Tests will retry once on failure (see `retries` under [cypress.json](/cypress.json)). If you are modify any tests or testing infrastructure, you should check that you're not introducing flakiness in the CI by searching for "Flaky tests:" at the bottom of each Cypress output, including passed runs (since they may have only passed on retry). You'll see something like:

```
====================================================================================================

Flaky tests: (passed after retry)

 - View builder variables ► flaky test (1 retry)

====================================================================================================
```

## Troubleshooting

If you see errors like:

```
Cypress detected that an uncaught error was thrown from a cross origin script.
```

You can Add this line to the root Cypress config to get more useful error messages:

```diff
 export default defineConfig({
   ...
+  chromeWebSecurity: false,
 });
```

## Other resources

- [Proposal: Cypress Tests for Models and Chains](https://www.notion.so/ml-infra/Proposal-Cypress-Tests-for-Models-and-Chains-17b91d24727380b8bb86c7713141c9f5?pvs=4)
