"""
业务逻辑服务层
包含所有业务逻辑处理
"""

from .overview_service import OverviewService
from .queue_service import QueueService
from .scheduled_task_service import ScheduledTaskService
from .alert_service import AlertService
from .analytics_service import AnalyticsService
from .settings_service import SettingsService
from .task_service import TaskService

# 监控服务
from .redis_monitor_service import RedisMonitorService
from .task_monitor_service import TaskMonitorService
from .worker_monitor_service import WorkerMonitorService
from .queue_monitor_service import QueueMonitorService
from .heartbeat_service import HeartbeatService
from .timeline_service import TimelineService
from .timeline_pg_service import TimelinePgService


class MonitorService:
    """
    统一的监控服务类

    整合所有监控服务，提供统一的接口
    """

    def __init__(self, redis_url: str = "redis://localhost:6379", redis_prefix: str = "jettask"):
        """
        初始化监控服务

        Args:
            redis_url: Redis 连接 URL
            redis_prefix: Redis 键前缀
        """
        # 创建基础 Redis 服务
        self.redis_service = RedisMonitorService(redis_url, redis_prefix)

        # 创建各个子服务
        self.task_service = TaskMonitorService(self.redis_service)
        self.worker_service = WorkerMonitorService(self.redis_service)
        self.queue_service = QueueMonitorService(self.redis_service)
        self.heartbeat_service = HeartbeatService(self.redis_service)
        self.timeline_service = TimelineService(self.redis_service)

    async def connect(self):
        """连接到 Redis"""
        await self.redis_service.connect()

    async def close(self):
        """关闭所有服务"""
        # 停止心跳扫描器
        await self.heartbeat_service.stop_heartbeat_scanner()
        # 关闭 Redis 连接
        await self.redis_service.close()

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器退出"""
        await self.close()

    # ==================== Task Monitor Methods ====================

    async def get_task_info(self, stream_id: str, queue_name: str):
        """获取单个任务的详细信息"""
        return await self.task_service.get_task_info(stream_id, queue_name)

    async def get_stream_info(self, queue_name: str):
        """获取 Stream 的统计信息"""
        return await self.task_service.get_stream_info(queue_name)

    async def get_queue_tasks(self, queue_name: str, start: str = "-", end: str = "+", count: int = 100, reverse: bool = False):
        """获取队列中的任务列表"""
        return await self.task_service.get_queue_tasks(queue_name, start, end, count, reverse)

    # ==================== Worker Monitor Methods ====================

    async def get_worker_heartbeats(self, queue_name: str):
        """获取指定队列的 Worker 心跳信息"""
        return await self.worker_service.get_worker_heartbeats(queue_name)

    async def get_queue_worker_summary(self, queue_name: str):
        """获取队列的 Worker 汇总统计信息（包含历史数据）"""
        return await self.worker_service.get_queue_worker_summary(queue_name)

    async def get_queue_worker_summary_fast(self, queue_name: str):
        """获取队列的 Worker 汇总统计信息（快速版，仅在线 Worker）"""
        return await self.worker_service.get_queue_worker_summary_fast(queue_name)

    async def get_worker_offline_history(self, limit: int = 100, start_time=None, end_time=None):
        """获取 Worker 下线历史记录"""
        return await self.worker_service.get_worker_offline_history(limit, start_time, end_time)

    # ==================== Queue Monitor Methods ====================

    async def get_all_queues(self):
        """获取所有队列名称"""
        return await self.queue_service.get_all_queues()

    async def get_queue_stats(self, queue_name: str):
        """获取队列统计信息（RabbitMQ 兼容格式）"""
        return await self.queue_service.get_queue_stats(queue_name)

    # ==================== Heartbeat Service Methods ====================

    async def start_heartbeat_scanner(self):
        """启动心跳扫描器"""
        await self.heartbeat_service.start_heartbeat_scanner()

    async def stop_heartbeat_scanner(self):
        """停止心跳扫描器"""
        await self.heartbeat_service.stop_heartbeat_scanner()

    async def check_worker_heartbeat(self, worker_id: str):
        """检查单个 Worker 的心跳状态"""
        return await self.heartbeat_service.check_worker_heartbeat(worker_id)

    async def get_heartbeat_stats(self):
        """获取心跳监控统计信息"""
        return await self.heartbeat_service.get_heartbeat_stats()

    # ==================== Timeline Service Methods ====================

    async def get_redis_timeline(self, queue_name: str, **kwargs):
        """获取 Redis Stream 时间轴数据"""
        return await self.timeline_service.get_redis_timeline(queue_name, **kwargs)

    # ==================== Utility Methods ====================

    def get_prefixed_queue_name(self, queue_name: str) -> str:
        """为队列名称添加前缀"""
        return self.redis_service.get_prefixed_queue_name(queue_name)

    @property
    def redis(self):
        """获取 Redis 客户端"""
        return self.redis_service.redis

    @property
    def redis_prefix(self) -> str:
        """获取 Redis 前缀"""
        return self.redis_service.redis_prefix


__all__ = [
    'OverviewService',
    'QueueService',
    'ScheduledTaskService',
    'AlertService',
    'AnalyticsService',
    'SettingsService',
    'TaskService',
    'MonitorService',
    'RedisMonitorService',
    'TaskMonitorService',
    'WorkerMonitorService',
    'QueueMonitorService',
    'HeartbeatService',
    'TimelineService',
    'TimelinePgService',
]