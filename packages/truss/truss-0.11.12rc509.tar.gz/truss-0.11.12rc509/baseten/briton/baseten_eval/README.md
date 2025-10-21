# Baseten Evaluations

## How to run

```sh
poetry install
export BASETEN_API_KEY=<key with access to model>
poetry run eval --config ./example_config.yaml
```

## How to use the config

Let's take an example:
```yaml
model:
  hf_tokenizer: mistralai/Mistral-7B-Instruct-v0.3
  port: 8080
evals:
  truncation:
  garbage:
  unk:
  llama3_mmlu:
    model_size: 8B
  llama3_gsm8k:
    model_size: 8B
  length_compare:
    target_model:
      hf_tokenizer: mistralai/Mistral-7B-Instruct-v0.3
      port: 8080
    num_examples: 5

log_level: WARNING
```

Best way to use the config is to refer to `EvalArgs` pydantic type in `types.py`
and individual eval settings types.

First let's look at `EvalArgs`. You specify details of the served model under
the model field. e.g. for hitting local model specify port, for baseten deployed
model refer to `BasetenDeployedModel` type.

Most importantly, you can specify a set of evals to run. This is a dict, with
eval name as key and eval settings as value. All evals are registerd in
`evals.py`. Each eval can define its own settings and they have to be passed
accordingly. Some don't take any settings and in that case settings can be left
blank. One can choose to run any subset of evals (by using only relevant keys).

Hopefully, above example serves as a good starting point.

You can set log_level, number of repetitions etc as well.

Number of examples or concurrency can be specified in the dataloader section at
the top level. Currently, only the sharegpt dataset is supported. Note that this
dataloader is a guidance to the eval, but the eval is free to choose something
else. e.g. gsm8k and mmlu use specific datasets and other settings.

## Local dev

- Run truss locally via docker, it would be available on port 8080
  - Typically you can do `make run_truss` from the parent briton folder to
    achieve this.
- The example config is already set up to hit the local model.

```sh
poetry run eval --config ./example_config.yaml
```

## Architecture and how to add new evals

The architecure is pretty lightweight. There's a model to evaluate and that's
the main assumption, there are very few restriction on how the eval is
implemented.

An eval should implement the `Eval` interface. In the load function the eval is
supplied details of the served model to eval, the default dataloader to
optionally use and few other helper objects. Eval specific settings should be
parsed here into typed objects and validations done on the settings to report
errors early.

`Hydrant` is a dependency injection equivalent helper that allows converting
typed objects such as `ServedModel` into useful entities such as the client,
tokenizer, data stream etc. This is a way of guiding use of recommended common
ways of doing things, but not enforcing.

`Reporter` is meant to allow reporting interesting information live, e.g.
failures, rather than have to wait till the end.

A report can be retured in the impl of `final` method, as the official
evaluation report.

The sequence of calling an eval is:
1. load
2. run
3. final

All loads are done for all evals before running any, to detect settings and
other minor issues early.

All evals should be registed in `evals.py`.

