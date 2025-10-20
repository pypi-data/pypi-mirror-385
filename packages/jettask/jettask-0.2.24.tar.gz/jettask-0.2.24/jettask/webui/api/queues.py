"""
队列模块 - 队列管理、任务处理、队列统计和监控
提供轻量级的路由入口，业务逻辑在 QueueService 中实现
"""
from fastapi import APIRouter, HTTPException, Request, Query, Path, Depends
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

from jettask.schemas import (
    TimeRangeQuery,
    TrimQueueRequest,
    TasksRequest,
    TaskActionRequest,
    BacklogLatestRequest,
    BacklogTrendRequest
)
from jettask.webui.services.queue_service import QueueService
from jettask.webui.services.task_service import TaskService
from jettask.utils.redis_monitor import RedisMonitorService

router = APIRouter(prefix="/queues", tags=["queues"])
logger = logging.getLogger(__name__)


# ============ 队列基础管理 ============

@router.get(
    "/{namespace}",
    summary="获取命名空间队列列表",
    description="获取指定命名空间下所有队列的基本信息和状态",
    responses={
        200: {
            "description": "成功返回队列列表",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "queues": [
                            {"name": "email_queue", "pending": 45, "processing": 3},
                            {"name": "sms_queue", "pending": 12, "processing": 1}
                        ]
                    }
                }
            }
        },
        500: {"description": "服务器内部错误"}
    }
)
async def get_queues(
    request: Request,
    namespace: str = Path(..., description="命名空间名称", example="default")
) -> Dict[str, Any]:
    """
    ## 获取命名空间队列列表

    获取指定命名空间下所有队列的基本信息，包括队列名称和任务统计。

    **返回信息包括**:
    - 队列名称
    - 待处理任务数
    - 处理中任务数
    - 其他队列状态信息

    **使用场景**:
    - 队列管理页面列表
    - 队列状态监控
    - 队列选择器

    **示例请求**:
    ```bash
    curl -X GET "http://localhost:8001/api/v1/queues/default"
    ```

    **注意事项**:
    - 返回该命名空间下的所有队列
    - 数据实时从 Redis 获取
    - 包含队列的基本统计信息
    """
    try:
        app = request.app
        if not app or not hasattr(app.state, 'namespace_data_access'):
            raise HTTPException(status_code=500, detail="Namespace data access not initialized")

        namespace_data_access = app.state.namespace_data_access
        return await QueueService.get_queues_by_namespace(namespace_data_access, namespace)
    except Exception as e:
        logger.error(f"获取队列列表失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))




@router.get(
    "/stats-v2/{namespace}",
    summary="获取队列统计信息 v2",
    description="获取队列的详细统计信息，支持消费者组和优先级队列",
    responses={
        200: {"description": "成功返回队列统计"},
        500: {"description": "服务器内部错误"}
    }
)
async def get_queue_stats(
    request: Request,
    namespace: str = Path(..., description="命名空间名称", example="default"),
    queue: Optional[str] = Query(None, description="队列名称，为空则返回所有队列", example="email_queue"),
    start_time: Optional[datetime] = Query(None, description="开始时间（ISO格式）"),
    end_time: Optional[datetime] = Query(None, description="结束时间（ISO格式）"),
    time_range: Optional[str] = Query(None, description="时间范围（如 1h, 24h, 7d）", example="24h")
) -> Dict[str, Any]:
    """
    ## 获取队列统计信息 v2

    获取队列的详细统计信息，支持消费者组详情和优先级队列统计。

    **增强特性**:
    - ✅ 支持消费者组详细统计
    - ✅ 支持优先级队列分析
    - ✅ 支持时间范围筛选
    - ✅ 支持单队列或全部队列查询

    **返回信息包括**:
    - 队列基本统计
    - 消费者组状态和积压
    - 优先级队列分布
    - 时间范围内的任务统计

    **使用场景**:
    - 队列详细监控
    - 消费者组管理
    - 优先级队列分析
    - 性能优化

    **示例请求**:
    ```bash
    # 获取指定队列的24小时统计
    curl -X GET "http://localhost:8001/api/v1/queues/stats-v2/default?queue=email_queue&time_range=24h"

    # 获取所有队列统计
    curl -X GET "http://localhost:8001/api/v1/queues/stats-v2/default?time_range=1h"
    ```

    **注意事项**:
    - v2 版本提供更详细的统计信息
    - 消费者组数据仅在使用 Stream 时可用
    - 建议使用时间范围参数限制数据量
    """
    try:
        app = request.app
        if not app or not hasattr(app.state, 'namespace_data_access'):
            raise HTTPException(status_code=500, detail="Namespace data access not initialized")

        namespace_data_access = app.state.namespace_data_access
        return await QueueService.get_queue_stats_v2(
            namespace_data_access, namespace, queue, start_time, end_time, time_range
        )
    except Exception as e:
        logger.error(f"获取队列统计v2失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ 消费者组统计 ============

@router.get(
    "/consumer-groups/{namespace}/{group_name}/stats",
    summary="获取消费者组统计",
    description="获取指定消费者组的详细统计信息和积压情况",
    responses={
        200: {
            "description": "成功返回消费者组统计",
            "content": {
                "application/json": {
                    "example": {
                        "group_name": "email_workers",
                        "pending_messages": 120,
                        "consumers": 5,
                        "lag": 95,
                        "last_delivered_id": "1697644800000-0"
                    }
                }
            }
        },
        400: {"description": "请求参数错误"},
        500: {"description": "服务器内部错误"}
    }
)
async def get_consumer_group_stats(
    request: Request,
    namespace: str = Path(..., description="命名空间名称", example="default"),
    group_name: str = Path(..., description="消费者组名称", example="email_workers")
) -> Dict[str, Any]:
    """
    ## 获取消费者组统计

    获取 Redis Stream 消费者组的详细统计信息，包括积压、消费者数量等。

    **返回信息包括**:
    - 消费者组名称
    - 待处理消息数 (pending)
    - 活跃消费者数量
    - 消费延迟 (lag)
    - 最后交付的消息 ID
    - 各消费者的详细状态

    **使用场景**:
    - 消费者组监控
    - 积压问题诊断
    - 消费者负载均衡
    - 性能优化

    **示例请求**:
    ```bash
    curl -X GET "http://localhost:8001/api/v1/queues/consumer-groups/default/email_workers/stats"
    ```

    **注意事项**:
    - 仅适用于使用 Redis Stream 的队列
    - 消费者组需提前创建
    - lag 值表示该组落后的消息数量
    - 建议定期监控 pending 和 lag 指标
    """
    try:
        app = request.app
        if not app or not hasattr(app.state, 'namespace_data_access'):
            raise HTTPException(status_code=500, detail="Namespace data access not initialized")

        namespace_data_access = app.state.namespace_data_access
        return await QueueService.get_consumer_group_stats(namespace_data_access, namespace, group_name)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"获取消费者组统计失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ Stream积压监控 ============

@router.get(
    "/stream-backlog/{namespace}",
    summary="获取 Stream 积压监控数据",
    description="获取 Redis Stream 的积压监控数据和历史趋势",
    responses={
        200: {
            "description": "成功返回 Stream 积压数据",
            "content": {
                "application/json": {
                    "example": {
                        "stream_name": "task_stream",
                        "current_length": 1500,
                        "consumer_groups": 3,
                        "total_pending": 250,
                        "history": [
                            {"timestamp": "2025-10-18T10:00:00Z", "length": 1400},
                            {"timestamp": "2025-10-18T11:00:00Z", "length": 1500}
                        ]
                    }
                }
            }
        },
        500: {"description": "服务器内部错误"}
    }
)
async def get_stream_backlog(
    request: Request,
    namespace: str = Path(..., description="命名空间名称", example="default"),
    stream_name: Optional[str] = Query(None, description="Stream 名称，为空则返回所有", example="task_stream"),
    hours: int = Query(24, ge=1, le=168, description="查询最近多少小时的数据", example=24)
) -> Dict[str, Any]:
    """
    ## 获取 Stream 积压监控数据

    获取 Redis Stream 的积压情况和历史趋势数据。

    **返回信息包括**:
    - Stream 当前长度
    - 消费者组数量
    - 总待处理消息数
    - 历史趋势数据（按小时）
    - 积压率变化趋势

    **使用场景**:
    - Stream 积压监控
    - 容量规划
    - 性能趋势分析
    - 异常检测

    **示例请求**:
    ```bash
    # 获取指定 Stream 最近24小时积压数据
    curl -X GET "http://localhost:8001/api/v1/queues/stream-backlog/default?stream_name=task_stream&hours=24"

    # 获取所有 Stream 的积压数据
    curl -X GET "http://localhost:8001/api/v1/queues/stream-backlog/default?hours=48"
    ```

    **注意事项**:
    - 仅适用于使用 Redis Stream 的队列
    - hours 参数范围: 1-168 (7天)
    - 历史数据按小时聚合
    - 建议定期监控积压趋势
    """
    try:
        app = request.app
        if not app or not hasattr(app.state, 'data_access'):
            raise HTTPException(status_code=500, detail="Data access not initialized")

        data_access = app.state.data_access
        return await QueueService.get_stream_backlog(data_access, namespace, stream_name, hours)
    except Exception as e:
        logger.error(f"获取Stream积压监控数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/stream-backlog/{namespace}/summary",
    summary="获取 Stream 积压汇总",
    description="获取命名空间下所有 Stream 的积压汇总信息",
    responses={
        200: {
            "description": "成功返回积压汇总",
            "content": {
                "application/json": {
                    "example": {
                        "total_streams": 5,
                        "total_length": 7500,
                        "total_pending": 850,
                        "avg_backlog_rate": 12.5,
                        "streams": [
                            {"name": "task_stream", "length": 1500, "pending": 250},
                            {"name": "email_stream", "length": 2000, "pending": 180}
                        ]
                    }
                }
            }
        },
        500: {"description": "服务器内部错误"}
    }
)
async def get_stream_backlog_summary(
    request: Request,
    namespace: str = Path(..., description="命名空间名称", example="default")
) -> Dict[str, Any]:
    """
    ## 获取 Stream 积压汇总

    获取指定命名空间下所有 Redis Stream 的积压汇总统计。

    **返回信息包括**:
    - Stream 总数
    - 总消息数
    - 总待处理消息数
    - 平均积压率
    - 各 Stream 的简要信息

    **使用场景**:
    - 全局积压监控
    - 命名空间健康检查
    - 快速问题定位
    - 管理报表

    **示例请求**:
    ```bash
    curl -X GET "http://localhost:8001/api/v1/queues/stream-backlog/default/summary"
    ```

    **注意事项**:
    - 实时计算，可能有延迟
    - 仅包含使用 Stream 的队列
    - 建议配合详细接口使用
    """
    try:
        app = request.app
        if not app or not hasattr(app.state, 'data_access'):
            raise HTTPException(status_code=500, detail="Data access not initialized")

        data_access = app.state.data_access
        return await QueueService.get_stream_backlog_summary(data_access, namespace)
    except Exception as e:
        logger.error(f"获取Stream积压监控汇总失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ 队列积压监控 ============

@router.post(
    "/backlog/latest/{namespace}",
    summary="获取最新积压数据快照",
    description="获取指定命名空间下队列的最新积压数据快照",
    responses={
        200: {
            "description": "成功返回积压快照数据",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "namespace": "default",
                        "timestamp": "2025-10-18T10:30:00Z",
                        "snapshots": [
                            {
                                "queue_name": "email_queue",
                                "pending_count": 120,
                                "processing_count": 8,
                                "completed_count": 5430,
                                "failed_count": 12,
                                "queue_size": 128,
                                "oldest_task_age": 45
                            }
                        ]
                    }
                }
            }
        },
        500: {"description": "服务器内部错误"}
    }
)
async def get_latest_backlog(
    request: Request,
    namespace: str = Path(..., description="命名空间名称", example="default"),
    backlog_request: BacklogLatestRequest = ...
) -> Dict[str, Any]:
    """
    ## 获取最新积压数据快照

    获取指定命名空间下一个或多个队列的最新积压数据快照，用于实时监控队列状态。

    **返回信息包括**:
    - 待处理任务数 (pending_count)
    - 处理中任务数 (processing_count)
    - 已完成任务数 (completed_count)
    - 失败任务数 (failed_count)
    - 队列大小 (queue_size)
    - 最老任务年龄（秒）

    **使用场景**:
    - 实时积压监控
    - 队列健康检查
    - 告警触发依据
    - 运维大盘展示

    **示例请求**:
    ```bash
    # 获取指定队列的积压快照
    curl -X POST "http://localhost:8001/api/v1/queues/backlog/latest/default" \\
      -H "Content-Type: application/json" \\
      -d '{
        "queues": ["email_queue", "sms_queue"]
      }'

    # 获取所有队列的积压快照
    curl -X POST "http://localhost:8001/api/v1/queues/backlog/latest/default" \\
      -H "Content-Type: application/json" \\
      -d '{
        "queues": []
      }'
    ```

    **注意事项**:
    - 数据为实时快照，反映当前时刻的队列状态
    - queues 参数为空或不提供时，返回所有队列的数据
    - oldest_task_age 为空表示队列中没有待处理任务
    - 建议配合告警规则使用，及时发现积压问题
    """
    try:
        app = request.app
        if not app or not hasattr(app.state, 'data_access'):
            raise HTTPException(status_code=500, detail="Data access not initialized")

        data_access = app.state.data_access
        queues = backlog_request.queues or []

        # TODO: 调用QueueService的积压监控方法
        # snapshots = await QueueService.get_latest_backlog(data_access, namespace, queues)

        return {
            "success": True,
            "namespace": namespace,
            "timestamp": datetime.now().isoformat(),
            "snapshots": [],
            "message": "Backlog monitoring endpoint - implementation pending"
        }
    except Exception as e:
        logger.error(f"获取最新积压数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/backlog/trend/{namespace}",
    summary="获取队列积压趋势",
    description="获取指定队列在一段时间内的积压趋势数据，支持多种时间粒度",
    responses={
        200: {
            "description": "成功返回积压趋势数据",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "namespace": "default",
                        "queue_name": "email_queue",
                        "time_range": "1h",
                        "interval": "5m",
                        "timestamps": [
                            "2025-10-18T10:00:00Z",
                            "2025-10-18T10:05:00Z",
                            "2025-10-18T10:10:00Z"
                        ],
                        "metrics": {
                            "pending": [120, 115, 108],
                            "processing": [8, 10, 9],
                            "completed": [5430, 5445, 5462],
                            "failed": [12, 12, 13]
                        },
                        "statistics": {
                            "peak_pending": 120,
                            "avg_pending": 114.3,
                            "avg_throughput": 10.7,
                            "overall_success_rate": 99.76
                        }
                    }
                }
            }
        },
        400: {"description": "请求参数错误"},
        500: {"description": "服务器内部错误"}
    }
)
async def get_backlog_trend(
    request: Request,
    namespace: str = Path(..., description="命名空间名称", example="default"),
    trend_request: BacklogTrendRequest = ...
) -> Dict[str, Any]:
    """
    ## 获取队列积压趋势

    获取指定队列在一段时间内的积压趋势数据，包括各项指标的时间序列和统计摘要。

    **支持的时间范围**:
    - `1h`: 最近1小时
    - `6h`: 最近6小时
    - `1d` 或 `24h`: 最近1天
    - `7d`: 最近7天
    - 或使用 `start_time` 和 `end_time` 指定精确时间范围

    **支持的时间间隔**:
    - `1m`: 1分钟粒度
    - `5m`: 5分钟粒度
    - `15m`: 15分钟粒度
    - `1h`: 1小时粒度

    **支持的指标类型**:
    - `pending`: 待处理任务数
    - `processing`: 处理中任务数
    - `completed`: 已完成任务数
    - `failed`: 失败任务数

    **返回信息包括**:
    - 时间戳序列
    - 各指标的时间序列数据
    - 统计摘要（峰值、平均值、成功率等）

    **使用场景**:
    - 积压趋势分析
    - 性能问题诊断
    - 容量规划
    - 历史数据回溯
    - 运维报表生成

    **示例请求**:
    ```bash
    # 获取指定队列最近1小时的积压趋势
    curl -X POST "http://localhost:8001/api/v1/queues/backlog/trend/default" \\
      -H "Content-Type: application/json" \\
      -d '{
        "queue_name": "email_queue",
        "time_range": "1h",
        "interval": "5m",
        "metrics": ["pending", "processing"]
      }'

    # 使用精确时间范围查询
    curl -X POST "http://localhost:8001/api/v1/queues/backlog/trend/default" \\
      -H "Content-Type: application/json" \\
      -d '{
        "queue_name": "sms_queue",
        "start_time": "2025-10-18T09:00:00Z",
        "end_time": "2025-10-18T10:00:00Z",
        "interval": "1m",
        "metrics": ["pending", "processing", "completed", "failed"]
      }'

    # 获取所有队列的趋势（不指定queue_name）
    curl -X POST "http://localhost:8001/api/v1/queues/backlog/trend/default" \\
      -H "Content-Type: application/json" \\
      -d '{
        "time_range": "24h",
        "interval": "1h"
      }'
    ```

    **注意事项**:
    - `time_range` 和 `start_time/end_time` 二选一，优先使用 `start_time/end_time`
    - 时间间隔越小，返回的数据点越多，建议根据时间范围选择合适的间隔
    - 建议时间范围: 1h→5m, 6h→15m, 24h→1h, 7d→1h
    - 统计摘要仅在请求所有指标时才完整
    - 数据来源于持久化存储，可能有轻微延迟
    """
    try:
        app = request.app
        if not app or not hasattr(app.state, 'data_access'):
            raise HTTPException(status_code=500, detail="Data access not initialized")

        data_access = app.state.data_access

        # TODO: 调用QueueService的积压趋势方法
        # trend_data = await QueueService.get_backlog_trend(
        #     data_access, namespace, trend_request
        # )

        return {
            "success": True,
            "namespace": namespace,
            "queue_name": trend_request.queue_name,
            "time_range": trend_request.time_range,
            "interval": trend_request.interval,
            "timestamps": [],
            "metrics": {},
            "statistics": {},
            "message": "Backlog trend endpoint - implementation pending"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"获取积压趋势失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ 任务管理 ============

def get_task_service(request: Request) -> TaskService:
    """获取任务服务实例"""
    if not hasattr(request.app.state, 'data_access'):
        raise HTTPException(status_code=500, detail="Data access not initialized")
    return TaskService(request.app.state.data_access)



@router.post(
    "/tasks-v2/{namespace}",
    summary="获取任务列表 v2",
    description="获取任务列表v2版本，支持tasks和task_runs表连表查询，提供更丰富的查询和过滤功能",
    responses={
        200: {
            "description": "成功返回任务列表",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": [
                            {
                                "task_id": "task-001",
                                "queue_name": "email_queue",
                                "status": "completed",
                                "created_at": "2025-10-18T10:00:00Z",
                                "runs": []
                            }
                        ],
                        "total": 150,
                        "page": 1,
                        "page_size": 20
                    }
                }
            }
        },
        400: {"description": "请求参数错误"},
        500: {"description": "服务器内部错误"}
    }
)
async def get_tasks_v2(request: Request, namespace: str):
    """
    ## 获取任务列表 v2

    获取任务列表的增强版本，支持 tasks 和 task_runs 表的连表查询，提供更强大的查询和过滤功能。

    **增强特性**:
    - ✅ 支持多表连接查询
    - ✅ 支持复杂过滤条件
    - ✅ 支持排序和分页
    - ✅ 返回任务执行历史

    **请求体参数**:
    ```json
    {
        "queue_name": "email_queue",  // 可选：队列名称
        "status": "completed",         // 可选：任务状态
        "page": 1,                     // 可选：页码，默认1
        "page_size": 20,               // 可选：每页数量，默认20
        "start_time": "2025-10-18T00:00:00Z",  // 可选：开始时间
        "end_time": "2025-10-18T23:59:59Z",    // 可选：结束时间
        "sort_by": "created_at",       // 可选：排序字段
        "sort_order": "desc"           // 可选：排序方向 (asc/desc)
    }
    ```

    **支持的任务状态**:
    - `pending`: 待处理
    - `processing`: 处理中
    - `completed`: 已完成
    - `failed`: 失败
    - `retrying`: 重试中

    **使用场景**:
    - 任务管理页面
    - 任务历史查询
    - 任务状态监控
    - 故障排查

    **示例请求**:
    ```bash
    # 查询指定队列的已完成任务
    curl -X POST "http://localhost:8001/api/v1/queues/tasks-v2/default" \\
      -H "Content-Type: application/json" \\
      -d '{
        "queue_name": "email_queue",
        "status": "completed",
        "page": 1,
        "page_size": 20
      }'

    # 查询指定时间范围的任务
    curl -X POST "http://localhost:8001/api/v1/queues/tasks-v2/default" \\
      -H "Content-Type: application/json" \\
      -d '{
        "start_time": "2025-10-18T00:00:00Z",
        "end_time": "2025-10-18T23:59:59Z",
        "sort_by": "created_at",
        "sort_order": "desc"
      }'
    ```

    **注意事项**:
    - v2 版本提供更详细的任务信息
    - 包含任务的执行历史（runs）
    - 建议使用分页避免一次查询过多数据
    - 时间参数使用 ISO 8601 格式

    Args:
        namespace: 命名空间
    """
    try:
        app = request.app
        if not app or not hasattr(app.state, 'namespace_data_access'):
            raise HTTPException(status_code=500, detail="Namespace data access not initialized")
        
        namespace_data_access = app.state.namespace_data_access
        
        # 解析请求体
        body = await request.json()
        
        return await QueueService.get_tasks_v2(namespace_data_access, namespace, body)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"获取任务列表v2失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ Redis监控 ============

