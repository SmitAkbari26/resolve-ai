from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from config import DATABASE_URL
from utils.logger import get_logger

logger = get_logger(__name__)


class Base(DeclarativeBase):
    pass


engine = create_async_engine(DATABASE_URL, echo=False, pool_size=10, max_overflow=20)
async_session_factory = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


from sqlalchemy import text

async def init_db():
    try:
        async with engine.begin() as conn:
            import db.schemas

            await conn.run_sync(Base.metadata.create_all)
            
            # Dynamically ensure tenant_id column exists on knowledge_documents table
            await conn.execute(
                text(
                    "ALTER TABLE knowledge_documents "
                    "ADD COLUMN IF NOT EXISTS tenant_id UUID REFERENCES tenants(id) ON DELETE SET NULL"
                )
            )
        logger.info("PostgreSQL database initialized")
    except Exception as e:
        logger.warning(f"PostgreSQL connection failed (continuing without DB): {e}")



async def get_db():
    async with async_session_factory() as session:
        try:
            yield session
            if session.is_active:
                await session.commit()
        except Exception:
            if session.is_active:
                await session.rollback()
            raise
        finally:
            try:
                await session.close()
            except Exception:
                pass

