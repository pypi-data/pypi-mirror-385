# 📚 Timesheet MCP Server 文档

欢迎来到 Timesheet MCP Server 的文档中心。这里提供了完整的指南、示例和参考资料。

## 📖 文档导航

### 🚀 快速开始

- **[快速入门指南](QUICK_START.md)** - 5 分钟快速上手
  - 安装方式
  - 基本配置
  - 首次使用

### 👤 用户指南

- **[用户指南](USER_GUIDE.md)** - 完整的使用教程
  - 常见工作流
  - 最佳实践
  - 高级用法
  - 常见问题解答

### 🔧 开发者指南

- **[部署指南](deployment-guide.md)** - 生产环境部署
  - Docker 部署
  - 系统要求
  - 性能优化

- **[测试指南](testing-guide.md)** - 开发和测试
  - 单元测试
  - 集成测试
  - 调试技巧

- **[内部分发指南](internal-distribution-guide.md)** - 团队内部使用
  - 团队配置
  - 共享方式

### 🔐 安全和认证

- **[Token 管理指南](TOKEN_MANAGEMENT.md)** - JWT Token 操作
  - 生成 Token
  - Token 刷新
  - 最佳实践

### 💡 使用示例

- **[详细用法示例](USAGE_EXAMPLES.md)** - 代码示例和场景
  - 实际使用场景
  - API 调用示例
  - 错误处理

---

## 🎯 按角色快速导航

### 👤 我是最终用户

1. 先读：[快速入门指南](QUICK_START.md) - 了解基础设置
2. 再读：[用户指南](USER_GUIDE.md) - 学习如何使用
3. 需要帮助：查看 [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md)

### 👨‍💻 我是开发者

1. 先读：[快速入门指南](QUICK_START.md) - 环境设置
2. 再读：[测试指南](testing-guide.md) - 运行测试
3. 部署：[部署指南](deployment-guide.md)
4. 安全：[Token 管理指南](TOKEN_MANAGEMENT.md)

### 🏢 我是系统管理员

1. 先读：[部署指南](deployment-guide.md) - 安装和配置
2. 再读：[内部分发指南](internal-distribution-guide.md) - 团队配置
3. 安全：[Token 管理指南](TOKEN_MANAGEMENT.md)

---

## 📊 工具速查表

### 个人工时管理

| 工具 | 用途 | 参考文档 |
|------|------|--------|
| `get_my_time_stats` | 获取工时统计 | [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) |
| `get_my_time_entries` | 查询工时记录 | [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) |
| `get_my_projects` | 列出参与项目 | [USER_GUIDE.md](USER_GUIDE.md) |

### 项目管理

| 工具 | 用途 | 参考文档 |
|------|------|--------|
| `get_project_detail` | 项目详情 | [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) |
| `get_projects` | 项目列表 | [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) |

### 报表

| 工具 | 用途 | 参考文档 |
|------|------|--------|
| `get_time_entry_report` | 工时报表 | [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) |

---

## 🔗 相关资源

### 官方资源

- 🌐 [项目主页](https://github.com/yangyuezheng/ai-emp)
- 📦 [PyPI 包](https://pypi.org/project/timesheet-mcp-server/)
- 🚀 [FastMCP 官方文档](https://github.com/jlopp/fastmcp)

### 支持

- 🐛 [报告问题](https://github.com/yangyuezheng/ai-emp/issues)
- 💬 [讨论区](https://github.com/yangyuezheng/ai-emp/discussions)
- 📧 [联系作者](mailto:yangyuezheng@example.com)

---

## 📝 文档版本

| 版本 | 日期 | 更新内容 |
|------|------|--------|
| 1.0.0 | 2025-10-20 | 初始版本发布 |

---

## ✨ 特色功能

### 🔐 安全的认证
- JWT Token 认证
- 支持长期 Token
- 自动刷新机制

### ⚡ 高性能
- 异步 API 调用
- 自动重试机制
- 连接池管理

### 🔄 完整的 API 覆盖
- 工时查询和统计
- 项目管理
- 报表生成
- 用户信息查询

### 📱 多平台支持
- Claude Desktop
- Cursor IDE
- 任何支持 MCP 的客户端

---

## 🚀 快速命令参考

### 安装

```bash
# 从 PyPI 安装
pip install timesheet-mcp-server

# 或使用 uvx（无需安装）
uvx timesheet-mcp-server
```

### 配置

编辑 `.cursor/mcp.json` 或 `~/.claude/claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "timesheet": {
      "command": "uvx",
      "args": ["timesheet-mcp-server"],
      "env": {
        "TIMESHEET_API_BASE_URL": "https://tms.ktvsky.com/api",
        "TIMESHEET_API_TOKEN": "your_jwt_token"
      }
    }
  }
}
```

### 使用

在 Claude 或 Cursor 中：

```
查询我 10 月份的工时统计
```

---

## 常见问题速答

**Q: 如何获取 JWT Token?**  
A: 查看 [Token 管理指南](TOKEN_MANAGEMENT.md)

**Q: 支持哪些客户端?**  
A: Claude Desktop、Cursor IDE，以及任何支持 MCP 协议的客户端

**Q: API 是否有速率限制?**  
A: 参考后端工时管理系统的文档

**Q: 如何离线使用?**  
A: 需要网络连接到工时管理系统 API

---

## 下一步

- 🎓 阅读 [快速入门指南](QUICK_START.md)
- 🔧 运行 [测试指南](testing-guide.md) 中的示例
- 🚀 参考 [部署指南](deployment-guide.md) 进行生产部署
- 💡 查看 [使用示例](USAGE_EXAMPLES.md) 获得灵感

---

**最后更新**: 2025年10月20日  
**版本**: 1.0.0  
**维护者**: Vincent Yang

