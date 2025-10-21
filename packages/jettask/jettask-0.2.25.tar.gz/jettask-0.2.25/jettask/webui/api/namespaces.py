"""
命名空间管理路由
提供命名空间的增删改查和管理功能
"""
from fastapi import APIRouter, HTTPException, Query, Path
from typing import Optional, List, Dict, Any
import logging
import traceback

from jettask.schemas import NamespaceCreate, NamespaceUpdate, NamespaceResponse, NamespaceStatisticsResponse
from jettask.webui.services.settings_service import SettingsService

logger = logging.getLogger(__name__)

# 创建独立的命名空间路由，设置 /namespaces 前缀
router = APIRouter(prefix="/namespaces", tags=["namespaces"])


@router.get(
    "/",
    summary="列出所有命名空间",
    description="获取系统中所有命名空间的列表，支持分页和按状态筛选",
    response_model=List[NamespaceResponse],
    responses={
        200: {
            "description": "成功返回命名空间列表"
        },
        500: {
            "description": "服务器内部错误",
            "content": {
                "application/json": {
                    "example": {"detail": "获取命名空间列表失败: Database error"}
                }
            }
        }
    }
)
async def list_namespaces(
    page: int = Query(1, ge=1, description="页码，从 1 开始", example=1),
    page_size: int = Query(20, ge=1, le=100, description="每页数量，范围 1-100", example=20),
    is_active: Optional[bool] = Query(None, description="是否只返回激活的命名空间", example=True)
) -> List[Dict[str, Any]]:
    """
    ## 列出所有命名空间

    获取系统中所有命名空间的列表，每个命名空间包含配置信息和连接状态。

    **功能说明**:
    - 支持分页查询，避免一次返回过多数据
    - 可按激活状态筛选命名空间
    - 返回每个命名空间的完整配置信息

    **使用场景**:
    - 命名空间管理页面
    - 环境切换选择列表
    - 系统配置概览

    **示例请求**:
    ```bash
    # 获取第一页的命名空间列表
    curl -X GET "http://localhost:8001/api/v1/namespaces/?page=1&page_size=20"

    # 只获取激活的命名空间
    curl -X GET "http://localhost:8001/api/v1/namespaces/?is_active=true"
    ```

    **注意事项**:
    - 返回的 Redis 和 PostgreSQL URL 会隐藏密码信息
    - 分页参数超出范围时返回空列表
    """
    try:
        return await SettingsService.list_namespaces(page, page_size, is_active)
    except Exception as e:
        logger.error(f"获取命名空间列表失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/",
    summary="创建新的命名空间",
    description="创建一个新的命名空间，可以选择直接配置或使用 Nacos 配置",
    response_model=NamespaceResponse,
    status_code=201,
    responses={
        201: {
            "description": "命名空间创建成功"
        },
        400: {
            "description": "请求参数错误",
            "content": {
                "application/json": {
                    "example": {"detail": "命名空间名称已存在"}
                }
            }
        },
        500: {
            "description": "服务器内部错误"
        }
    }
)
async def create_namespace(
    namespace: NamespaceCreate
) -> Dict[str, Any]:
    """
    ## 创建新的命名空间

    创建一个新的命名空间，用于隔离不同环境或项目的任务队列。

    **配置模式**:
    1. **direct 模式**: 直接提供 Redis 和 PostgreSQL 连接字符串
    2. **nacos 模式**: 通过 Nacos 配置键获取连接字符串

    **请求体参数**:
    ```json
    {
        "name": "production",
        "description": "生产环境命名空间",
        "config_mode": "direct",
        "redis_url": "redis://:password@localhost:6379/0",
        "pg_url": "postgresql://user:password@localhost:5432/jettask"
    }
    ```

    **使用场景**:
    - 创建新的环境隔离（如 dev、staging、production）
    - 多项目隔离
    - 多租户场景

    **示例请求**:
    ```bash
    # 使用直接配置模式
    curl -X POST "http://localhost:8001/api/v1/namespaces/" \\
      -H "Content-Type: application/json" \\
      -d '{
        "name": "production",
        "description": "生产环境",
        "config_mode": "direct",
        "redis_url": "redis://:password@localhost:6379/0",
        "pg_url": "postgresql://user:password@localhost:5432/jettask"
      }'

    # 使用 Nacos 配置模式
    curl -X POST "http://localhost:8001/api/v1/namespaces/" \\
      -H "Content-Type: application/json" \\
      -d '{
        "name": "staging",
        "description": "预发布环境",
        "config_mode": "nacos",
        "redis_nacos_key": "staging.redis.url",
        "pg_nacos_key": "staging.pg.url"
      }'
    ```

    **注意事项**:
    - 命名空间名称必须唯一
    - Redis 连接字符串格式: `redis://[password@]host:port/db`
    - PostgreSQL 连接字符串格式: `postgresql://user:password@host:port/database`
    - 创建后会自动验证连接是否可用
    """
    try:
        return await SettingsService.create_namespace(namespace)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"创建命名空间失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{namespace_name}",
    summary="获取命名空间详细信息",
    description="获取指定命名空间的完整配置信息和状态",
    response_model=NamespaceResponse,
    responses={
        200: {
            "description": "成功返回命名空间详情"
        },
        404: {
            "description": "命名空间不存在",
            "content": {
                "application/json": {
                    "example": {"detail": "命名空间 'production' 不存在"}
                }
            }
        },
        500: {
            "description": "服务器内部错误"
        }
    }
)
async def get_namespace(
    namespace_name: str = Path(..., description="命名空间名称", example="default")
) -> Dict[str, Any]:
    """
    ## 获取命名空间详细信息

    获取指定命名空间的完整配置信息，包括 Redis、PostgreSQL 配置和连接状态。

    **返回信息包括**:
    - 命名空间基本信息（名称、描述、启用状态）
    - Redis 连接配置
    - PostgreSQL 连接配置
    - 连接 URL
    - 配置版本号
    - 创建和更新时间

    **使用场景**:
    - 查看命名空间详细配置
    - 验证命名空间设置
    - 配置管理界面

    **示例请求**:
    ```bash
    curl -X GET "http://localhost:8001/api/v1/namespaces/default"
    ```

    **注意事项**:
    - 返回的连接字符串会隐藏敏感信息（如密码）
    - 如果命名空间不存在，返回 404 错误
    """
    try:
        return await SettingsService.get_namespace(namespace_name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"获取命名空间失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.put(
    "/{namespace_name}",
    summary="更新命名空间配置",
    description="更新指定命名空间的配置信息，支持部分更新",
    response_model=NamespaceResponse,
    responses={
        200: {
            "description": "命名空间更新成功"
        },
        400: {
            "description": "请求参数错误",
            "content": {
                "application/json": {
                    "example": {"detail": "配置参数无效"}
                }
            }
        },
        404: {
            "description": "命名空间不存在",
            "content": {
                "application/json": {
                    "example": {"detail": "命名空间 'production' 不存在"}
                }
            }
        },
        500: {
            "description": "服务器内部错误"
        }
    }
)
async def update_namespace(
    namespace_name: str = Path(..., description="命名空间名称", example="default"),
    namespace: NamespaceUpdate = ...
) -> Dict[str, Any]:
    """
    ## 更新命名空间配置

    更新指定命名空间的配置信息，所有字段都是可选的，只更新提供的字段。

    **可更新的字段**:
    - 描述信息
    - 配置模式（direct/nacos）
    - Redis 连接配置
    - PostgreSQL 连接配置
    - 启用状态

    **请求体参数**:
    ```json
    {
        "description": "更新后的描述",
        "enabled": true
    }
    ```

    **使用场景**:
    - 修改命名空间描述
    - 更新连接配置
    - 启用或禁用命名空间

    **示例请求**:
    ```bash
    # 更新描述和状态
    curl -X PUT "http://localhost:8001/api/v1/namespaces/default" \\
      -H "Content-Type: application/json" \\
      -d '{
        "description": "默认命名空间（已更新）",
        "enabled": true
      }'

    # 更新 Redis 配置
    curl -X PUT "http://localhost:8001/api/v1/namespaces/production" \\
      -H "Content-Type: application/json" \\
      -d '{
        "config_mode": "direct",
        "redis_url": "redis://:newpassword@localhost:6380/1"
      }'
    ```

    **注意事项**:
    - 更新配置后会自动验证新的连接是否可用
    - 如果有任务正在处理，建议谨慎更新
    - 只提供需要更新的字段，未提供的字段保持不变
    """
    try:
        return await SettingsService.update_namespace(namespace_name, namespace)
    except ValueError as e:
        status_code = 404 if "不存在" in str(e) else 400
        raise HTTPException(status_code=status_code, detail=str(e))
    except Exception as e:
        logger.error(f"更新命名空间失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/{namespace_name}",
    summary="删除命名空间",
    description="删除指定的命名空间，默认命名空间不能删除",
    responses={
        200: {
            "description": "命名空间删除成功",
            "content": {
                "application/json": {
                    "example": {"success": True, "message": "命名空间已删除"}
                }
            }
        },
        400: {
            "description": "操作不允许",
            "content": {
                "application/json": {
                    "example": {"detail": "默认命名空间不能删除"}
                }
            }
        },
        404: {
            "description": "命名空间不存在",
            "content": {
                "application/json": {
                    "example": {"detail": "命名空间 'production' 不存在"}
                }
            }
        },
        500: {
            "description": "服务器内部错误"
        }
    }
)
async def delete_namespace(
    namespace_name: str = Path(..., description="命名空间名称", example="staging")
) -> Dict[str, Any]:
    """
    ## 删除命名空间

    删除指定的命名空间及其所有相关配置。

    **删除规则**:
    - 默认命名空间（default）不能删除
    - 删除前会检查是否还有活跃的任务
    - 删除操作不可逆，请谨慎操作

    **使用场景**:
    - 清理不再使用的环境
    - 移除测试命名空间
    - 环境下线

    **示例请求**:
    ```bash
    curl -X DELETE "http://localhost:8001/api/v1/namespaces/staging"
    ```

    **注意事项**:
    - 删除命名空间会清除该命名空间下的所有配置
    - 不会删除 Redis 和 PostgreSQL 中的实际数据
    - 建议删除前先备份重要数据
    - 如果有任务正在处理，删除操作可能会失败
    """
    try:
        return await SettingsService.delete_namespace(namespace_name)
    except ValueError as e:
        status_code = 400 if "默认命名空间" in str(e) else 404
        raise HTTPException(status_code=status_code, detail=str(e))
    except Exception as e:
        logger.error(f"删除命名空间失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))



@router.get(
    "/{namespace_name}/statistics",
    summary="获取命名空间统计信息",
    description="获取指定命名空间的统计数据，包括队列数、任务数、Worker 数等",
    response_model=NamespaceStatisticsResponse,
    responses={
        200: {
            "description": "成功返回统计信息"
        },
        404: {
            "description": "命名空间不存在",
            "content": {
                "application/json": {
                    "example": {"detail": "命名空间 'production' 不存在"}
                }
            }
        },
        500: {
            "description": "服务器内部错误"
        }
    }
)
async def get_namespace_statistics(
    namespace_name: str = Path(..., description="命名空间名称", example="default")
) -> Dict[str, Any]:
    """
    ## 获取命名空间统计信息

    获取指定命名空间的实时统计数据，用于监控和分析。

    **统计指标包括**:
    - 队列总数
    - 任务总数
    - 活跃 Worker 数
    - Redis 内存使用情况
    - 数据库连接数

    **使用场景**:
    - 命名空间监控面板
    - 资源使用分析
    - 容量规划
    - 性能优化

    **示例请求**:
    ```bash
    curl -X GET "http://localhost:8001/api/v1/namespaces/default/statistics"
    ```

    **返回示例**:
    ```json
    {
        "success": true,
        "data": {
            "total_queues": 5,
            "total_tasks": 1250,
            "active_workers": 12,
            "redis_memory_usage": 10485760,
            "db_connections": 5
        },
        "namespace": "default"
    }
    ```

    **注意事项**:
    - 统计数据为实时查询，可能会有轻微延迟
    - Redis 内存使用单位为字节（bytes）
    - 如果命名空间未启用，某些统计数据可能为 0
    """
    try:
        return await SettingsService.get_namespace_statistics(namespace_name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"获取命名空间统计信息失败: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

__all__ = ['router']