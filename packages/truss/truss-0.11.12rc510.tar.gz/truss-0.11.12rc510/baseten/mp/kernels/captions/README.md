# Server-Client Orchestrator

I wrote this script (alongside claude) to speed up my dev-loop and see what impact code changes were making to the torch + cpu profiles. It launches the server + client all in one script. Each time you run it, it automatically packages up:

- torch profiles (if they exist)
- formatted blite traces (json + csvs)
- gpu memory/utilization profiles over time
- compilation cache size over time in job folders per run.
- list of all triton kernels (or elementwise, etc. it's configurable) called in execution (if a torch profile is saved)

into a run-specific folder. You can run it with the `--trials` flag to repeat runs for a given configuration. Once all trials are done, it'll take averages and other stats in a CSV to share w/ the greater team. This helps verify what impact your latest code changes had on the kernel-level + CPU-timing-level.

## Prereqs

Install requirements.
```bash
# These dependencies do not and should not mess w/ the existing `mirager` `.venv`
uv pip install pandas matplotlib psutil pyyaml
```

Copy this python file `run.py` in `/mirager`.

Put the `mirage_config.yaml` sent privately in `/mirager`. The python script relies on a file named `mirage_config.yaml` being present by default.

## Usage Examples

You must set `CUDA_VISIBLE_DEVICES` to however many GPUs you want to run on (based on whichever ones are free).

### Single Trial
```bash
# Basic run - starts server, launches client, collects traces and GPU metrics
python3 run.py name_of_experiment

# Same as above, using --name flag instead of positional argument
python3 run.py --name name_of_experiment

# Run with flush mode - clears torch compilation cache before starting
# Useful when testing code changes to ensure clean compilation
python3 run.py name_of_experiment --flush

# Run with custom configuration file - use different server/client commands
# Allows adapting the experiment setup for different settings.
python3 run.py name_of_experiment --config my_custom_config.yaml
```

### Multiple Trials
```bash
# Run experiment 5 times - generates statistical summaries across trials
python3 run.py name_of_experiment --trials 5
# Run 3 trials with cache clearing - ensures each trial starts with clean state + gets stats
python3 run.py my_experiment --trials 3 --flush
```

## Notes / Troubleshooting

Remember, to get blite traces from the code and aggregated stats on them in CSV format, you need `BLITE_TRACING_ENABLED=1` and your python code to have `start_event`, `end_event`, and `write_trace` markers.  You can also set `CLIENT_TIMEOUT_MIN` which is the client stall timeout in minutes (default: 3). If client log file doesn't change for this duration (which happens sometimes if someone else jumps on a GPU while you're running code, or there's a network issue, etc.), the trial is terminates. Applies to both single trial and multi-trial modes (see below for more).

## Command Line Arguments

- **`name`** (positional, optional): Custom folder name for traces
- **`--name NAME`**: Alternative way to specify folder name  
- **`--flush`**: Cleans the torch compilation cache before starting the server-client run.
- **`--config FILE`**: Use custom configuration file (default: `mirage_config.yaml`)
- **`--trials N`**: Run N trials (must be positive integer)

<details>
<summary><strong>What happens from start to finish in run.py</strong></summary>

### Setup Phase (PREMAIN):
- Load configuration from YAML file
- Attempts to kill existing processes matching configured patterns (double check this though!)
- Verify GPU is clean / ready to go (memory < 10MB, utilization = 0%) - first run only
- Optionally flush temporary files if `--flush` flag used
- Reinstall `mirage` package if marker file exists. So if you make any file changes, then it'll automatically update the `.venv` with the correct code.
- Capture environment variables to `env_output.txt`

### Monitoring Setup:
- Start 3 background monitoring threads:
  - GPU usage monitor (memory, utilization every few seconds)
  - TorchInductor directory size monitor
  - Continuous plot updater

### Main Execution Loop:
- Launch server process with configured command
- Monitor server log for ready signal (e.g., "Server is ready")
- Once ready, launch client process with configured script
- Monitor client log file for completion marker or timeout
- If client stalls (no log activity for CLIENT_TIMEOUT_MIN), terminate trial

### Post-Execution (POSTMAIN):
- Stop all monitoring threads + kill server/client remaining processes
- Organize trace files (blite + torch)
- Generate plots

</details>

## Output Structure

### Single Trial
```
/mirager/torch_traces/experiment_name/
├── gpu_history.csv
├── gpu_memory_usage.png
├── gpu_utilization.png
├── torchinductor_size_history.csv
├── torchinductor_size.png
├── server_output.log
├── client_log.txt
├── trace_*.json (original trace files)
├── trace_*.csv (converted files for traces <1MB)
├── triton_kernels.txt
└── env_output.txt
```

### Multiple Trials
```
/mirager/torch_traces/experiment_name/
├── trial_1/
│   ├── gpu_history.csv
│   ├── gpu_memory_usage.png
│   ├── gpu_utilization.png
│   ├── torchinductor_size_history.csv
│   ├── torchinductor_size.png
│   ├── server_output.log
│   ├── client_log.txt
│   ├── trace_*.json
│   ├── trace_*.csv
│   └── triton_kernels.txt
├── trial_2/
│   └── (same structure as trial_1)
├── trial_N/
│   └── (same structure as trial_1)
├── summary_trace.csv (aggregated statistics)
├── detailed_trace.csv (all data points with trial/file info)
└── env_output.txt (captured once)
```

## Statistical Output Files

### `summary_trace.csv`
Aggregated statistics across all trials:
```csv
name                 count  mean     std     min     max     median   num_trials  raw_values
init_process_group   9      2.916    0.864   2.11    4.3     2.59     9           "[3.74, 2.13, 3.19, 2.59, 4.3, 3.83, 2.15, 2.11, 2.2]"
load_vae_encoder     9      1.071    0.262   0.87    1.45    0.89     9           "[0.99, 1.39, 0.88, 1.41, 0.87, 0.89, 0.89, 1.45, 0.87]"
denoising_loop       8      244.18   0.537   243.36  244.94  244.29   8           "[244.6, 243.36, 244.52, 244.18, 243.75, 244.4, 243.69, 244.94]"
...
```

### `detailed_trace.csv`
Every data point with metadata:
```csv
name              dur (secs)  trial  csv_file
decoding_latents  10.39       2      name_of_experimentdeployment_trace_733153.csv
decoding_latents  9.94        2      name_of_experimentdeployment_trace_733153.csv
decoding_latents  9.42        4      name_of_experimentdeployment_trace_969367.csv
decoding_latents  10.05       4      name_of_experimentdeployment_trace_969367.csv
...
```

<details>
<summary><strong>Key Features Explained</strong></summary>

## Key Features Explained

### Trace File Conversion
- Only JSON trace files **< 1MB** are converted to CSV
- **Smart selection**: Chooses the trace file with the most events (most comprehensive)
- Only **one CSV file per trial** is generated (no multiple CSV files)
- CSV files contain events with duration > 0.1 seconds
- Tracks total request time from "download_audio" to "uploading_result"

### Multi-Trial Workflow
1. Run experiment N times
2. Create trial-specific folders immediately when each trial starts
3. Write all files directly to trial folders (no post-trial moving)
4. Track trial success/failure status
5. Mark failed trials with `TRIAL_FAILED.txt` marker file
6. Wait 2 seconds between trials
7. Generate summary statistics across **successful trials only**
8. Create detailed trace file with trial/file metadata

### Client Timeout Protection
- Monitors `client_log.txt` for activity every 5 seconds
- If log file doesn't change for `CLIENT_TIMEOUT_MIN` minutes, terminates the trial
- Default timeout: 3 minutes (configurable via environment variable)
- Applies to both single trial and multi-trial modes
- Prevents infinite hanging when client stalls

### GPU Cleanup Verification
- Verifies GPU state after killing processes (first run only)
- Checks memory usage ≤ 10MB and compute utilization = 0% for all visible GPUs
- Warns if GPUs still have active processes or memory usage
- Helps ensure clean experiment environment
- Uses `CUDA_VISIBLE_DEVICES` to determine which GPUs to check

### GPU & System Monitoring
- Real-time GPU memory and utilization tracking
- TorchInductor directory size monitoring
- Continuous plot updates during execution
- Environment variable capture

## Trial Failure Handling

### What Happens When a Trial Fails:
- **Folder Creation**: Trial folders (`trial_1`, `trial_2`, etc.) are created sequentially regardless of failures
- **Failure Marking**: Failed trials get a `TRIAL_FAILED.txt` marker file with timestamp
- **Continuation**: Remaining trials continue to run normally
- **CSV Aggregation**: Only **successful trials** are included in summary statistics
- **Clear Reporting**: Final summary shows success rate and lists failed trial numbers

### Example with Failures:
```
Running 5 trials...
✓ Trial 1 completed successfully
✗ Trial 2 failed: Client timeout after 3 minutes
✓ Trial 3 completed successfully  
✗ Trial 4 failed: Server startup error
✓ Trial 5 completed successfully

TRIAL SUMMARY
Successful trials: 3/5
Success rate: 60.0%
Successful trial numbers: [1, 3, 5]
Failed trial numbers: [2, 4]
```

### Output Structure with Failures:
```
experiment_folder/
├── trial_1/ (✓ successful - included in summary)
├── trial_2/ (✗ failed - excluded from summary)
│   └── TRIAL_FAILED.txt
├── trial_3/ (✓ successful - included in summary)  
├── trial_4/ (✗ failed - excluded from summary)
│   └── TRIAL_FAILED.txt
├── trial_5/ (✓ successful - included in summary)
├── summary_trace.csv (only trials 1, 3, 5)
└── detailed_trace.csv (only trials 1, 3, 5)
```

## Error Handling

The script properly handles:
- Invalid arguments (shows usage help)
- Missing config files (shows error message)
- Setup failures (no cleanup attempts)
- Keyboard interrupts (graceful shutdown)
- File conversion errors (continues with other files)
- **Trial failures (continues with remaining trials, excludes failed data from aggregation)**

</details>
