# LLM instructions

These are simple oneliner bullet point items for coding agents and humans alike.

## Testing

Packages

* A files unit style tests should be in the same package as the file.
* A files intergration or public api test should in a package with `_test` suffixed to the name.

Asserts

* Use the `assert.*` and `require.*` checks from github.com/stretchr/testify.

 style

* Add helper functions to `balancer_test_helpers.go`, if they're used in more than 1 file.
* Prefer table driven tests when possible.

Metrics and logs

* When adding new metrics, add tests to existing metrics tests.
* When adding new logs, _consider_ if existing tests should verify the new logs.

## Observability

Logging

* All logging uses zerolog
* Avoid `Msgf`, prefer using `Msg` with extra info using `Str`, `Int` etc.

Metrics

* Metrics uses Victoria Metrics
* Many interfaces have a `metricsSet` field for collecting metrics in.

## Documentation

* Avoid trivial one-line comments inside functions.
* Add comments to each function that explains why it exists and who calls it.

