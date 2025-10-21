# Frontend env configs

Frontend env configs allow injecting environment-specific configuration values across both runtime environments like prod/staging/dev and self-hosted customer environments into our frontend TypeScript code. These config values are important for connecting to different services, like Segment for analytics or Stripe for billing, as well as disabling entire integrations in particular environments. There are a series of config files under the root `env-configs` folder, including:

1. A base `env-configs/config.json` file - This is used during local development
2. Separate json files fork each deployment environment, organized in folders by owner

When an environment is deployed via GitHub action, the appropriate json file is copied to `env-configs/config.json`. This file is then read by our webpack config and the configuration values are injected into the frontend code at compile time. 

## How to add a new config value

Add the value to all config files under `env-configs`. If a particular feature or integration shouldn't be enabled in one environment, you can set the value in that environment to an empty string. For the sake of this example, we'll add a new config value called `MY_NEW_CONFIG_VALUE`.

Run `npm run validate-env-configs` to ensure it's been added to every config properly. 

Use `ENV_CONFIG.MY_NEW_CONFIG_VALUE` to refer to the value in your frontend code.

You can override the value in your development environment by setting it as an environment variable before running the webpack server. If the environment variable is JSON-encoded, it will be injected as-is. Otherwise it will be injected as a string.

For example, you could run:
```sh
# MY_NEW_CONFIG_VALUE will be injected as a number
MY_NEW_CONFIG_VALUE=123 npm start

# MY_NEW_CONFIG_VALUE will be injected as a string: "abc"
MY_NEW_CONFIG_VALUE="abc" npm start

# MY_NEW_CONFIG_VALUE will be injected as a string since `abc` is not JSON parsable
MY_NEW_CONFIG_VALUE=abc npm start
```

## Advantages

- Enforces a strong separation across environments, lowering the risk of accidentally leaking information across environments, especially for self-hosted customers.
- TypeScript type safety since we infer the type of `ENV_CONFIG` based on `env-configs/config.json`.
- No runtime overhead since values are injected at compile time.
- No pollution or risk of collision with environment variables.
- The consistency of the config files is validated in the CI with the [./validate-configs.js] script, reducing the risk of breaks on deployment to a particular environment.

## Precautions

- Because these values are compiled into the frontend code, they should not contain sensitive information like secrets.
