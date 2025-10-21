"""任务持久化模块

负责解析Redis Stream消息，并将任务数据批量插入PostgreSQL数据库。
"""

import json
import logging
import traceback
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import insert

from jettask.db.models.task import Task

logger = logging.getLogger(__name__)


class TaskPersistence:
    """任务持久化处理器

    职责：
    - 解析Stream消息为任务信息
    - 批量插入任务到PostgreSQL的tasks表
    - 处理插入失败的降级策略
    """

    def __init__(
        self,
        async_session_local: sessionmaker,
        namespace_id: str,
        namespace_name: str
    ):
        """初始化任务持久化处理器

        Args:
            async_session_local: SQLAlchemy会话工厂
            namespace_id: 命名空间ID
            namespace_name: 命名空间名称
        """
        self.AsyncSessionLocal = async_session_local
        self.namespace_id = namespace_id
        self.namespace_name = namespace_name

    def parse_stream_message(self, task_id: str, data: dict) -> Optional[dict]:
        """解析Stream消息为任务信息（返回完整的字段）

        Args:
            task_id: 任务ID（Redis Stream ID）
            data: 消息数据

        Returns:
            解析后的任务信息字典，失败返回None
        """
        try:
            from jettask.utils.serializer import loads_str

            if b'data' in data:
                task_data = loads_str(data[b'data'])
            else:
                task_data = {}
                for k, v in data.items():
                    key = k.decode('utf-8') if isinstance(k, bytes) else k
                    if isinstance(v, bytes):
                        try:
                            value = loads_str(v)
                        except:
                            value = str(v)
                    else:
                        value = v
                    task_data[key] = value

            # 如果配置了命名空间，检查消息是否属于该命名空间
            # if self.namespace_id:
            #     msg_namespace_id = task_data.get('__namespace_id')
            #     # 如果消息没有namespace_id且当前不是默认命名空间，跳过
            #     if msg_namespace_id != self.namespace_id:
            #         if not (msg_namespace_id is None and self.namespace_id == 'default'):
            #             logger.debug(f"Skipping message from different namespace: {msg_namespace_id} != {self.namespace_id}")
            #             return None

            queue_name = task_data['queue']
            task_name = task_data.get('name', task_data.get('task', 'unknown'))

            created_at = None
            if 'trigger_time' in task_data:
                try:
                    timestamp = float(task_data['trigger_time'])
                    created_at = datetime.fromtimestamp(timestamp, tz=timezone.utc)
                except:
                    pass

            # 返回完整的字段，包括所有可能为None的字段
            return {
                'id': task_id,
                'queue_name': queue_name,
                'task_name': task_name,
                'task_data': json.dumps(task_data),
                'priority': int(task_data.get('priority', 0)),
                'retry_count': int(task_data.get('retry', 0)),
                'max_retry': int(task_data.get('max_retry', 3)),
                'status': 'pending',
                'result': None,  # 新任务没有结果
                'error_message': None,  # 新任务没有错误信息
                'created_at': created_at,
                'started_at': None,  # 新任务还未开始
                'completed_at': None,  # 新任务还未完成
                'scheduled_task_id': task_data.get('scheduled_task_id'),  # 调度任务ID
                'metadata': json.dumps(task_data.get('metadata', {})),
                'worker_id': None,  # 新任务还未分配worker
                'execution_time': None,  # 新任务还没有执行时间
                'duration': None,  # 新任务还没有持续时间
                'namespace_id': self.namespace_id  # 添加命名空间ID
            }

        except Exception as e:
            logger.error(f"Error parsing stream message for task {task_id}: {e}")
            logger.error(traceback.format_exc())
            return None

    async def insert_tasks(self, tasks: List[Dict[str, Any]]) -> int:
        """批量插入任务到PostgreSQL（使用ORM）

        Args:
            tasks: 任务信息列表

        Returns:
            实际插入的记录数
        """
        if not tasks:
            return 0

        logger.info(f"Attempting to insert {len(tasks)} tasks to tasks table")

        try:
            async with self.AsyncSessionLocal() as session:
                # 准备tasks表的数据
                tasks_data = []
                for task in tasks:
                    task_data = json.loads(task['task_data'])

                    # 从task_data中获取scheduled_task_id
                    scheduled_task_id = task_data.get('scheduled_task_id') or task.get('scheduled_task_id')

                    # 根据是否有scheduled_task_id来判断任务来源
                    if scheduled_task_id:
                        source = 'scheduler'  # 定时任务
                    else:
                        source = 'redis_stream'  # 普通任务

                    tasks_data.append({
                        'stream_id': task['id'],  # Redis Stream ID作为stream_id
                        'queue': task['queue_name'],
                        'namespace': self.namespace_name,
                        'scheduled_task_id': str(scheduled_task_id) if scheduled_task_id else None,
                        'payload': json.loads(task['task_data']),  # 解析为dict
                        'priority': task['priority'],
                        'created_at': task['created_at'],
                        'source': source,
                        'task_metadata': json.loads(task.get('metadata', '{}'))  # 对应模型的 task_metadata 字段
                    })

                # 批量插入 - 使用 ORM 的 INSERT ON CONFLICT DO NOTHING
                logger.debug(f"Executing batch insert with {len(tasks_data)} tasks")

                try:
                    # 使用 PostgreSQL 的 insert().on_conflict_do_nothing()
                    stmt = insert(Task).values(tasks_data).on_conflict_do_nothing(
                        constraint='tasks_pkey'  # 主键冲突则跳过
                    )

                    await session.execute(stmt)
                    await session.commit()

                    # ORM 的 on_conflict_do_nothing 不返回 rowcount，我们假设全部成功
                    inserted_count = len(tasks_data)
                    logger.debug(f"Tasks table batch insert transaction completed: {inserted_count} tasks")
                    return inserted_count

                except Exception as e:
                    logger.error(f"Error in batch insert, trying fallback: {e}")
                    await session.rollback()

                    # 降级为逐条插入（更稳妥）
                    total_inserted = 0

                    for task_dict in tasks_data:
                        try:
                            stmt = insert(Task).values(**task_dict).on_conflict_do_nothing(
                                constraint='tasks_pkey'
                            )
                            await session.execute(stmt)
                            await session.commit()
                            total_inserted += 1
                        except Exception as single_error:
                            logger.error(f"Failed to insert task {task_dict.get('stream_id')}: {single_error}")
                            await session.rollback()

                    if total_inserted > 0:
                        logger.info(f"Fallback insert completed: {total_inserted} tasks inserted")
                    else:
                        logger.info(f"No new tasks inserted in fallback mode")

                    return total_inserted

        except Exception as e:
            logger.error(f"Error inserting tasks to PostgreSQL: {e}")
            logger.error(traceback.format_exc())
            return 0

    async def batch_insert_tasks(self, tasks: List[Dict[str, Any]]) -> int:
        """批量插入任务（兼容 buffer.py 调用接口）

        Args:
            tasks: 任务记录列表

        Returns:
            实际插入的记录数
        """
        if not tasks:
            return 0

        logger.info(f"[BATCH INSERT] 批量插入 {len(tasks)} 条任务...")

        try:
            async with self.AsyncSessionLocal() as session:
                # 准备 ORM 数据
                insert_data = []
                for record in tasks:
                    # record 是从 consumer.py 传入的格式
                    insert_data.append({
                        'stream_id': record['stream_id'],
                        'queue': record['queue'],
                        'namespace': record['namespace'],
                        'scheduled_task_id': record.get('scheduled_task_id'),
                        'payload': record.get('payload', {}),
                        'priority': record.get('priority', 0),
                        'created_at': record.get('created_at'),
                        'source': record.get('source', 'redis_stream'),
                        'task_metadata': record.get('metadata', {})
                    })

                # 批量插入 - 使用 PostgreSQL 的 INSERT ON CONFLICT DO NOTHING
                # 使用约束名称而不是列名
                stmt = insert(Task).values(insert_data).on_conflict_do_nothing(
                    constraint='tasks_pkey'
                )

                await session.execute(stmt)
                await session.commit()

                logger.info(f"[BATCH INSERT] ✓ 成功插入 {len(insert_data)} 条任务")
                return len(insert_data)

        except Exception as e:
            logger.error(f"[BATCH INSERT] ✗ 批量插入失败: {e}", exc_info=True)
            return 0

    async def batch_update_tasks(self, updates: List[Dict[str, Any]]) -> int:
        """批量更新任务执行状态到 task_runs 表

        使用 PostgreSQL 的 INSERT ... ON CONFLICT DO UPDATE 实现 UPSERT 操作，
        如果记录存在则更新，不存在则插入。

        Args:
            updates: 更新记录列表，每条记录包含：
                - stream_id: Redis Stream ID（主键）
                - status: 任务状态
                - result: 执行结果
                - error: 错误信息
                - started_at: 开始时间
                - completed_at: 完成时间
                - retries: 重试次数

        Returns:
            实际更新的记录数
        """
        if not updates:
            return 0

        logger.info(f"[BATCH UPDATE] 批量更新 {len(updates)} 条任务状态...")
        logger.info(f"[BATCH UPDATE] 更新记录示例: {updates[0] if updates else 'N/A'}")

        try:
            from sqlalchemy.dialects.postgresql import insert
            from ..db.models import TaskRun
            from ..utils.serializer import loads_str
            from datetime import datetime, timezone

            # 对相同 stream_id 的记录进行去重，保留最新的
            # 使用字典，key 是 stream_id，value 是记录（后面的会覆盖前面的）
            deduplicated = {}
            for record in updates:
                stream_id = record['stream_id']
                deduplicated[stream_id] = record

            # 转换回列表
            unique_updates = list(deduplicated.values())

            if len(unique_updates) < len(updates):
                logger.info(
                    f"[BATCH UPDATE] 去重: {len(updates)} 条 → {len(unique_updates)} 条 "
                    f"(合并了 {len(updates) - len(unique_updates)} 条重复记录)"
                )

            async with self.AsyncSessionLocal() as session:
                # 准备 UPSERT 数据
                upsert_data = []
                for record in unique_updates:
                    logger.debug(f"处理记录: {record}")
                    # 解析 result 字段（如果是序列化的字符串）
                    result = record.get('result')
                    if result and isinstance(result, bytes):
                        try:
                            result = loads_str(result)
                        except Exception:
                            result = result.decode('utf-8') if isinstance(result, bytes) else result

                    # 解析 error 字段
                    error = record.get('error')
                    if error and isinstance(error, bytes):
                        error = error.decode('utf-8')

                    # 计算执行时长
                    duration = None
                    started_at = record.get('started_at')
                    completed_at = record.get('completed_at')
                    if started_at and completed_at:
                        duration = completed_at - started_at

                    # 解析 status 字段
                    status = record.get('status')
                    if status and isinstance(status, bytes):
                        status = status.decode('utf-8')

                    # 解析 consumer 字段
                    consumer = record.get('consumer')
                    if consumer and isinstance(consumer, bytes):
                        consumer = consumer.decode('utf-8')

                    upsert_record = {
                        'stream_id': record['stream_id'],
                        'status': status,
                        'result': result,
                        'error': error,
                        'started_at': started_at,
                        'completed_at': completed_at,
                        'retries': record.get('retries', 0),
                        'duration': duration,
                        'consumer': consumer,
                        'updated_at': datetime.now(timezone.utc),
                    }
                    logger.debug(f"upsert_record: {upsert_record}")
                    upsert_data.append(upsert_record)

                logger.info(f"[BATCH UPDATE] 准备写入 {len(upsert_data)} 条记录")

                # 批量 UPSERT - 如果存在则更新，不存在则插入
                stmt = insert(TaskRun).values(upsert_data)

                # 定义冲突时的更新策略
                # 使用 COALESCE 避免用 NULL 覆盖已有数据
                from sqlalchemy import func
                stmt = stmt.on_conflict_do_update(
                    constraint='task_runs_pkey',
                    set_={
                        # status 总是更新（状态变化）
                        'status': stmt.excluded.status,
                        # 其他字段：如果新值不是 NULL，则更新；否则保留旧值
                        'result': func.coalesce(stmt.excluded.result, TaskRun.result),
                        'error': func.coalesce(stmt.excluded.error, TaskRun.error),
                        'started_at': func.coalesce(stmt.excluded.started_at, TaskRun.started_at),
                        'completed_at': func.coalesce(stmt.excluded.completed_at, TaskRun.completed_at),
                        'retries': func.coalesce(stmt.excluded.retries, TaskRun.retries),
                        'duration': func.coalesce(stmt.excluded.duration, TaskRun.duration),
                        'consumer': func.coalesce(stmt.excluded.consumer, TaskRun.consumer),
                        # updated_at 总是更新
                        'updated_at': stmt.excluded.updated_at,
                    }
                )

                await session.execute(stmt)
                await session.commit()

                logger.info(f"[BATCH UPDATE] ✓ 成功更新 {len(upsert_data)} 条任务状态")
                return len(upsert_data)

        except Exception as e:
            logger.error(f"[BATCH UPDATE] ✗ 批量更新失败: {e}", exc_info=True)
            return 0
