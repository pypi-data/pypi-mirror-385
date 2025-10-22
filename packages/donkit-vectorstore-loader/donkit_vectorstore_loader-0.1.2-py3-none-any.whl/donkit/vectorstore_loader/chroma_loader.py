import re
from typing import Any
from typing import Dict
from typing import List
from urllib.parse import urlparse
from uuid import UUID, uuid4

import chromadb
from chromadb.api.models import Collection
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from loguru import logger

from .vectorstore_loader_abstract import VectorstoreLoaderAbstract


class ChromaVectorstoreLoader(VectorstoreLoaderAbstract):
    def __init__(
        self,
        collection_name: str,
        embeddings: Embeddings,
        database_uri: str = "http://localhost:8000",
    ) -> None:
        self.collection_name = collection_name
        self.embeddings = embeddings

        # Parse database URI to extract host and port
        parsed = urlparse(database_uri)
        host = parsed.hostname or "localhost"
        port = parsed.port or 8000

        self.client = chromadb.HttpClient(
            host=host, port=port, settings=chromadb.Settings(allow_reset=True)
        )

        self.collection = self._ensure_collection(collection_name)

    def _ensure_collection(self, name: str) -> Collection:
        """Create or get existing collection."""
        try:
            collection = self.client.get_collection(name=name)
            logger.info(f"Using existing ChromaDB collection: {name}")
        except Exception:
            collection = self.client.create_collection(
                name=name, metadata={"description": "RAG document chunks"}
            )
            logger.info(f"Created ChromaDB collection: {name}")
        return collection

    def load_data(self, text: str, **kwargs: Any) -> Any:
        """
        Loads a document or split chunks into ChromaDB.
        """
        split_doc = kwargs.get("split_doc", False)
        document_id = kwargs.get("document_id") or str(uuid4())
        user_metadata = kwargs.get("metadata", {})

        if split_doc:
            chunks = [c.strip() for c in text.split("\n\n") if c.strip()]
        else:
            chunks = [text.strip()]

        # Generate embeddings
        embeddings = self.embeddings.embed_documents(chunks)

        ids = []
        documents = []
        metadatas = []
        embeddings_list = []

        for idx, (chunk_text, vector) in enumerate(zip(chunks, embeddings)):
            doc_id = f"{document_id}_{idx}"
            ids.append(doc_id)
            documents.append(chunk_text)

            metadata = user_metadata.copy() if user_metadata else {}
            metadata.update(
                {
                    "document_id": document_id,
                    "chunk_index": idx,
                    "page_number": metadata.get("page_number", 0),
                    "category": metadata.get("category", "other"),
                    "additional_info": str(metadata.get("additional_info", {})),
                }
            )

            # Add filename if provided
            if filename := user_metadata.get("filename"):
                metadata["filename"] = filename
            metadatas.append(metadata)
            embeddings_list.append(vector)

        # Add documents to collection
        self.collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings_list,
        )

        logger.info(f"Inserted {len(ids)} chunks into ChromaDB")
        return ids

    def load_text(self, text: str, **kwargs: Dict[str, Any]) -> Dict[str, str]:
        """
        Load a single text chunk into ChromaDB.
        """
        ids = self.load_data(text, split_doc=False, **kwargs)
        return {"ids": ids}

    @staticmethod
    def sanitize_vector(vector: list[float], precision: int = 10) -> list[float]:
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
    def clean_text(text: str) -> str:
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
        Process and load a list of documents into ChromaDB.
        """
        processed_docs: List[Document] = []
        embeddings = self.embeddings.embed_documents(
            [self.clean_text(doc.page_content) for doc in documents]
        )
        # Prepare data for ChromaDB
        ids = []
        documents_list = []
        metadatas = []
        embeddings_list = []
        for idx, (doc, vector) in enumerate(zip(processed_docs, embeddings)):
            doc_id = f"{doc.metadata.get('document_id')}_{idx}"
            ids.append(doc_id)
            documents_list.append(doc.page_content)
            metadata = {
                "document_id": doc.metadata.get("document_id"),
                "page_number": doc.metadata.get("page_number", 0),
                "category": doc.metadata.get("category", "other"),
                "chunk_index": idx,
                "additional_info": str(doc.metadata.get("additional_info", {})),
            }

            # Add filename if provided
            if filename := doc.metadata.get("filename"):
                metadata["filename"] = filename
            metadatas.append(metadata)
            embeddings_list.append(vector)
        # Load into ChromaDB
        if ids:
            logger.info(f"Loading {len(ids)} chunks into ChromaDB.")
            self.collection.add(
                ids=ids,
                documents=documents_list,
                metadatas=metadatas,
                embeddings=embeddings_list,
            )
        return ids

    def delete_document_from_vectorstore(
        self, document_id: str | None = None, filename: str | None = None
    ) -> bool:
        """
        Delete document and associated filenames from ChromaDB.
        """
        try:
            if document_id:
                # Delete by document_id
                where_clause = {"document_id": document_id}
            elif filename:
                # Delete by filename
                where_clause = {"filename": filename}
            else:
                raise ValueError("No document_id or filename provided")
            # Get documents to delete first
            results = self.collection.get(where=where_clause)
            if results["ids"]:
                self.collection.delete(ids=results["ids"])
                logger.info(f"Deleted {len(results['ids'])} documents from ChromaDB")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting data from ChromaDB: {e}")
            return False
