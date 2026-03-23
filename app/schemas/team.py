"""
Team Space 请求/响应模型
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ============================================================
# Admin API - 请求模型
# ============================================================

class AdminTeamCreateRequest(BaseModel):
    """创建团队请求"""
    name: str = Field(..., description="团队名称", max_length=100)
    description: str = Field("", description="团队描述")


class AdminTeamUpdateRequest(BaseModel):
    """更新团队请求"""
    name: Optional[str] = Field(None, description="团队名称", max_length=100)
    description: Optional[str] = Field(None, description="团队描述")
    status: Optional[str] = Field(None, description="状态: active/disabled")


class AdminTeamMemberAddRequest(BaseModel):
    """添加成员请求"""
    agent_id: str = Field(..., description="Agent ID")


# ============================================================
# Admin API - 响应模型
# ============================================================

class AdminTeamMemberItem(BaseModel):
    """团队成员（管理员视图）"""
    id: str
    agent_id: str
    agent_name: str
    role: str
    self_introduction: Optional[str]
    added_at: datetime

    class Config:
        from_attributes = True


class AdminTeamDetail(BaseModel):
    """团队详情（管理员视图）"""
    id: str
    name: str
    description: str
    status: str
    member_count: int
    members: List[AdminTeamMemberItem]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AdminTeamItem(BaseModel):
    """团队列表项（管理员视图）"""
    id: str
    name: str
    description: str
    status: str
    member_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AdminTeamPageResponse(BaseModel):
    """团队分页响应"""
    items: List[AdminTeamItem] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 20
    total_pages: int = 1


# ============================================================
# Agent API - 响应模型
# ============================================================

class AgentTeamInfo(BaseModel):
    """Agent 视角的团队信息"""
    id: str
    name: str
    description: str
    status: str

    class Config:
        from_attributes = True


class AgentTeamIntroRequest(BaseModel):
    """Agent 提交自我介绍请求"""
    self_introduction: str = Field(..., description="自我介绍内容")


class AgentTeamProfileResponse(BaseModel):
    """团队介绍响应"""
    content: str
    version: int
    updated_at: datetime
