#!/usr/bin/env python3
"""
Document Ingester Template using Veris Memory MCP SDK.

This template demonstrates how to build document ingestion pipelines that:
1. Fetch documents from various sources (web, files, APIs)
2. Process and summarize content
3. Store in Veris Memory with rich metadata
4. Handle errors and provide progress tracking

Installation:
    pip install veris-memory-mcp-sdk aiohttp beautifulsoup4 pypdf

Usage:
    1. Set environment variables:
       export VERIS_MEMORY_SERVER_URL="https://your-veris-instance.com"
       export VERIS_MEMORY_API_KEY="your-api-key"  # Optional
    2. Run: python document_ingester.py

Customize the ingester by modifying the DocumentProcessor and IngestionPipeline classes.
"""

import asyncio
import hashlib
import logging
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urljoin, urlparse

try:
    import aiohttp
    from bs4 import BeautifulSoup
except ImportError:
    print("❌ Missing dependencies. Run: pip install aiohttp beautifulsoup4")
    exit(1)

from veris_memory_sdk import MCPClient, MCPConfig, MCPError

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class DocumentMetadata:
    """Metadata for processed documents."""

    source_url: Optional[str] = None
    source_type: str = "unknown"  # web, file, api
    title: Optional[str] = None
    author: Optional[str] = None
    publish_date: Optional[str] = None
    content_hash: Optional[str] = None
    content_length: int = 0
    processing_timestamp: Optional[str] = None
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


@dataclass
class ProcessedDocument:
    """Container for processed document content and metadata."""

    content: str
    summary: str
    metadata: DocumentMetadata
    chunks: List[Dict[str, Any]] = None

    def __post_init__(self):
        if self.chunks is None:
            self.chunks = []


class DocumentProcessor:
    """Processes various document types into structured content."""

    def __init__(self, chunk_size: int = 1000, overlap: int = 100):
        """Initialize processor with chunking parameters."""
        self.chunk_size = chunk_size
        self.overlap = overlap

    async def process_web_page(self, url: str) -> ProcessedDocument:
        """Process a web page into structured content."""
        logger.info(f"Processing web page: {url}")

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status != 200:
                        raise ValueError(f"HTTP {response.status} for {url}")

                    html_content = await response.text()

            except Exception as e:
                raise ValueError(f"Failed to fetch {url}: {e}")

        # Parse HTML content
        soup = BeautifulSoup(html_content, "html.parser")

        # Extract title
        title = soup.find("title")
        title_text = title.get_text().strip() if title else urlparse(url).path

        # Extract main content (remove nav, footer, ads, etc.)
        for element in soup(["nav", "footer", "aside", "script", "style"]):
            element.decompose()

        # Get text content
        content = soup.get_text()
        # Clean up whitespace
        content = re.sub(r"\s+", " ", content).strip()

        # Generate summary (simple extractive approach)
        summary = self._generate_summary(content, max_length=200)

        # Create metadata
        metadata = DocumentMetadata(
            source_url=url,
            source_type="web",
            title=title_text,
            content_hash=hashlib.md5(content.encode()).hexdigest(),
            content_length=len(content),
            processing_timestamp=asyncio.get_event_loop().time(),
            tags=self._extract_tags(content),
        )

        # Create chunks for large content
        chunks = self._create_chunks(content) if len(content) > self.chunk_size else []

        return ProcessedDocument(content=content, summary=summary, metadata=metadata, chunks=chunks)

    async def process_text_file(self, file_path: Union[str, Path]) -> ProcessedDocument:
        """Process a text file into structured content."""
        file_path = Path(file_path)
        logger.info(f"Processing text file: {file_path}")

        if not file_path.exists():
            raise ValueError(f"File not found: {file_path}")

        # Read file content
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
        except UnicodeDecodeError:
            # Try with different encoding
            with open(file_path, "r", encoding="latin-1") as f:
                content = f.read().strip()

        # Generate summary
        summary = self._generate_summary(content, max_length=200)

        # Create metadata
        metadata = DocumentMetadata(
            source_url=str(file_path),
            source_type="file",
            title=file_path.stem,
            content_hash=hashlib.md5(content.encode()).hexdigest(),
            content_length=len(content),
            processing_timestamp=asyncio.get_event_loop().time(),
            tags=[file_path.suffix[1:]] if file_path.suffix else [],
        )

        # Create chunks for large content
        chunks = self._create_chunks(content) if len(content) > self.chunk_size else []

        return ProcessedDocument(content=content, summary=summary, metadata=metadata, chunks=chunks)

    def _generate_summary(self, content: str, max_length: int = 200) -> str:
        """Generate a simple extractive summary."""
        if len(content) <= max_length:
            return content

        # Simple approach: take first few sentences
        sentences = re.split(r"[.!?]+", content)
        summary = ""
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            if len(summary + sentence) > max_length:
                break
            summary += sentence + ". "

        return summary.strip() or content[:max_length] + "..."

    def _extract_tags(self, content: str, max_tags: int = 5) -> List[str]:
        """Extract simple tags from content."""
        # Simple keyword extraction (can be enhanced with NLP)
        words = re.findall(r"\b[a-zA-Z]{4,}\b", content.lower())
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1

        # Get most frequent words as tags
        common_words = {
            "the",
            "and",
            "for",
            "are",
            "but",
            "not",
            "you",
            "all",
            "can",
            "had",
            "her",
            "was",
            "one",
            "our",
            "out",
            "day",
            "get",
            "has",
            "him",
            "his",
            "how",
            "man",
            "may",
            "new",
            "now",
            "old",
            "see",
            "two",
            "way",
            "who",
            "boy",
            "did",
            "its",
            "let",
            "put",
            "say",
            "she",
            "too",
            "use",
        }
        tags = [
            word
            for word, freq in sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
            if word not in common_words
        ][:max_tags]

        return tags

    def _create_chunks(self, content: str) -> List[Dict[str, Any]]:
        """Split content into overlapping chunks."""
        if len(content) <= self.chunk_size:
            return []

        chunks = []
        start = 0
        chunk_num = 0

        while start < len(content):
            end = min(start + self.chunk_size, len(content))
            chunk_text = content[start:end]

            chunks.append(
                {
                    "chunk_number": chunk_num,
                    "text": chunk_text,
                    "start_offset": start,
                    "end_offset": end,
                    "length": len(chunk_text),
                }
            )

            start += self.chunk_size - self.overlap
            chunk_num += 1

        return chunks


