"""工时管理系统 MCP 服务器

这是一个基于 FastMCP 2.0 框架构建的 MCP 服务器，为 Claude/Cursor 等 AI 助手
提供工时管理系统的 API 访问能力。

主要功能:
- 查询工时记录
- 查询项目信息
- 健康检查和状态监控

技术栈:
- FastMCP 2.0 (MCP 协议实现)
- httpx (异步 HTTP 客户端)
- pydantic (数据验证)
"""
import asyncio
import logging
from typing import Any

from fastmcp import FastMCP

from config.settings import settings

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.MCP_LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# 创建 FastMCP 服务器实例
mcp = FastMCP("timesheet-mcp-server")


@mcp.tool()
async def health_check() -> dict[str, Any]:
    """健康检查 - 检查 MCP 服务器和 API 连接状态
    
    这个工具用于诊断和监控 MCP 服务器的运行状态，包括:
    - MCP 服务器是否正常运行
    - 与工时管理系统 API 的连接是否正常
    - API 认证是否有效
    
    返回信息:
        success: 是否成功
        status: 状态 (healthy/unhealthy)
        api_connected: API 是否连接成功
        api_url: 当前使用的 API 地址
        message: 详细状态信息
    
    使用场景:
        - 初次配置后验证连接
        - 排查 Token 过期问题
        - 监控服务器运行状态
    """
    try:
        from src.client import api_client
        
        # 测试 API 连接
        result = await api_client.get("/projects", params={"page": 1, "limit": 1})
        
        return {
            "success": True,
            "status": "healthy",
            "api_connected": True,
            "message": "MCP 服务器运行正常，API 连接正常",
            "api_response": result.get("code", "unknown"),
            "api_url": api_client.base_url
        }
    except Exception as e:
        return {
            "success": False,
            "status": "unhealthy",
            "api_connected": False,
            "message": f"MCP 服务器异常: {str(e)}",
        }


@mcp.tool()
async def get_my_time_entries(
    page: int = 1,
    limit: int = 10,
    project_id: int = None,
    start_date: str = None,
    end_date: str = None,
    status: str = None,
) -> dict[str, Any]:
    """获取我的工时记录 - 查询当前用户的工时记录列表
    
    查询当前登录用户的工时记录，支持按项目、时间范围、审批状态等多种条件过滤。
    返回的数据包括工作日期、工时数、工作内容、项目信息、审批状态等详细信息。
    
    参数说明:
        page: 页码，从 1 开始 (默认: 1)
        limit: 每页显示的记录数 (默认: 10，建议范围: 1-100)
        project_id: 项目ID，只显示该项目的工时记录 (可选)
        start_date: 开始日期，格式: YYYY-MM-DD，如 "2025-01-01" (可选)
        end_date: 结束日期，格式: YYYY-MM-DD，如 "2025-01-31" (可选)
        status: 审批状态 (可选):
            - "submitted": 已提交，等待审批
            - "approved": 已通过审批
            - "rejected": 已被驳回
    
    返回数据:
        success: 是否成功
        data: 工时记录列表，包含:
            - total: 总记录数
            - page: 当前页码
            - limit: 每页记录数
            - data: 工时记录数组，每条包括:
                - date: 工作日期
                - hours: 工时数
                - description: 工作内容
                - project_name: 项目名称
                - status: 审批状态
        message: 操作结果描述
    
    使用示例:
        - 查看最近工时: get_my_time_entries(limit=20)
        - 查询某个项目: get_my_time_entries(project_id=123)
        - 按时间范围: get_my_time_entries(start_date="2025-01-01", end_date="2025-01-31")
        - 查询待审批: get_my_time_entries(status="submitted")
        - 组合查询: get_my_time_entries(project_id=123, start_date="2025-01-01", status="approved")
    """
    try:
        from src.client import api_client
        
        # 构建查询参数
        params = {"page": page, "limit": limit}
        
        if project_id is not None:
            params["project_id"] = project_id
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        if status:
            params["status"] = status
        
        # 调用 API
        result = await api_client.get("/time-entries/my", params=params)
        
        # 直接返回结果，不做额外处理
        return {
            "success": True,
            "data": result,
            "message": "成功获取工时记录"
        }
        
    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        logger.error(f"获取工时记录失败: {error_detail}")
        return {
            "success": False,
            "data": {},
            "message": f"获取工时记录失败: {str(e)}"
        }


