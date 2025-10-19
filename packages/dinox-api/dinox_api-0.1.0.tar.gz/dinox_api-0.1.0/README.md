# Dinox API Python 客户端

[![PyPI version](https://badge.fury.io/py/dinox-api.svg)](https://badge.fury.io/py/dinox-api)
[![Python Version](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://github.com/JimEverest/DinoSync/actions/workflows/test.yml/badge.svg)](https://github.com/JimEverest/DinoSync/actions/workflows/test.yml)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

一个功能完整、易于使用的 Python 异步客户端库，用于与 Dinox AI 笔记服务进行交互。

---

## 📦 安装

### 通过 PyPI 安装（推荐）

```bash
pip install dinox-api
```

### 从源码安装

```bash
git clone https://github.com/JimEverest/DinoSync.git
cd DinoSync
pip install -e .
```

---

## ✨ 特性

- ✅ **完整的 API 覆盖** - 支持所有可用的 Dinox API 接口
- ✅ **异步支持** - 基于 aiohttp，性能优异
- ✅ **类型提示** - 完整的类型注解，IDE 友好
- ✅ **错误处理** - 详细的错误信息和异常处理
- ✅ **易于使用** - 简洁的 API 设计，上下文管理器支持
- ✅ **安全配置** - 使用 .env 文件管理敏感信息
- ✅ **全面测试** - 22 个测试用例，100% 通过率

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置 API Token

复制环境变量模板并配置您的 Token：

```bash
# Linux/Mac
cp env.example .env

# Windows
copy env.example .env
```

编辑 `.env` 文件：

```bash
DINOX_API_TOKEN=your_actual_token_here
```

### 3. 基础使用

```python
import asyncio
from dinox_client import DinoxClient

async def main():
    async with DinoxClient(api_token="YOUR_TOKEN") as client:
        # 获取笔记列表
        notes = await client.get_notes_list()
        print(f"获取到 {len(notes)} 天的笔记")
        
        # 遍历笔记
        for day_note in notes:
            print(f"日期: {day_note['date']}")
            for note in day_note['notes']:
                print(f"  - {note['title']}")

asyncio.run(main())
```

---

## 📚 主要功能

### 场景 1：查询和管理笔记（笔记服务器）

```python
# 使用默认配置（笔记服务器）
async with DinoxClient(api_token=token) as client:
    # 获取所有笔记
    notes = await client.get_notes_list()
    
    # 增量同步
    recent = await client.get_notes_list(last_sync_time="2025-10-18 00:00:00")
    
    # 根据 ID 查询
    note = await client.get_note_by_id("note-id-here")
```

### 场景 2：搜索和创建笔记（AI 服务器）

```python
from dinox_client import DinoxClient, DinoxConfig

# 配置使用 AI 服务器
config = DinoxConfig(
    api_token=token,
    base_url="https://aisdk.chatgo.pro"  # AI 服务器
)

async with DinoxClient(config=config) as client:
    # 搜索笔记
    result = await client.search_notes(["关键词"])
    print(result['content'])
    
    # 创建笔记
    await client.create_note("# 标题\n\n内容")
    
    # 获取卡片盒
    boxes = await client.get_zettelboxes()
```

### 场景 3：完整应用示例

```python
import json
from pathlib import Path

async def complete_workflow():
    token = "YOUR_TOKEN"
    
    # 1. 使用笔记服务器同步笔记
    print("步骤1: 同步笔记...")
    async with DinoxClient(api_token=token) as client:
        notes = await client.get_notes_list()
        print(f"获取到 {len(notes)} 天的笔记")
    
    # 2. 使用 AI 服务器搜索特定内容
    print("\n步骤2: 搜索笔记...")
    config_ai = DinoxConfig(
        api_token=token,
        base_url="https://aisdk.chatgo.pro"
    )
    async with DinoxClient(config=config_ai) as client:
        result = await client.search_notes(["Python", "API"])
        print(f"找到相关内容")
        
        # 3. 创建新笔记
        print("\n步骤3: 创建新笔记...")
        await client.create_note("# 新笔记\n\n通过 API 创建")
        print("创建成功")
```

---

## 🧪 运行测试

```bash
# 运行所有测试
python -m pytest test_dinox_client.py -v

# 查看示例
python example.py
```

**测试结果**：
```
======================== 22 passed in 3.79s ========================
```

---

## 📖 API 参考

### ⚠️ 重要说明：两个 API 服务器

Dinox 目前有两个 API 服务器，支持不同的功能：

| 服务器 | URL | 支持的 API |
|--------|-----|-----------|
| **笔记服务器** | `https://dinoai.chatgo.pro` | `get_notes_list`, `get_note_by_id` |
| **AI服务器** | `https://aisdk.chatgo.pro` | `search_notes`, `create_note`, `get_zettelboxes` |

**默认使用笔记服务器**。如需使用搜索和创建功能，请配置使用 AI 服务器：

```python
from dinox_client import DinoxClient, DinoxConfig

# 使用 AI 服务器
config = DinoxConfig(
    api_token="YOUR_TOKEN",
    base_url="https://aisdk.chatgo.pro"  # AI 服务器
)
client = DinoxClient(config=config)
```

### 可用的方法

| 方法 | 功能 | 服务器 | 状态 |
|------|------|--------|------|
| `get_notes_list(...)` | 获取笔记列表，支持增量同步 | 笔记服务器 | ✅ 可用 |
| `get_note_by_id(note_id)` | 根据 ID 查询笔记 | 笔记服务器 | ✅ 可用 |
| `search_notes(keywords)` | 搜索笔记 | AI服务器 | ✅ 可用 |
| `get_zettelboxes()` | 获取卡片盒列表 | AI服务器 | ✅ 可用 |
| `create_note(content, ...)` | 创建笔记（支持卡片盒） | AI服务器 | ✅ 可用 |
| `format_sync_time(dt)` | 格式化同步时间 | 本地 | ✅ 可用 |

---

## ⚠️ 错误处理

```python
from dinox_client import DinoxAPIError

try:
    async with DinoxClient(api_token=token) as client:
        notes = await client.get_notes_list()
except DinoxAPIError as e:
    print(f"错误: [{e.code}] {e.message}")
    print(f"HTTP 状态: {e.status_code}")
```

---

## 🎯 最佳实践

### 1. 使用上下文管理器

```python
# ✅ 推荐：自动管理连接
async with DinoxClient(api_token=token) as client:
    notes = await client.get_notes_list()

# ❌ 不推荐：需要手动管理
client = DinoxClient(api_token=token)
await client.connect()
try:
    notes = await client.get_notes_list()
finally:
    await client.close()
```

### 2. 使用环境变量管理 Token

```python
import os
from dotenv import load_dotenv

load_dotenv()
token = os.environ.get("DINOX_API_TOKEN")
```

### 3. 实现增量同步

只获取更新的笔记，减少数据传输和处理时间。

---

## 📁 项目结构

```
dinox_api_py/
├── dinox_client.py           # 核心客户端库
├── test_dinox_client.py      # 测试套件（22个测试）
├── example.py                # 使用示例
├── requirements.txt          # 项目依赖
├── .env                      # 环境变量（不提交到Git）
├── env.example              # 环境变量模板
├── .gitignore               # Git忽略文件
├── README.md                # 本文件
└── docs/                    # 详细文档
    ├── Python客户端使用文档.md
    ├── 获取笔记列表（同步接口）.md
    └── ...
```

---

## 🔧 配置选项

### DinoxConfig

```python
from dinox_client import DinoxClient, DinoxConfig

config = DinoxConfig(
    api_token="YOUR_TOKEN",              # 必需
    base_url="https://dinoai.chatgo.pro", # 可选
    timeout=30                            # 可选，单位：秒
)

client = DinoxClient(config=config)
```

---

## 📊 性能

在标准网络条件下的性能表现：

- 单次获取笔记列表：~1.2秒
- 5个并发请求：~1.5秒（总计）
- 平均响应时间：~0.3秒/请求

---

## 🛠️ 故障排除

### 问题：找不到 DINOX_API_TOKEN

**解决方案**：
1. 确认已创建 `.env` 文件
2. 检查 Token 配置格式：`DINOX_API_TOKEN=your_token_here`
3. 确保没有多余的空格或引号

### 问题：API 返回 404 错误

**原因**：该 API 端点暂未部署

**解决方案**：使用其他可用的 API 方法，参考上面的 API 状态表

---

## 📄 许可证

本项目采用 MIT 许可证。

---

## 📞 技术支持

- **Email**: zmyjust@gmail.com
- **GitHub**: https://github.com/ryzencool/dinox-sync
- **官网**: https://dinox.info
- **详细文档**: [docs/Python客户端使用文档.md](docs/Python客户端使用文档.md)

---

## 🙏 致谢

感谢 Dinox 团队提供优秀的 API 服务！

---

**开始使用 Dinox Python Client，让笔记管理更简单！** 🎉

