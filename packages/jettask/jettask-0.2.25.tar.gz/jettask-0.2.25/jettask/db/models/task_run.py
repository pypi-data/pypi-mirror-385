"""
TaskRun 模型

对应 task_runs 表，用于存储任务执行记录
"""
from sqlalchemy import Column, String, Integer, Text, TIMESTAMP, Float, Index, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from typing import Optional, Dict, Any

from ..base import Base


class TaskRun(Base):
    """
    任务执行记录表

    存储每次任务执行的状态、结果和执行时间等信息
    """
    __tablename__ = 'task_runs'

    # 主键 - Redis Stream ID
    stream_id = Column(Text, primary_key=True, comment='Redis Stream 事件ID，关联到 tasks 表')

    # 执行状态
    status = Column(String(50), nullable=True, comment='任务状态 (pending/running/success/failed/retrying)')

    # 执行结果
    result = Column(JSONB, nullable=True, comment='任务执行结果')
    error = Column(Text, nullable=True, comment='错误信息（如果失败）')

    # 执行时间
    started_at = Column(Float, nullable=True, comment='开始执行时间（Unix 时间戳）')
    completed_at = Column(Float, nullable=True, comment='完成时间（Unix 时间戳）')

    # 重试次数
    retries = Column(Integer, nullable=True, default=0, comment='重试次数')

    # 执行时长（秒）
    duration = Column(Float, nullable=True, comment='执行时长（秒）')

    # 消费者信息
    consumer = Column(Text, nullable=True, comment='执行该任务的消费者ID')

    # 记录创建和更新时间
    created_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        comment='记录创建时间'
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        comment='记录更新时间'
    )

    # 索引
    __table_args__ = (
        Index('idx_task_runs_status', 'status'),
        Index('idx_task_runs_started_at', 'started_at'),
        Index('idx_task_runs_completed_at', 'completed_at'),
        Index('idx_task_runs_created_at', 'created_at'),
    )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'stream_id': self.stream_id,
            'status': self.status,
            'result': self.result,
            'error': self.error,
            'started_at': self.started_at,
            'completed_at': self.completed_at,
            'retries': self.retries,
            'duration': self.duration,
            'consumer': self.consumer,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:
        return f"<TaskRun(stream_id='{self.stream_id}', status='{self.status}')>"
