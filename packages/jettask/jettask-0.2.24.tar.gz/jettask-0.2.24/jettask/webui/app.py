import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from jettask.webui.services import MonitorService

logger = logging.getLogger(__name__)

# 创建全局监控器实例
monitor = MonitorService()

@asynccontextmanager
async def lifespan(app: FastAPI):

    # Startup
    try:
        import os
        # 检查是否使用Nacos配置
        use_nacos = os.getenv('USE_NACOS', 'false').lower() == 'true'

        # 直接使用 connector.py 管理数据库连接
        from jettask.config.task_center import task_center_config

        # 存储配置信息在 app.state 中，供路由使用
        app.state.redis_url = os.environ.get('JETTASK_REDIS_URL', 'redis://localhost:6379/0')
        app.state.pg_url = os.environ.get('JETTASK_PG_URL', 'postgresql+asyncpg://jettask:123456@localhost:5432/jettask')
        app.state.redis_prefix = os.environ.get('JETTASK_REDIS_PREFIX', 'jettask')

        # 记录任务中心配置
        logger.info("=" * 60)
        logger.info("任务中心配置:")
        logger.info(f"  配置模式: {'Nacos' if use_nacos else '环境变量'}")
        logger.info(f"  元数据库: {task_center_config.meta_db_host}:{task_center_config.meta_db_port}/{task_center_config.meta_db_name}")
        logger.info(f"  API服务: {task_center_config.api_host}:{task_center_config.api_port}")
        logger.info(f"  基础URL: {task_center_config.base_url}")
        logger.info("=" * 60)

        # 连接 monitor
        # await monitor.connect()
        # # 启动心跳扫描器
        # await monitor.start_heartbeat_scanner()
        # # 将 monitor 存储到 app.state 供新路由使用
        # app.state.monitor = monitor

        # PostgreSQL consumer 已弃用，由统一的数据库管理器处理
        logging.info("PostgreSQL consumer disabled (use --with-consumer to enable)")

        logger.info("JetTask WebUI 启动成功")
    except Exception as e:
        logger.error(f"启动失败: {e}")
        import traceback
        traceback.print_exc()
        raise

    yield

    # Shutdown
    try:
        # 停止心跳扫描器
        await monitor.stop_heartbeat_scanner()
        await monitor.close()

        # 数据库连接池由 connector.py 全局管理
        # 不需要显式关闭，它们会在进程结束时自动清理

        logger.info("JetTask WebUI 关闭完成")
    except Exception as e:
        logger.error(f"关闭时出错: {e}")
        import traceback
        traceback.print_exc()

app = FastAPI(title="Jettask Monitor", lifespan=lifespan)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源（生产环境应该指定具体域名）
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法
    allow_headers=["*"],  # 允许所有请求头
)

# 配置 Namespace 自动注入中间件
# 这个中间件会自动检测路由中的 {namespace} 参数，并注入到 request.state.ns
from jettask.webui.middleware import NamespaceMiddleware
app.add_middleware(NamespaceMiddleware)
logger.info("NamespaceMiddleware 已注册 - 所有包含 {namespace} 的路由将自动注入命名空间上下文")

# 注册 API 路由
from jettask.webui.api import api_router
app.include_router(api_router)

# ============ WebSocket 实时推送 ============
# （parse_time_duration 已移除，因为 PG 时间轴路由已迁移）

# ============ 已迁移路由 ============
# 以下路由已迁移到模块化的 API 路由：
# - GET /api/queues → api/queues.py
# - GET /api/queue/{queue_name}/stats → api/queues.py
# - GET /api/queue/{queue_name}/workers → api/workers.py
# - GET /api/queue/{queue_name}/worker-summary → api/workers.py
# - GET /api/workers/offline-history → api/workers.py
# - GET /api/global-stats → api/overview.py
# - GET /api/global-stats/light → api/overview.py
# ====================================

# GET /api/queue/{queue_name}/workers/offline-history → 已迁移到 api/workers.py


# ============ PostgreSQL 路由已迁移 ============
# 以下路由已迁移到 api/analytics.py：
# - GET /api/pg/tasks → GET /api/v1/analytics/pg/tasks
# - GET /api/pg/stats → GET /api/v1/analytics/pg/stats
# - GET /api/pg/task/{task_id} → GET /api/v1/analytics/pg/task/{task_id}
# ==============================================

if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    uvicorn.run(app, host="0.0.0.0", port=8000)