# MP ci

Self hosted runner for MP ci. We need dedicated setup with access to high end GPUs such as H100. It's setup here as a helm chart.


## Deploy

```sh
export GITHUB_TOKEN=[github token here]
make deploy
```

## github token

An example token can be found in 1Password as `MP ci job github pat`. That's a temporary token that we should replace with a more permanent one.

The github token needs the following permissions on baseten repo:

Administration: read and write (most important)
Content: read and write
Actions: read and write (may not be needed)
