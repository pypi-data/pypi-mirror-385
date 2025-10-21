# Sentry Events Filtering

When deployed, the baseten application is integrated with [Sentry](https://sentry.io/organizations/baseten/issues/?project=2307828) to help with error reporting using the [Python Sentry SDK](https://docs.sentry.io/platforms/python/).

The Python Sentry SDK will create a sentry event when either of those things happens:

- An exception is raised and not handled by the django app or celery workers
- A log with the `ERROR` level is logged by the django app or celery workers

We have a bit of control over which error events are sent to Sentry and the content of said events. This is done with the [SentryEventFilter](/backend/common/observability/sentry_event_filter.py) class.

## SentryEventFilter

This class purpose is to filter out unwanted events from making it to Sentry, filter out sensitive information and enrich events with more context.

### Configuration

The SentryEventFilter is configured in the `settings/in_cluster.py` file.

```
# Sentry.io
SENTRY_FILTERED_OUT_EXCEPTIONS = [
    AuthCanceled,
    GraphQLResourceNotFoundError,
    ...
]

SENTRY_USER_CAUSED_EXCEPTIONS = [GraphQLResourceNotValidatedError]

SENTRY_IGNORED_LOGGERS = ["django.security.DisallowedHost"]

_sentry_event_filter = SentryEventFilter(
    SENSITIVE_LOGGING_ENABLED,
    SENTRY_FILTERED_OUT_EXCEPTIONS,
    SENTRY_USER_CAUSED_EXCEPTIONS,
    SENTRY_IGNORED_LOGGERS,
```

## Event filtering

### Exception Class based filtering

This is done by specifying a list of `Exception` in the `SENTRY_FILTERED_OUT_EXCEPTIONS` setting. This will end up in the `exceptions_deny_list` field of the class. On every events, the filter will check if the exception that caused the event is in the `exceptions_deny_list`. If it is, it will log a message and prevent the event from being sent to Sentry.

### Logger Name based filtering

This is done by specifying a list of `logger names` in the `SENTRY_IGNORED_LOGGERS` setting. This will end up `ignored_loggers` field of the `SentryEventFilter`. On every events, the filter will check if the event if coming from one the the logger specified in the `ignored_loggers`. If it is, the event is ignored and will not be sent to Sentry.

## Marking an event as "user-caused"

This is done by specifying a list of `Exception` in the `SENTRY_USER_CAUSED_EXCEPTIONS` setting. This will end up in the `user_caused_exceptions` field of the class. On every events, the filter will check if the exception that caused the event is in the `user_caused_exceptions`. If it is, it will add the `user_caused` tag to the event. Sentry is configured to route events where the `user_caused` tag is set to the user alerting channels in slack (#alerts-users-staging and #alerts-users-production).
