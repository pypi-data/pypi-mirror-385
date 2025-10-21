# B10 Transfer

Accelerate cold starts by loading previous PyTorch compilation artifacts. This library enables caching of `torch.compile()` results across Baseten deployments, reducing compilation latencies by up to 5x.

## Quick Start

### For Standard Models (`model.py`)

```python
from b10_transfer import load_compile_cache, save_compile_cache, OperationStatus

class Model:
    def load(self):
        # Load your model first
        self.model = YourModel().to("cuda")
        
        # Try to load existing compile cache
        cache_loaded = load_compile_cache()
        
        if cache_loaded == OperationStatus.ERROR:
            print("Run in eager mode, skipping torch compile")
        else:
            # Compile your model
            self.model = torch.compile(self.model, mode="max-autotune-no-cudagraphs")
            
            # Warm up with representative inputs to trigger compilation
            self.model("dummy input")
            self.model("another dummy input")
            
            # Save cache if it was newly created
            if cache_loaded != OperationStatus.SUCCESS:
                save_compile_cache()
```

### For vLLM Custom Servers

Add to your `config.yaml`:

```yaml
requirements:
  - b10-transfer

start_command: "b10-compile-cache & vllm serve ..."
```

The `b10-compile-cache` CLI tool automatically handles cache loading and saving for vLLM deployments.

## Requirements

Add to your `config.yaml`:

```yaml
requirements:
  - b10-transfer
```

**Note:** Requires b10cache enabled in your Baseten environment.

## API Reference

### Core Functions

#### `load_compile_cache() -> OperationStatus`

Load previously saved compilation cache for the current model environment.

**Returns:**
- `OperationStatus.SUCCESS` → Cache successfully loaded
- `OperationStatus.SKIPPED` → Cache already exists locally  
- `OperationStatus.ERROR` → General errors (b10fs unavailable, validation failed)
- `OperationStatus.DOES_NOT_EXIST` → No cache file found for this environment

#### `save_compile_cache() -> OperationStatus`

Save the current model's torch compilation cache for future deployments.

**Returns:**
- `OperationStatus.SUCCESS` → Cache successfully saved
- `OperationStatus.SKIPPED` → Cache already exists in shared directory
- `OperationStatus.ERROR` → General errors (insufficient space, validation failed)

#### `save_vllm_compile_cache() -> None`

Specialized function for vLLM deployments that:
1. Attempts to load existing cache first
2. Waits for vLLM server readiness
3. Automatically saves cache after compilation

### Utility Functions

#### `clear_local_cache() -> bool`

Clear the local PyTorch compilation cache directory.

**Returns:**
- `True` → Cache cleared successfully or didn't exist
- `False` → Failed to clear cache

#### `get_cache_info() -> Dict[str, Any]`

Get comprehensive information about current cache state.

**Returns:**
```python
{
    "environment_key": str,           # Unique environment identifier
    "local_cache_exists": bool,       # Local torch cache status
    "b10fs_enabled": bool,           # B10FS availability
    "b10fs_cache_exists": bool,      # Remote cache status
    "local_cache_size_mb": float,    # Local cache size (if exists)
    "b10fs_cache_size_mb": float     # Remote cache size (if exists)
}
```

#### `list_available_caches() -> Dict[str, Any]`

List all available cache files with metadata.

**Returns:**
```python
{
    "caches": [                      # List of cache files
        {
            "filename": str,         # Cache file name
            "environment_key": str,  # Environment identifier  
            "size_mb": float,        # File size in MB
            "is_current_environment": bool,  # Matches current env
            "created_time": float    # Creation timestamp
        }
    ],
    "current_environment": str,      # Current environment key
    "total_caches": int,            # Number of cache files
    "current_cache_exists": bool,   # Current env has cache
    "b10fs_enabled": bool          # B10FS availability
}
```

### Constants

#### `OperationStatus` Enum

Status codes returned by cache operations:

- `OperationStatus.SUCCESS` → Operation completed successfully
- `OperationStatus.ERROR` → Operation failed due to error
- `OperationStatus.DOES_NOT_EXIST` → Cache file not found (load operations only)
- `OperationStatus.SKIPPED` → Operation not needed (cache already exists)

### Exceptions

#### `CacheError`

Base exception for cache operations.

#### `CacheValidationError`

Raised when path validation or security checks fail.

#### `CacheOperationInterrupted`

Raised when operations are stopped due to insufficient disk space.

## Configuration

The library automatically configures itself, but you can override defaults:

```bash
# Cache directories
export TORCHINDUCTOR_CACHE_DIR="/tmp/torchinductor_$(whoami)"
export B10FS_CACHE_DIR="/cache/model/compile_cache"
export LOCAL_WORK_DIR="/app"

# Cache limits
export MAX_CACHE_SIZE_MB="1024"        # 1GB max archive size
export MAX_CONCURRENT_SAVES="50"       # Concurrent save operations

# Required for functionality
export BASETEN_FS_ENABLED="1"
```

## How It Works

### Environment-Specific Caching

Caches are automatically keyed by hardware environment to ensure compatibility:

**GPU Environments:**
- **GPU Device Name**: e.g., "NVIDIA GeForce RTX 4090"
- **CUDA Version**: e.g., "12.1"

**CPU Environments:**
- **CPU Architecture**: e.g., "x86_64", "arm64"
- **Platform**: e.g., "Linux", "Darwin", "Windows"

This ensures cached artifacts work correctly across similar hardware configurations while supporting both GPU and CPU-only deployments.

### Atomic Operations

1. **Load**: B10FS → local temp → extract to torch cache directory
2. **Save**: Compress torch cache → B10FS temp → atomic rename  
3. **Space Monitoring**: Operations interrupted if disk space insufficient

## Debugging

```python
# Enable debug logging
import logging
logging.getLogger('b10_transfer').setLevel(logging.DEBUG)

# Check cache status
info = b10_transfer.get_cache_info()
print(f"Environment: {info['environment_key']}")
print(f"Local cache: {info['local_cache_exists']}")
print(f"Remote cache: {info['b10fs_cache_exists']}")

# List all available caches
caches = b10_transfer.list_available_caches()
print(f"Total caches: {caches['total_caches']}")
for cache in caches['caches']:
    print(f"  {cache['filename']} ({cache['size_mb']:.1f} MB)")
```

---

[Baseten Documentation](https://docs.baseten.co/development/model/torch-compile-cache)
