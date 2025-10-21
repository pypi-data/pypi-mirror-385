# BYFUID Generator

High-performance BYFUID generation tool that provides a command-line interface for generating and validating BYFUID strings.

## Features

- Generate random BYFUID
- Generate BYFUID using specified user data
- Generate BYFUID using custom data
- Validate BYFUID length

## Installation

Ensure you have Python 3.7 or later installed. Then install using pip:

```bash
pip install git+https://gitee.com/byusi/byfuid
```
> GitHub `pip install git+https://github/byusiteam/byfuid`

## Usage

### Generate BYFUID

```bash
byfuid generate
```

- Using specified user data:

```bash
byfuid generate -u "user12345678"
```

- Using custom data:

```bash
byfuid generate -c "my custom data"
```

- Using both user data and custom data:

```bash
byfuid generate -u "test12345678" -c "hello"
```

### Validate BYFUID

```bash
byfuid validate "BYFUID string"
```

## Examples

```bash
# Generate a random BYFUID
byfuid generate

# Generate a BYFUID with user data
byfuid generate -u "user12345678"

# Generate a BYFUID with custom data
byfuid generate -c "my custom data"

# Validate BYFUID length
byfuid validate "BYFUID string"
```

## Python API
```python
from byfuid import generate_byfuid, validate_byfuid_length

# 生成 BYFUID
byfuid_str = generate_byfuid(
    user_data="user12345678",
    custom_data="订单支付成功"
)

# 验证长度
is_valid = validate_byfuid_length(byfuid_str)
```

## Contributions

Code contributions and documentation improvements are welcome. Please submit a Pull Request or Issue to the project repository.

## License

This project uses the MIT License. For details, please see the LICENSE file.