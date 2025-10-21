# Inference Templates

This document provides a comprehensive overview of the inference templates support matrix, organized by **Weight Source**, **Model Type**, and **Inference Stack**.

## Overview

Inference templates enable flexible model deployment by supporting various combinations of weight sources, model types, and inference stacks. This system allows for deploying models from different sources (Hugging Face, Baseten checkpoints) with different architectures (full models, LoRA adapters, Whisper models) using various inference engines.

## Support Matrix

### Currently Supported Combinations ✅

| Weight Source | Model Type | Inference Stack | Status |
|---------------|------------|-----------------|---------|
| HF | Full | VLLM | ✅ Supported |
| BasetenCheckpoint | Full | VLLM | ✅ Supported |
| BasetenCheckpoint | Whisper | VLLM | ✅ Supported |
| BasetenCheckpoint | LoRA | VLLM | ✅ Supported |

### Planned Future Support 🚧

| Weight Source | Model Type | Inference Stack | Status |
|---------------|------------|-----------------|---------|
| BasetenCheckpoint | Full | BasetenInferenceStack (BIS) | 🚧 Planned |
| BasetenCheckpoint | LoRA | BasetenInferenceStack (BIS) | 🚧 Planned |
| HF | LoRA | VLLM | 🚧 Planned |
| HF | Full | BasetenInferenceStack (BIS) | 🚧 Planned |

### Not Supported ❌

| Weight Source | Model Type | Inference Stack | Status |
|---------------|------------|-----------------|---------|
| S3 | Any | Any | ❌ No S3 support across any configuration |
