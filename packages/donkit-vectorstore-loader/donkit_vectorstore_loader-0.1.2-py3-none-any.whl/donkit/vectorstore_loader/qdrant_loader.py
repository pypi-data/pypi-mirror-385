import re
from typing import Any
from urllib.parse import urlparse
from uuid import NAMESPACE_URL
from uuid import UUID
from uuid import uuid4
from uuid import uuid5

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from loguru import logger
from qdrant_client import QdrantClient
from qdrant_client import models
from qdrant_client.models import TextIndexType

from .vectorstore_loader_abstract import VectorstoreLoaderAbstract


def parse_qdrant_url(url: str) -> tuple[str, int, bool]:
    if "://" not in url:
        url = f"http://{url}"
    parsed = urlparse(url)
    host = parsed.hostname or "localhost"
    port = parsed.port or 6333
    use_https = parsed.scheme == "https"
    return host, port, use_https


class QdrantVectorstoreLoader(VectorstoreLoaderAbstract):
    def __init__(
        self,
        collection_name: str,
        embeddings: Embeddings,
        database_uri: str = "http://localhost:6333",
    ) -> None:
        self.collection_name = collection_name
        self.embeddings = embeddings
        host, port, use_https = parse_qdrant_url(database_uri)

        self.client = QdrantClient(
            host=host,
            port=port,
            https=use_https,
        )

        self.dimension = self._detect_dimension()
        self._ensure_collection(collection_name)

    def _detect_dimension(self) -> int:
        """Detect vector dimension from embeddings."""
        test_vector = self.embeddings.embed_query("test")
        dimension = len(test_vector)
        logger.info(f"Detected embedding dimension: {dimension}")
        return dimension

    def _ensure_collection(self, name: str, vector_dim: int | None = None) -> None:
        """Create or get existing collection."""
        try:
            self.client.get_collection(collection_name=name)
            logger.info(f"Using existing Qdrant collection: {name}")
        except Exception:
            # Collection doesn't exist, create it
            self.client.create_collection(
                collection_name=name,
                vectors_config=models.VectorParams(
                    size=vector_dim or self.dimension,
                    distance=models.Distance.COSINE,
                ),
            )
            logger.info(f"Created Qdrant collection: {name}")

            # Create indexes
            try:
                self.client.create_payload_index(
                    collection_name=name,
                    field_name="text",
                    field_schema=models.TextIndexParams(
                        type=TextIndexType.TEXT,
                        tokenizer=models.TokenizerType.WORD,
                        min_token_len=2,
                        max_token_len=20,
                        lowercase=True,
                    ),
                )
                self.client.create_payload_index(
                    collection_name=name,
                    field_name="document_id",
                    field_schema="keyword",
                )
                self.client.create_payload_index(
                    collection_name=name,
                    field_name="filename",
                    field_schema="keyword",
                )
            except Exception as e:
                logger.warning(f"Error creating indexes: {e}")

    def load_text(self, text: str, **kwargs: dict[str, Any]) -> dict[str, str]:
        """
        Load a single text chunk into Qdrant.
        """
        document_id = kwargs.get("document_id") or str(uuid4())
        user_metadata = kwargs.get("metadata", {})

        # Generate embedding
        embeddings = self.embeddings.embed_documents([text.strip()])

        point_id = uuid5(NAMESPACE_URL, f"{document_id}_0")
        payload = {
            "text": text.strip(),
            "document_id": document_id,
            "chunk_index": 0,
            "page_number": user_metadata.get("page_number", 0),
            "category": user_metadata.get("category", "other"),
            "additional_info": str(user_metadata.get("additional_info", {})),
        }

        # Add filename if provided
        if filename := user_metadata.get("filename"):
            payload["filename"] = filename

        point = models.PointStruct(
            id=str(point_id),
            vector=self._sanitize_vector(embeddings[0]),
            payload=payload,
        )

        self.client.upsert(
            collection_name=self.collection_name,
            points=[point],
        )

        logger.info(f"Inserted text into Qdrant collection '{self.collection_name}'")
        return {"ids": [str(point_id)]}

    @staticmethod
    def _sanitize_vector(vector: list[float], precision: int = 10) -> list[float]:
        result: list[float] = []
        for x in vector:
            if not isinstance(x, (int, float)):
                raise ValueError(f"Non-numeric value in vector: {x} ({type(x)})")
            if x != x or x in (float("inf"), float("-inf")):
                raise ValueError(f"Invalid value: {x}")
            dec = float(format(float(x), f".{precision}f"))
            result.append(dec)
        return result

    @staticmethod
    def _clean_text(text: str) -> str:
        text = re.sub(r"\[.*?\]", "", text)
        text = re.sub(r"\{.*?\}", "", text)
        text = re.sub(r"\(.*?\)", "", text)
        text = re.sub(r"<.*?>", "", text)
        text = re.sub(r"\.{2,}", "", text)
        text = re.sub(r"\s+", " ", text)
        text = re.sub(r"[^\w\s]", "", text)
        return text.strip()

    def load_documents(
        self,
        task_id: UUID,
        documents: list[Document],
    ) -> list[str]:
        """
        Process and load a list of documents into Qdrant.
        """
        if not documents:
            return []

        # Generate embeddings
        embeddings = self.embeddings.embed_documents(
            [self._clean_text(doc.page_content) for doc in documents]
        )

        # Prepare points for Qdrant
        points = []
        ids = []
        for idx, (doc, vector) in enumerate(zip(documents, embeddings)):
            point_id = uuid5(
                NAMESPACE_URL, f"{doc.metadata.get('document_id') or uuid4()}_{idx}"
            )
            ids.append(str(point_id))

            payload = {
                "text": doc.page_content,
                "document_id": doc.metadata.get("document_id"),
                "page_number": doc.metadata.get("page_number", 0),
                "category": doc.metadata.get("category", "other"),
                "chunk_index": idx,
                "additional_info": str(doc.metadata.get("additional_info", {})),
            }

            # Add filename if provided
            if filename := doc.metadata.get("filename"):
                payload["filename"] = filename

            points.append(
                models.PointStruct(
                    id=str(point_id),
                    vector=self._sanitize_vector(vector),
                    payload=payload,
                )
            )

        # Load into Qdrant
        if points:
            logger.info(f"Loading {len(points)} chunks into Qdrant.")
            self.client.upsert(
                collection_name=self.collection_name,
                points=points,
            )

        return ids

    def delete_document_from_vectorstore(
        self, document_id: str | None = None, filename: str | None = None
    ) -> bool:
        """
        Delete document from Qdrant.
        """
        try:
            if document_id:
                # Delete by document_id
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=models.FilterSelector(
                        filter=models.Filter(
                            must=[
                                models.FieldCondition(
                                    key="document_id",
                                    match=models.MatchValue(value=document_id),
                                )
                            ]
                        )
                    ),
                )
            elif filename:
                # Delete by filename
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=models.FilterSelector(
                        filter=models.Filter(
                            must=[
                                models.FieldCondition(
                                    key="filename",
                                    match=models.MatchValue(value=filename),
                                )
                            ]
                        )
                    ),
                )
            else:
                raise ValueError("No document_id or filename provided")

            logger.info(
                f"Deleted document from Qdrant collection '{self.collection_name}'"
            )
            return True
        except Exception as e:
            logger.error(f"Error deleting data from Qdrant: {e}")
            return False
