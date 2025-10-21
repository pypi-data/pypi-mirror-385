# 🚀 docpipe-ai PyPI 自动发布指南

## 📋 概述

本文档描述了如何使用 GitHub Actions 工作流自动发布 docpipe-ai 包到 PyPI。

## 🔧 当前配置

### 项目信息
- **包名**: `docpipe-ai`
- **版本**: 动态从 `src/docpipe_ai/__init__.py` 读取
- **Python 版本**: >=3.11
- **构建后端**: hatchling

### 版本文件位置
```
src/docpipe_ai/__init__.py
```
版本号定义在此文件中：
```python
__version__ = "0.2.0"
```

## 🔑 配置要求

### 1. PyPI API Token

1. 访问 [PyPI Account Settings](https://pypi.org/manage/account/)
2. 生成新的 API Token
3. 设置权限范围为 `docpipe-ai` 项目

### 2. GitHub Secrets

在仓库设置中添加：

- `PYPI_API_TOKEN`: 你的 PyPI API token

### 3. GitHub Environments

已配置 `pypi` 环境：
- **环境名称**: `pypi`
- **环境URL**: https://pypi.org/p/docpipe-ai
- **保护规则**: 可根据需要配置

## 🚀 发布流程

### 标准发布流程

```bash
# 1. 更新版本号
echo '__version__ = "0.2.1"' > src/docpipe_ai/__init__.py

# 2. 提交代码
git add src/docpipe_ai/__init__.py
git commit -m "bump: version 0.2.1"

# 3. 创建标签
git tag v0.2.1

# 4. 推送标签（自动触发发布）
git push origin v0.2.1

# ✅ CI 自动构建并发布到 PyPI
```

### 批量发布多个版本

```bash
# 发布补丁版本
git tag v0.2.2 && git push origin v0.2.2

# 发布次版本
git tag v0.3.0 && git push origin v0.3.0

# 发布主版本
git tag v1.0.0 && git push origin v1.0.0
```

### 手动触发发布

1. 进入 GitHub 仓库的 Actions 页面
2. 选择 "Build and Publish to PyPI" 工作流
3. 点击 "Run workflow"
4. 选择分支并运行

## 📁 工作流文件

### 1. 发布工作流 (`.github/workflows/publish.yml`)

纯净的构建和发布工作流，分为两个阶段：

```yaml
name: Build and Publish to PyPI

on:
  push:
    tags: [ "v*" ]  # 只在推送标签时触发发布
  workflow_dispatch:  # 允许手动触发

jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.version.outputs.version }}

    steps:
    - uses: actions/checkout@v4
      with:
        fetch-depth: 0

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install uv
      uses: astral-sh/setup-uv@v3
      with:
        version: "latest"

    - name: Extract version
      id: version
      run: |
        # 从 __init__.py 提取版本号
        VERSION=$(grep '__version__' src/docpipe_ai/__init__.py | cut -d'"' -f2)
        echo "version=$VERSION" >> $GITHUB_OUTPUT
        echo "Package version: $VERSION"

    - name: Build package
      run: |
        # 清理旧的构建文件
        rm -rf dist/ build/ *.egg-info/

        # 构建包
        uv build --wheel --sdist

        # 显示构建的文件
        ls -la dist/

    - name: Check package
      run: |
        python -m pip install twine
        python -m twine check dist/*

    - name: Upload build artifacts
      uses: actions/upload-artifact@v4
      with:
        name: dist-packages
        path: dist/
        retention-days: 7

  publish:
    needs: build
    runs-on: ubuntu-latest
    environment:
      name: pypi
      url: https://pypi.org/p/docpipe-ai
    permissions:
      id-token: write  # 必需：受信任发布
      contents: read    # 必需：读取仓库内容

    steps:
    - name: Download build artifacts
      uses: actions/download-artifact@v4
      with:
        name: dist-packages
        path: dist/

    - name: Display package info
      run: |
        echo "Version: ${{ needs.build.outputs.version }}"
        ls -la dist/

    - name: Publish to PyPI
      uses: pypa/gh-action-pypi-publish@release/v1
      with:
        password: ${{ secrets.PYPI_API_TOKEN }}
        verbose: true
        skip-existing: true
```

### 2. 工作流架构

发布工作流分为两个阶段：

#### Build 阶段
- 检出代码
- 设置 Python 3.11 环境
- 安装 uv 构建工具
- 从 `__init__.py` 提取版本号
- 构建 wheel 和 sdist 包
- 运行 twine 检查
- 上传构建产物

#### Publish 阶段
- 下载构建产物
- 显示包信息
- 发布到 PyPI

## 🔧 常用命令

### 本地测试构建

```bash
# 安装构建工具
pip install hatchling twine

# 构建包
python -m build

# 检查包
twine check dist/*

# 本地安装测试
pip install dist/docpipe_ai-*.whl
```

### 版本管理

```bash
# 查看当前版本
python -c "import docpipe_ai; print(docpipe_ai.__version__)"

# 查看所有标签
git tag --sort=-version:refname

# 删除本地标签
git tag -d v0.2.1

# 删除远程标签
git push origin --delete v0.2.1
```

## ⚠️ 注意事项

### 1. 版本号规范
- 使用语义化版本：`主版本.次版本.补丁版本`
- 当前版本：`0.2.0`
- 开发版本使用 `alpha/beta/rc` 后缀

### 2. 发布前检查清单
- [ ] 版本号已更新
- [ ] CHANGELOG.md 已更新（如果有）
- [ ] 本地构建测试通过
- [ ] 代码已提交到主分支

### 3. 故障排除

#### 发布失败
- 检查 `PYPI_API_TOKEN` 是否正确
- 确认版本号没有冲突
- 查看 Actions 日志获取详细错误信息

#### 构建失败
- 检查 `pyproject.toml` 配置
- 确认所有依赖都正确声明
- 运行本地构建测试

## 📚 相关链接

- [PyPI 项目页面](https://pypi.org/project/docpipe-ai/)
- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [Hatchling 构建工具](https://hatch.pypa.io/latest/)
- [uv 包管理器](https://github.com/astral-sh/uv)

## 🎯 发布示例

### 发布补丁版本 (0.2.1)

```bash
# 1. 更新版本
echo '__version__ = "0.2.1"' > src/docpipe_ai/__init__.py

# 2. 提交并推送
git add src/docpipe_ai/__init__.py
git commit -m "bump: version 0.2.1 - fix issues"
git tag v0.2.1
git push origin v0.2.1

# 3. 等待 CI 完成，检查 PyPI
```

### 发布次版本 (0.3.0)

```bash
# 1. 更新版本
echo '__version__ = "0.3.0"' > src/docpipe_ai/__init__.py

# 2. 提交并推送
git add src/docpipe_ai/__init__.py
git commit -m "feat: version 0.3.0 - new features"
git tag v0.3.0
git push origin v0.3.0

# 3. 等待 CI 完成，检查 PyPI
```

---

此配置已为 docpipe-ai 项目量身定制，支持可靠的自动化发布流程！