# 📦 分发方案总结

## 🎯 推荐方案（按使用场景）

### 方案 1️⃣: PyPI 发布（最推荐）⭐⭐⭐⭐⭐

**适用**: 希望用户最简单安装

**用户操作**:
```bash
# 仅需一行命令！
uvx timesheet-mcp-server
```

**Claude Desktop 配置**:
```json
{
  "mcpServers": {
    "timesheet": {
      "command": "uvx",
      "args": ["timesheet-mcp-server"],
      "env": {
        "TIMESHEET_API_BASE_URL": "http://127.0.0.1:8080/api",
        "TIMESHEET_API_TOKEN": "your-jwt-token"
      }
    }
  }
}
```

**优点**:
- ✅ 用户体验最好
- ✅ 一行命令安装
- ✅ 自动依赖管理
- ✅ 版本管理简单
- ✅ 无需访问源代码

**发布步骤**: 见 `PUBLISH.md`

---

### 方案 2️⃣: Git 仓库直接安装 ⭐⭐⭐⭐

**适用**: 内部团队有 Git 访问权限

**用户操作**:
```bash
# 从 Git 仓库安装
uvx --from git+https://g.ktvsky.com/yangyuezheng/ai-emp.git@feature/mcp-server-v2-fastmcp#subdirectory=timesheet-mcp-server-v2 timesheet-mcp-server
```

**Claude Desktop 配置**:
```json
{
  "mcpServers": {
    "timesheet": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://g.ktvsky.com/yangyuezheng/ai-emp.git@feature/mcp-server-v2-fastmcp#subdirectory=timesheet-mcp-server-v2",
        "fastmcp",
        "run",
        "src/server.py"
      ],
      "env": {
        "TIMESHEET_API_BASE_URL": "http://127.0.0.1:8080/api",
        "TIMESHEET_API_TOKEN": "your-jwt-token"
      }
    }
  }
}
```

**优点**:
- ✅ 利用现有 Git 权限
- ✅ 无需额外基础设施
- ✅ 支持 uvx 直接安装
- ✅ 可以指定分支/tag

**缺点**:
- ❌ 需要 Git 访问权限
- ❌ 配置稍微复杂

---

### 方案 3️⃣: 一键安装脚本 ⭐⭐⭐

**适用**: 快速演示或内部分发

**用户操作**:
```bash
# 下载安装脚本
curl -O https://your-server.com/install.sh

# 或直接运行
curl -fsSL https://your-server.com/install.sh | bash

# 或从本地运行
cd /path/to/timesheet-mcp-server-v2
./install.sh
```

**安装脚本功能**:
- 自动检查 Python 环境
- 自动安装 uvx（如需要）
- 交互式配置引导
- 自动生成 Claude Desktop 配置
- 备份现有配置

**优点**:
- ✅ 用户体验友好
- ✅ 自动化配置
- ✅ 适合非技术用户
- ✅ 支持多种安装来源

---

### 方案 4️⃣: 私有 PyPI 服务器（企业级） ⭐⭐⭐⭐⭐

**适用**: 大型企业内部

**搭建 DevPI 服务器**:
```bash
# 安装
pip install devpi-server devpi-web

# 初始化
devpi-init

# 启动
devpi-server --start --host 0.0.0.0 --port 3141
```

**用户操作**:
```bash
# 从私有 PyPI 安装
uvx --index-url http://your-devpi-server:3141/root/dev/+simple/ timesheet-mcp-server
```

**优点**:
- ✅ 完全内部控制
- ✅ 专业的包管理
- ✅ 支持多版本
- ✅ 安全可控

**缺点**:
- ❌ 需要搭建基础设施
- ❌ 维护成本

---

## 📊 方案对比

| 方案 | 安装难度 | 用户体验 | 维护成本 | 安全性 | 适用规模 |
|------|----------|----------|----------|--------|----------|
| **PyPI 公开** | ⭐ | ⭐⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐ | 所有 |
| **Git 仓库** | ⭐⭐ | ⭐⭐⭐⭐ | ⭐ | ⭐⭐⭐⭐ | 小团队 |
| **安装脚本** | ⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ | 演示/快速部署 |
| **私有 PyPI** | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 大企业 |
| **Docker** | ⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ | 容器化环境 |

## 🚀 快速决策指南

### 你的团队 < 10 人？
→ **使用 Git 仓库方案**

