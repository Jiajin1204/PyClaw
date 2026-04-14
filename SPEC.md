# PyClaw AI Agent 规格文档

## 1. 项目概述

- **项目名称**: PyClaw
- **项目类型**: Python AI 智能体框架
- **核心功能**: 一个可自我编写和执行脚本的AI智能体，支持多操作系统、工具系统、会话管理和长期记忆
- **目标用户**: 开发者、数据科学家、运维工程师

## 2. 核心功能

### 2.1 内置工具 (Core Tools)
- **read**: 读取文件内容
- **write**: 写入文件内容
- **exec**: 执行Python脚本/命令

### 2.2 工具系统 (Tool System)
- 核心内置工具 (read, write, exec)
- Skill 系统: 可扩展的技能模块
- MCP (Model Context Protocol) 支持

### 2.3 大模型支持
- OpenAI 兼容 API
- Anthropic 兼容 API
- 可配置 base URL
- 配置文件中指定模型

### 2.4 会话管理
- 会话存储为 JSONL 文件
- 支持会话恢复 (重启后可继续)
- 每个会话有唯一 ID

### 2.5 长期记忆
- MEMORY.md 文件存储持久记忆
- 会话启动时加载

### 2.6 控制台命令
- `/help` - 显示帮助文档
- `/new` - 开启新会话
- `/switch <session_id>` - 切换会话
- `/sessions` - 列出所有会话
- `/delete <session_id>` - 删除会话
- `/memory` - 查看当前记忆
- `/clear` - 清屏
- `/exit` - 退出程序

## 3. 技术架构

```
pyclaw/
├── config.json           # 配置文件
├── MEMORY.md             # 长期记忆文件
├── sessions/             # 会话存储目录
│   └── <session_id>.jsonl
├── tools/                # 工具目录
│   ├── __init__.py
│   ├── base.py           # 工具基类
│   ├── read.py           # read 工具
│   ├── write.py          # write 工具
│   ├── exec.py           # exec 工具
│   └── registry.py       # 工具注册器
├── skills/               # 技能目录
│   └── skill.py          # Skill 基类
├── models/               # 模型适配器
│   ├── __init__.py
│   ├── base.py           # 模型基类
│   ├── openai.py         # OpenAI 适配器
│   └── anthropic.py      # Anthropic 适配器
├── session.py            # 会话管理
├── agent.py              # 智能体核心
├── cli.py                # 命令行界面
└── main.py               # 入口文件
```

## 4. 配置文件格式 (config.json)

```json
{
    "model": {
        "provider": "openai",  // openai 或 anthropic
        "model": "gpt-4",
        "api_key": "your-api-key",
        "base_url": "https://api.openai.com/v1",
        "max_tokens": 4096,
        "temperature": 0.7
    },
    "system_prompt": "You are PyClaw, an AI agent that can read, write and execute code.",
    "session_dir": "sessions",
    "memory_file": "MEMORY.md",
    "tools": {
        "exec": {
            "timeout": 60,
            "working_dir": "workspace"
        }
    }
}
```

## 5. 会话格式 (JSONL)

每行是一个 JSON 对象:
```json
{"role": "user", "content": "hello", "timestamp": "2024-01-01T00:00:00"}
{"role": "assistant", "content": "Hi!", "timestamp": "2024-01-01T00:00:01", "tool_calls": [...]}
```

## 6. 界面交互

### 6.1 启动界面
```
╔═══════════════════════════════════════════╗
║           PyClaw AI Agent                 ║
║═══════════════════════════════════════════║
Session: abc123  |  Model: gpt-4
Type /help for commands
───────────────────────────────────────────
>
```

### 6.2 工具执行输出
```
[TOOL] read file: "/path/to/file.py"
[TOOL] write file: "/path/to/..."
[TOOL] exec: "python script.py"
```

## 7. 验收标准

- [x] 配置从 config.json 加载
- [x] 支持 OpenAI 和 Anthropic API
- [x] read/write/exec 工具正常工作
- [x] 会话保存为 JSONL 并可恢复
- [x] MEMORY.md 持久记忆
- [x] 所有控制台命令正常
- [x] 工具执行时控制台打印 (截断到2行)
- [x] 模块化设计，易于扩展
- [x] 支持 Skill 和 MCP 扩展
- [x] 不损害系统 Python 环境 (虚拟环境)
