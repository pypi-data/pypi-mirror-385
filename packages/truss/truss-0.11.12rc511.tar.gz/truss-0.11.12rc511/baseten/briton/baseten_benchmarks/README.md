# Baseten benchmarks

## How to install

```sh
uv sync
```

## How to run

To hit a local OpenAI server running on post 10001

```sh
uv run baseten_benchmark --backend generic \
  --api_url http://localhost:10001/v1/chat/completions \
  --api_key this_does_not_matter \
  --model deepseek \
  --num_prompts 1 2 4 8 16 \
  --concurrency 1 2 4 8 16 \
  --random_input 1024 \
  --output_len 1024 \
  --input_type custom \
  --stream \
  --tokenizer deepseek-ai/DeepSeek-R1 \
  --output_file latency.csv \
  --warmup_requests 2 \
  --prompt_style messages
```

For now `input_type` `custom` uses a fixed text file.

## How to publish

```sh
uv publish --token [your pypi token here]
```

## How to lint

```sh
uv run ruff check
uv run ruff format
```