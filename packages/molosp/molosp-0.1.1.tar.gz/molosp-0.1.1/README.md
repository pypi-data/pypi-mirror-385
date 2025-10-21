# molosp

**MO**dule **LO**ader for **SP**ark - A utility package for dynamically loading Python modules from S3 into AWS Glue/Spark jobs.

## Installation

```bash
pip install molosp
```

## Usage

```python
from molosp.loader import load_external_module

# Load a module from S3 into your Spark job
module = load_external_module(
    spark_context=sc,
    helper_module_s3_url="s3://my-bucket/path/to/module.py",
    module_name="my_module"
)

# Use the loaded module
module.some_function()
```

## Features

- **Dynamic Module Loading**: Download and import Python modules from S3 at runtime
- **Spark Integration**: Automatically adds modules to SparkContext PyFiles
- **Automatic Path Management**: Handles sys.path configuration for imported modules

## Development

```bash
# Install with dev dependencies
pip install -e .[dev]

# Run tests
PYTHONPATH=src python -m unittest discover tests
```

## License

MIT License - See LICENSE file for details.
