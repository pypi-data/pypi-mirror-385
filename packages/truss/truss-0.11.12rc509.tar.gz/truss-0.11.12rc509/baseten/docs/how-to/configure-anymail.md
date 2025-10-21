# Configuring Anymail

Anymail supported ESPs: https://anymail.dev/en/stable/esps/

In order to override the default Sendgrid email implementation for production environments, two settings must be 
provided:

* EMAIL_BACKEND; and
* ANYMAIL_CONFIG

EMAIL_BACKEND needs to be set to the Anymail backend for that specific provider.  E.g. 
`anymail.backends.amazon_sesv2.EmailBackend`

ANYMAIL_CONFIG is the json config payload for the given ESP.  An example config is here: 
https://anymail.dev/en/stable/esps/amazon_ses/#settings. The default Sendgrid value is 
> {"SENDGRID_API_KEY": "' + config("SENDGRID_API_KEY", "") + '"}

# Dependencies
For any newly supported ESPs wanting to be used in the application, a dependency must be added to the `django-anymail` 
extras.  For example, adding support for `Mailgun`, you would add the `mailgun` extra to the `django-anymail` 
dependency.
