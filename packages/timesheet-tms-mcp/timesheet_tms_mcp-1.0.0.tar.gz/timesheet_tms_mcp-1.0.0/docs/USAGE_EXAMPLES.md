# MCP 工具使用示例

本文档提供常见使用场景的示例。

## 📊 工时统计与分析

### 1. 查看本月工时完成情况

```
请帮我查看 2025 年 10 月的工时填报情况
```

MCP 会调用：`get_my_time_stats(year=2025, month=10)`

返回示例：
```json
{
  "success": true,
  "data": {
    "year": 2025,
    "month": 10,
    "total_workdays": 23,
    "filled_days": 12,
    "missing_days": 11,
    "total_hours": 84,
    "average_hours_per_day": 7.0,
    "completion_rate": 52.2,
    "project_distribution": [
      {
        "project": "IPTV-软件开发 (IPTV)",
        "hours": 50,
        "percentage": 59.5
      },
      {
        "project": "基础版软件开发 (VOD)",
        "hours": 24,
        "percentage": 28.6
      },
      {
        "project": "音乐软件开发 (音乐服务)",
        "hours": 10,
        "percentage": 11.9
      }
    ],
    "missing_dates": [
      "2025-10-01", "2025-10-02", "2025-10-03",
      "2025-10-06", "2025-10-07", "2025-10-08",
      "2025-10-09", "2025-10-10", "2025-10-11",
      "2025-10-18", "2025-10-20"
    ]
  },
  "message": "成功获取 2025 年 10 月工时统计"
}
```

AI 会友好地展示：
```
您 10 月份的工时填报情况：

📅 填报进度：
- 应填写：23 个工作日
- 已填写：12 个工作日  
- 缺少：11 个工作日
- 完成率：52.2%

⏱️ 工时统计：
- 总工时：84 小时
- 平均每天：7.0 小时

📊 项目分布：
1. IPTV-软件开发 (IPTV)：50 小时 (59.5%)
2. 基础版软件开发 (VOD)：24 小时 (28.6%)
3. 音乐软件开发 (音乐服务)：10 小时 (11.9%)

⚠️ 缺少工时的日期：
2025-10-01, 2025-10-02, 2025-10-03, 2025-10-06, 2025-10-07, 
2025-10-08, 2025-10-09, 2025-10-10, 2025-10-11, 2025-10-18, 2025-10-20

建议尽快补填这些日期的工时记录！
```

### 2. 查询具体工时记录

```
帮我查看 10 月 14-17 日的工时记录
```

MCP 会调用：`get_my_time_entries(start_date="2025-10-14", end_date="2025-10-17", limit=20)`

## 🏗️ 项目管理

### 3. 查看我参与的项目

```
我参与了哪些项目？
```

MCP 会调用：`get_my_projects(limit=50)`

返回示例：
```json
{
  "success": true,
  "data": {
    "total": 5,
    "data": [
      {
        "id": 127,
        "name": "IPTV-软件开发",
        "type": "engineering",
        "level": "level2",
        "parent_id": 125,
        "business_line": "IPTV",
        "business_line_id": 11
      },
      {
        "id": 23,
        "name": "基础版软件开发",
        "type": "rd",
        "level": "level2",
        "parent_id": 7,
        "business_line": "VOD"
      }
    ]
  }
}
```

AI 会展示：
```
您当前参与的项目：

1. IPTV-软件开发 (ID: 127)
   - 类型：engineering
   - 层级：二级项目
   - 业务线：IPTV
   
2. 基础版软件开发 (ID: 23)
   - 类型：rd (研发)
   - 层级：二级项目
   - 业务线：VOD
```

### 4. 查看项目详情

```
帮我查看 IPTV-软件开发项目（ID: 127）的详细信息
```

MCP 会调用：`get_project_detail(project_id=127)`

返回示例：
```json
{
  "success": true,
  "data": {
    "id": 127,
    "name": "IPTV-软件开发",
    "type": "engineering",
    "level": "level2",
    "parent_id": 125,
    "parent_name": "IPTV项目",
    "business_line": "IPTV",
    "business_line_id": 11,
    "member_count": 8,
    "members": [
      {
        "id": 29,
        "username": "yangyuezheng",
        "real_name": "杨月政",
        "role_in_project": "member"
      },
      {
        "id": 74,
        "username": "niuxinxin",
        "real_name": "牛欣欣",
        "role_in_project": "manager"
      }
    ],
    "managers": [
      {
        "id": 74,
        "username": "niuxinxin",
        "real_name": "牛欣欣",
        "role_in_project": "manager"
      }
    ]
  }
}
```

