# Async request service

Run the async request service. It runs on port 9001 by default:
```
make run-server
```

Run the request processor. It runs on port 9002 by default (for metrics and liveness probes):
```
make run-processor
```

Test:
```
moon run test
```

## Database
This project uses [sqlalchemy](https://www.sqlalchemy.org/) as its ORM and [alembic](https://alembic.sqlalchemy.org/en/latest/) to manage DB migrations

To setup the dev and test DBs. It will create the databases and apply the alembic migrations

```
make dev-db
```

### Make a new migrations
If you change the tables definition, you will need to generate a new migration and apply it
```
alembic revision --autogenerate -m "describe you change here"

alembic upgrade head
```

You can revert a migration by running
```
alembic downgrade -1
```

## Run async request service locally

If running the async request service from VS Code (including in a codespace), you should add the `./async-request-service` folder as a separate VS Code workspace root. Open the command palette (Cmd + Shift + P) and select "Add folder to workspace", then navigate to the "async-request-service" folder.

When you open a new VS Code terminal, you'll be asked which folder to use. To run the async request service, make sure you select the "async-request-service" folder. Then run:

```
uv sync
```

### Async request service API:
```
uv run python core/server.py --reload

OR

export DB_HOST=$(minikube ip)
export DB_PORT=$(kubectl get service -n baseten baseten-postgres-np -o jsonpath={.spec.ports[0].nodePort})
make run-server
```

### Queue processor:

You'll first need a `DJANGO_API_KEY` to properly interface with your local Django server. You can get this by running the following command in your Django project:
```
uv run manage.py create_async_request_service_account --global
```

```
uv run python core/processor_server.py

OR

export DB_HOST=$(minikube ip)
export DB_PORT=$(kubectl get service -n baseten baseten-postgres-np -o jsonpath={.spec.ports[0].nodePort})
export DJANGO_API_KEY=<api key outputted from running the above command>
make run-processor
```

### Webhook server:
In its own terminal, start the local_webhook_server:
```
make run-local-webhook
```


### Running tests locally:
To run the tests locally, you'll need to set the `DB_HOST` and `DB_PORT` environment variables.
```
export DB_HOST=$(minikube ip)
export DB_PORT=$(kubectl get service -n baseten baseten-postgres-np -o jsonpath={.spec.ports[0].nodePort})
make test
```
After setting the environment variables, you can also run the tests manually:
```
uv run pytest tests/... # specify the test file or directory
```

### Sample request
Run this in a different terminal using curl or any REST client you like. 
Don't forget to use the localtunnel url in the 'webhook_endpoint' field.

#### Running an async inference on a model deployment
```
curl --request POST \
  --url http://localhost:9090/environments/production/async_predict \
  --header "Authorization: Api-Key $BASETEN_API_KEY" \
  --header 'Content-Type: application/json' \
  --header 'Host: model-n4q95w5d.api.dev.baseten.co' \
  --data '{
	"model_input": "THIS IS SOME TEXT IN UPPER CASE SO I SEE IT IN LOGS EASILY",
	"webhook_endpoint": "http://0.0.0.0:9003/webhook",
	"max_time_in_queue_seconds": 100,
	"inference_retry_config": {
		"max_attempts": 3,
		"initial_delay_ms": 1000,
		"max_delay_ms": 5000
	}
}'
```
Getting async request status:
```
curl --request GET \
  --url http://localhost:9090/async_request/653335653076454c8c76dc48f75d526d \
  --header "Authorization: Api-Key $BASETEN_API_KEY" \
  --header 'Host: model-n4q95w5d.api.dev.baseten.co'
```

#### Running an async inference on a chain deployment
```
curl --request POST \
  --url http://localhost:9090/environments/production/async_run_remote \
  --header "Authorization: Api-Key $BASETEN_API_KEY" \
  --header 'Content-Type: application/json' \
  --header 'Host: chain-n4q95w5d.api.dev.baseten.co' \
  --data '{
	"model_input": "THIS IS SOME TEXT IN UPPER CASE SO I SEE IT IN LOGS EASILY",
	"webhook_endpoint": "http://0.0.0.0:9003/webhook"
}'
```
Getting async request status:
```
curl --request GET \
  --url http://localhost:9090/async_request/653335653076454c8c76dc48f75d526d \
  --header "Authorization: Api-Key $BASETEN_API_KEY" \
  --header 'Host: chain-n4q95w5d.api.dev.baseten.co'
```

## Testing on staging
To test the end to end async request feature in staging, you'll need something to receive the webhook. This project comes with a very lightweight fastapi server to do just that. See `tests/local_webhook_server.py` for the details.

You will also need something to forward the webhook requests from the queue-processor deployed on staging (or dev or prod) to you local machine. We recommend using [localtunnel](https://theboroer.github.io/localtunnel-www/), but you can use any tool you like to do this.

Here is an example using `localtunnel` and the `local_webhook_server`
```
# install the localtunnel client
> npm install -g localtunnel

# In its own terminal, start localtunnel
> lt --port 9003
your url is: https://two-hairs-bake.loca.lt

# In its own terminal, start the local_webhook_server
> make run-local-webhook

# In a different terminal using curl or any REST client you like
# Don't forget to use the localtunnel url in the 'webhook_endpoint' field
curl --request POST \
  --url https://model-5wo8m73y.api.staging.baseten.co/environments/production/async_predict \
  --header "Authorization: Api-Key $BASETEN_API_KEY" \
  --header 'Content-Type: application/json' \
  --data '{
	"model_input": {"prompt":"cowboy riding of in the sunset"},
	"webhook_endpoint": "https://two-hairs-bake.loca.lt/webhook",
	"max_time_in_queue_seconds": 100,
	"inference_retry_config": {
		"max_attempts": 3,
		"initial_delay_ms": 1000,
		"max_delay_ms": 5000
	}
}'
```

## Tracing async requests
Right now the async request service only supports propagating request traces to Beefeater's `/predict` endpoint. We do this so we can reuse the same async request ID as a trace ID throughout the async request lifecycle. This is important for debugging and monitoring purposes.

This works as follows:
1. When `/async_predict` is called, Beefeater creates a `request_id` and passes it to the async request service.
2. When the async request service is ready to run the inference, it sends a request to Beefeater's `/predict` endpoint with the `request_id` included as the `trace_id` in the `traceparent` header. This allows Beefeater to associate the inference request with the original async request ID and trace it throughout its lifecycle.

We use a couple of [OpenTelemetry-specific concepts](https://opentelemetry.io/docs/languages/python/cookbook/#manually-setting-span-context) to achieve this:
1. A [`TracerProvider`](https://opentelemetry.io/docs/specs/otel/trace/api/#tracerprovider) is initialized once in the processor server, this will create a globally accessible `TracerProvider` object that can be used throughout the service to obtain tracers.
2. A [`Tracer`](https://opentelemetry.io/docs/specs/otel/trace/api/#tracer) object is used to create spans for a request, right now we create one in the `beefeater_client`. This is where we create a span for the request to Beefeater's `/predict` endpoint.
3. A [`SpanContext`](https://opentelemetry.io/docs/specs/otel/trace/api/#spancontext) object is created to specify the trace ID and span ID for a request. This is used to create the `traceparent` header that is propagated to Beefeater. We explicitly set the `trace_id` to the `request_id` so that we can trace the request throughout its lifecycle.
4. We create a [`TraceContextTextMapPropagator` propagator](https://opentelemetry.io/docs/specs/otel/context/api-propagators/#propagator-types) that is used to create and inject a [`traceparent` header](https://www.w3.org/TR/trace-context/#traceparent-header) into the request. This is used to propagate the trace ID from the async request service to Beefeater.
