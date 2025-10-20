"""批量缓冲区管理器

负责收集任务数据和ACK信息，批量写入数据库并ACK。
支持 INSERT 和 UPDATE 两种操作类型。
"""

import time
import asyncio
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class BatchBuffer:
    """批量缓冲区管理器

    负责：
    1. 收集任务数据和ACK信息
    2. 判断是否应该刷新（批量大小或超时）
    3. 批量写入数据库并ACK
    """

    def __init__(
        self,
        max_size: int = 1000,
        max_delay: float = 5.0,
        operation_type: str = 'insert'  # 'insert' 或 'update'
    ):
        """初始化缓冲区

        Args:
            max_size: 缓冲区最大容量（条数）
            max_delay: 最大延迟时间（秒）
            operation_type: 操作类型，'insert' 或 'update'
        """
        self.max_size = max_size
        self.max_delay = max_delay
        self.operation_type = operation_type

        # 任务数据缓冲区
        self.records: List[Dict[str, Any]] = []
        self.contexts: List[Any] = []  # 保存 TaskContext 用于 ACK

        # 刷新控制
        self.last_flush_time = time.time()
        self.flush_lock = asyncio.Lock()

        # 统计信息
        self.total_flushed = 0
        self.flush_count = 0

    def add(self, record: dict, context: Any = None):
        """添加到缓冲区

        Args:
            record: 任务数据或更新数据
            context: TaskContext（用于 ACK）
        """
        self.records.append(record)
        if context:
            self.contexts.append(context)

    def should_flush(self) -> bool:
        """判断是否应该刷新

        Returns:
            是否需要刷新
        """
        if not self.records:
            return False

        # 缓冲区满了
        if len(self.records) >= self.max_size:
            logger.info(
                f"[{self.operation_type.upper()}] 缓冲区已满 "
                f"({len(self.records)}/{self.max_size})，触发刷新"
            )
            return True

        # 超时了
        elapsed = time.time() - self.last_flush_time
        if elapsed >= self.max_delay:
            logger.info(
                f"[{self.operation_type.upper()}] 缓冲区超时 "
                f"({elapsed:.1f}s >= {self.max_delay}s)，触发刷新"
            )
            return True

        return False

    async def flush(self, db_manager):
        """刷新缓冲区到数据库

        1. 批量写入数据库
        2. 批量ACK（如果有context）
        3. 清空缓冲区

        Args:
            db_manager: 数据库管理器，需要有 batch_insert_tasks 或 batch_update_tasks 方法
        """
        async with self.flush_lock:
            if not self.records:
                return 0

            count = len(self.records)
            start_time = time.time()

            try:
                logger.info(f"[{self.operation_type.upper()}] 开始批量刷新 {count} 条记录...")

                # 1. 批量写入数据库
                if self.operation_type == 'insert':
                    await db_manager.batch_insert_tasks(self.records)
                    logger.info(f"  ✓ 批量插入 {count} 条任务记录")
                else:  # update
                    print(f'{self.records=}')
                    await db_manager.batch_update_tasks(self.records)
                    logger.info(f"  ✓ 批量更新 {count} 条任务状态")

                # 2. 批量ACK（如果使用 Jettask 的 context）
                if self.contexts:
                    for ctx in self.contexts:
                        if hasattr(ctx, 'ack'):
                            await ctx.ack()
                    logger.info(f"  ✓ 批量确认 {len(self.contexts)} 条消息")

                # 3. 清空缓冲区
                self.records.clear()
                self.contexts.clear()
                self.last_flush_time = time.time()

                # 4. 统计
                self.total_flushed += count
                self.flush_count += 1
                elapsed = time.time() - start_time

                logger.info(
                    f"[{self.operation_type.upper()}] ✓ 批量刷新完成! "
                    f"本次: {count}条, "
                    f"耗时: {elapsed:.3f}s, "
                    f"总计: {self.total_flushed}条 ({self.flush_count}次刷新)"
                )

                return count

            except Exception as e:
                logger.error(
                    f"[{self.operation_type.upper()}] ✗ 批量刷新失败: {e}",
                    exc_info=True
                )
                # 失败时清空缓冲区，避免无限重试
                self.records.clear()
                self.contexts.clear()
                raise

    def get_stats(self) -> dict:
        """获取统计信息

        Returns:
            统计信息字典
        """
        return {
            'operation_type': self.operation_type,
            'current_size': len(self.records),
            'max_size': self.max_size,
            'total_flushed': self.total_flushed,
            'flush_count': self.flush_count,
            'avg_per_flush': self.total_flushed // self.flush_count if self.flush_count > 0 else 0
        }
