# PyPI 发布指南

## 📦 包信息

- **包名**: cc-balancer
- **当前版本**: 0.1.0
- **PyPI 链接**: https://pypi.org/project/cc-balancer/0.1.0/
- **许可证**: MIT

## 🎯 发布流程总结

### 1. 准备工作

确保项目结构完整且配置正确：

```bash
# 项目结构
CC-B/
├── cc_balancer/          # 主包目录
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   └── ...
├── tests/               # 测试目录
├── pyproject.toml       # 包配置文件
├── README.md           # 项目说明
└── LICENSE             # 许可证文件
```

### 2. 安装构建工具

```bash
pip install --upgrade build twine
```

### 3. 清理旧构建

```bash
rm -rf dist/ build/ *.egg-info
```

### 4. 构建分发包

```bash
python -m build
```

这将生成：
- `dist/cc_balancer-0.1.0-py3-none-any.whl` - Wheel 包 (~40 KB)
- `dist/cc_balancer-0.1.0.tar.gz` - 源码包 (~47 KB)

### 5. 上传到 PyPI

```bash
python -m twine upload dist/* \
  --username __token__ \
  --password YOUR_PYPI_TOKEN
```

**重要**: PyPI Token 格式
- Username: `__token__`
- Password: `pypi-AgEIcHlwaS5vcmcCJGRm...` (完整的 token)

## 🔐 PyPI 凭据管理

### Token 存储位置

**当前使用的 Token**:
```
username: __token__
password: pypi-AgEIcHlwaS5vcmcCJGRmYWIyYTk2LTdiYjQtNDI0Yi1hNGVkLTAzYTJlNzU4MWNmYQACKlszLCI0N2Q1ZGEzNS01NzY4LTQ3ODktOTRkZS1hYTM1M2E0NzBlYzYiXQAABiAz4beBKwO0flbveTzlNWXniC9MObJZEBuuqiJ3JFM_lA
```

### 使用 .pypirc 配置（可选）

创建 `~/.pypirc` 文件：

```ini
[pypi]
  username = __token__
  password = pypi-AgEIcHlwaS5vcmcCJGRmYWIyYTk2...

[testpypi]
  username = __token__
  password = pypi-AgEIcHlwaS5vcmcCJGRm...
```

配置后可以简化上传命令：
```bash
python -m twine upload dist/*
```

## 📥 用户安装指南

### 安装包

```bash
pip install cc-balancer
```

### 验证安装

```bash
cc-balancer --help
```

### 基本使用

```bash
# 使用默认配置运行
cc-balancer

# 指定配置文件
cc-balancer --config /path/to/config.yaml

# 自定义主机和端口
cc-balancer --host 127.0.0.1 --port 8080

# 开发模式（自动重载）
cc-balancer --reload
```

## 🔄 版本更新流程

### 1. 更新版本号

编辑 `pyproject.toml`:

```toml
[project]
name = "cc-balancer"
version = "0.2.0"  # 更新这里
```

### 2. 更新 CHANGELOG

在 `CHANGELOG.md` 中添加更新内容：

```markdown
## [0.2.0] - 2025-10-21

### Added
- 新功能描述

### Changed
- 变更说明

### Fixed
- 修复的问题
```

### 3. 重新构建和发布

```bash
# 清理旧构建
rm -rf dist/ build/ *.egg-info

# 构建新版本
python -m build

# 上传到 PyPI
python -m twine upload dist/* --username __token__ --password YOUR_TOKEN
```

### 4. 创建 Git 标签

```bash
git tag -a v0.2.0 -m "Release version 0.2.0"
git push origin v0.2.0
```

## ✅ 发布检查清单

- [ ] 更新版本号 (`pyproject.toml`)
- [ ] 更新 CHANGELOG.md
- [ ] 运行所有测试 (`pytest`)
- [ ] 代码格式检查 (`black`, `ruff`)
- [ ] 类型检查 (`mypy`)
- [ ] 清理旧构建文件
- [ ] 构建分发包
- [ ] 检查构建产物
- [ ] 上传到 PyPI
- [ ] 验证安装
- [ ] 创建 Git 标签
- [ ] 更新文档

## 🛠️ 常见问题

### 1. 上传失败：文件已存在

**问题**: `File already exists`

**解决**: PyPI 不允许覆盖已发布的版本，必须更新版本号

```bash
# 更新版本号后重新构建
python -m build
python -m twine upload dist/*
```

### 2. Token 认证失败

**问题**: `Invalid or non-existent authentication information`

**解决**: 确认 token 格式正确
- Username 必须是 `__token__`
- Password 是完整的 `pypi-` 开头的 token

### 3. 包名冲突

**问题**: Package name already taken

**解决**: 选择不同的包名或联系当前包所有者

### 4. 依赖版本冲突

**问题**: 用户安装时依赖冲突

**解决**:
- 在 `pyproject.toml` 中放宽依赖版本要求
- 使用 `>=` 而不是 `==` 指定版本

```toml
dependencies = [
    "fastapi>=0.100.0",  # 好
    "fastapi==0.100.0",  # 可能导致冲突
]
```

## 📊 包统计

查看包的下载统计：
- PyPI 页面: https://pypi.org/project/cc-balancer/
- 下载统计: https://pypistats.org/packages/cc-balancer

## 🔍 测试发布（可选）

使用 TestPyPI 进行测试：

```bash
# 上传到 TestPyPI
python -m twine upload --repository testpypi dist/*

# 从 TestPyPI 安装测试
pip install --index-url https://test.pypi.org/simple/ cc-balancer
```

## 📝 License 配置注意事项

当前配置使用旧格式，可能在未来版本中被弃用。建议更新为新格式：

### 旧格式（当前）
```toml
license = {text = "MIT"}
classifiers = [
    "License :: OSI Approved :: MIT License",
]
```

### 新格式（推荐）
```toml
license = "MIT"
license-files = ["LICENSE"]
# 移除 classifiers 中的 License 行
```

## 🎉 发布历史

### v0.1.0 (2025-10-21)
- ✅ 首次发布到 PyPI
- ✅ 基础功能实现
- ✅ FastAPI 代理服务器
- ✅ 多提供商路由
- ✅ 配置文件支持
- ✅ 健康检查端点
- ✅ CLI 命令行工具

## 📚 相关资源

- [PyPI 官方文档](https://packaging.python.org/)
- [setuptools 文档](https://setuptools.pypa.io/)
- [twine 文档](https://twine.readthedocs.io/)
- [版本规范 (PEP 440)](https://www.python.org/dev/peps/pep-0440/)
- [PyPI Token 管理](https://pypi.org/help/#apitoken)

## 🤝 贡献指南

如果其他开发者想要发布新版本：

1. 确保拥有 PyPI token
2. 遵循语义化版本规范
3. 更新文档和 CHANGELOG
4. 通过所有测试
5. 创建 PR 并等待审核
6. 合并后由维护者发布

---

**最后更新**: 2025-10-21
**维护者**: CC-Balancer Contributors
**联系方式**: GitHub Issues
