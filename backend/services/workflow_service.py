from sqlalchemy.ext.asyncio import AsyncSession

from workflows.support_workflow import SupportWorkflowOrchestrator
from workflows.state import SupportWorkflowState
from services.workflow_execution_service import WorkflowExecutionService
from services.workflow_step_service import WorkflowStepService
from schemas.workflow_execution_schema import WorkflowExecutionCreate
from utils.helpers import generate_id
from utils.logger import get_logger

logger = get_logger(__name__)


class WorkflowService:

    def __init__(self, db: AsyncSession):
        self.db = db
        self._exec_service = WorkflowExecutionService(db)
        self._step_service = WorkflowStepService(db)
        self.orchestrator = SupportWorkflowOrchestrator(db)

    async def execute_workflow(
        self,
        user_query: str,
        conversation_id: str,
        user_id: str = "",
        user_email: str = "",
        ticket_id: str = "",
        stream_callback = None,
        tenant_id: str | None = None,
        company_name: str = "our company",
    ) -> dict:

        workflow_id = generate_id("WRK")

        # Load available agents from DB for dynamic assignment
        available_agents = []
        try:
            from services.agent_service import AgentService
            agent_svc = AgentService(self.db)
            agents = await agent_svc.get_agents_by_status("active")
            available_agents = [
                {
                    "id": str(a.id),
                    "name": a.name,
                    "agent_type": a.agent_type,
                    "description": a.description,
                }
                for a in agents
            ]
        except Exception as e:
            logger.warning(f"Could not load available agents: {e}")

        state: SupportWorkflowState = {
            "workflow_id": workflow_id,
            "workflow_db_id": "",
            "conversation_id": conversation_id,
            "user_id": user_id,
            "user_email": user_email,
            "user_query": user_query,
            "status": "running",
            "agent_trace": [],
            "runtime_events": [],
            "tool_calls": [],
            "skip_notifications": not bool(user_email),
            "stream_callback": stream_callback,
            "available_agents": available_agents,
            "tenant_id": tenant_id,
            "company_name": company_name,
        }


        if ticket_id:
            state["ticket_id"] = ticket_id
            from services.ticket_service import TicketService
            try:
                ticket_svc = TicketService(self.db)
                ticket = await ticket_svc.get_ticket_by_id(ticket_id)
                if ticket:
                    state["ticket"] = {
                        "id": str(ticket.id),
                        "user_id": str(ticket.user_id),
                        "conversation_id": str(ticket.conversation_id) if ticket.conversation_id else None,
                        "category": ticket.category,
                        "priority": ticket.priority,
                        "status": ticket.status,
                        "severity_score": ticket.severity_score,
                        "summary": ticket.summary,
                        "description": ticket.description,
                        "resolution": ticket.resolution,
                        "suggested_action": ticket.suggested_action,
                        "assigned_agent": ticket.assigned_agent,
                        "created_at": ticket.created_at.isoformat() if ticket.created_at else None,
                        "updated_at": ticket.updated_at.isoformat() if ticket.updated_at else None,
                    }
            except Exception as e:
                logger.warning(f"Failed to load existing ticket for state: {e}")


        # Commit and close the session to release it back to the connection pool
        # during the long-running orchestrator and agent/LLM execution loop.
        try:
            await self.db.commit()
            await self.db.close()
        except Exception as e:
            logger.warning(f"Could not close DB session before orchestrator: {e}")

        result = await self.orchestrator.run(state)

        return result

    async def resume_workflow(
        self,
        workflow_id: str,
        approval_decision: str,
        decided_by: str = "system",
    ) -> dict:

        logger.info(
            f"Resuming workflow {workflow_id} | "
            f"Decision={approval_decision} | "
            f"By={decided_by}"
        )

        return await self.orchestrator.resume(
            workflow_id=workflow_id,
            approval_decision=approval_decision,
            decided_by=decided_by,
        )
