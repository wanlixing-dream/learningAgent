# core/memory_schema.py
"""多范围长期记忆 Schema"""

import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, List, Optional

VALID_MEMORY_TYPES = {
    "fact",
    "preference",
    "weakness",
    "milestone",
    "misconception",
    "resource",
    "session_summary",
}


@dataclass
class MemoryRecord:
    """
    长期记忆条目

    Fields:
        id: 唯一标识
        user_id: 用户 ID
        domain: 学习领域
        session_id: 关联会话 ID
        agent_id: 创建该条目的 Agent
        memory_type: 类型 (fact / preference / weakness / ...)
        content: 记忆内容
        entities: 提取的实体列表
        importance: 重要性 (0.0 ~ 1.0)
        confidence: 置信度 (0.0 ~ 1.0)
        source: 来源（如 add_knowledge / vibe_quiz）
        metadata: 额外元数据
        created_at: 创建时间 ISO 格式
        updated_at: 更新时间 ISO 格式
        access_count: 访问次数
    """

    content: str
    domain: str
    memory_type: str
    user_id: str = "default"
    session_id: Optional[str] = None
    agent_id: str = ""
    id: str = field(default_factory=lambda: f"mem_{uuid.uuid4().hex[:12]}")
    entities: List[str] = field(default_factory=list)
    importance: float = 0.5
    confidence: float = 0.5
    source: str = ""
    metadata: Dict = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    access_count: int = 0

    def __post_init__(self):
        # 校验 memory_type
        if self.memory_type not in VALID_MEMORY_TYPES:
            raise ValueError(
                f"Invalid memory_type '{self.memory_type}'. "
                f"Must be one of: {sorted(VALID_MEMORY_TYPES)}"
            )
        # 钳位 importance 和 confidence
        self.importance = max(0.0, min(1.0, self.importance))
        self.confidence = max(0.0, min(1.0, self.confidence))

    def to_dict(self) -> dict:
        """序列化为字典"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "MemoryRecord":
        """从字典反序列化"""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    def touch(self) -> None:
        """更新访问计数和时间"""
        self.access_count += 1
        self.updated_at = datetime.now().isoformat()