配置复制给用户：
```json
{
  "mcpServers": {
    "timesheet": {
      "command": "uvx",
      "args": ["--from", "git+https://...", "fastmcp", "run", "src/server.py"],
      "env": {
        "TIMESHEET_API_BASE_URL": "http://127.0.0.1:8080/api",
        "TIMESHEET_API_TOKEN": "替换为你的token"
      }
    }
  }
}
```

### 你的团队 10-50 人？
→ **发布到 PyPI**

用户仅需：
```bash
uvx timesheet-mcp-server
```

### 你的团队 > 50 人？
→ **搭建私有 PyPI 服务器**

提供内网访问地址即可。

### 需要快速演示？
→ **使用安装脚本**

```bash
./install.sh
```

---

## 📝 用户使用文档模板

### 给用户的邮件/通知模板

```
主题：工时管理 MCP Server 使用指南

Hi Team,

我们的工时管理系统现已支持 Claude Desktop 集成！

【快速开始】

1. 确保你已安装 Claude Desktop
   下载地址：https://claude.ai/download

2. 获取你的 JWT Token
   - 登录工时系统: http://127.0.0.1:8080
   - 浏览器 F12 -> Network -> 查看请求头 Authorization
   - 复制 Bearer 后的 token

3. 安装 MCP Server（选择其一）

   方式 A（推荐）- 一键安装：
   curl -fsSL https://your-server.com/install.sh | bash

   方式 B - 手动配置：
   编辑 Claude Desktop 配置文件
   macOS: ~/Library/Application Support/Claude/claude_desktop_config.json

   添加以下内容（替换 your-jwt-token）：
   {
     "mcpServers": {
       "timesheet": {
         "command": "uvx",
         "args": ["timesheet-mcp-server"],
         "env": {
           "TIMESHEET_API_BASE_URL": "http://127.0.0.1:8080/api",
           "TIMESHEET_API_TOKEN": "your-jwt-token"
         }
       }
     }
   }

4. 重启 Claude Desktop

5. 开始使用！
   在 Claude 中尝试：
   - "请帮我查询我的工时记录"
   - "请列出所有项目"
   - "本周工时统计"

【功能列表】
✅ 工时记录查询（2个工具）
✅ 用户查询（3个工具）
✅ 项目查询（7个工具）
✅ 报表统计（5个工具）

【获取帮助】
- 文档：https://your-docs-site.com
- 问题反馈：your-support-channel

祝使用愉快！
```

---

## 🔄 版本更新通知

当发布新版本时，通知用户：

```
📢 工时管理 MCP Server 更新 v2.1.0

【新功能】
✨ 新增 XXX 功能
✨ 优化 XXX 性能

【Bug 修复】
🐛 修复 XXX 问题

【更新方法】
# PyPI 用户：自动更新，无需操作
# Git 仓库用户：
git pull origin main

# 然后重启 Claude Desktop

【变更详情】
https://github.com/.../CHANGELOG.md
```

---

## 📊 使用统计（可选）

如果需要了解使用情况，可以添加简单的统计：

```python
# 在 tools 中添加（可选）
async def track_usage(tool_name: str):
    try:
        async with httpx.AsyncClient() as client:
            await client.post(
                "https://internal-analytics.com/api/track",
                json={"tool": tool_name, "timestamp": datetime.now().isoformat()}
            )
    except:
        pass  # 不影响主功能
```

---

## ✅ 检查清单

发布前确认：

- [ ] 选择合适的分发方案
- [ ] 准备用户文档
- [ ] 测试安装流程
- [ ] 准备 Token 获取指南
- [ ] 设置支持渠道
- [ ] 准备更新通知模板
- [ ] （可选）设置使用统计

---

## 🆘 常见问题

### Q: 用户没有 Python 环境怎么办？
A: 使用 uvx 方式，它会自动管理 Python 环境。

### Q: Token 过期怎么办？
A: 用户重新获取 Token，更新配置文件中的 `TIMESHEET_API_TOKEN`。

### Q: 如何回滚到旧版本？
A:
```bash
# PyPI
uvx timesheet-mcp-server@2.0.0

# Git
指定 tag: git+https://...@v2.0.0#subdirectory=...
```

### Q: 如何知道哪些用户在使用？
A: 可以在后端 API 添加使用日志，或使用可选的统计功能。

---

**相关文档**:
- 发布指南: `PUBLISH.md`
- 部署方案详解: `docs/deployment-guide.md`
- 内部分发指南: `docs/internal-distribution-guide.md`
- 测试指南: `docs/testing-guide.md`
