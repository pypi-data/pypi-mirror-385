# Cadence CLI

## Install

```shell
pip install jetbrains-cadence
```

This will create a `cadence` script in your current environment.

## Getting Started

```shell
cadence login
```

If you want to use Cadence CLI in the non-interactive environment, you
can [create the token manually](https://api.cadence.jetbrains.com/app/jettrain/token.html) and pass it via
`CADENCE_TOKEN` environment variable

### Start the execution from YAML config

```shell
cadence execution start --preset path/to/config.yaml
```

This will print the ID of the started execution.

### Basic Example

```yaml
working_dir: .
cmd:
  - python3 main.py
description: basic preset

provisioning:
  gpu_type: H200
  gpu_count: 1

env:
  python:
    version: 3.11
    pip:
      requirements_path: requirements.txt

project_sync:
  local:
    root: .
    storage_name: Cadence Storage
    uri: ""
    storage_type: DEFAULT

outputs:
  - type: OUTPUT
    storage_name: Cadence Storage
    uri: ""
    path: outputs # `./outputs` will be saved to S3
    storage_type: DEFAULT
```

### More Examples

Please see the [cadence-examples](https://github.com/JetBrains/cadence-examples) repository for more in-depth examples.