@router.get(
    "/redis/monitor/{namespace}",
    summary="获取 Redis 性能监控数据",
    description="获取指定命名空间的 Redis 实时性能监控数据，包括内存使用、连接数、命令统计等",
    responses={
        200: {
            "description": "成功返回 Redis 监控数据",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "namespace": "default",
                        "redis_info": {
                            "used_memory": "10485760",
                            "used_memory_human": "10M",
                            "connected_clients": "25",
                            "total_commands_processed": "1500000",
                            "instantaneous_ops_per_sec": "150",
                            "keyspace_hits": "98500",
                            "keyspace_misses": "1500"
                        },
                        "performance": {
                            "hit_rate": "98.5%",
                            "qps": 150,
                            "memory_fragmentation_ratio": 1.2
                        }
                    }
                }
            }
        },
        500: {"description": "服务器内部错误"}
    }
)
async def get_redis_monitor(request: Request, namespace: str):
    """
    ## 获取 Redis 性能监控数据

    获取指定命名空间的 Redis 实例的实时性能监控数据。

    **监控指标包括**:
    - **内存使用**: 已用内存、峰值内存、内存碎片率
    - **连接信息**: 当前连接数、阻塞的客户端数
    - **命令统计**: 总命令数、每秒操作数（QPS）
    - **缓存命中**: 命中次数、未命中次数、命中率
    - **持久化**: RDB/AOF 状态、最后保存时间
    - **键空间**: 各数据库的键数量和过期键数量

    **性能指标**:
    - `hit_rate`: 缓存命中率
    - `qps`: 每秒查询数
    - `memory_fragmentation_ratio`: 内存碎片率

    **使用场景**:
    - Redis 性能监控
    - 容量规划
    - 性能优化
    - 故障诊断
    - 运维大盘

    **示例请求**:
    ```bash
    curl -X GET "http://localhost:8001/api/v1/queues/redis/monitor/default"
    ```

    **注意事项**:
    - 数据实时获取，反映当前时刻的 Redis 状态
    - 频繁调用可能对 Redis 性能有轻微影响
    - 建议监控间隔设置为 5-10 秒
    - 内存碎片率 > 1.5 时建议重启 Redis

    Args:
        namespace: 命名空间
    """
    try:
        app = request.app
        if not app or not hasattr(app.state, 'namespace_data_access'):
            raise HTTPException(status_code=500, detail="Namespace data access not initialized")
        
        namespace_data_access = app.state.namespace_data_access
        redis_monitor_service = RedisMonitorService(namespace_data_access)
        return await redis_monitor_service.get_redis_monitor_data(namespace)
    except Exception as e:
        logger.error(f"获取Redis监控数据失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/redis/slow-log/{namespace}",
    summary="获取 Redis 慢查询日志",
    description="获取 Redis 的慢查询日志，用于诊断性能问题",
    responses={
        200: {
            "description": "成功返回慢查询日志",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "namespace": "default",
                        "slow_logs": [
                            {
                                "id": 12345,
                                "timestamp": 1697644800,
                                "duration_us": 15000,
                                "command": "KEYS pattern*",
                                "client_addr": "127.0.0.1:54321"
                            }
                        ],
                        "total": 10
                    }
                }
            }
        },
        500: {"description": "服务器内部错误"}
    }
)
async def get_redis_slow_log(
    request: Request,
    namespace: str,
    limit: int = Query(10, ge=1, le=100, description="返回记录数，范围 1-100", example=10)
):
    """
    ## 获取 Redis 慢查询日志

    获取 Redis 实例的慢查询日志，帮助识别性能瓶颈和优化查询。

    **日志信息包括**:
    - 日志 ID
    - 执行时间戳
    - 执行耗时（微秒）
    - 执行的命令
    - 客户端地址和端口

    **使用场景**:
    - 性能问题诊断
    - 慢查询优化
    - Redis 性能分析
    - 识别不合理的命令使用

    **示例请求**:
    ```bash
    # 获取最近10条慢查询日志
    curl -X GET "http://localhost:8001/api/v1/queues/redis/slow-log/default?limit=10"

    # 获取最近50条慢查询日志
    curl -X GET "http://localhost:8001/api/v1/queues/redis/slow-log/default?limit=50"
    ```

    **注意事项**:
    - 慢查询阈值由 Redis 配置 `slowlog-log-slower-than` 决定（默认10ms）
    - 日志按时间倒序返回（最新的在前）
    - 慢查询日志存储在内存中，重启后清空
    - 建议定期检查并优化慢查询
    - 常见慢命令: KEYS、SMEMBERS、HGETALL（大集合）

    Args:
        namespace: 命名空间
        limit: 返回记录数
    """
    try:
        app = request.app
        if not app or not hasattr(app.state, 'namespace_data_access'):
            raise HTTPException(status_code=500, detail="Namespace data access not initialized")
        
        namespace_data_access = app.state.namespace_data_access
        redis_monitor_service = RedisMonitorService(namespace_data_access)
        return await redis_monitor_service.get_slow_log(namespace, limit)
    except Exception as e:
        logger.error(f"获取Redis慢查询日志失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/redis/command-stats/{namespace}",
    summary="获取 Redis 命令统计",
    description="获取 Redis 各类命令的执行统计信息，包括调用次数、耗时等",
    responses={
        200: {
            "description": "成功返回命令统计",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "namespace": "default",
                        "command_stats": [
                            {
                                "command": "GET",
                                "calls": 1500000,
                                "usec": 45000000,
                                "usec_per_call": 30.0
                            },
                            {
                                "command": "SET",
                                "calls": 800000,
                                "usec": 32000000,
                                "usec_per_call": 40.0
                            }
                        ],
                        "total_commands": 25
                    }
                }
            }
        },
        500: {"description": "服务器内部错误"}
    }
)
async def get_redis_command_stats(request: Request, namespace: str):
    """
    ## 获取 Redis 命令统计

    获取 Redis 实例的命令执行统计信息，用于分析命令使用情况和性能优化。

    **统计信息包括**:
    - 命令名称
    - 调用次数 (calls)
    - 总耗时（微秒）(usec)
    - 平均耗时（微秒/次）(usec_per_call)

    **使用场景**:
    - 分析 Redis 命令使用模式
    - 识别高频命令
    - 性能优化
    - 命令耗时分析
    - 容量规划

    **示例请求**:
    ```bash
    curl -X GET "http://localhost:8001/api/v1/queues/redis/command-stats/default"
    ```

    **返回示例**:
    ```json
    {
        "success": true,
        "namespace": "default",
        "command_stats": [
            {"command": "GET", "calls": 1500000, "usec": 45000000, "usec_per_call": 30.0},
            {"command": "SET", "calls": 800000, "usec": 32000000, "usec_per_call": 40.0},
            {"command": "HGETALL", "calls": 50000, "usec": 8000000, "usec_per_call": 160.0}
        ],
        "total_commands": 25
    }
    ```

    **注意事项**:
    - 统计数据为累计值，从 Redis 启动开始计算
    - 重启 Redis 后统计清零
    - 按调用次数降序排序
    - 可通过 `usec_per_call` 识别慢命令
    - 建议关注平均耗时较高的命令

    Args:
        namespace: 命名空间
    """
    try:
        app = request.app
        if not app or not hasattr(app.state, 'namespace_data_access'):
            raise HTTPException(status_code=500, detail="Namespace data access not initialized")
        
        namespace_data_access = app.state.namespace_data_access
        redis_monitor_service = RedisMonitorService(namespace_data_access)
        return await redis_monitor_service.get_command_stats(namespace)
    except Exception as e:
        logger.error(f"获取Redis命令统计失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/redis/stream-stats/{namespace}",
    summary="获取 Redis Stream 统计",
    description="获取 Redis Stream 的详细统计信息，包括长度、消费者组、消息等",
    responses={
        200: {
            "description": "成功返回 Stream 统计",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "namespace": "default",
                        "streams": [
                            {
                                "stream_name": "task_stream",
                                "length": 1500,
                                "first_entry_id": "1697644800000-0",
                                "last_entry_id": "1697731200000-5",
                                "groups": [
                                    {
                                        "name": "workers",
                                        "consumers": 5,
                                        "pending": 120,
                                        "last_delivered_id": "1697730000000-3"
                                    }
                                ]
                            }
                        ]
                    }
                }
            }
        },
        500: {"description": "服务器内部错误"}
    }
)
async def get_redis_stream_stats(
    request: Request,
    namespace: str,
    stream_name: Optional[str] = Query(None, description="Stream 名称，为空则返回所有 Stream 的统计", example="task_stream")
):
    """
    ## 获取 Redis Stream 统计

    获取 Redis Stream 的详细统计信息，包括消息数量、消费者组状态等。

    **Stream 统计信息包括**:
    - Stream 名称
    - 消息总数（length）
    - 第一条消息 ID
    - 最后一条消息 ID
    - 消费者组列表及其状态

    **消费者组统计**:
    - 组名称
    - 消费者数量
    - 待处理消息数 (pending)
    - 最后交付的消息 ID

    **使用场景**:
    - Stream 使用情况监控
    - 消费者组管理
    - 积压分析
    - 容量规划
    - 性能优化

    **示例请求**:
    ```bash
    # 获取所有 Stream 的统计
    curl -X GET "http://localhost:8001/api/v1/queues/redis/stream-stats/default"

    # 获取指定 Stream 的统计
    curl -X GET "http://localhost:8001/api/v1/queues/redis/stream-stats/default?stream_name=task_stream"
    ```

    **注意事项**:
    - 仅返回使用 Redis Stream 的队列统计
    - 消息 ID 格式为 `timestamp-sequence`
    - pending 表示已分配但未确认的消息数
    - 建议监控 pending 消息数，及时处理积压

    Args:
        namespace: 命名空间
        stream_name: 可选，指定 Stream 名称
    """
    try:
        app = request.app
        if not app or not hasattr(app.state, 'namespace_data_access'):
            raise HTTPException(status_code=500, detail="Namespace data access not initialized")
        
        namespace_data_access = app.state.namespace_data_access
        redis_monitor_service = RedisMonitorService(namespace_data_access)
        return await redis_monitor_service.get_stream_stats(namespace, stream_name)
    except Exception as e:
        logger.error(f"获取Redis Stream统计失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============ 任务管理 ============

@router.get(
    "/{namespace}/tasks",
    summary="获取队列任务列表（简化版）",
    description="获取指定队列的任务列表，向后兼容的简化版本",
    responses={
        200: {
            "description": "成功返回任务列表",
            "content": {
                "application/json": {
                    "example": {
                        "success": True,
                        "data": [
                            {
                                "task_id": "task-001",
                                "queue_name": "email_queue",
                                "status": "completed",
                                "created_at": "2025-10-18T10:00:00Z"
                            }
                        ],
                        "total": 50
                    }
                }
            }
        },
        500: {"description": "服务器内部错误"}
    }
)
async def get_queue_tasks_simple(
    request: Request,
    namespace: str,
    queue_name: str = Query(..., description="队列名称", example="email_queue"),
    start_time: Optional[str] = Query(None, description="开始时间（ISO格式或 \"-\" 表示最早）", example="2025-10-18T00:00:00Z"),
    end_time: Optional[str] = Query(None, description="结束时间（ISO格式或 \"+\" 表示最新）", example="2025-10-18T23:59:59Z"),
    limit: int = Query(50, ge=1, le=1000, description="返回数量限制，范围 1-1000", example=50)
):
    """
    ## 获取队列任务列表（简化版）

    获取指定队列的任务列表，这是一个简化版本的API，用于向后兼容。

    **功能特点**:
    - ✅ 简单的时间范围查询
    - ✅ 支持分页限制
    - ✅ 按时间倒序返回（最新的在前）
    - ✅ 向后兼容旧版本

    **查询参数**:
    - `queue_name`: 队列名称（必填）
    - `start_time`: 开始时间，可选，默认 "-" 表示最早
    - `end_time`: 结束时间，可选，默认 "+" 表示最新
    - `limit`: 返回数量限制

    **使用场景**:
    - 快速查看队列任务
    - 简单的任务列表查询
    - 旧版本API兼容

    **示例请求**:
    ```bash
    # 获取队列最近50条任务
    curl -X GET "http://localhost:8001/api/v1/queues/default/tasks?queue_name=email_queue&limit=50"

    # 获取指定时间范围的任务
    curl -X GET "http://localhost:8001/api/v1/queues/default/tasks?queue_name=email_queue&start_time=2025-10-18T00:00:00Z&end_time=2025-10-18T23:59:59Z&limit=100"
    ```

    **注意事项**:
    - 默认从新到旧排序（reverse=True）
    - 如需更复杂的查询，请使用 `POST /tasks-v2/{namespace}` 接口
    - 时间参数支持 ISO 8601 格式或 "-"/"+" 特殊值
    - 最大返回1000条记录

    Args:
        namespace: 命名空间
        queue_name: 队列名称
        start_time: 开始时间（可选）
        end_time: 结束时间（可选）
        limit: 返回数量限制

    Returns:
        任务列表
    """
    try:
        if not hasattr(request.app.state, 'monitor'):
            raise HTTPException(status_code=500, detail="Monitor service not initialized")

        monitor = request.app.state.monitor
        result = await monitor.get_queue_tasks(
            queue_name,
            start_time or "-",
            end_time or "+",
            limit,
            reverse=True  # 默认从新到旧
        )

        return result
    except Exception as e:
        logger.error(f"获取队列 {queue_name} 任务列表失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


__all__ = ['router']