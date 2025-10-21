# How to create new github actions - dev flow

Developing a new github action requires running it many times to get it right.
Running it requires it to be registered with github. Actions get registered
automatically as they land the main (or master) branch. So typically we create a
placeholder for the new github action and land to main (or master). Afterwards,
one can keep making changes to the github action in a branch. Github UI allows
running the action from a branch, just make sure it's set to trigger on
`workflow_dispatch`, which basically means that it's allowed to be triggered
manually.

## Steps

- Create a PR with the placeholder github action and land it
  - Make sure it's set to trigger on `workflow_dispatch`
  - [example pr](https://github.com/basetenlabs/benchmarks/pull/27/files)
  - example action content:

```yaml
name: My action

on:
  workflow_dispatch:
    inputs:
        content:
          description: 'Please specify content here'
          required: true

jobs:
  my_job:
    runs-on: python:3.11-alpine

    steps:
    - name: Checkout code
        uses: actions/checkout@v2
    - name: Echo Hello World
      run: echo "Hello, World!"
```

- Land this PR and make sure you see the action show up in github actions page
  of your repo
  - It's ok to get a review from any engineer, tell them this is just for
    process, content is irrelevant
- Iterate on the github action in a branch
  - Trigger the action from github actions UI of your repo to try things out
