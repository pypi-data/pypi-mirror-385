"""
Task 模型

对应 tasks 表，用于存储任务消息（实际表结构）
"""
from sqlalchemy import Column, String, Integer, Text, TIMESTAMP, Index
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from typing import Optional, Dict, Any

from ..base import Base


class Task(Base):
    """
    任务消息表

    存储发送到队列的任务消息
    """
    __tablename__ = 'tasks'

    # 主键 - Redis Stream ID
    stream_id = Column(Text, primary_key=True, comment='Redis Stream 事件ID')

    # 队列和命名空间
    queue = Column(Text, nullable=False, comment='队列名称')
    namespace = Column(Text, nullable=False, comment='命名空间')

    # 定时任务关联
    scheduled_task_id = Column(Text, nullable=True, comment='关联的定时任务ID')

    # 消息数据
    payload = Column(JSONB, nullable=False, comment='消息载荷（任务数据）')

    # 优先级
    priority = Column(Integer, nullable=True, comment='优先级（数字越小优先级越高）')

    # 时间戳
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        comment='创建时间'
    )

    # 来源
    source = Column(Text, nullable=False, comment='消息来源（如 scheduler, manual, api）')

    # 元数据
    task_metadata = Column('metadata', JSONB, nullable=True, comment='任务元数据')

    # 索引
    __table_args__ = (
        Index('idx_tasks_queue', 'queue'),
        Index('idx_tasks_namespace', 'namespace'),
        Index('idx_tasks_queue_namespace', 'queue', 'namespace'),
        Index('idx_tasks_scheduled_task_id', 'scheduled_task_id'),
        Index('idx_tasks_created_at', 'created_at'),
        Index('idx_tasks_source', 'source'),
    )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'stream_id': self.stream_id,
            'queue': self.queue,
            'namespace': self.namespace,
            'scheduled_task_id': self.scheduled_task_id,
            'payload': self.payload,
            'priority': self.priority,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'source': self.source,
            'metadata': self.task_metadata,
        }

    def __repr__(self) -> str:
        return f"<Task(stream_id='{self.stream_id}', queue='{self.queue}', namespace='{self.namespace}')>"
