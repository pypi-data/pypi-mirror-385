# 版本号统一管理

## ✅ 已完成的配置

项目已配置为统一的版本号管理方式，现在**只需要在一个地方**修改版本号。

### 📝 修改内容

1. **删除了 `setup.py`** - 已被 `pyproject.toml` 替代
2. **修改了 `seetrain/__init__.py`** - 动态读取版本号
3. **修改了 `seetrain/seetrain/__init__.py`** - 动态读取版本号
4. **添加了 Python 3.8 兼容依赖** - `importlib-metadata`

## 🎯 如何使用

### 更新版本号（只需一步！）

1. 打开 `pyproject.toml`
2. 修改第 7 行的版本号：

```toml
[project]
name = "seetrain-ml"
version = "0.1.7"  # 👈 只需要改这里！
```

3. 完成！所有地方的版本号会自动同步。

### 版本号读取机制

- **安装后**：自动从包元数据读取（`importlib.metadata`）
- **开发环境**：如果包未安装，使用 `0.1.6-dev` 作为标识

### 验证版本号

```bash
# 安装开发模式
pip install -e .

# 验证版本
python3 -c "import seetrain; print(seetrain.__version__)"
```

## 📊 对比

| 方式 | 修改位置 | 维护难度 |
|------|---------|---------|
| **之前** | 3个文件（pyproject.toml, setup.py, __init__.py） | ❌ 困难 |
| **现在** | 1个文件（pyproject.toml） | ✅ 简单 |

## 🔧 技术实现

版本号通过以下代码动态读取（已配置在 `__init__.py` 中）：

```python
try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    from importlib_metadata import version, PackageNotFoundError

try:
    __version__ = version("seetrain-ml")
except PackageNotFoundError:
    __version__ = "0.1.6-dev"
```

## 💡 优势

- ✅ **单一数据源** - 避免版本号不一致
- ✅ **自动同步** - 无需手动更新多个文件
- ✅ **标准化** - 遵循 PEP 621 标准
- ✅ **开发友好** - 开发环境有明确标识
- ✅ **向后兼容** - 支持 Python 3.8+

