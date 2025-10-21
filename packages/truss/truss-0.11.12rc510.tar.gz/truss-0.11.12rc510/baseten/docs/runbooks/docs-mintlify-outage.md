# How to address a docs outage

We currently maintain two docs sites:

* `docs.baseten.co` from [https://github.com/basetenlabs/docs.baseten.co](https://github.com/basetenlabs/docs.baseten.co)
* `truss.baseten.co` from [https://github.com/basetenlabs/truss/tree/main/docs](https://github.com/basetenlabs/truss/tree/main/docs)

Docs are hosted by Mintlify. If Mintlify has downtime, there's nothing we can do on our end. If the docs issue is something we caused, such as pushing a bad change, just revert the commit in GitHub.

## Mintlify access

Mintlify uses an email-based magic link signup, so I can't put creds in 1Password. Our current plan allows for 5 users. Currently, the following people have access:

1. philip.kiely@baseten.co
2. jonathan@baseten.co
3. amir@baseten.co
4. phil@baseten.co

## Mintlify support

We have access to Slack support in the `#mintlify-baseten` channel. Anyone can join this channel and ping for support if there is an outage. We should also report any downtime detected in the channel even if it resolves itself.
