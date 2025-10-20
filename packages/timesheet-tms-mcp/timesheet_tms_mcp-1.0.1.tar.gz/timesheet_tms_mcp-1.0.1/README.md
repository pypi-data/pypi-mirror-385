# Timesheet MCP Server V2

基于 FastMCP 2.0 框架构建的工时管理系统 MCP Server。

## 特性

- 🚀 使用 FastMCP 2.0 框架，性能优异
- 📡 支持 stdio 传输方式（默认）
- 🔐 JWT Token 认证
- 📊 完整的工时管理功能
- ✅ 完善的单元测试
- 📖 详细的文档

## 快速开始

### 方式一：从 PyPI 直接安装（推荐）⭐

```bash
pip install timesheet-tms-mcp
```

### 方式二：从 GitHub 直接安装

```bash
# 从 main 分支安装最新开发版本
pip install git+https://github.com/yangyuezheng/ai-emp@main#subdirectory=timesheet-mcp-server-v2

# 或从 GitHub Releases 安装稳定版本
pip install https://github.com/yangyuezheng/ai-emp/releases/download/v1.0.0/timesheet_tms_mcp-1.0.0-py3-none-any.whl
```

### 方式三：使用 uvx 运行本地版本

```bash
# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置 API URL 和 Token

# 直接运行（uvx 会自动安装依赖）
uvx --from . fastmcp run src/server.py
```

### 方式四：使用 uv

```bash
# 安装依赖
uv pip install -r requirements.txt

# 运行服务器
uv run src/server.py
```

### 方式五：传统 pip 方式

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 运行服务器
python src/server.py
```

### 配置环境变量

编辑 `.env` 文件：

```env
# API 配置
TIMESHEET_API_BASE_URL=http://127.0.0.1:8080/api
TIMESHEET_API_TOKEN=your-jwt-token-here

# MCP 配置
MCP_TRANSPORT=stdio
MCP_LOG_LEVEL=INFO

# 功能开关
ENABLE_CACHE=true
CACHE_TTL=300
```

### 在 Claude Desktop 中使用

#### 使用 uvx（推荐）⭐

```json
{
  "mcpServers": {
    "timesheet": {
      "command": "uvx",
      "args": ["timesheet-tms-mcp"],
      "env": {
        "TIMESHEET_API_BASE_URL": "https://tms.ktvsky.com/api",
        "TIMESHEET_API_TOKEN": "your-jwt-token"
      }
    }
  }
}
```

#### 使用 Python（传统方式）

```json
{
  "mcpServers": {
    "timesheet": {
      "command": "python",
      "args": ["/path/to/timesheet-mcp-server-v2/src/server.py"],
      "env": {
        "TIMESHEET_API_BASE_URL": "https://tms.ktvsky.com/api",
        "TIMESHEET_API_TOKEN": "your-jwt-token"
      }
    }
  }
}
```

## 可用 Tools

### 工时记录管理
- `create_time_entry` - 创建工时记录
- `update_time_entry` - 更新工时记录
- `delete_time_entry` - 删除工时记录
- `submit_time_entry` - 提交工时记录审批
- `batch_create_time_entries` - 批量创建工时记录
- `get_my_time_entries` - 获取我的工时记录
- `get_my_time_stats` - ⭐ 获取个人工时统计（应填/已填/缺少天数，项目分布）
- `get_recent_time_entries` - 获取最近工时记录

### 用户查询
- `get_user_by_name` - 根据用户名查询用户
- `get_user_time_entries` - 查询指定用户工时记录

### 审批管理
- `get_pending_approvals` - 获取待我审批的工时
- `approve_time_entry` - 审批通过工时记录
- `reject_time_entry` - 拒绝工时记录
- `batch_approve_time_entries` - 批量审批工时
- `get_my_approval_history` - 获取我的审批历史

### 项目管理
- `get_projects` - 获取所有项目列表
- `get_my_projects` - ⭐ 获取我参与的项目列表
- `get_project_detail` - ⭐ 获取项目详情（包含父项目、成员、项目经理）
- `get_my_projects_tree` - 获取我的项目树
- `get_project_members` - 获取项目成员
- `get_project_time_plan` - 获取项目工时计划
- `