from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime


class SubTaskSubmissionItem(BaseModel):
    name: str = Field(..., description="产出物名称")
    path: str = Field(..., description="文件路径")
    type: Literal['file', 'directory', 'config', 'doc', 'other'] = Field(default='file', description="类型")
    description: str = Field(default="", description="简要说明")
    status: Literal['completed', 'pending'] = Field(default='completed', description="状态")


class SubTaskSubmission(BaseModel):
    items: List[SubTaskSubmissionItem] = Field(default_factory=list, description="产出物列表")
    summary: str = Field(default="", description="提交说明")
    submitted_at: Optional[str] = Field(default=None, description="提交时间")


class SubmissionRequest(BaseModel):
    submission: Optional[SubTaskSubmission] = Field(default=None, description="提交清单")
