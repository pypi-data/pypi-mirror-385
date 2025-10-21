# Quantize DSV3 to FP4

## Setup and timings

Due to the model size and context length we want to support, we need 4x8xH200 nodes.

1. Bring up the 4 nodes connected via IB with a shared file system.
2. Pull the bf16 checkpoint from s3 to the head node.
3. Convert the bf16 checkpoint to a specific format for DSV3 quantization script across 4 nodes. The resulting weights should be on the shared file system. This conversion will take about 1 hour.
4. The sample data _must be formatted as a json list of strings_, the strings are the chat templated prompts to the model. This file should be on the shared file system.
5. Run the calibration script on all 4 nodes. For supporting context length 131k about 1-1:15 hours. This will generate the amax values.
6. Run the quantization script on the head node. This will generate the FP4 checkpoint. It will take about 30 minutes.
7. Inject the shared embedding and lm head into MTP layer. This will generate the final FP4 checkpoint. It will take about 20 minutes.
8. Copy all non-safetensor files from the original repo to your final FP4 repo.
9. Push the final FP4 checkpoint to s3.


Tips:
- takes a long time, use tmux to run the commands in the background.
- some commands work silently, wait for them to finish.
- use s5cmd for aws file operations for speed.


#### Setup variables

```bash
# set up variables to run the conversion (all nodes)
export HF_BF16_CKPT=/path/to/shared/storage/cursor_weights_mystery  # bf16 weights  
export DS_CKPT=/path/to/shared/storage/cursor_weights_mystery_mp32
export FP4_QUANT_PATH=/path/to/shared/storage/cursor_weights_mystery_fp4_test_amax
export HF_FP4_PATH=/path/to/shared/storage/cursor_weights_mystery_fp4_test
export HF_FP4_FINAL_PATH=/path/to/shared/storage/cursor_weights_mystery_fp4_test_mtp
export SAMPLES_FILE=/path/to/shared/storage/samples_cursor_mystery_clean.json
```

#### Convert the bf16 checkpoint for DSV3 quantization script

On the head node, pull the bf16 checkpoint from s3 and convert it to the specific format for DSV3 quantization script.

```bash
# download the BF16 checkpoint from s3
aws s3 cp --recursive s3://path/to/weights/cursor_weights_mystery .

# convert the HF checkpoint to a specific format for Deepseek
python convert.py --hf-ckpt-path $HF_BF16_CKPT --save-path $DS_CKPT --n-experts 256 --model-parallel 32
```

#### Run the calibration scripts

On each node, run the following commands, substituting the appropriate values for the variables.

```bash
export BT_GROUP_SIZE=4
export BT_NUM_GPUS=8
export BT_NODE_RANK={the_rank_of_the_node [0, 1, 2, 3]}
export BT_LEADER_ADDR={the address of the head node}
export NUM_SAMPLES=5

torchrun --nnodes $BT_GROUP_SIZE  --node_rank=$BT_NODE_RANK  --master_addr=$BT_LEADER_ADDR --nproc-per-node $BT_NUM_GPUS --master_port=12346 ptq.py --model_path $DS_CKPT --config config_671B.json --quant_cfg NVFP4_DEFAULT_CFG --output_path $FP4_QUANT_PATH/cursor_mystery_amax --samples_file $SAMPLES_FILE --batch_size 1 --calib_size $NUM_SAMPLES
```

#### Quantize the checkpoint to FP4

We provide a one-step-script which will:

- Quantize the weights to NVFP4
- Copy miscellaneous files to the quantized checkpoint

```bash
./quantize_fp8_to_nvfp4.sh --amax_path $FP4_QUANT_PATH --fp4_output_path $HF_FP4_PATH --fp8_hf_path $HF_BF16_CKPT --world_size 32
```

#### Inject shared embedding and lm head into MTP layer

```bash
python inject_mtp.py $HF_FP4_PATH $HF_FP4_FINAL_PATH
```

After this, you must copy _all non-safetensor files_ from the original repo to your FP4 repo.

#### Push the final FP4 checkpoint to s3

```bash
aws s3 cp --recursive $HF_FP4_FINAL_PATH s3://path/to/weights/cursor_weights_mystery_fp4
```