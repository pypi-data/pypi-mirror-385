# Inference Runtime Library
Accelerating Speculative Decoding in TensorRT-LLM

## Suffix Automaton
```
pip install -v -e irl
python
>>> from irl_ext import extend_cpu
>>> extend_cpu(request_id=123, tokens=[1, 2, 3, 4, 1, 2], max_draft_len=3)
[3, 4, 1]
```