AI 会展示：
```
IPTV-软件开发项目详情：

📋 基本信息：
- 项目ID：127
- 项目名称：IPTV-软件开发
- 项目类型：engineering (工程)
- 项目层级：二级项目
- 父项目：IPTV项目 (ID: 125)
- 业务线：IPTV (ID: 11)

👥 项目团队：
- 总人数：8 人

👨‍💼 项目经理：
- 牛欣欣 (niuxinxin)

👥 项目成员：
1. 杨月政 (yangyuezheng) - 成员
2. 牛欣欣 (niuxinxin) - 经理
...
```

### 5. 查询所有项目列表

```
给我看看公司有哪些项目，特别是 IPTV 业务线的
```

MCP 会调用：`get_projects(business_line_id=11, limit=50)`

## 🔍 综合查询示例

### 场景1：月度工时总结

```
帮我做一个 10 月份的工时总结报告
```

AI 会依次调用：
1. `get_my_time_stats(year=2025, month=10)` - 获取统计数据
2. `get_my_time_entries(start_date="2025-10-01", end_date="2025-10-31", limit=100)` - 获取详细记录
3. `get_my_projects()` - 获取参与的项目信息

然后生成完整报告。

### 场景2：项目工时分析

```
分析一下我在 IPTV-软件开发项目上 10 月份的工时投入
```

AI 会：
1. `get_project_detail(project_id=127)` - 获取项目详情
2. `get_my_time_entries(start_date="2025-10-01", end_date="2025-10-31", project_id=127)` - 获取该项目的工时
3. 分析并展示结果

### 场景3：快速填报提醒

```
我本月还有哪些天没填工时？帮我列出来
```

AI 会调用：
1. `get_my_time_stats(year=2025, month=10)` - 获取统计，包含 `missing_dates`
2. 展示缺失日期列表

### 场景4：跨项目工时对比

```
对比一下我在 IPTV、VOD 两个业务线的工时投入
```

AI 会：
1. `get_my_time_entries(start_date="2025-10-01", end_date="2025-10-31", limit=200)`
2. 按业务线分组统计
3. 生成对比分析

## 💡 高级用法

### 自动化工时提醒

在 Claude Desktop 中设置定时提醒：

```
每周五下午提醒我：
1. 查看本周工时填报情况
2. 列出未填写的日期
3. 提醒我及时填写
```

### 工时异常检测

```
检查一下我最近一个月的工时记录，看看有没有异常：
- 是否有天数超过 8 小时
- 是否有周末填报
- 是否有连续多天未填报
```

### 项目切换建议

```
基于我最近 3 个月的工时分布，帮我分析：
1. 我主要在哪些项目上工作
2. 各项目的时间占比
3. 是否需要调整项目优先级
```

## 🎯 实用技巧

### 1. 使用自然语言

不需要记住工具名称，直接说：
- ❌ "调用 get_my_time_stats(2025, 10)"
- ✅ "我 10 月份工时填了多少？"

### 2. 组合查询

AI 会自动组合多个工具：
```
帮我整理一份给领导的周报，包括：
1. 本周工作时长
2. 参与的项目
3. 各项目时间分配
```

### 3. 数据导出

```
把我 10 月份的工时数据整理成表格，包含：
- 日期
- 项目
- 工时
- 工作内容
```

AI 会调用相关工具并格式化输出。

## ⚠️ 注意事项

1. **日期格式**：使用 YYYY-MM-DD 格式，如 "2025-10-20"
2. **项目ID**：查询项目详情时需要准确的项目 ID
3. **分页查询**：大量数据时注意使用 limit 参数
4. **工作日计算**：工时统计只计算周一到周五，不包含周末和节假日

## 🔧 故障排查

### 查询返回空数据

**原因**：
1. 确实没有相关数据
2. 日期范围不对
3. 项目ID错误

**解决**：
```
先查看我有哪些项目: get_my_projects()
然后再查询具体项目工时
```

### Token 过期

**症状**：所有查询都返回 401 错误

**解决**：
1. 检查 `.mcp.json` 中的 Token 是否正确
2. 重新生成长期 Token
3. 更新配置并重启 MCP 服务器

## 📞 获取帮助

如果遇到问题，可以：
1. 查看 [README.md](../README.md)
2. 查看 [TOKEN_MANAGEMENT.md](TOKEN_MANAGEMENT.md)
3. 使用 `health_check()` 工具检查连接状态