class IngestionPipeline:
    """Main ingestion pipeline that processes and stores documents."""

    def __init__(self, mcp_config: MCPConfig, processor: Optional[DocumentProcessor] = None):
        """Initialize pipeline with MCP configuration."""
        self.mcp_config = mcp_config
        self.processor = processor or DocumentProcessor()
        self.mcp_client: Optional[MCPClient] = None
        self.stats = {"processed": 0, "stored": 0, "failed": 0, "skipped": 0}

    async def start(self):
        """Start the ingestion pipeline."""
        logger.info("Starting document ingestion pipeline...")
        self.mcp_client = MCPClient(self.mcp_config)
        await self.mcp_client.connect()
        logger.info("✅ Connected to Veris Memory")

    async def stop(self):
        """Stop the ingestion pipeline."""
        if self.mcp_client:
            await self.mcp_client.disconnect()
        logger.info("Pipeline stopped")

    async def ingest_url(self, url: str, user_id: str = "ingester") -> Optional[str]:
        """Ingest a single URL."""
        try:
            # Process document
            doc = await self.processor.process_web_page(url)
            self.stats["processed"] += 1

            # Store in Veris Memory
            result = await self._store_document(doc, user_id)
            self.stats["stored"] += 1

            logger.info(f"✅ Ingested: {url} -> {result.get('id')}")
            return result.get("id")

        except Exception as e:
            logger.error(f"❌ Failed to ingest {url}: {e}")
            self.stats["failed"] += 1
            return None

    async def ingest_file(
        self, file_path: Union[str, Path], user_id: str = "ingester"
    ) -> Optional[str]:
        """Ingest a single file."""
        try:
            # Process document
            doc = await self.processor.process_text_file(file_path)
            self.stats["processed"] += 1

            # Store in Veris Memory
            result = await self._store_document(doc, user_id)
            self.stats["stored"] += 1

            logger.info(f"✅ Ingested: {file_path} -> {result.get('id')}")
            return result.get("id")

        except Exception as e:
            logger.error(f"❌ Failed to ingest {file_path}: {e}")
            self.stats["failed"] += 1
            return None

    async def ingest_batch_urls(
        self, urls: List[str], user_id: str = "ingester", max_concurrency: int = 5
    ) -> Dict[str, Any]:
        """Ingest multiple URLs concurrently."""
        logger.info(f"Ingesting {len(urls)} URLs with max_concurrency={max_concurrency}")

        semaphore = asyncio.Semaphore(max_concurrency)

        async def ingest_with_semaphore(url: str) -> Optional[str]:
            async with semaphore:
                return await self.ingest_url(url, user_id)

        # Process all URLs
        results = await asyncio.gather(
            *[ingest_with_semaphore(url) for url in urls], return_exceptions=True
        )

        # Compile results
        successful_ids = [r for r in results if isinstance(r, str)]
        failed_count = sum(1 for r in results if r is None or isinstance(r, Exception))

        return {
            "total": len(urls),
            "successful": len(successful_ids),
            "failed": failed_count,
            "document_ids": successful_ids,
        }

    async def _store_document(self, doc: ProcessedDocument, user_id: str) -> Dict[str, Any]:
        """Store processed document in Veris Memory."""
        if not self.mcp_client:
            raise MCPError("MCP client not connected")

        # Prepare content for storage
        content_data = {
            "title": doc.metadata.title or "Untitled Document",
            "content": doc.content,
            "summary": doc.summary,
            "source": doc.metadata.source_url,
            "content_hash": doc.metadata.content_hash,
            "content_length": doc.metadata.content_length,
            "tags": doc.metadata.tags,
            "chunks": len(doc.chunks),
            "processed_at": doc.metadata.processing_timestamp,
        }

        # Store main document
        result = await self.mcp_client.call_tool(
            tool_name="store_context",
            arguments={
                "type": "document",
                "content": content_data,
                "metadata": {
                    "source_type": doc.metadata.source_type,
                    "ingestion_pipeline": "document_ingester",
                    "user_id": user_id,
                    **{k: v for k, v in doc.metadata.__dict__.items() if v is not None},
                },
            },
            user_id=user_id,
        )

        # Store chunks separately for better search granularity
        document_id = result.get("id")
        if doc.chunks and document_id:
            await self._store_chunks(doc.chunks, document_id, user_id)

        return result

    async def _store_chunks(
        self, chunks: List[Dict[str, Any]], parent_document_id: str, user_id: str
    ):
        """Store document chunks as separate context items."""
        chunk_calls = []

        for chunk in chunks:
            chunk_calls.append(
                {
                    "name": "store_context",
                    "arguments": {
                        "type": "document_chunk",
                        "content": {
                            "text": chunk["text"],
                            "chunk_number": chunk["chunk_number"],
                            "parent_document_id": parent_document_id,
                            "start_offset": chunk["start_offset"],
                            "end_offset": chunk["end_offset"],
                        },
                        "metadata": {
                            "parent_document": parent_document_id,
                            "chunk_type": "text_segment",
                            "ingestion_pipeline": "document_ingester",
                        },
                    },
                    "user_id": user_id,
                    "trace_id": f"chunk-{parent_document_id}-{chunk['chunk_number']}",
                }
            )

        # Store chunks in batches
        if chunk_calls:
            try:
                await self.mcp_client.call_tools(chunk_calls, max_concurrency=3)
                logger.debug(f"Stored {len(chunks)} chunks for document {parent_document_id}")
            except Exception as e:
                logger.warning(f"Failed to store some chunks: {e}")

    def get_stats(self) -> Dict[str, int]:
        """Get ingestion statistics."""
        return self.stats.copy()


