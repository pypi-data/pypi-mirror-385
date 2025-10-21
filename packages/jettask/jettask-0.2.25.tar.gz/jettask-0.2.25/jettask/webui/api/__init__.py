"""
API v1 路由模块集合
"""
from fastapi import APIRouter

# 导入8个主要模块的路由
from .overview import router as overview_router      # 概览
from .namespaces import router as namespaces_router  # 命名空间
from .queues import router as queues_router         # 队列
from .scheduled import router as scheduled_router    # 定时任务
from .alerts import router as alerts_router         # 告警
from .settings import router as settings_router      # 设置
from .workers import router as workers_router        # Worker 监控

# 创建 v1 总路由，添加统一的 /api/v1 前缀
api_router = APIRouter(prefix="/api/v1")

# 按功能模块组织路由
api_router.include_router(overview_router)    # 系统概览、健康检查
api_router.include_router(namespaces_router)  # 命名空间管理（独立路由）
api_router.include_router(queues_router)      # 队列管理、任务处理
api_router.include_router(scheduled_router)   # 定时任务管理
api_router.include_router(alerts_router)      # 告警规则管理
api_router.include_router(settings_router)    # 系统配置
api_router.include_router(workers_router)     # Worker 监控

__all__ = ['api_router']


