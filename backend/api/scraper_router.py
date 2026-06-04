from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from uuid import UUID, uuid4
from db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from services.knowledge_document_service import KnowledgeDocumentService
from utils.scraper import scrape_url
from utils.logger import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/scraper", tags=["Scraper"])


class ScrapeRequest(BaseModel):
    url: str
    tenant_id: str
    title: str | None = None


class ScrapeTenantRequest(BaseModel):
    tenant_id: str


@router.post("/scrape-and-ingest")
async def scrape_and_ingest(payload: ScrapeRequest, db: AsyncSession = Depends(get_db)):
    """Scrape a web page, extract clean text, and ingest it into knowledge base & ChromaDB
    scoped to the given tenant."""
    try:
        url = payload.url.strip()
        if not url.startswith(("http://", "https://")):
            raise HTTPException(status_code=400, detail="Invalid URL format. Must start with http:// or https://")

        tenant_uuid: UUID | None = None
        try:
            tenant_uuid = UUID(payload.tenant_id)
        except (ValueError, AttributeError):
            raise HTTPException(status_code=400, detail="Invalid tenant_id UUID format")

        # 1. Scrape content
        clean_text = await scrape_url(url)
        if not clean_text or not clean_text.strip():
            raise HTTPException(status_code=400, detail="Scraper retrieved empty content from page")

        # 2. Ingest using KnowledgeDocumentService (scoped to tenant)
        doc_service = KnowledgeDocumentService(db)
        title = payload.title or url
        file_content = clean_text.encode("utf-8")
        filename = f"scraped_{uuid4().hex[:8]}.txt"

        doc, chunks = await doc_service.upload_and_ingest(
            file_content=file_content,
            filename=filename,
            title=title,
            document_type="web_page",
            uploaded_by="web_scraper",
            tenant_id=tenant_uuid,
        )

        return {
            "success": True,
            "document_id": str(doc.id),
            "title": doc.title,
            "tenant_id": str(tenant_uuid),
            "chunks_ingested": chunks,
            "message": f"Scraped and indexed {chunks} chunks from {url} for tenant {tenant_uuid}",
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Web scraper ingestion failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/scrape-tenant-domains")
async def scrape_tenant_domains(payload: ScrapeTenantRequest, db: AsyncSession = Depends(get_db)):
    """Scrape ALL registered domains for a tenant and ingest their content into the knowledge base."""
    try:
        tenant_uuid = UUID(payload.tenant_id)

        from repositories.widget_domain_repository import WidgetDomainRepository
        domain_repo = WidgetDomainRepository(db)
        domains = await domain_repo.get_by_tenant_id(tenant_uuid)

        if not domains:
            return {"success": False, "message": "No domains registered for this tenant", "results": []}

        doc_service = KnowledgeDocumentService(db)
        results = []

        for domain_record in domains:
            domain = domain_record.domain
            url = f"https://{domain}" if not domain.startswith("http") else domain
            try:
                clean_text = await scrape_url(url)
                if not clean_text or not clean_text.strip():
                    results.append({"domain": domain, "success": False, "error": "Empty content"})
                    continue

                file_content = clean_text.encode("utf-8")
                filename = f"scraped_{uuid4().hex[:8]}.txt"

                doc, chunks = await doc_service.upload_and_ingest(
                    file_content=file_content,
                    filename=filename,
                    title=f"{domain} - Home Page",
                    document_type="web_page",
                    uploaded_by="web_scraper",
                    tenant_id=tenant_uuid,
                )
                results.append({
                    "domain": domain,
                    "success": True,
                    "document_id": str(doc.id),
                    "chunks_ingested": chunks,
                })
            except Exception as domain_err:
                logger.warning(f"Failed to scrape domain {domain}: {domain_err}")
                results.append({"domain": domain, "success": False, "error": str(domain_err)})

        return {
            "success": True,
            "tenant_id": str(tenant_uuid),
            "total_domains": len(domains),
            "results": results,
        }
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid tenant_id UUID format")
    except Exception as e:
        logger.error(f"Tenant domain scraping failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

