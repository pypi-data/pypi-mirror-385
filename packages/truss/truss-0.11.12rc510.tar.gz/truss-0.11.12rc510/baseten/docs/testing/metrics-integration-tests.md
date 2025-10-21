# Metrics integration tests

The metrics integration tests run our model metrics queries against mock data stored inside a local instance of [VictoraMetrics](https://docs.victoriametrics.com/Single-server-VictoriaMetrics.html). This allows us to test that user-facing model metrics are queried, processed, and returned correctly from the backend, including across a range of conditions and edge cases.

The tests are configured to run automatically on every PR and master commit in the [backend](/.github/workflows/backend.yml) GitHub actions workflow.

At the time of writing, we have test cases to cover inference volume, response time (inference time), and E2E response time. We should work to build out this suite of tests over time, especially as metric queries are added or modified.

## How they work

Each time the test suite is run:

1. The [vm_server](/backend/oracles/tests/queries/metrics_integration/conftest.py) fixture spawns a `victoria-metrics` server process which listens on port 8428. The server starts with no metrics data.
2. For each test case:
   1. Mock data is generated using the [`ScrapableSeries`](/backend/oracles/tests/queries/metrics_integration/metric_generator.py) classes.
   2. The mock data is then ingested into the VictoriaMetrics server (see `VMServer.ingest()`). The model version ID and org namespace labels change for every test (just as in the normal backend unit tests), allowing us to isolate data between different test cases in the same session.
   3. The corresponding metrics are requested via the `range_model_metrics` and `instant_model_metrics` GraphQL queries.
   4. The response data is asserted to be correct, either exactly or within some approximation error, depending on the exact test.
3. One all test cases are done running, the `victoria-metrics` server is killed.

As an example, `test_inference_volume_by_status` creates data for the `model_requests_total` metric exposed by beefeater. The following code creates three series (separate counters) for this metric with different status codes. Each `.inc()` corresponds to a model request at a certain timestamp:

```py
counter.add_labels(status="200").inc(ts(50)).inc(ts(60)).inc(ts(70)).inc(ts(150))
counter.add_labels(status="404").inc(ts(200)).inc(ts(250))
counter.add_labels(status="500").inc(ts(150))
```

After the metrics API is called, we check that the result matches our expectations based on the exact input data:

```py
assert range_data["range_model_metrics"] == {
    "inference_volume_by_status": [
        {
            "timestamp": format_timestamp_for_gql(timestamp),
            "status_2xx": status_2xx,
            "status_4xx": status_4xx,
            "status_5xx": status_5xx,
        }
        for timestamp, status_2xx, status_4xx, status_5xx in [
            # Each inc() above corresponds to a (1 request / 30 seconds * 60 seconds / 1 minute = 2 requests / minute)
            # increase in the below data
            (ts(0), 0.0, 0.0, 0.0),
            (ts(30), 0.0, 0.0, 0.0),
            # status="200" @ 50, 60
            (ts(60), 4.0, 0.0, 0.0),
            # status="200" @ 70
            (ts(90), 2.0, 0.0, 0.0),
            (ts(120), 0.0, 0.0, 0.0),
            # status="200" @ 150; status="500" @ 150
            (ts(150), 2.0, 0.0, 2.0),
            (ts(180), 0.0, 0.0, 0.0),
            # status="404" @ 200
            (ts(210), 0.0, 2.0, 0.0),
            (ts(240), 0.0, 0.0, 0.0),
            # status="404" @ 250
            (ts(270), 0.0, 2.0, 0.0),
            (ts(300), 0.0, 0.0, 0.0),
        ]
    ]
}
```

Note that because the metrics data is synthetic, these tests do not cover the instrumentation and scraping steps in the metrics observability process.

## Writing test cases

Metrics integration test cases follow many of the same conventions as unit test cases, including the arrange-act-assert formula. In general, **each test case should create one, minimal set of mock data but may run multiple queries against that data.** Usually we want to limit test cases to a small, coherent set of assertions, but since loading the mock data into Victoria Metrics take a bit of time, we want to reduce this overhead.

For example, the `test_beefeater_latency` test creates latency histogram metrics for a single model version and queries the `instant_model_metrics.e2e_response_time_percentiles`, `instant_model_metrics.average_e2e_response_time`, and `range_model_metrics.e2e_response_time_percentiles` against this metric data.

## Running tests locally

To run the test cases locally, you must first install VictoriaMetrics:

```sh
./bin/install_vm.sh
```

Then you can run the tests:

```sh
# Using `ut` alias from bin/baseten_aliases.sh

# Test model metrics
ut -m 'metrics_integration' oracles/tests/queries/metrics_integration/test_metrics.py

# Test billing metrics
ut -m 'metrics_integration' oracles/tests/queries/metrics_integration/test_billing_metrics.py
```

## References

- [test_metrics.py](/backend/oracles/tests/queries/metrics_integration/test_metrics.py) - Test case definitions
- [conftest.py](/backend/oracles/tests/queries/metrics_integration/conftest.py) - `vm_server` fixture definition
- [mock_metrics.py](/backend/oracles/tests/queries/metrics_integration/mock_metrics.py) - Support code for creating mock metrics data
