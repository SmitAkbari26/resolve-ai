import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Text,
    DateTime,
    Boolean,
    ForeignKey,
    Enum,
    JSON,
    UUID,
)
from sqlalchemy.orm import relationship
from db.database import Base


def utc_now():
    return datetime.now(timezone.utc)


class UserRecord(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    role = Column(
        Enum("customer", "agent", "manager", "admin", name="user_role"),
        default="customer",
    )
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    # Relationships
    tickets = relationship("TicketRecord", back_populates="user")
    conversations = relationship("ConversationRecord", back_populates="user")
    notifications = relationship("NotificationRecord", back_populates="user")
    comments = relationship("TicketCommentRecord", back_populates="user")


class CustomerProfileRecord(Base):
    __tablename__ = "customer_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    phone = Column(String(50), nullable=True)
    company = Column(String(255), nullable=True)
    subscription_plan = Column(String(100), nullable=True)
    preferred_language = Column(String(50), default="en")
    timezone = Column(String(100), default="UTC")
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)


class ConversationRecord(Base):
    __tablename__ = "conversations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    channel = Column(String(50), default="web_chat")
    sentiment = Column(String(50), default="neutral")
    status = Column(String(50), default="active")
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    # Relationships
    user = relationship("UserRecord", back_populates="conversations")
    messages = relationship("ConversationMessageRecord", back_populates="conversation")
    ticket = relationship("TicketRecord", back_populates="conversation", uselist=False)


class ConversationMessageRecord(Base):
    __tablename__ = "conversation_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(
        UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False
    )
    role = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    metadata_ = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    # Relationships
    conversation = relationship("ConversationRecord", back_populates="messages")


class TicketRecord(Base):
    __tablename__ = "tickets"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    conversation_id = Column(
        UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=True
    )
    category = Column(String(100), nullable=False)
    priority = Column(
        Enum("low", "medium", "high", "critical", name="ticket_priority"),
        default="medium",
    )
    status = Column(
        Enum(
            "open",
            "in_progress",
            "pending_customer",
            "pending_approval",
            "resolved",
            "closed",
            "escalated",
            name="ticket_status",
        ),
        default="open",
    )
    severity_score = Column(Float, default=0.0)
    summary = Column(Text, nullable=False)
    description = Column(Text, default="")
    resolution = Column(Text, default="")
    suggested_action = Column(String(255), default="")
    assigned_agent = Column(String(255), nullable=True)
    metadata_ = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    # Relationships
    user = relationship("UserRecord", back_populates="tickets")
    conversation = relationship("ConversationRecord", back_populates="ticket")
    approvals = relationship("ApprovalRecord", back_populates="ticket")
    comments = relationship("TicketCommentRecord", back_populates="ticket")
    attachments = relationship("TicketAttachmentRecord", back_populates="ticket")
    histories = relationship("TicketHistoryRecord", back_populates="ticket")
    workflows = relationship("WorkflowExecutionRecord", back_populates="ticket")
    escalations = relationship("EscalationRecord", back_populates="ticket")


class TicketCommentRecord(Base):
    __tablename__ = "ticket_comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id = Column(UUID(as_uuid=True), ForeignKey("tickets.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    comment = Column(Text, nullable=False)
    is_internal = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    # Relationships
    ticket = relationship("TicketRecord", back_populates="comments")
    user = relationship("UserRecord", back_populates="comments")


class TicketAttachmentRecord(Base):
    __tablename__ = "ticket_attachments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id = Column(UUID(as_uuid=True), ForeignKey("tickets.id"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(Text, nullable=False)
    file_type = Column(String(100), nullable=True)
    uploaded_by = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    # Relationships
    ticket = relationship("TicketRecord", back_populates="attachments")


class TicketHistoryRecord(Base):
    __tablename__ = "ticket_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id = Column(UUID(as_uuid=True), ForeignKey("tickets.id"), nullable=False)
    field_name = Column(String(100), nullable=False)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    changed_by = Column(String(255), nullable=True)
    changed_at = Column(DateTime(timezone=True), default=utc_now)

    # Relationships
    ticket = relationship("TicketRecord", back_populates="histories")


class ApprovalRecord(Base):
    __tablename__ = "approvals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id = Column(UUID(as_uuid=True), ForeignKey("tickets.id"), nullable=False)
    approval_type = Column(String(100), nullable=False)
    reason = Column(Text, default="")
    amount = Column(Float, nullable=True)
    status = Column(
        Enum("pending", "approved", "rejected", name="approval_status"),
        default="pending",
    )
    requested_by = Column(String(255), default="system")
    decided_by = Column(String(255), nullable=True)
    decision_notes = Column(Text, default="")
    created_at = Column(DateTime(timezone=True), default=utc_now)
    decided_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    ticket = relationship("TicketRecord", back_populates="approvals")


