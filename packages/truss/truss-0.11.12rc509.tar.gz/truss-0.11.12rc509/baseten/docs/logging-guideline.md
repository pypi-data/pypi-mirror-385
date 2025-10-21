# Logging Guideline
Logs are a great tool to understand what happens in a system. We can be liberal with adding logging, the cost is minimal and the benefits can be huge. At Baseten, we typically use 3 levels:

## INFO
*INFO* should be used for the normal stuff. There is nothing to do, there is nothing to change, there is nothing wrong, but they provide great visibility into what is going on in the system and are an important debugging tool. When developing a feature, think about what could go wrong and what information would help you identify the issue; those are the things you want to log at info level.
* Important feature usage audit
  * Model creation
  * App creation
* Invalid user input
  * Unknown organization
  * Invalid parameter value
Monitor after production upgrade to ensure that there are not an abnormal amount of INFO logs.

## WARN
*WARN* should be used for the abnormal stuff. Something went wrong but it doesn't require any human intervention.. *yet*. The can be a great indicator that the system’s health is degrading.
* Temporary non-critical errors
  * Communication failure in a frequent cron-job
  * Retryable non-critical network related failure
* Handled but suspicious events
  * Continuation on worklet run that is not suspended
  * Trying to process an already processed pynode requirements
If WARN logs persist, you might have a bug. They need to be monitored daily.

## ERROR
*ERROR* is an important error that is unhandled and causes a loss of service.
* Unretryable end-user API call
  * Critical failure in a worklet run
  * Invalid SQL sent to UDM database that causes UDM to crash
* Unexpected unhandled error
  * Never before seen exception coming from a third party service
  * Completely invalid behavior from a component
  * Server side exception leaving the service unhandled
  * Parameter considered valid by on application layer reaches an application layer that realizes it is invalid
An ERROR is a bug. Either you should handle a certain use case, either you should WARN instead. Any ERROR log must lead to a developer action. Inaction is not an option.
## Exception monitoring
*INFO*: Monitor in an aggregated fashion. An abnormal increase in INFO logs might hide a real bug. Individual log lines are useful when investigating issues or client claims. You do not want these in Sentry

*WARN*: Monitor daily. These logs are always supposed to be temporary and infrequent. You might want to log these in Sentry.

*ERROR*: Direct developer communication (Slack, Email, ...). There's a bug, there needs to be a linear issue and a fix. You definitely want to log these in Sentry.

## Things to avoid
* Avoid logging in tight loops which have the potential of overwhelming the logging system and the application as well. In such cases one should collect requisite info in the loop and log after the loop.
