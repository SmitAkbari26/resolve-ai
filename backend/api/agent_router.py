from uuid import UUID

from db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from services.agent_service import AgentService
from schemas.agent_schema import AgentCreate, AgentUpdate, AgentResponse

router = APIRouter(prefix="/agents", tags=["Agents"])


@router.post("", response_model=AgentResponse)
async def create_agent_api(payload: AgentCreate, db: AsyncSession = Depends(get_db)):
    try:
        service = AgentService(db)
        return await service.create_agent(payload)
    except Exception as ex:
        raise HTTPException(status_code=400, detail=str(ex))


@router.get("", response_model=list[AgentResponse])
async def get_agents_api(db: AsyncSession = Depends(get_db)):
    service = AgentService(db)
    return await service.get_agents()


@router.get("/type/{agent_type}", response_model=list[AgentResponse])
async def get_type_agents_api(agent_type: str, db: AsyncSession = Depends(get_db)):
    service = AgentService(db)
    return await service.get_agents_by_type(agent_type)


@router.get("/status/{status}", response_model=list[AgentResponse])
async def get_status_agents_api(status: str, db: AsyncSession = Depends(get_db)):
    service = AgentService(db)
    return await service.get_agents_by_status(status)


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent_api(agent_id: UUID, db: AsyncSession = Depends(get_db)):
    service = AgentService(db)
    agent = await service.get_agent_by_id(str(agent_id))
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.put("/{agent_id}", response_model=AgentResponse)
async def update_agent_api(
    agent_id: UUID, payload: AgentUpdate, db: AsyncSession = Depends(get_db)
):
    service = AgentService(db)
    agent = await service.update_agent(str(agent_id), payload)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.delete("/{agent_id}")
async def delete_agent_api(agent_id: UUID, db: AsyncSession = Depends(get_db)):
    service = AgentService(db)
    deleted = await service.delete_agent(str(agent_id))
    if not deleted:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"message": "Agent deleted successfully"}