class EscalationRecord(Base):
    __tablename__ = "escalations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id = Column(UUID(as_uuid=True), ForeignKey("tickets.id"), nullable=False)
    escalation_level = Column(Integer, default=1)
    reason = Column(Text, nullable=False)
    escalated_to = Column(String(255), nullable=True)
    status = Column(String(50), default="active")
    created_at = Column(DateTime(timezone=True), default=utc_now)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    ticket = relationship("TicketRecord", back_populates="escalations")


class AgentRecord(Base):
    __tablename__ = "agents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    agent_type = Column(String(100), nullable=False)
    description = Column(Text, default="")
    model_name = Column(String(255), nullable=True)
    status = Column(String(50), default="active")
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)


class WorkflowExecutionRecord(Base):
    __tablename__ = "workflow_executions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ticket_id = Column(UUID(as_uuid=True), ForeignKey("tickets.id"), nullable=True)
    workflow_type = Column(String(100), nullable=False)
    current_step = Column(String(100), nullable=True)
    status = Column(
        Enum(
            "pending",
            "running",
            "waiting_approval",
            "completed",
            "failed",
            "cancelled",
            name="workflow_status",
        ),
        default="pending",
    )
    started_at = Column(DateTime(timezone=True), default=utc_now)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    failed_reason = Column(Text, nullable=True)
    created_by = Column(String(255), nullable=True)

    # Relationships
    ticket = relationship("TicketRecord", back_populates="workflows")
    steps = relationship("WorkflowStepRecord", back_populates="workflow")


class WorkflowStepRecord(Base):
    __tablename__ = "workflow_steps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_execution_id = Column(
        UUID(as_uuid=True), ForeignKey("workflow_executions.id"), nullable=False
    )
    step_name = Column(String(255), nullable=False)
    agent_id = Column(UUID(as_uuid=True), ForeignKey("agents.id"), nullable=True)
    status = Column(String(50), default="pending")
    input_payload = Column(JSON, default=dict)
    output_payload = Column(JSON, default=dict)
    started_at = Column(DateTime(timezone=True), default=utc_now)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)

    # Relationships
    workflow = relationship("WorkflowExecutionRecord", back_populates="steps")


class KnowledgeDocumentRecord(Base):
    __tablename__ = "knowledge_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    document_type = Column(String(100), nullable=False)
    source_path = Column(Text, nullable=False)
    uploaded_by = Column(String(255), nullable=True)
    version = Column(Integer, default=1)
    status = Column(String(50), default="active")
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    # Relationships
    chunks = relationship("DocumentChunkRecord", back_populates="document")


class DocumentChunkRecord(Base):
    __tablename__ = "document_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(
        UUID(as_uuid=True), ForeignKey("knowledge_documents.id"), nullable=False
    )
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    embedding_id = Column(String(255), nullable=True)
    metadata_ = Column("metadata", JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    # Relationships
    document = relationship("KnowledgeDocumentRecord", back_populates="chunks")


class NotificationRecord(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    ticket_id = Column(UUID(as_uuid=True), ForeignKey("tickets.id"), nullable=True)
    notification_type = Column(String(100), nullable=False)
    channel = Column(String(50), default="email")
    subject = Column(String(255), nullable=True)
    message = Column(Text, nullable=False)
    status = Column(
        Enum("pending", "sent", "failed", "read", name="notification_status"),
        default="pending",
    )
    sent_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    # Relationships
    user = relationship("UserRecord", back_populates="notifications")


class PolicyRecord(Base):
    __tablename__ = "policies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    active = Column(Boolean, default=True)
    version = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)


class AuditLogRecord(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String, nullable=False)
    action = Column(String(100), nullable=False)
    agent_name = Column(String(100), nullable=True)
    details = Column(JSON, default=dict)
    timestamp = Column(DateTime(timezone=True), default=utc_now)


class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    slug = Column(String(100), nullable=False, unique=True)
    api_key = Column(String(255), nullable=False, unique=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    widget_configuration = relationship(
        "WidgetConfiguration",
        back_populates="tenant",
        uselist=False,
    )
    widget_domains = relationship(
        "WidgetDomain",
        back_populates="tenant",
    )


class WidgetConfiguration(Base):
    __tablename__ = "widget_configurations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id"),
        nullable=False,
        unique=True,
    )
    primary_color = Column(String(20), default="#8b5cf6")
    position = Column(String(20), default="right")
    company_name = Column(String(255))
    welcome_message = Column(String(1000))
    width = Column(Integer, default=430)
    height = Column(Integer, default=720)
    border_radius = Column(Integer, default=32)
    launcher_size = Column(Integer, default=64)
    show_badge = Column(Boolean, default=True)
    fullscreen_mobile = Column(Boolean, default=True)
    auto_open = Column(Boolean, default=False)
    auto_open_delay = Column(Integer, default=2000)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)
    tenant = relationship(
        "Tenant",
        back_populates="widget_configuration",
    )


class WidgetDomain(Base):
    __tablename__ = "widget_domains"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id"),
        nullable=False,
    )
    domain = Column(String(500), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    tenant = relationship(
        "Tenant",
        back_populates="widget_domains",
    )