@mcp.tool()
async def get_projects(
    page: int = 1,
    limit: int = 10,
    status: str = None,
    business_line_id: int = None,
) -> dict[str, Any]:
    """获取项目列表 - 查询系统中的项目信息
    
    查询工时管理系统中的项目列表，支持按状态、业务线等条件过滤。
    返回项目的基本信息，包括项目名称、类型、业务线、创建时间等。
    
    参数说明:
        page: 页码，从 1 开始 (默认: 1)
        limit: 每页显示的记录数 (默认: 10，建议范围: 1-100)
        status: 项目状态过滤 (可选):
            - "active": 进行中的项目
            - "completed": 已完成的项目
            - "archived": 已归档的项目
        business_line_id: 业务线ID，只显示该业务线的项目 (可选)
    
    返回数据:
        success: 是否成功
        data: 项目列表，包含:
            - total: 总项目数
            - page: 当前页码
            - limit: 每页记录数
            - data: 项目数组，每个项目包括:
                - id: 项目ID
                - name: 项目名称
                - type: 项目类型
                - business_line: 业务线名称
                - level: 项目级别
                - created_at: 创建时间
        message: 操作结果描述
    
    使用示例:
        - 查看所有项目: get_projects(limit=50)
        - 按业务线查询: get_projects(business_line_id=8)
        - 查询进行中项目: get_projects(status="active")
        - 组合查询: get_projects(business_line_id=8, status="active", limit=20)
    """
    try:
        from src.client import api_client
        
        # 构建查询参数
        params = {"page": page, "limit": limit}
        
        if status:
            params["status"] = status
        if business_line_id is not None:
            params["business_line_id"] = business_line_id
        
        # 调用 API
        result = await api_client.get("/projects", params=params)
        
        # 处理响应数据，计算总数
        total = 0
        if isinstance(result, dict) and 'data' in result:
            data = result['data']
            if isinstance(data, dict) and 'total' in data:
                total = data['total']
            elif isinstance(data, list):
                total = len(data)
        elif isinstance(result, list):
            total = len(result)
        
        return {
            "success": True,
            "data": result,
            "message": f"成功获取项目列表，共 {total} 个项目"
        }
        
    except Exception as e:
        return {
            "success": False,
            "data": {},
            "message": f"获取项目列表失败: {str(e)}"
        }


@mcp.tool()
async def get_my_time_stats(
    year: int,
    month: int,
) -> dict[str, Any]:
    """获取个人工时统计 - 分析当前用户某月的工时完成情况
    
    分析指定月份的工时填报情况，包括:
    - 应填写工时天数（工作日数量）
    - 已填写工时天数
    - 缺少工时天数
    - 总工时数
    - 平均每天工时
    - 各项目工时分布
    
    参数说明:
        year: 年份，如 2025
        month: 月份，1-12
    
    返回数据:
        success: 是否成功
        data: 统计数据
            - year: 年份
            - month: 月份
            - total_workdays: 总工作日天数（排除周末和节假日）
            - filled_days: 已填写工时天数
            - missing_days: 缺少工时天数
            - total_hours: 总工时数
            - average_hours_per_day: 平均每天工时
            - project_distribution: 各项目工时分布
            - missing_dates: 缺少工时的具体日期列表
        message: 操作结果描述
    
    使用示例:
        - 查询本月工时: get_my_time_stats(year=2025, month=10)
        - 查询上月工时: get_my_time_stats(year=2025, month=9)
    """
    from datetime import datetime, timedelta
    import calendar
    from src.client import api_client
    
    try:
        # 获取当月的开始和结束日期
        start_date = f"{year}-{month:02d}-01"
        last_day = calendar.monthrange(year, month)[1]
        end_date = f"{year}-{month:02d}-{last_day:02d}"
        
        # 获取当月所有工时记录
        result = await api_client.get(
            "/time-entries/my",
            params={
                "start_date": start_date,
                "end_date": end_date,
                "limit": 1000,  # 获取所有记录
            }
        )
        
        # 解析数据
        time_entries = []
        if isinstance(result, dict) and 'data' in result:
            if isinstance(result['data'], list):
                time_entries = result['data']
            elif isinstance(result['data'], dict) and 'data' in result['data']:
                time_entries = result['data']['data']
        
        # 计算工作日天数（排除周末）
        total_workdays = 0
        workday_dates = set()
        current_date = datetime(year, month, 1)
        while current_date.month == month:
            # 0=周一, 6=周日
            if current_date.weekday() < 5:  # 周一到周五
                total_workdays += 1
                workday_dates.add(current_date.date())
            current_date += timedelta(days=1)
        
        # 统计已填写的日期
        filled_dates = set()
        total_hours = 0
        project_hours = {}
        
        for entry in time_entries:
            # 解析工作日期
            work_date = entry.get('work_date', '')
            if work_date:
                date_obj = datetime.fromisoformat(work_date.replace('Z', '+00:00')).date()
                filled_dates.add(date_obj)
            
            # 累计工时
            hours = entry.get('work_hours', 0)
            total_hours += hours
            
            # 按项目统计
            project_name = entry.get('project_name', '未知项目')
            business_line = entry.get('business_line_name', '')
            project_key = f"{project_name} ({business_line})" if business_line else project_name
            project_hours[project_key] = project_hours.get(project_key, 0) + hours
        
        # 计算缺少工时的日期
        missing_dates = sorted([d for d in workday_dates if d not in filled_dates])
        
        # 计算平均工时
        filled_days = len(filled_dates)
        average_hours = total_hours / filled_days if filled_days > 0 else 0
        
        # 构建项目分布列表
        project_distribution = [
            {"project": proj, "hours": hrs, "percentage": round(hrs / total_hours * 100, 1) if total_hours > 0 else 0}
            for proj, hrs in sorted(project_hours.items(), key=lambda x: x[1], reverse=True)
        ]
        
        return {
            "success": True,
            "data": {
                "year": year,
                "month": month,
                "total_workdays": total_workdays,
                "filled_days": filled_days,
                "missing_days": len(missing_dates),
                "total_hours": total_hours,
                "average_hours_per_day": round(average_hours, 2),
                "project_distribution": project_distribution,
                "missing_dates": [str(d) for d in missing_dates],
                "completion_rate": round(filled_days / total_workdays * 100, 1) if total_workdays > 0 else 0,
            },
            "message": f"成功获取 {year} 年 {month} 月工时统计"
        }
        
    except Exception as e:
        import traceback
        logger.error(f"获取工时统计失败: {traceback.format_exc()}")
        return {
            "success": False,
            "data": {},
            "message": f"获取工时统计失败: {str(e)}"
        }