async def main():
    """Main ingestion example."""
    # Configuration
    server_url = os.getenv("VERIS_MEMORY_SERVER_URL", "http://localhost:8000")
    api_key = os.getenv("VERIS_MEMORY_API_KEY")

    veris_config = MCPConfig(
        server_url=server_url,
        api_key=api_key,
        max_retries=3,
        request_timeout_ms=60000,  # Longer timeout for document processing
    )

    print(f"🚀 Starting Document Ingestion Pipeline")
    print(f"📡 Veris Memory Server: {server_url}")
    print(f"🔐 API Key: {'✅ Set' if api_key else '❌ Not set'}")

    # Create and start pipeline
    pipeline = IngestionPipeline(veris_config)
    await pipeline.start()

    try:
        # Example 1: Ingest a single URL
        print("\n📄 Ingesting example web page...")
        doc_id = await pipeline.ingest_url("https://httpbin.org/html", user_id="demo_user")
        if doc_id:
            print(f"✅ Stored document: {doc_id}")

        # Example 2: Ingest multiple URLs in batch
        print("\n📚 Ingesting batch of URLs...")
        urls = [
            "https://httpbin.org/html",
            "https://httpbin.org/json",
            # Add more URLs as needed
        ]

        batch_result = await pipeline.ingest_batch_urls(
            urls, user_id="demo_user", max_concurrency=2
        )
        print(f"✅ Batch ingestion complete: {batch_result}")

        # Example 3: Ingest local files (if available)
        print("\n📁 Looking for local files to ingest...")
        current_dir = Path(".")
        text_files = list(current_dir.glob("*.md")) + list(current_dir.glob("*.txt"))

        for file_path in text_files[:3]:  # Limit to first 3 files
            print(f"📄 Ingesting: {file_path}")
            doc_id = await pipeline.ingest_file(file_path, user_id="demo_user")
            if doc_id:
                print(f"✅ Stored file: {file_path} -> {doc_id}")

        # Show final statistics
        stats = pipeline.get_stats()
        print(f"\n📊 Final Statistics:")
        print(f"   Processed: {stats['processed']}")
        print(f"   Stored: {stats['stored']}")
        print(f"   Failed: {stats['failed']}")
        print(f"   Skipped: {stats['skipped']}")

    except KeyboardInterrupt:
        print("\n⏹️  Ingestion interrupted by user")
    except Exception as e:
        logger.error(f"Pipeline error: {e}")
    finally:
        await pipeline.stop()
        print("🏁 Ingestion pipeline stopped")


if __name__ == "__main__":
    asyncio.run(main())
