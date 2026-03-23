"""
Team Space 数据模型
"""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, DateTime, Index, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Team(Base):
    """团队"""
    __tablename__ = "team"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False, unique=True, comment="团队名称")
    description = Column(Text, default="", comment="团队描述")
    status = Column(String(20), default="active", index=True, comment="状态: active/disabled")
    team_task_id = Column(String(36), nullable=True, index=True, comment="团队初始化任务ID")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系
    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")
    profile = relationship("TeamProfile", back_populates="team", uselist=False, cascade="all, delete-orphan")


class TeamMember(Base):
    """团队成员"""
    __tablename__ = "team_member"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    team_id = Column(String(36), ForeignKey("team.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_id = Column(String(36), nullable=False, index=True)
    self_introduction = Column(Text, default=None, comment="自我介绍内容，NULL 表示未完成")
    added_at = Column(DateTime, default=datetime.now, comment="加入时间")

    # 联合唯一索引
    __table_args__ = (
        Index("ix_team_member_team_agent", "team_id", "agent_id", unique=True),
    )

    # 关系
    team = relationship("Team", back_populates="members")


class TeamProfile(Base):
    """团队介绍文件"""
    __tablename__ = "team_profile"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    team_id = Column(String(36), ForeignKey("team.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    content = Column(Text, default="", comment="完整的团队介绍 markdown")
    version = Column(Integer, default=1, comment="版本号，每次更新 +1")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    # 关系
    team = relationship("Team", back_populates="profile")


class TeamProfileTemplate(Base):
    """介绍生成模板"""
    __tablename__ = "team_profile_template"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    content = Column(Text, nullable=False, default="", comment="jinja2 模板")
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")

    @staticmethod
    def get_default_template() -> str:
        """获取默认模板"""
        return """# {{team_name}} 团队介绍

## 团队简介
{{team_description}}

## 团队成员
{{members}}

## 加入我们
如需与本团队合作，请联系团队负责人。
"""
