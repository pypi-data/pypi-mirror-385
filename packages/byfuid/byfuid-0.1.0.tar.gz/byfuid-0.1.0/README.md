# BYFUID 生成器

高性能 BYFUID 生成工具，提供命令行接口用于生成和验证 BYFUID 字符串。

## 功能特性

- 生成随机 BYFUID
- 使用指定用户数据生成 BYFUID
- 使用自定义数据生成 BYFUID
- 验证 BYFUID 长度

## 安装

请确保你已经安装了 Python 3.7 或更高版本。然后使用 pip 安装：

```bash
pip install git+https://gitee.com/byusi/byfuid
```
> GitHub `pip install git+https://github/byusiteam/byfuid`

## 使用方法

### 生成 BYFUID

```bash
byfuid generate
```

- 使用指定用户数据：

```bash
byfuid generate -u "user12345678"
```

- 使用自定义数据：

```bash
byfuid generate -c "我的自定义数据"
```

- 使用用户数据和自定义数据：

```bash
byfuid generate -u "test12345678" -c "hello"
```

### 验证 BYFUID

```bash
byfuid validate "BYFUID字符串"
```

## 示例

```bash
# 生成随机 BYFUID
byfuid generate

# 生成带有用户数据的 BYFUID
byfuid generate -u "user12345678"

# 生成带有自定义数据的 BYFUID
byfuid generate -c "我的自定义数据"

# 验证 BYFUID 长度
byfuid validate "BYFUID字符串"
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

## 贡献

欢迎贡献代码和改进文档。请提交 Pull Request 或 Issue 到项目仓库。

## 许可证

该项目使用 MIT 许可证。详情请查看 LICENSE 文件。