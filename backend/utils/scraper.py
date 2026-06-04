import httpx
import re
from bs4 import BeautifulSoup
from utils.logger import get_logger

logger = get_logger(__name__)

def clean_html(html_content: str) -> str:
    """Extract clean text content from HTML content, removing scripts, styles, etc."""
    try:
        soup = BeautifulSoup(html_content, "html.parser")
        # Remove script and style elements
        for script in soup(["script", "style", "meta", "noscript", "header", "footer", "nav"]):
            script.decompose()
        
        # Get text and collapse whitespace
        text = soup.get_text(separator=" ")
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = "\n".join(chunk for chunk in chunks if chunk)
        return text
    except Exception as e:
        logger.warning(f"BeautifulSoup parsing failed, falling back to regex: {e}")
        # Fallback to regex cleaning if bs4 is not available or fails
        text = re.sub(r'<script.*?</script>', '', html_content, flags=re.DOTALL)
        text = re.sub(r'<style.*?</style>', '', text, flags=re.DOTALL)
        text = re.sub(r'<.*?>', ' ', text)
        return " ".join(text.split())

async def scrape_url(url: str) -> str:
    """Scrape a URL and return cleaned text content."""
    logger.info(f"Scraping URL: {url}")
    async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
        response = await client.get(url, headers={
            "User-Agent": "ResolveAI-Bot/1.0 (+http://localhost:8000)"
        })
        response.raise_for_status()
        return clean_html(response.text)
