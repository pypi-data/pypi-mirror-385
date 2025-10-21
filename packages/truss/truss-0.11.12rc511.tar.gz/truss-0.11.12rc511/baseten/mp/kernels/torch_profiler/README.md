# GPU Kernel Analyzer

Analyzes GPU kernel execution patterns from PyTorch profiler JSON traces to identify performance bottlenecks and idle time. FYI this code has a lot of work to be done, if it's helpful to others we can further develop this.

## Usage

For viewing kernel frequeny, durations, etc. for a `trace.json` you get for `prof.export_chrome_trace(...)`. You can load it into perfetto for the temporal analysis, but this allows you to view aggregated results (i.e. list of kernels launched, frequency/duration of each, gaps, etc.).

### Simple commands

Looking @ durations:
```bash
# Show top 10 most frequent kernels
python profiler.py trace.json
# Show top 20 kernels by percentage of total GPU time
python profiler.py trace.json --top 20 --sort duration-percentage
# Show kernels sorted by average duration
python profiler.py trace.json --sort duration
```

Looking @ gaps between kernels:
```bash
# Analyze idle gaps between kernels
python profiler.py trace.json --gaps
# Focus on gaps between 1-100μs (filter out noise and extreme outliers), the units are in ms
python profiler.py trace.json --gaps --hist-min 1 --hist-max 100
# Sort gaps by frequency instead of average duration
python profiler.py trace.json --gaps --gap-sort count
# python profiler.py trace.json --output kernels.txt --gap-output gaps.txt --gaps
```

You'll see results like this, for example:

```bash
=== GPU KERNEL ANALYSIS ===

Total unique kernel types found: 57
Total kernel launches: 1163615
Results sorted by: percentage of total duration

TOP 200 GPU KERNELS BY PERCENTAGE OF TOTAL DURATION:
========================================================================================================================================================================================================
Rank    Kernel Name                                       Count     Avg Duration (μs)   Total Duration (μs)   Std Dev (μs)      % of Total    % Duration
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
1       kernel_cutlass_kernel_flash_attncuteflash_fwd_..  1584      26064.18            41285654.07           4982.90           0.1           35.2
2       elementwise_kernel                                240435    113.63              27321102.39           213.97            20.7          23.3
3       void at::native::(anonymous namespace)::CatArr..  7920      1078.01             8537856.10            228.07            0.7           7.3
4       ncclDevKernel_SendRecv                            12672     486.59              6166012.79            1826.04           1.1           5.3
5       ncclDevKernel_AllGather_RING_LL                   1728      2737.73             4730788.86            22960.33          0.1           4.0
6       vectorized_elementwise_kernel                     220678    19.88               4388101.89            42.52             19.0          3.7
7       nvjet_tst_256x256_64x4_2x1_2cta_v_bz_TNT          1914      2195.57             4202328.20            1019.00           0.2           3.6
8       cudaLaunchKernel                                  550698    6.53                3596628.00            1287.99           47.3          3.1
9       nvjet_tst_256x256_64x4_2x2_2cta_v_bz_TNT          4884      668.07              3262847.33            324.49            0.4           2.8
10      void at::native::(anonymous namespace)::CatArr..  6336      428.64              2715871.38            86.00             0.5           2.3
...
...
...
```

and this


