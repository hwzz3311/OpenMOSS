"""
Agent 端点 - 团队相关
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.auth.dependencies import get_current_agent
from app.models.agent import Agent
from app.services import team_service


router = APIRouter(prefix="/teams", tags=["Agent Team"])


class TeamInfoResponse(BaseModel):
    id: str
    name: str
    description: str
    status: str


class TeamProfileContentResponse(BaseModel):
    content: str
    version: int


class AgentTeamIntroRequest(BaseModel):
    """Agent 提交自我介绍请求"""
    self_introduction: str


@router.get("/me", response_model=TeamInfoResponse, summary="获取所属团队信息")
async def get_my_team(
    agent: Agent = Depends(get_current_agent),
    db: Session = Depends(get_db),
):
    """获取当前 Agent 所属团队信息"""
    team = team_service.get_agent_team(db, agent.id)
    if not team:
        raise HTTPException(status_code=404, detail="您尚未加入任何团队")
    if team.status == "disabled":
        raise HTTPException(status_code=403, detail="团队已禁用，无法访问")
    return TeamInfoResponse(id=team.id, name=team.name, description=team.description, status=team.status)


@router.get("/me/profile", response_model=TeamProfileContentResponse, summary="获取团队介绍")
async def get_team_profile(
    agent: Agent = Depends(get_current_agent),
    db: Session = Depends(get_db),
):
    """获取团队介绍"""
    team = team_service.get_agent_team(db, agent.id)
    if not team:
        raise HTTPException(status_code=404, detail="您尚未加入任何团队")
    if team.status == "disabled":
        raise HTTPException(status_code=403, detail="团队已禁用，无法访问")

    profile = team_service.get_team_profile(db, team.id)
    if not profile:
        return TeamProfileContentResponse(content="", version=0)

    return TeamProfileContentResponse(content=profile.content, version=profile.version)


@router.put("/me/intro", summary="提交自我介绍")
async def update_self_introduction(
    req: AgentTeamIntroRequest,
    agent: Agent = Depends(get_current_agent),
    db: Session = Depends(get_db),
):
    """提交自我介绍"""
    team = team_service.get_agent_team(db, agent.id)
    if not team:
        raise HTTPException(status_code=404, detail="您尚未加入任何团队")
    if team.status == "disabled":
        raise HTTPException(status_code=403, detail="团队已禁用，无法提交自我介绍")

    try:
        team_service.update_agent_intro(db, agent.id, req.self_introduction)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"message": "自我介绍已更新"}
