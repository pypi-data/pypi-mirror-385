# load_test

## Installation

Download `uv` if you don't have it already:

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Run `uv sync` to install the dependencies:

```sh
uv sync
```

## Usage

Activate the virtual environment:

```sh
source .venv/bin/activate
```

Run the `locust` UI:

```sh
locust --host http://localhost:8000 --model-name deepseek-ai/DeepSeek-R1
```

Start a tunnel:

```sh
kubectl port-forward <pod-name> 8089:8089
```

Open the UI in your browser at `http://localhost:8089`

You can also run this entirely in the terminal by running it in `--headless` mode:

```sh
locust \
  --host https://inference.mc-dev.baseten.co \
  --model-name meta-llama/Llama-4-Scout-17B-16E-Instruct \
  --users 1 \
  --spawn-rate 1 \
  --api-key "<API_KEY>" \
  --input-tokens 512 \
  --output-tokens 64 \
  --headless \
  --only-summary
```

## Plotting

Given an output CSV file from a `locust` run, you can plot the results using the following command:

```sh
uv run python plot_metrics.py <csv_file> --window-size <window-size>
```

Where `window-size` is the size of the moving average window in seconds.
