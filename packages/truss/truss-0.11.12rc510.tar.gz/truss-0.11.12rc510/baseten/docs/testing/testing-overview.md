# Testing at Baseten -- An Overview

Testing is critical at Baseten as in any other modern Organization. Perhaps even
more so because we use Python, which doesn't provide type safety. Thankfully,
Python ecosystem has great tools for testing.

We have many kinds of tests:

1. Smoke tests
1. Intra-service integrations tests
1. Cypress tests
1. Cross-service integrations tests
1. Backend Unit tests

We also have frontend unit tests, but they are so few that let me omit them
here. That is certainly an area we could improve on. 

Note that, whatever is not covered by the above tests, we're effectively testing
manually or our users are effectively testing it for us (at great cost).

## Testing Pyramid

We follow the [Google testing
pyramid](https://testing.googleblog.com/2015/04/just-say-no-to-more-end-to-end-tests.html).
As one goes down the above list, the purview of tests decreases and the number
greatly increases. This is not a coincidence. As the purview of a test
increases, it tends to become slower, flakier, more costly in resource usage,
and harder to debug. This doesn't mean we should only have unit tests, in fact,
initially, we just had unit tests, and that wasn't working well. We need the
right balance of all kinds of tests. There's consensus that the first, most
basic test provides the best ROI because having a test is so much better than
having no tests. So, by having even a few large-view tests, we get tremendous
value.

## General Guidelines

* Use the testing pyramid to get a sense of how many or which tests may be
  needed
* If something is not easy to test, that usually means something's wrong in the
  architecture that should get fixed
* Try to make sure that every change you make is covered by a test, adding more
  tests as needed
* Use regular coding practices, such as keeping the code DRY, for testing code
* It's ok and usually good to refactor code to be tested to be able to test it;
  testing very often forces good coding practices such as dependency injection
* Don't try to test internal details of a class or a module. These are likely to
  change. But there can be exceptions; use your judgment.
* Consider and anticipate failure cases and their effects.  Test that these failure
  cases cause the appropriate behavior. Avoid testing only happy path.

## Test Type Details

Let's flip the pyramid and go in the order of importance.

### Backend unit tests

* We have over a thousand of them
* We use pytest for these
* Pytest has very good integration with Django, including the database
* We have a lot of fixtures defined in conftest.py that provide most of the
  common entities such as worklets and applications. These are very useful in
  writing tests. Where possible, these should be utilized rather than
  constructed adhoc.
* Table driven tests work great; check out `@pytest.mark.parameterize`
* These tests run on every PR and are quick; you can write a lot of them without
  worry

### Intra-service integration tests

* We use pytest for these as well
* They cover more complex things than a unit, e.g., there are tests for the
  worklet engine, that cover the entire engine
* Another import example is API tests for our HTTP and Graphql endpoints. Django
  provides a handy client object to invoke API endpoints.

### Cypress tests

* These tests run using the baseten web UI, by simulating user actions
* They test our frontend as well as the backend
* Backend is limited in these tests currently. e.g., only local pynodes can be
  used because there's no k8s cluster and thus no real pynodes, or models.
* Tend to be flaky; lots of care needs to be taken to add retries and timeouts

### Cross-service integration tests

* Introduced recently, these allow testing interactions between our services,
  such as Django, pynodes, models, tekton, etc.
* They use the same codespace environment that we use for development
* It takes very long to run these, the codespace environment itself takes ~10
  mins to startup, so these are costly to run
* Even though these are expensive, we still need many more of these as we don't
  have enough coverage for cross-service testing
* They don't test a specific PR but report the last PR if a test fails

### Smoke tests

* If there's smoke, there must be fire
* These run every 30 mins on staging
* They're just meant to detect if something is egregiously wrong
* Think of what one would want to check manually on staging
* They don't test a specific PR but report the last PR if a test fails
* It's possible that the break in these tests is not due to a code change but
  something else being wrong on the staging environment
