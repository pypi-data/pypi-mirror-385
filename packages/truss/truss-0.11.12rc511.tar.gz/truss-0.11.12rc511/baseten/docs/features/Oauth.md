# OAuth in Baseten

Baseten supports OAuth2 for authenticating users via Google and GitHub. We use the `python-social-auth` library which includes the `GoogleOAuth2` and `GithubOAuth2` backends.

## Mock oauth server

To test these OAuth flows locally, we use a mock oauth server that mimics the role of the OAuth provider. To use it locally, you must run the mock oauth server in a separate shell alongside Django:

```sh
node cypress/plugins/mock-oauth-server.js
```

You should now be able to login to Baseten by clicking the "Sign in with Test Provider" button on the login page.

Here's how it works:

- The `SOCIAL_LOGINS` [frontend env config](../local-dev/env-configs.md) specifies which social auths (OAuth providers) are supported in each environment and are therefore displayed on the login page. For local development, this is set to the `test` provider.
- The [mock oauth server](/cypress/plugins/mock-oauth-server.js) runs an HTTP server on port 8020 which will authenticate a hard-coded user `social.user@example.com`.
- [social_auth_test.py](/backend/common/social_auth_test.py) defines a `BaseOAuth2` backend that can authenticate against the mock oauth server.

Since the server always responds with the same user information, to test the account creation flow multiple times, you'll need to delete the `social.user@example.com` org from Billip.

### In Cypress

The [signup_with_social_spec](/cypress/e2e/users/signup_with_social_spec.ts) Cypress test simulates both creating an account and logging into an existing account via Cypress. It runs the mock oauth server for the duration of the test using the `mock-oauth-server:start` and `mock-oauth-server:stop` Cypress tasks.


## Testing GitHub OAuth locally

Create an OAuth app in your personal GitHub account [here](https://github.com/settings/applications/new) with the following settings:
* `Homepage URL`: `http://localhost:8000/`
*  `Authorization callback URL`: `http://localhost:8000/auth/complete/github/`

Save the Client ID and Client secret you generate in the constants in [base.py](/backend/baseten/settings/base.py)
```
SOCIAL_AUTH_GITHUB_KEY = config("SOCIAL_AUTH_GITHUB_KEY", "<YOUR CLIENT ID>")
SOCIAL_AUTH_GITHUB_SECRET = config("SOCIAL_AUTH_GITHUB_SECRET", "<YOUR CLIENT SECRET>")
```

Comment out the following lines in [local_base.py](/backend/baseten/settings/local_base.py)
```
# AUTHENTICATION_BACKENDS = COMMON_AUTHENTICATION_BACKENDS + (
#     "common.social_auth_test.SocialAuthTest",
# )
```

Make sure `"github"` is added to `SOCIAL_LOGINS` in [config.json](/env-configs/config.json):
```
"SOCIAL_LOGINS": ["test", "github"],
```

Run your django and node servers like usual and you should be able to authenticate via GitHub!
