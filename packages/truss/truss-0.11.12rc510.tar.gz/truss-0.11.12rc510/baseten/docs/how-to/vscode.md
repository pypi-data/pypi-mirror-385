# VSCode

Most vscode settings are automatically set.

## Extensions

We recommend a couple of extensions: you can see the list in `.vscode/extensions.json`. The only mandatory one is "editorconfig" & "pylance". Python & Typescript extensions are installed by default

## Setup Python interpreter

When opening the project we recommend setting the python interpreter correctly:

1. You only need to `poetry install` and use the right python venv in vscode `⌘+⇧+p` -> `Python: Select Interpreter`. It should look like `Python 3.x.x ('baseten-xyz-xyz') ...` and potentially have on the far right a `Poetry` tag
