import asyncio
from datetime import datetime, timezone
from neo4j import AsyncSession
from agents.register import AGENT_REGISTRY
from agents.conversation_agent import ConversationAgent
from agents.resolve_agent import ResolveAgent
from db.memory_store import store_workflow_state, get_workflow_state
from services.workflow_execution_service import WorkflowExecutionService
from services.workflow_step_service import WorkflowStepService
from utils.logger import get_logger

logger = get_logger(__name__)


class SupportWorkflowOrchestrator:

    def __init__(
        self,
        db: AsyncSession,
    ):
        self._workflow_exec_service = WorkflowExecutionService(db)
        self._workflow_step_service = WorkflowStepService(db)

    async def run(self, state: dict) -> dict:

        conversation_agent = ConversationAgent()
        state = await conversation_agent(state)

        if state.get("status") == "failed":
            logger.error("ConversationAgent failed — aborting workflow")
            return state

        if state.get("short_circuit"):
            logger.info("ConversationAgent short-circuited — completing workflow")
            state["status"] = "completed"
            return state

        # If we need workflow agents (not short-circuited), create database record now
        if not state.get("workflow_db_id"):
            try:
                from schemas.workflow_execution_schema import WorkflowExecutionCreate

                db_payload = WorkflowExecutionCreate(
                    ticket_id=state.get("ticket_id") or None,
                    workflow_type="support_resolution",
                    status="running",
                    created_by=state.get("user_id") or "system",
                )
                db_record = await self._workflow_exec_service.create_workflow(
                    db_payload
                )
                state["workflow_db_id"] = str(db_record.id)
                logger.info(
                    f"WorkflowExecution created in DB: {state['workflow_db_id']}"
                )
            except Exception as e:
                logger.warning(
                    f"Could not create WorkflowExecution DB record: {e} — "
                    f"proceeding without DB tracking"
                )

        plan = ["resolve_agent"]
        state["plan"] = plan
        logger.info(f"Execution plan: {plan}")

        state = await self._execute_plan(state, plan, start_index=0)

        if state.get("ticket_id") and state.get("ticket"):
            from utils.ticket_messages import format_ticket_created_reply

            if "TCK-" in (state.get("ai_response") or "") or not state.get(
                "ai_response"
            ):
                state["ai_response"] = format_ticket_created_reply(state["ticket"])

        return state

    async def resume(
        self,
        workflow_id: str,
        approval_decision: str,
        decided_by: str = "system",
    ) -> dict:

        state = get_workflow_state(workflow_id)

        if not state:
            logger.error(f"No saved state for workflow: {workflow_id}")
            return {
                "status": "failed",
                "error": f"Workflow {workflow_id} not found or expired",
            }

        if state.get("status") != "paused":
            logger.warning(
                f"Workflow {workflow_id} is not paused "
                f"(status={state.get('status')})"
            )
            return state

        logger.info(
            f"Resuming workflow {workflow_id} | "
            f"Decision={approval_decision} | "
            f"By={decided_by}"
        )

        state["approval_decision"] = approval_decision
        state["requires_approval"] = False
        state["status"] = "running"

        state["runtime_events"].append(
            {
                "type": "workflow_resumed",
                "workflow_id": workflow_id,
                "approval_decision": approval_decision,
                "decided_by": decided_by,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )

        if approval_decision == "rejected":
            state["ai_response"] = (
                "Your request has been reviewed and could not be approved "
                "at this time. Please contact our support team for further "
                "assistance."
            )
            state["status"] = "completed"
            await self._finalize_db(state, "completed")
            return state

        plan = ["resolve_agent"]
        state["plan"] = plan

        logger.info("Resuming ResolveAgent execution after approval.")
        state = await self._execute_plan(state, plan, start_index=0)

        return state



    async def _execute_parallel(self, state, agents: list):
        """Run agents; single-agent steps mutate state in-place for correctness."""
        if len(agents) == 1:
            return await AGENT_REGISTRY[agents[0]]()(state)

        tasks = [AGENT_REGISTRY[name]()(state.copy()) for name in agents]
        results = await asyncio.gather(*tasks)
        return await self._merge_results(state, results)

    async def _merge_results(self, base_state: dict, results: list[dict]) -> dict:
        """Merge a list of agent result dicts into base_state.
        Later agents' keys override earlier ones.
        """
        for result in results:
            if isinstance(result, dict):
                base_state.update(result)
        return base_state

    async def _execute_plan(
        self,
        state: dict,
        plan: list[str],
        start_index: int = 0,
    ) -> dict:

        for group in plan:

            # ─── Normalise: plan is a flat list of agent-name strings
            # Each item may be a str (single agent) or a list (parallel group)
            if isinstance(group, str):
                agent_group = [group]
                group_label = group
            else:
                agent_group = group
                group_label = str(group)

            # Skip unknown agents
            unknown = [a for a in agent_group if a not in AGENT_REGISTRY]
            if unknown:
                logger.warning(f"Skipping unknown agents in plan: {unknown}")
                agent_group = [a for a in agent_group if a in AGENT_REGISTRY]
                if not agent_group:
                    continue

            await self._record_step_start(state, group_label)

            state = await self._execute_parallel(state, agent_group)

            await self._record_step_end(state, group_label)

            if state.get("status") == "paused":
                logger.info(f"Workflow paused at agent: {group}")

                state_copy = state.copy()
                state_copy.pop("stream_callback", None)
                store_workflow_state(
                    state.get("workflow_id", ""),
                    state_copy,
                )
                await self._finalize_db(state, "waiting_approval")
                return state

            if state.get("status") == "failed":
                logger.error(f"Workflow failed at agent: {group}")
                await self._finalize_db(state, "failed")
                return state

        state["status"] = "completed"
        logger.info("Workflow completed successfully")
        await self._finalize_db(state, "completed")
        return state

    async def _record_step_start(self, state: dict, agent_name: str):
        # Use independent session to avoid interfering with the orchestrator's transaction
        from db.database import async_session_factory

        async with async_session_factory() as step_db:
            step_service = WorkflowStepService(step_db)
            workflow_db_id = state.get("workflow_db_id")
            if workflow_db_id:
                from schemas.workflow_step_schema import WorkflowStepCreate

                # Try to resolve agent_id from DB by matching agent_type to step name
                resolved_agent_id = None
                try:
                    from services.agent_service import AgentService
                    agent_svc = AgentService(step_db)
                    matched = await agent_svc.get_agents_by_type(agent_name)
                    if matched:
                        resolved_agent_id = matched[0].id
                    else:
                        # fallback: search active agents whose name contains the step key
                        all_agents = await agent_svc.get_agents_by_status("active")
                        step_key = agent_name.replace("_agent", "").lower()
                        for ag in all_agents:
                            if step_key in ag.name.lower() or step_key in (ag.agent_type or "").lower():
                                resolved_agent_id = ag.id
                                break
                except Exception as e:
                    logger.debug(f"Could not resolve agent_id for step '{agent_name}': {e}")

                payload = WorkflowStepCreate(
                    workflow_execution_id=workflow_db_id,
                    step_name=agent_name,
                    agent_id=resolved_agent_id,
                    status="running",
                    input_payload={
                        "plan": state.get("plan", []),
                        "category": state.get("detected_category"),
                        "urgency": state.get("urgency"),
                    },
                )
                step = await step_service.create_workflow_step(payload)
                if step:
                    state["_current_step_id"] = str(step.id)
                await step_db.commit()

    async def _record_step_end(self, state: dict, agent_name: str):
        # Use independent session to avoid interfering with orchestrator's transaction
        from db.database import async_session_factory

        async with async_session_factory() as step_db:
            step_service = WorkflowStepService(step_db)
            step_id = state.get("_current_step_id")
            if step_id:
                from schemas.workflow_step_schema import WorkflowStepUpdate
                from datetime import datetime, timezone

                output_payload = {
                    "status": state.get("status"),
                    "ticket_id": state.get("ticket_id"),
                    "approval_id": state.get("approval_id"),
                    "ai_response": state.get("ai_response"),
                    "error": state.get("error"),
                }
                payload = WorkflowStepUpdate(
                    status=state.get("status", "completed"),
                    output_payload=output_payload,
                    completed_at=datetime.now(timezone.utc),
                    error_message=state.get("error"),
                )
                await step_service.update_workflow_step(step_id, payload)
                await step_db.commit()

    async def _finalize_db(
        self,
        state: dict,
        final_status: str,
    ):
        if not self._workflow_exec_service:
            return
        try:
            workflow_db_id = state.get("workflow_db_id")
            if workflow_db_id:
                from schemas.workflow_execution_schema import WorkflowExecutionUpdate
                from datetime import datetime, timezone

                payload = WorkflowExecutionUpdate(
                    ticket_id=state.get("ticket_id"),
                    status=final_status,
                    current_step=(
                        state.get("plan", [None])[-1] if state.get("plan") else None
                    ),
                    failed_reason=state.get("error"),
                    completed_at=(
                        datetime.now(timezone.utc)
                        if final_status in ["completed", "failed"]
                        else None
                    ),
                )
                await self._workflow_exec_service.update_workflow(
                    workflow_db_id,
                    payload,
                )
        except Exception as e:
            logger.warning(f"DB workflow finalize failed: {e}")
