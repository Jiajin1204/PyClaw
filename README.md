# PyClaw AI Agent

一个可自我编写和执行脚本的 Python AI 智能体，支持多操作系统、会话管理、长期记忆和工具扩展。

## 特性

- **核心工具**: 内置 read/write/exec 工具，可读写文件和执行代码
- **多模型支持**: OpenAI 和 Anthropic 兼容 API
- **会话管理**: JSONL 文件存储，重启后可恢复
- **长期记忆**: MEMORY.md 文件持久存储
- **MCP 支持**: 可连接 MCP 服务器扩展工具
- **Skill 系统**: 可扩展的技能模块
- **跨平台**: 支持 Linux/macOS/Windows
- **虚拟环境**: 不损害系统 Python 环境

## 快速开始

### 1. 安装

**Linux/macOS:**
```bash
./run.sh
```

**Windows:**
```cmd
run.bat
```

首次运行会自动创建虚拟环境并安装依赖。

### 2. 配置

编辑 `config.json`：

```json
{
    "model": {
        "provider": "openai",
        "model": "gpt-4",
        "api_key": "你的API密钥",
        "base_url": "https://api.openai.com/v1",
        "max_tokens": 4096,
        "temperature": 0.7
    }
}
```

| 参数 | 说明 |
|------|------|
| provider | `openai` 或 `anthropic` |
| model | 模型名称，如 `gpt-4`、`claude-3-sonnet` |
| api_key | 你的 API 密钥 |
| base_url | API 端点地址 |

### 3. 运行

```bash
./run.sh
```

启动后显示：
```
╔═══════════════════════════════════════════╗
║           PyClaw AI Agent                  ║
║═══════════════════════════════════════════║
Session: abc123    |  Model: gpt-4
───────────────────────────────────────────

Type /help for commands or just start chatting.
>
```

## 控制台命令

| 命令 | 说明 |
|------|------|
| `/help` | 显示帮助 |
| `/new` | 开启新会话 |
| `/switch <id>` | 切换到指定会话 |
| `/sessions` | 列出所有会话 |
| `/delete <id>` | 删除指定会话 |
| `/memory` | 查看当前记忆 |
| `/memory <text>` | 添加内容到记忆 |
| `/clear` | 清屏 |
| `/exit` | 退出 |

## 内置工具

### read
读取文件内容。
```json
{"file_path": "/path/to/file.txt"}
```

### write
写入内容到文件（自动创建目录）。
```json
{"file_path": "/path/to/file.txt", "content": "Hello World"}
```

### exec
执行 Python 代码或 Shell 命令。
```json
{"command": "print('Hello from Python!')", "language": "python"}
{"command": "ls -la", "language": "shell"}
```

## 文件结构

```
pyclaw/
├── config.json           # 配置文件
├── MEMORY.md             # 长期记忆
├── sessions/             # 会话存储 (JSONL)
├── workspace/            # exec 工作目录
├── tools/                # 工具模块
│   ├── base.py
│   ├── read.py
│   ├── write.py
│   ├── exec_tool.py
│   └── registry.py
├── skills/               # 技能模块
├── models/              # 模型适配器
│   ├── openai.py
│   └── anthropic.py
├── session.py            # 会话管理
├── agent.py              # 智能体核心
├── cli.py                # 命令行界面
└── mcp.py                # MCP 协议支持
```

## MCP 配置

在 `config.json` 中添加 MCP 服务器：

```json
{
    "mcp": {
        "enabled": true,
        "servers": [
            {
                "name": "my-server",
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/dir"]
            }
        ]
    }
}
```

## Skill 开发

创建自定义技能：

```python
# skills/my_skill.py
from skills import Skill

class MySkill(Skill):
    def __init__(self):
        super().__init__("my_skill", "My custom skill")

    def execute(self, **kwargs):
        return "Skill executed!"

    def get_tools(self):
        return [{
            "type": "function",
            "function": {
                "name": "my_tool",
                "description": "My custom tool",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        }]
```

## 示例对话

```
> 用 Python 写一个快速排序

[TOOL] write: {"file_path": "workspace/quick_sort.py", ...}
[TOOL] exec: {"command": "python workspace/quick_sort.py", ...}

def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)

print(quick_sort([3, 6, 8, 10, 1, 2, 1]))
# 输出: [1, 1, 2, 3, 6, 8, 10]
```

## 常见问题

**Q: 提示 "API key" 错误？**
A: 检查 `config.json` 中的 `api_key` 是否正确配置。

**Q: 如何使用代理？**
A: 在 `config.json` 中设置 `proxy` 字段，或在运行前设置环境变量 `HTTP_PROXY`/`HTTPS_PROXY`。

**Q: exec 执行超时？**
A: 在 `config.json` 的 `tools.exec` 中增加 `timeout` 值（秒）。

**Q: 如何切换模型？**
A: 修改 `config.json` 中 `model.provider` 为 `openai` 或 `anthropic`，并设置对应的 `model` 名称。