```bash
=== GPU IDLE TIME GAP ANALYSIS ===

Total gaps found: 768617
Total idle time: 492925583.12 μs
Average gap duration: 641.31 μs
Active streams: 5
  Stream 7: 389538 gaps, 16930824.84 μs idle time
  Stream 3316414: 359748 gaps, 161017813.79 μs idle time
  Stream 23: 16131 gaps, 153657273.72 μs idle time
  Stream 59: 2080 gaps, 108107922.49 μs idle time
  Stream 47: 1120 gaps, 53211748.28 μs idle time

GAP DURATION HISTOGRAM:
================================================================================
     0.5-577531.0 μs │████████████████████████████████████████│ 768613
577531.0-1155061.5 μs │░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│    0
1155061.5-1732592.0 μs │░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│    0
1732592.0-2310122.6 μs │░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│    0
2310122.6-2887653.1 μs │░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│    0
2887653.1-3465183.6 μs │░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│    0
3465183.6-4042714.2 μs │░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│    0
4042714.2-4620244.7 μs │░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│    0
4620244.7-5197775.2 μs │░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│    0
5197775.2-5775305.7 μs │░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│    0
5775305.7-6352836.3 μs │░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│    0
6352836.3-6930366.8 μs │░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│    0
6930366.8-7507897.3 μs │░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│    0
7507897.3-8085427.8 μs │░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│    0
8085427.8-8662958.4 μs │░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░│    4
================================================================================

TOP 30 KERNEL PAIRS BY AVERAGE GAP DURATION:
========================================================================================================================================================================================================
Rank    Kernel Transition                                                                 Count     Avg Gap (μs)    Max Gap (μs)    Min Gap (μs)    Std Dev (μs)
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
1       void at::native::(anonymous namespace)::distribution_elementwise_grid_stride_...  1         73203.73        73203.73        73203.73        0.00
2       void at::native::(anonymous namespace)::indexSelectLargeIndex<c10::BFloat16, ...  2         53541.77        106269.72       813.82          74568.58
3       reduce_kernel → void at::native::(anonymous namespace)::indexSelectLargeIndex...  2         39010.61        77615.48        405.73          54595.54
4       ncclDevKernel_AllGather_RING_LL → ncclDevKernel_AllGather_RING_LL                 130       13828.64        439147.02       1.82            50008.64
5       ncclDevKernel_AllGather_RING_LL → ncclDevKernel_SendRecv                          3200      13050.05        8497548.78      5463.21         150108.82
...
...
...
```

### Full Options

```bash
usage: profiler.py [-h] [--pstep PSTEP] [--top TOP] [--output OUTPUT]
                   [--sort {count,duration,percentage,duration-percentage}]
                   [--verbose] [--gaps] [--gap-output GAP_OUTPUT]
                   [--gap-top GAP_TOP]
                   [--gap-sort {count,avg,avggap,max,maxgap,stdev}]
                   [--hist-min HIST_MIN] [--hist-max HIST_MAX]
                   json_file

Analyze GPU kernels from PyTorch profiler JSON trace files

positional arguments:
  json_file             Path to the PyTorch profiler JSON trace file

options:
  -h, --help                  show this help message and exit
  --pstep PSTEP               Filter analysis to a specific ProfilerStep number
  --top TOP, -t TOP           Number of top kernels to display (default: 10)
  --output OUTPUT, -o OUTPUT  Optional output file to save detailed results
                        
  --sort {count,duration,percentage,duration-percentage}, -s {count,duration,percentage,duration-percentage}
                              
                              Sort kernels by count (frequency), duration (avg 
                              execution time), percentage (% of total launches), or 
                              duration-percentage (% of total duration). Default: count
  --verbose, -v               Show full kernel names in addition to simplified names
  --gaps, -g                  Run gap analysis to identify idle time between kernels
  --gap-output GAP_OUTPUT     Optional output file to save detailed gap analysis results
  --gap-top GAP_TOP           Number of top kernel pairs to display in gap analysis (default: 15)
  --gap-sort {count,avg,avggap,max,maxgap,stdev}
                              Sort gap analysis results by count (frequency), 
```


### Large traces
The tool (is supposed to) automatically caches parsed traces to speed up repeated analysis. This is WIP, doesn't work properly. For very large traces, the initial parsing will (not implemented yet) take time but subsequent runs will be fast.

### Reports

You can also get a `kernel_analysis.txt` which shows more detailed results, and full names of each kernel.

```bash
DETAILED GPU KERNEL ANALYSIS
==================================================
Results sorted by: percentage of total duration
==================================================

Rank 1: cudaLaunchKernel
  Count: 67815 (47.4% of total launches)
  Total Duration: 10370110.57 μs (44.8% of total duration)
  Average Duration: 152.92 μs
  Standard Deviation: 1348.42 μs
  Example Full Name: cudaLaunchKernel
--------------------------------------------------
Rank 2: kernel_cutlass_kernel_flash_attncuteflash_fwd_sm100FlashAttentionForwardSm100_object_at__tensor0000odiv811101213_tensor0000odiv811101213_tensor0000odiv810111213_tensor0000odiv811101213_No_0
  Count: 192 (0.1% of total launches)
  Total Duration: 4982934.45 μs (21.5% of total duration)
  Average Duration: 25952.78 μs
  Standard Deviation: 4946.15 μs
  Example Full Name: kernel_cutlass_kernel_flash_attncuteflash_fwd_sm100FlashAttentionForwardSm100_object_at__tensor0000odiv811101213_tensor0000odiv811101213_tensor0000odiv810111213_tensor0000odiv811101213_No_0
...
...
...
```

