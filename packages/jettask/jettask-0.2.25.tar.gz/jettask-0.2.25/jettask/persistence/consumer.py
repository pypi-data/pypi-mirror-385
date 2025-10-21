"""PostgreSQL Consumer - 基于通配符队列的新实现

完全替换旧的 consumer.py 实现，使用 Jettask 通配符队列功能。
"""

import time
import logging
from datetime import datetime, timezone

from jettask import Jettask
from jettask.core.context import TaskContext
from jettask.db.connector import get_pg_engine_and_factory, DBConfig
from .buffer import BatchBuffer
from .persistence import TaskPersistence

logger = logging.getLogger(__name__)


class PostgreSQLConsumer:
    """PostgreSQL Consumer - 基于通配符队列

    核心特性：
    1. 使用 @app.task(queue='*') 监听所有队列
    2. 使用 @app.task(queue='TASK_CHANGES') 处理状态更新
    3. 批量 INSERT 和 UPDATE
    4. 自动队列发现（Jettask 内置）
    """

    def __init__(
        self,
        pg_config,  # 可以是字典或配置对象
        redis_config,  # 可以是字典或配置对象
        prefix: str = "jettask",
        namespace_id: str = None,
        namespace_name: str = None,
        batch_size: int = 1000,
        flush_interval: float = 5.0
    ):
        """初始化 PG Consumer

        Args:
            pg_config: PostgreSQL配置（字典或对象）
            redis_config: Redis配置（字典或对象）
            prefix: Redis键前缀
            node_id: 节点ID（兼容旧接口，不使用）
            namespace_id: 命名空间ID
            namespace_name: 命名空间名称
            enable_backlog_monitor: 是否启用积压监控（兼容旧接口，不使用）
            backlog_monitor_interval: 积压监控间隔（兼容旧接口，不使用）
            batch_size: 批量大小
            flush_interval: 刷新间隔（秒）
        """
        self.pg_config = pg_config
        self.redis_config = redis_config
        self.redis_prefix = prefix
        self.namespace_id = namespace_id
        self.namespace_name = namespace_name or "default"

        # 构建 Redis URL（兼容字典和对象两种格式）
        if isinstance(redis_config, dict):
            # 字典格式 - 优先使用 'url' 字段
            redis_url = redis_config.get('url') or redis_config.get('redis_url')
            if not redis_url:
                # 从独立字段构建
                password = redis_config.get('password', '')
                host = redis_config.get('host', 'localhost')
                port = redis_config.get('port', 6379)
                db = redis_config.get('db', 0)
                redis_url = f"redis://"
                if password:
                    redis_url += f":{password}@"
                redis_url += f"{host}:{port}/{db}"
        else:
            # 对象格式
            redis_url = f"redis://"
            if hasattr(redis_config, 'password') and redis_config.password:
                redis_url += f":{redis_config.password}@"
            redis_url += f"{redis_config.host}:{redis_config.port}/{redis_config.db}"

        self.redis_url = redis_url
        logger.debug(f"构建 Redis URL: {redis_url}")

        # 数据库引擎和会话（将在 start 时初始化）
        self.async_engine = None
        self.AsyncSessionLocal = None
        self.db_manager = None

        # 创建 Jettask 应用
        self.app = Jettask(
            redis_url=redis_url,
            redis_prefix=prefix
        )

        # 创建两个独立的批量缓冲区
        # 1. INSERT 缓冲区（用于新任务持久化）
        self.insert_buffer = BatchBuffer(
            max_size=batch_size,
            max_delay=flush_interval,
            operation_type='insert'
        )

        # 2. UPDATE 缓冲区（用于任务状态更新）
        self.update_buffer = BatchBuffer(
            max_size=batch_size // 2,  # 状态更新通常更频繁，用较小的批次
            max_delay=flush_interval,
            operation_type='update'
        )

        # 注册任务
        self._register_tasks()

        # 运行控制
        self._running = False

    def _register_tasks(self):
        """注册任务处理器"""
        # 创建闭包函数来访问实例属性
        consumer = self  # 捕获 self 引用

        @self.app.task(queue='*', auto_ack=False)
        async def _handle_persist_task(ctx: TaskContext, **kwargs):
            return await consumer._do_handle_persist_task(ctx, **kwargs)

        @self.app.task(queue='TASK_CHANGES', auto_ack=False)
        async def _handle_status_update(ctx: TaskContext, **kwargs):
            print(f'[PG Consumer] 处理状态更新: {ctx.event_id} {kwargs=}')
            return await consumer._do_handle_status_update(ctx, **kwargs)

    async def _do_handle_persist_task(self, ctx: TaskContext, **kwargs):
        """处理任务持久化（INSERT）

        使用通配符 queue='*' 监听所有队列
        Jettask 会自动发现新队列并开始消费

        Args:
            ctx: Jettask 自动注入的任务上下文（包含 queue, event_id 等）
            **kwargs: 任务的原始数据字段
        """
        # 跳过 TASK_CHANGES 队列（由另一个任务处理）
        if ctx.queue == f'{self.redis_prefix}:QUEUE:TASK_CHANGES':
            await ctx.ack()
            return

        try:
            # 提取纯队列名（去掉 prefix:QUEUE: 前缀）
            queue_name = ctx.queue.replace(f'{self.redis_prefix}:QUEUE:', '')

            # 记录真实的队列名称（用于验证通配符队列功能）
            logger.info(f"[持久化任务] 完整路径: {ctx.queue}, 队列名: {queue_name}, Stream ID: {ctx.event_id}")

            # 构建任务记录
            trigger_time = kwargs.get('trigger_time', time.time())
            if isinstance(trigger_time, (str, bytes)):
                trigger_time = float(trigger_time)

            priority = kwargs.get('priority', 0)
            if isinstance(priority, (str, bytes)):
                priority = int(priority)

            record = {
                'stream_id': ctx.event_id,
                'queue': ctx.queue.replace(f'{self.redis_prefix}:QUEUE:', ''),
                'task_name': kwargs.get('task_name', 'unknown'),
                'payload': kwargs.get('payload', {}),
                'priority': priority,
                'created_at': datetime.fromtimestamp(trigger_time, tz=timezone.utc),
                'scheduled_task_id': kwargs.get('scheduled_task_id'),
                'namespace': self.namespace_name,
                'source': 'scheduler' if kwargs.get('scheduled_task_id') else 'redis_stream',
            }

            # 添加到缓冲区（不立即处理，不立即 ACK）
            self.insert_buffer.add(record, ctx)

            # 检查是否需要刷新（批量大小或超时）
            if self.insert_buffer.should_flush():
                await self.insert_buffer.flush(self.db_manager)

            # 同时检查 UPDATE 缓冲区是否需要刷新（利用这次机会）
            if self.update_buffer.should_flush():
                await self.update_buffer.flush(self.db_manager)

        except Exception as e:
            logger.error(f"持久化任务失败: {e}", exc_info=True)
            # 出错也要 ACK，避免消息堆积
            await ctx.ack()

    async def _do_handle_status_update(self, ctx: TaskContext, **kwargs):
        """处理任务状态更新（UPDATE）

        消费 TASK_CHANGES 队列，批量更新数据库中的任务状态

        Args:
            ctx: Jettask 自动注入的任务上下文
            **kwargs: 任务的原始数据字段（包含 task_id）
        """
        try:
            # 从消息中获取 task_id
            task_id = kwargs.get('task_id')
            if not task_id:
                logger.warning(f"TASK_CHANGES 消息缺少 task_id: {ctx.event_id}")
                await ctx.ack()
                return

            # 从 Redis Hash 中读取完整的任务状态信息
            # task_id 格式: test5:TASK:event_id:queue:task_name
            # 我们需要查询 Redis Hash 获取状态信息
            redis_client = ctx.app.async_binary_redis
            # 查询任务状态 Hash
            task_info = await redis_client.hgetall(task_id)
            logger.info(f"task_id={task_id!r}")
            logger.info(f"task_info={task_info!r}")
            if not task_info:
                logger.warning(f"无法找到任务状态信息: {task_id}")
                await ctx.ack()
                return

            # 从 task_id 中提取 event_id (stream_id)
            # task_id 格式: prefix:TASK:event_id:queue:task_name
            parts = task_id.split(':')
            if len(parts) >= 3:
                event_id = parts[2]  # 提取 event_id
            else:
                logger.error(f"无效的 task_id 格式: {task_id}")
                await ctx.ack()
                return

            # 解析各个字段（binary redis 返回 bytes）
            # 1. retries
            retries = task_info.get(b'retries', 0)
            if isinstance(retries, bytes):
                retries = int(retries.decode('utf-8')) if retries else 0
            elif isinstance(retries, str):
                retries = int(retries) if retries else 0

            # 2. started_at
            started_at = task_info.get(b'started_at')
            if started_at:
                if isinstance(started_at, bytes):
                    started_at = float(started_at.decode('utf-8'))
                elif isinstance(started_at, str):
                    started_at = float(started_at)

            # 3. completed_at
            completed_at = task_info.get(b'completed_at')
            if completed_at:
                if isinstance(completed_at, bytes):
                    completed_at = float(completed_at.decode('utf-8'))
                elif isinstance(completed_at, str):
                    completed_at = float(completed_at)

            # 4. consumer
            consumer = task_info.get(b'consumer')
            if consumer:
                if isinstance(consumer, bytes):
                    consumer = consumer.decode('utf-8')

            # 5. status
            status = task_info.get(b'status')
            if status:
                if isinstance(status, bytes):
                    status = status.decode('utf-8')

            # 6. result (保持原始 bytes，在 persistence.py 中解析)
            result = task_info.get(b'result')

            # 7. error/exception
            error = task_info.get(b'exception') or task_info.get(b'error')

            update_record = {
                'stream_id': event_id,
                'status': status,
                'result': result,  # bytes 格式，稍后解析
                'error': error,
                'started_at': started_at,
                'completed_at': completed_at,
                'retries': retries,
                'consumer': consumer,
            }

            logger.info(f"update_record={update_record!r}")

            print(f'{update_record=}')
            # 添加到状态更新缓冲区
            self.update_buffer.add(update_record, ctx)

            # 检查是否需要刷新（批量大小或超时）
            if self.update_buffer.should_flush():
                await self.update_buffer.flush(self.db_manager)

            # 同时检查 INSERT 缓冲区是否需要刷新（利用这次机会）
            if self.insert_buffer.should_flush():
                await self.insert_buffer.flush(self.db_manager)

        except Exception as e:
            logger.error(f"更新任务状态失败: {e}", exc_info=True)
            # 出错也要 ACK
            await ctx.ack()

    async def start(self, concurrency: int = 4):
        """启动 Consumer

        Args:
            concurrency: 并发数
        """
        logger.info(f"Starting PostgreSQL consumer (wildcard queue mode)")
        logger.info(f"Namespace: {self.namespace_name} ({self.namespace_id or 'N/A'})")

        # 1. 使用 connector.py 统一管理数据库连接
        # 解析 PostgreSQL 配置为标准 DSN
        dsn = DBConfig.parse_pg_config(self.pg_config)

        # 使用全局单例引擎和会话工厂
        self.async_engine, self.AsyncSessionLocal = get_pg_engine_and_factory(
            dsn,
            pool_size=50,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=300,
            echo=False
        )

        logger.debug(f"使用全局 PostgreSQL 连接池: {dsn[:50]}...")

        # 2. 初始化任务持久化管理器
        self.db_manager = TaskPersistence(
            async_session_local=self.AsyncSessionLocal,
            namespace_id=self.namespace_id,
            namespace_name=self.namespace_name
        )

        # 3. 设置运行状态
        self._running = True

        # 注意：不在主进程启动定时刷新任务，因为缓冲区在子进程中
        # 刷新逻辑已集成到任务处理函数中（每次处理任务时都会检查是否需要刷新）

        # 启动 Worker（使用通配符队列）
        logger.info("=" * 60)
        logger.info(f"启动 PG Consumer (通配符队列模式)")
        logger.info("=" * 60)
        logger.info(f"命名空间: {self.namespace_name} ({self.namespace_id or 'N/A'})")
        logger.info(f"监听队列: * (所有队列) + TASK_CHANGES (状态更新)")
        logger.info(f"INSERT 批量: {self.insert_buffer.max_size} 条")
        logger.info(f"UPDATE 批量: {self.update_buffer.max_size} 条")
        logger.info(f"刷新间隔: {self.insert_buffer.max_delay} 秒")
        logger.info(f"并发数: {concurrency}")
        logger.info("=" * 60)

        try:
            # 启动 Worker
            # 需要同时监听两个队列：
            # 1. '*' - 通配符匹配所有常规任务队列（INSERT）
            # 2. 'TASK_CHANGES' - 专门的状态更新队列（UPDATE）
            await self.app.start(
                queues=['*', 'TASK_CHANGES'],  # 🎯 关键：监听所有队列 + 状态更新队列
                concurrency=concurrency
            )
        finally:
            await self.stop()

    async def stop(self):
        """停止 Consumer"""
        logger.info("停止 PG Consumer...")
        self._running = False

        # 注意：定时刷新任务已移除，刷新逻辑集成在任务处理中

        # 最后刷新一次缓冲区
        try:
            if self.insert_buffer.records:
                await self.insert_buffer.flush(self.db_manager)
            if self.update_buffer.records:
                await self.update_buffer.flush(self.db_manager)
        except Exception as e:
            logger.error(f"最终刷新失败: {e}")

        # 注意：不关闭数据库引擎，因为它是全局单例，由 connector.py 管理
        # 多个 consumer 实例可能共享同一个引擎

        # 打印统计信息
        insert_stats = self.insert_buffer.get_stats()
        update_stats = self.update_buffer.get_stats()

        logger.info("=" * 60)
        logger.info("PG Consumer 统计信息")
        logger.info("=" * 60)
        logger.info(f"INSERT: 总计 {insert_stats['total_flushed']} 条, "
                   f"刷新 {insert_stats['flush_count']} 次, "
                   f"平均 {insert_stats['avg_per_flush']} 条/次")
        logger.info(f"UPDATE: 总计 {update_stats['total_flushed']} 条, "
                   f"刷新 {update_stats['flush_count']} 次, "
                   f"平均 {update_stats['avg_per_flush']} 条/次")
        logger.info("=" * 60)

        logger.info("PG Consumer 已停止")
