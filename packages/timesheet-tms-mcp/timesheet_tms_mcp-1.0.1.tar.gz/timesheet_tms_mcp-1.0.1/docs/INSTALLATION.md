# Timesheet MCP 安装指南

本文档介绍如何安装和配置 Timesheet MCP Server。

## 快速安装

### 方式 1: 从 PyPI 安装（最简单）⭐

```bash
pip install timesheet-tms-mcp
```

然后在 Claude Desktop 或 Cursor 的 MCP 配置中添加：

```json
{
  "mcpServers": {
    "timesheet": {
      "command": "uvx",
      "args": ["timesheet-tms-mcp"],
      "env": {
        "TIMESHEET_API_BASE_URL": "https://tms.ktvsky.com/api",
        "TIMESHEET_API_TOKEN": "your-jwt-token-here"
      }
    }
  }
}
```

### 方式 2: 从 GitHub 安装

```bash
# 安装最新开发版本
pip install git+https://github.com/yangyuezheng/ai-emp@main#subdirectory=timesheet-mcp-server-v2

# 或安装指定版本
pip install git+https://github.com/yangyuezheng/ai-emp@v1.0.0#subdirectory=timesheet-mcp-server-v2
```

### 方式 3: 本地开发模式

```bash
# 进入项目目录
cd timesheet-mcp-server-v2

# 安装依赖
pip install -e ".[dev]"

# 运行服务器
python -m src.server
```

## 配置说明

### 环境变量

创建 `.env` 文件（如果使用本地模式）：

```env
# API 配置
TIMESHEET_API_BASE_URL=https://tms.ktvsky.com/api
TIMESHEET_API_TOKEN=your-jwt-token-here

# MCP 配置
MCP_TRANSPORT=stdio
MCP_LOG_LEVEL=INFO
```

### JWT Token 获取

1. **生成长期有效的 Token**（推荐）：
   ```bash
   cd backend
   go run cmd/generate_jwt/main.go -username=你的用户名 -expiration-days=365
   ```

2. **从现有账号获取**：
   - 登录工时管理系统
   - 从浏览器开发工具查看 Authorization header

### Claude Desktop 配置

编辑 `~/.config/Claude/claude_desktop_config.json`（或 `~/Library/Application Support/Claude/claude_desktop_config.json` on macOS）：

```json
{
  "mcpServers": {
    "timesheet": {
      "command": "uvx",
      "args": ["timesheet-tms-mcp"],
      "env": {
        "TIMESHEET_API_BASE_URL": "https://tms.ktvsky.com/api",
        "TIMESHEET_API_TOKEN": "your-jwt-token-here"
      }
    }
  }
}
```

### Cursor 配置

编辑 `.cursor/mcp.json` 在你的项目目录：

```json
{
  "mcpServers": {
    "timesheet-mcp": {
      "command": "uvx",
      "args": ["timesheet-tms-mcp"],
      "env": {
        "TIMESHEET_API_BASE_URL": "https://tms.ktvsky.com/api",
        "TIMESHEET_API_TOKEN": "your-jwt-token-here"
      }
    }
  }
}
```

## 验证安装

### 检查是否安装成功

```bash
# 检查包是否安装
pip show timesheet-tms-mcp

# 尝试导入
python -c "from src.server import main; print('✓ 安装成功')"

# 或用 uvx 直接运行
uvx timesheet-tms-mcp --help
```

### 测试 MCP 连接

在 Claude 中测试：

```
查询我10月份的工时记录
```

或使用工具列表查看所有可用工具。

## 常见问题

### Q: 如何更新到最新版本？

```bash
pip install --upgrade timesheet-tms-mcp
```

### Q: Token 过期了怎么办？

重新生成 Token：

```bash
cd backend
go run cmd/generate_jwt/main.go -username=你的用户名 -expiration-days=365
```

然后更新配置文件中的 `TIMESHEET_API_TOKEN`。

### Q: MCP 服务无法连接？

1. 检查 API_BASE_URL 是否正确
2. 检查 Token 是否过期
3. 检查网络连接
4. 查看 MCP 服务器日志

### Q: 如何从本地版本升级到 PyPI 版本？

```bash
# 卸载本地版本
pip uninstall timesheet-tms-mcp

# 从 PyPI 安装
pip install timesheet-tms-mcp
```

## 开发和贡献

如果你想贡献代码，请参考 [开发指南](../DEVELOPMENT.md)。

## 获取帮助

- 📖 查看 [README](../README.md) 了解工具列表
- 📝 查看 [使用指南](./USER_GUIDE.md) 了解常见用法
- 🔧 查看 [API 文档](./API.md) 了解详细信息
