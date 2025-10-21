# eslint-plugin-baseten

Allow relative imports only inside of the pages

## Installation

You'll first need to install [ESLint](https://eslint.org/):

```sh
npm i eslint --save-dev
```

Next, install `eslint-plugin-baseten`:

```sh
npm install eslint-plugin-baseten --save-dev
```

## Usage

Add `baseten` to the plugins section of your `.eslintrc` configuration file. You can omit the `eslint-plugin-` prefix:

```json
{
    "plugins": [
        "baseten"
    ]
}
```


Then configure the rules you want to use under the rules section.

```json
{
    "rules": {
        "baseten/imports": [
            "error",
            {
                "allowRelativeImports": ["/frontend/pages/*"]
            }
        ]
    }
}
```

## Supported Rules

* Fill in provided rules here
