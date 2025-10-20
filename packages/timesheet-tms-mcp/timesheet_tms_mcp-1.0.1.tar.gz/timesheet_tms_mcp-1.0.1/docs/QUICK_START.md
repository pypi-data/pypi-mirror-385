# Timesheet MCP Server - 快速入门指南

## 📋 目录

1. [简介](#简介)
2. [安装](#安装)
3. [配置](#配置)
4. [使用](#使用)
5. [可用工具](#可用工具)
6. [故障排除](#故障排除)

---

## 简介

**Timesheet MCP Server** 是一个基于 FastMCP 2.0 的 Model Context Protocol 服务器，用于与工时管理系统集成。它提供了一套完整的 API，让您能够：

- 📊 查询个人工时记录和统计
- 👥 管理项目和项目成员
- 📈 生成工时报表
- 🔍 查询用户和项目信息

---

## 安装

### 方式 1：使用 pip（推荐）

```bash
# 从 PyPI 安装最新版本
pip install timesheet-mcp-server

# 指定版本安装
pip install timesheet-mcp-server==1.0.0
```

### 方式 2：从源代码安装

```bash
# 克隆仓库
git clone https://github.com/yangyuezheng/ai-emp.git
cd ai-emp/timesheet-mcp-server-v2

# 安装依赖
pip install -e .
```

### 方式 3：使用 uvx（无需安装）

```bash
# 直接运行，uvx 会自动处理依赖
uvx timesheet-mcp-server
```

---

## 配置

### 环境变量

MCP 服务器需要以下环境变量：

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `TIMESHEET_API_BASE_URL` | 工时管理系统 API 地址 | `https://tms.ktvsky.com/api` |
| `TIMESHEET_API_TOKEN` | JWT 认证令牌 | `eyJhbGc...` |

### 配置 Claude Desktop

编辑 `~/.claude/claude_desktop_config.json`：

```json
{
  "mcpServers": {
    "timesheet": {
      "command": "uvx",
      "args": ["timesheet-mcp-server"],
      "env": {
        "TIMESHEET_API_BASE_URL": "https://tms.ktvsky.com/api",
        "TIMESHEET_API_TOKEN": "your_jwt_token_here"
      }
    }
  }
}
```

### 配置 Cursor IDE

编辑 `.cursor/mcp.json`：

```json
{
  "mcpServers": {
    "timesheet-mcp": {
      "command": "uvx",
      "args": ["timesheet-mcp-server"],
      "env": {
        "TIMESHEET_API_BASE_URL": "https://tms.ktvsky.com/api",
        "TIMESHEET_API_TOKEN": "your_jwt_token_here"
      }
    }
  }
}
```

### 生成 JWT Token

参考 [TOKEN_MANAGEMENT.md](TOKEN_MANAGEMENT.md) 了解如何生成长期有效的 JWT Token。

---

## 使用

### 在 Claude Desktop 中使用

1. 启动 Claude Desktop
2. 确保 MCP 服务器已配置并启动
3. 在对话中使用以下工具：

```
@timesheet 获取我的工时记录
```

### 在 Cursor IDE 中使用

1. 打开 Cursor IDE
2. 确保 `.cursor/mcp.json` 已正确配置
3. 使用 MCP 工具查询工时信息

---

## 可用工具

### 1. 获取个人工时统计 `get_my_time_stats`

**功能**：获取指定月份的工时填报情况

**参数**：
- `year` (int, 必需): 年份，如 2025
- `month` (int, 必需): 月份，1-12

**返回值**：
```json
{
  "year": 2025,
  "month": 10,
  "total_workdays": 22,
  "filled_days": 20,
  "missing_days": 2,
  "total_hours": 160,
  "average_hours_per_day": 8.0,
  "project_distribution": {
    "项目A": 80,
    "项目B": 80
  },
  "missing_dates": ["2025-10-01", "2025-10-02"]
}
```

**示例**：
```
获取我 2025 年 10 月的工时统计
```

---

### 2. 获取个人工时记录 `get_my_time_entries`

**功能**：查询个人的工时记录

**参数**：
- `page` (int, 默认: 1): 页码
- `limit` (int, 默认: 10): 每页数量
- `project_id` (int, 可选): 特定项目的工时
- `start_date` (str, 可选): 开始日期，格式 YYYY-MM-DD
- `end_date` (str, 可选): 结束日期，格式 YYYY-MM-DD
- `status` (str, 可选): 审批状态 (submitted/approved/rejected)

**返回值**：
```json
{
  "total": 100,
  "page": 1,
  "limit": 10,
  "data": [
    {
      "date": "2025-10-01",
      "hours": 8,
      "description": "开发功能 X",
      "project_name": "项目A",
      "status": "approved"
    }
  ]
}
```

**示例**：
```
查询我 10 月份的工时记录
查询项目 A 的工时记录
```

---

### 3. 获取我参与的项目 `get_my_projects`

**功能**：列出当前用户参与的所有项目

**参数**：
- `page` (int, 默认: 1): 页码
- `limit` (int, 默认: 20): 每页数量

**返回值**：
```json
{
  "total": 5,
  "page": 1,
  "limit": 20,
  "data": [
    {
      "id": 123,
      "name": "项目A",
      "type": "rd",
      "level": "level1",
      "business_line": "研发部",
      "created_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

**示例**：
```
列出我参与的所有项目
```

---

### 4. 获取项目详情 `get_project_detail`

**功能**：获取项目的详细信息

**参数**：
- `project_id` (int, 必需): 项目 ID

**返回值**：
```json
{
  "id": 123,
  "name": "项目A",
  "type": "rd",
  "level": "level1",
  "business_line": "研发部",
  "members": [
    {
      "id": 1,
      "name": "张三",
      "role": "member"
    }
  ],
  "managers": [
    {
      "id": 2,
      "name": "李四",
      "role": "manager"
    }
  ]
}
```

**示例**：
```
查询项目 123 的详情
```

---

### 5. 获取项目列表 `get_projects`

**功能**：获取系统中的所有项目

**参数**：
- `page` (int, 默认: 1): 页码
- `limit` (int, 默认: 10): 每页数量
- `status` (str, 可选): 项目状态 (active/completed/archived)
- `business_line_id` (int, 可选): 特定业务线

**返回值**：
```json
{
  "total": 50,
  "page": 1,
  "limit": 10,
  "data": [
    {
      "id": 123,
      "name": "项目A",
      "type": "rd",
      "business_line": "研发部",
      "level": "level1",
      "created_at": "2025-01-01T00:00:00Z"
    }
  ]
}
```

---

### 6. 生成工时报表 `get_time_entry_report`

**功能**：生成工时报表

**参数**：
- `start_date` (str, 必需): 开始日期，格式 YYYY-MM-DD
- `end_date` (str, 必需): 结束日期，格式 YYYY-MM-DD
- `project_id` (int, 可选): 特定项目
- `user_id` (int, 可选): 特定用户

**示例**：
```
生成 2025 年 10 月的工时报表
```

---

## 实战示例

### 场景 1：查看本月工时完成情况

```
请帮我查看 2025 年 10 月的工时填报情况，包括应该填写多少天，已经填写了多少天
```

**结果**：
- 总工作日：22 天
- 已填写：20 天
- 缺失：2 天
- 缺失日期：10 月 1 日、10 月 2 日

---

### 场景 2：查询特定项目的工时

```
查询我在项目 A 的所有工时记录
```

**结果**：
- 项目名称：项目 A
- 工时总数：80 小时
- 最近工时记录：...

---

### 场景 3：了解项目信息

```
我想了解项目 123 的详情，包括项目经理和成员
```

**结果**：
- 项目名称、类型、业务线
- 项目经理列表
- 项目成员列表

---

## 故障排除

### 问题 1：Token 过期

**错误信息**：`{"error": "无效或过期的令牌"}`

**解决方案**：
1. 生成新的 JWT Token
2. 更新环境变量 `TIMESHEET_API_TOKEN`
3. 重启 MCP 服务器

参考：[TOKEN_MANAGEMENT.md](TOKEN_MANAGEMENT.md)

---

### 问题 2：无法连接到 API

**错误信息**：`Connection refused` 或 `HTTP 502`

**解决方案**：
1. 检查 `TIMESHEET_API_BASE_URL` 是否正确
2. 确认网络连接
3. 检查防火墙设置

---

### 问题 3：Permission Denied

**错误信息**：`Permission denied`

**解决方案**：
1. 确认 Token 对应的用户有权限
2. 检查 JWT Token 的 role 字段

---

## 更多资源

- 📖 [详细用法示例](USAGE_EXAMPLES.md)
- 🔐 [Token 管理指南](TOKEN_MANAGEMENT.md)
- 🧪 [测试指南](testing-guide.md)
- 🚀 [部署指南](deployment-guide.md)

---

## 支持

遇到问题？请访问：
- 🐛 [GitHub Issues](https://github.com/yangyuezheng/ai-emp/issues)
- 📧 Email: yangyuezheng@example.com

---

**版本**: 1.0.0  
**最后更新**: 2025年10月20日

