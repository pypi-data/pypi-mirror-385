"""
ScheduledTask 和 TaskExecutionHistory 模型

对应 scheduled_tasks 和 task_execution_history 表，用于定时任务调度
"""
from sqlalchemy import (
    Column, BigInteger, String, Integer, Text, Boolean,
    TIMESTAMP, Index, Numeric, ForeignKey
)
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from typing import Optional, Dict, Any, List

from ..base import Base


class ScheduledTask(Base):
    """
    定时任务表

    定时任务以 queue 为核心，定期向指定队列发送消息
    """
    __tablename__ = 'scheduled_tasks'

    # 主键
    id = Column(BigInteger, primary_key=True, autoincrement=True, comment='自增主键')

    # 唯一标识
    scheduler_id = Column(
        String(255),
        nullable=False,
        unique=True,
        comment='任务的唯一标识符（用于去重）'
    )

    # 任务类型
    task_type = Column(
        String(50),
        nullable=False,
        comment='任务类型: cron, interval, once'
    )

    # 任务执行相关
    queue_name = Column(String(100), nullable=False, comment='目标队列名')
    namespace = Column(String(100), default='default', comment='命名空间')
    task_args = Column(JSONB, default=[], comment='任务参数')
    task_kwargs = Column(JSONB, default={}, comment='任务关键字参数')

    # 调度相关
    cron_expression = Column(String(100), comment='cron表达式 (task_type=cron时使用)')
    interval_seconds = Column(Numeric(10, 2), comment='间隔秒数 (task_type=interval时使用)')
    next_run_time = Column(TIMESTAMP(timezone=True), comment='下次执行时间')
    last_run_time = Column(TIMESTAMP(timezone=True), comment='上次执行时间')

    # 状态和控制
    enabled = Column(Boolean, default=True, comment='是否启用')
    max_retries = Column(Integer, default=3, comment='最大重试次数')
    retry_delay = Column(Integer, default=60, comment='重试延迟(秒)')
    timeout = Column(Integer, default=300, comment='任务超时时间(秒)')
    priority = Column(Integer, comment='任务优先级 (1=最高, 数字越大优先级越低，NULL=默认最低)')

    # 元数据 (使用 column name override 避免与 SQLAlchemy 的 metadata 属性冲突)
    description = Column(Text, comment='任务描述')
    tags = Column(JSONB, default=[], comment='标签')
    task_metadata = Column('metadata', JSONB, default={}, comment='额外元数据')

    # 时间戳
    created_at = Column(
        TIMESTAMP(timezone=True),
        default=datetime.utcnow,
        comment='创建时间'
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment='更新时间'
    )

    # 索引
    __table_args__ = (
        Index('idx_scheduled_tasks_next_run', 'next_run_time', postgresql_where=(enabled == True)),  # noqa: E712
        Index('idx_scheduled_tasks_task_type', 'task_type'),
        Index('idx_scheduled_tasks_queue', 'queue_name'),
        Index('idx_scheduled_tasks_enabled', 'enabled'),
        Index('idx_scheduled_tasks_scheduler_id', 'scheduler_id', unique=True),
    )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'scheduler_id': self.scheduler_id,
            'task_type': self.task_type,
            'queue_name': self.queue_name,
            'namespace': self.namespace,
            'task_args': self.task_args,
            'task_kwargs': self.task_kwargs,
            'cron_expression': self.cron_expression,
            'interval_seconds': float(self.interval_seconds) if self.interval_seconds else None,
            'next_run_time': self.next_run_time.isoformat() if self.next_run_time else None,
            'last_run_time': self.last_run_time.isoformat() if self.last_run_time else None,
            'enabled': self.enabled,
            'max_retries': self.max_retries,
            'retry_delay': self.retry_delay,
            'timeout': self.timeout,
            'priority': self.priority,
            'description': self.description,
            'tags': self.tags,
            'metadata': self.task_metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:
        return f"<ScheduledTask(id={self.id}, scheduler_id='{self.scheduler_id}', queue='{self.queue_name}', type='{self.task_type}')>"


class TaskExecutionHistory(Base):
    """
    任务执行历史表

    记录定时任务的执行历史
    """
    __tablename__ = 'task_execution_history'

    # 主键
    id = Column(BigInteger, primary_key=True, autoincrement=True)

    # 关联任务
    task_id = Column(
        BigInteger,
        nullable=False,
        comment='关联的任务ID（外键到 scheduled_tasks.id）'
    )
    event_id = Column(String(255), nullable=False, comment='执行事件ID')

    # 执行信息
    scheduled_time = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        comment='计划执行时间'
    )
    started_at = Column(TIMESTAMP(timezone=True), comment='实际开始时间')
    finished_at = Column(TIMESTAMP(timezone=True), comment='完成时间')

    # 执行结果
    status = Column(
        String(50),
        nullable=False,
        comment='状态: pending, running, success, failed, timeout'
    )
    result = Column(JSONB, comment='执行结果')
    error_message = Column(Text, comment='错误信息')
    retry_count = Column(Integer, default=0, comment='重试次数')

    # 性能指标
    duration_ms = Column(Integer, comment='执行耗时(毫秒)')
    worker_id = Column(String(100), comment='执行的worker ID')

    # 时间戳
    created_at = Column(
        TIMESTAMP(timezone=True),
        default=datetime.utcnow,
        comment='创建时间'
    )

    # 索引
    __table_args__ = (
        Index('idx_task_history_task_id', 'task_id'),
        Index('idx_task_history_event_id', 'event_id'),
        Index('idx_task_history_status', 'status'),
        Index('idx_task_history_scheduled', 'scheduled_time'),
        Index('idx_task_history_created', 'created_at'),
    )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'task_id': self.task_id,
            'event_id': self.event_id,
            'scheduled_time': self.scheduled_time.isoformat() if self.scheduled_time else None,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'finished_at': self.finished_at.isoformat() if self.finished_at else None,
            'status': self.status,
            'result': self.result,
            'error_message': self.error_message,
            'retry_count': self.retry_count,
            'duration_ms': self.duration_ms,
            'worker_id': self.worker_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        return f"<TaskExecutionHistory(id={self.id}, task_id={self.task_id}, event_id='{self.event_id}', status='{self.status}')>"