@mcp.tool()
async def get_my_projects(
    page: int = 1,
    limit: int = 20,
) -> dict[str, Any]:
    """获取我参与的项目列表
    
    查询当前用户参与的所有项目，包括项目的基本信息和状态。
    
    参数说明:
        page: 页码，从 1 开始 (默认: 1)
        limit: 每页显示的记录数 (默认: 20)
    
    返回数据:
        success: 是否成功
        data: 项目列表，包含:
            - total: 总项目数
            - page: 当前页码
            - limit: 每页记录数
            - data: 项目数组，每个项目包括:
                - id: 项目ID
                - name: 项目名称
                - type: 项目类型
                - level: 项目层级 (level1/level2)
                - parent_id: 父项目ID（如果是二级项目）
                - business_line: 业务线名称
                - business_line_id: 业务线ID
                - created_at: 创建时间
        message: 操作结果描述
    
    使用示例:
        - 查看我的项目: get_my_projects()
        - 分页查询: get_my_projects(page=2, limit=10)
    """
    from src.client import api_client
    
    try:
        result = await api_client.get(
            "/projects/my",
            params={"page": page, "limit": limit}
        )
        return {
            "success": True,
            "data": result,
            "message": "成功获取我参与的项目列表"
        }
    except Exception as e:
        import traceback
        logger.error(f"获取我参与的项目失败: {traceback.format_exc()}")
    return {
            "success": False,
            "data": {},
            "message": f"获取我参与的项目失败: {str(e)}"
        }


@mcp.tool()
async def get_project_detail(
    project_id: int,
) -> dict[str, Any]:
    """获取项目详情 - 查询项目的完整信息
    
    获取项目的详细信息，包括:
    - 项目基本信息（名称、类型、层级）
    - 父项目信息（如果是二级项目）
    - 项目成员列表
    - 项目经理信息
    - 业务线信息
    - 工时计划信息
    
    参数说明:
        project_id: 项目ID
    
    返回数据:
        success: 是否成功
        data: 项目详情
            - id: 项目ID
            - name: 项目名称
            - type: 项目类型 (rd/engineering/sales等)
            - level: 项目层级 (level1/level2)
            - parent_id: 父项目ID
            - parent_name: 父项目名称（如果是二级项目）
            - business_line: 业务线名称
            - business_line_id: 业务线ID
            - members: 项目成员列表
            - managers: 项目经理列表
            - time_plan: 工时计划信息
            - created_at: 创建时间
            - updated_at: 更新时间
        message: 操作结果描述
    
    使用示例:
        - 查询项目详情: get_project_detail(project_id=127)
    """
    from src.client import api_client
    
    try:
        # 获取项目基本信息
        result = await api_client.get(f"/projects/{project_id}")
        
        return {
            "success": True,
            "data": result,
            "message": f"成功获取项目 {project_id} 的详细信息"
        }
        
    except Exception as e:
        import traceback
        logger.error(f"获取项目详情失败: {traceback.format_exc()}")
        return {
            "success": False,
            "data": {},
            "message": f"获取项目详情失败: {str(e)}"
        }


# 运行服务器
if __name__ == "__main__":
    import asyncio
    
    # 验证配置
    try:
        settings.validate()
        logger.info("配置验证成功")
    except ValueError as e:
        logger.error(f"配置错误: {e}")
        raise

    logger.info("启动工时管理系统 MCP 服务器...")
    asyncio.run(mcp.run())


def main() -> None:
    """MCP 服务器主入口点"""
    try:
        settings.validate()
        logger.info("配置验证成功")
    except ValueError as e:
        logger.error(f"配置错误: {e}")
        raise

    logger.info("启动工时管理系统 MCP 服务器...")
    asyncio.run(mcp.run())


if __name__ == "__main__":
    main()