You can also get a `gap_report.txt`:

```bash
DETAILED GPU GAP ANALYSIS
==================================================

Total gaps found: 768617
Total idle time: 492925583.12 μs
Average gap duration: 641.31 μs

Active streams: 5
  Stream 7: 389538 gaps, 16930824.84 μs idle time
  Stream 3316414: 359748 gaps, 161017813.79 μs idle time
  Stream 23: 16131 gaps, 153657273.72 μs idle time
  Stream 59: 2080 gaps, 108107922.49 μs idle time
  Stream 47: 1120 gaps, 53211748.28 μs idle time

Gap Duration Histogram:
------------------------------
     0.5-433148.4 μs: 768611
433148.4-866296.3 μs:    2
866296.3-1299444.2 μs:    0
1299444.2-1732592.0 μs:    0
1732592.0-2165739.9 μs:    0
2165739.9-2598887.8 μs:    0
2598887.8-3032035.7 μs:    0
3032035.7-3465183.6 μs:    0
3465183.6-3898331.5 μs:    0
3898331.5-4331479.4 μs:    0
4331479.4-4764627.3 μs:    0
4764627.3-5197775.2 μs:    0
5197775.2-5630923.1 μs:    0
5630923.1-6064071.0 μs:    0
6064071.0-6497218.9 μs:    0
6497218.9-6930366.8 μs:    0
6930366.8-7363514.7 μs:    0
7363514.7-7796662.6 μs:    0
7796662.6-8229810.5 μs:    0
8229810.5-8662958.4 μs:    4

Kernel Pairs Ranked by average gap duration:
--------------------------------------------------
Rank 1: void at::native::(anonymous namespace)::distribution_elementwise_grid_stride_kernel<float, 4, at::native::templates::cuda::normal_and_transform<float, float, at::CUDAGeneratorImpl*, at::native::templates::cuda::normal_kernel<at::CUDAGeneratorImpl*>(at::TensorBase const&, double, double, at::CUDAGeneratorImpl*)::{lambda()#1}::operator()() const::{lambda()#2}::operator()() const::{lambda(float)#1}>(at::TensorIteratorBase&, at::CUDAGeneratorImpl*, at::native::templates::cuda::normal_kernel<at::CUDAGeneratorImpl*>(at::TensorBase const&, double, double, at::CUDAGeneratorImpl*)::{lambda()#1}::operator()() const::{lambda()#2}::operator()() const::{lambda(float)#1})::{lambda(curandStatePhilox4_32_10*)#2}, at::native::(anonymous namespace)::distribution_nullary_kernel<float, float, float4, at::CUDAGeneratorImpl*, at::native::templates::cuda::normal_and_transform<float, float, at::CUDAGeneratorImpl*, at::native::templates::cuda::normal_kernel<at::CUDAGeneratorImpl*>(at::TensorBase const&, double, double, at::CUDAGeneratorImpl*)::{lambda()#1}::operator()() const::{lambda()#2}::operator()() const::{lambda(float)#1}>(at::TensorIteratorBase&, at::CUDAGeneratorImpl*, at::native::templates::cuda::normal_kernel<at::CUDAGeneratorImpl*>(at::TensorBase const&, double, double, at::CUDAGeneratorImpl*)::{lambda()#1}::operator()() const::{lambda()#2}::operator()() const::{lambda(float)#1})::{lambda(curandStatePhilox4_32_10*)#2}, at::native::templates::cuda::normal_kernel<at::CUDAGeneratorImpl*>(at::TensorBase const&, double, double, at::CUDAGeneratorImpl*)::{lambda()#1}::operator()() const::{lambda()#2}::operator()() const::{lambda(float)#1}>(at::TensorIteratorBase&, at::CUDAGeneratorImpl*, at::native::templates::cuda::normal_and_transform<float, float, at::CUDAGeneratorImpl*, at::native::templates::cuda::normal_kernel<at::CUDAGeneratorImpl*>(at::TensorBase const&, double, double, at::CUDAGeneratorImpl*)::{lambda()#1}::operator()() const::{lambda()#2}::operator()() const::{lambda(float)#1}>(at::TensorIteratorBase&, at::CUDAGeneratorImpl*, at::native::templates::cuda::normal_kernel<at::CUDAGeneratorImpl*>(at::TensorBase const&, double, double, at::CUDAGeneratorImpl*)::{lambda()#1}::operator()() const::{lambda()#2}::operator()() const::{lambda(float)#1})::{lambda(curandStatePhilox4_32_10*)#2} const&, at::native::templates::cuda::normal_kernel<at::CUDAGeneratorImpl*>(at::TensorBase const&, double, double, at::CUDAGeneratorImpl*)::{lambda()#1}::operator()() const::{lambda()#2}::operator()() const::{lambda(float)#1})::{lambda(int, float)#1}>(long, at::PhiloxCudaState, at::native::templates::cuda::normal_and_transform<float, float, at::CUDAGeneratorImpl*, at::native::templates::cuda::normal_kernel<at::CUDAGeneratorImpl*>(at::TensorBase const&, double, double, at::CUDAGeneratorImpl*)::{lambda()#1}::operator()() const::{lambda()#2}::operator()() const::{lambda(float)#1}>(at::TensorIteratorBase&, at::CUDAGeneratorImpl*, at::native::templates::cuda::normal_kernel<at::CUDAGeneratorImpl*>(at::TensorBase const&, double, double, at::CUDAGeneratorImpl*)::{lambda()#1}::operator()() const::{lambda()#2}::operator()() const::{lambda(float)#1})::{lambda(curandStatePhilox4_32_10*)#2}, at::native::(anonymous namespace)::distribution_nullary_kernel<float, float, float4, at::CUDAGeneratorImpl*, at::native::templates::cuda::normal_and_transform<float, float, at::CUDAGeneratorImpl*, at::native::templates::cuda::normal_kernel<at::CUDAGeneratorImpl*>(at::TensorBase const&, double, double, at::CUDAGeneratorImpl*)::{lambda()#1}::operator()() const::{lambda()#2}::operator()() const::{lambda(float)#1}>(at::TensorIteratorBase&, at::CUDAGeneratorImpl*, at::native::templates::cuda::normal_kernel<at::CUDAGeneratorImpl*>(at::TensorBase const&, double, double, at::CUDAGeneratorImpl*)::{lambda()#1}::operator()() const::{lambda()#2}::operator()() const::{lambda(float)#1})::{lambda(curandStatePhilox4_32_10*)#2}, at::native::templates::cuda::normal_kernel<at::CUDAGeneratorImpl*>(at::TensorBase const&, double, double, at::CUDAGeneratorImpl*)::{lambda()#1}::operator()() const::{lambda()#2}::operator()() const::{lambda(float)#1}>(at::TensorIteratorBase&, at::CUDAGeneratorImpl*, at::native::templates::cuda::normal_and_transform<float, float, at::CUDAGeneratorImpl*, at::native::templates::cuda::normal_kernel<at::CUDAGeneratorImpl*>(at::TensorBase const&, double, double, at::CUDAGeneratorImpl*)::{lambda()#1}::operator()() const::{lambda()#2}::operator()() const::{lambda(float)#1}>(at::TensorIteratorBase&, at::CUDAGeneratorImpl*, at::native::templates::cuda::normal_kernel<at::CUDAGeneratorImpl*>(at::TensorBase const&, double, double, at::CUDAGeneratorImpl*)::{lambda()#1}::operator()() const::{lambda()#2}::operator()() const::{lambda(float)#1})::{lambda(curandStatePhilox4_32_10*)#2} const&, at::native::templates::cuda::normal_kernel<at::CUDAGeneratorImpl*>(at::TensorBase const&, double, double, at::CUDAGeneratorImpl*)::{lambda()#1}::operator()() const::{lambda()#2}::operator()() const::{lambda(float)#1})::{lambda(int, float)#1}) → vectorized_elementwise_kernel
  Count: 1
  Average Gap: 73203.73 μs
  Max Gap: 73203.73 μs
  Min Gap: 73203.73 μs
  Std Dev: 0.00 μs
  Total Gap Time: 73203.73 μs
------------------------------
...
...
...
```
