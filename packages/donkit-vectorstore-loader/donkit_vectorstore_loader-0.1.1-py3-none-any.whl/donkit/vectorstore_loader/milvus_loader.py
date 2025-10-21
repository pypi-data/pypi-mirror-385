import re
from typing import Any
from uuid import UUID, uuid4

from langchain_core.embeddings import Embeddings
from loguru import logger
from pymilvus import MilvusClient, DataType

from .vectorstore_loader_abstract import VectorstoreLoaderAbstract


class MilvusVectorstoreLoader(VectorstoreLoaderAbstract):
    def __init__(
        self,
        collection_name: str,
        embeddings: Embeddings,
        database_uri: str = "http://localhost:19530",
    ) -> None:
        self.collection_name = collection_name
        self.embeddings = embeddings

        # Initialize Milvus client
        self.client = MilvusClient(
            uri=database_uri,
        )

        self.dimension = self._detect_dimension()
        self.collection = self._ensure_collection(collection_name)

    def _detect_dimension(self) -> int:
        """Detect vector dimension from embeddings."""
        test_vector = self.embeddings.embed_query("test")
        dimension = len(test_vector)
        logger.info(f"Detected embedding dimension: {dimension}")
        return dimension

    def _ensure_collection(self, name: str):
        """Create or get existing collection."""
        if self.client.has_collection(name):
            logger.info(f"Using existing Milvus collection: {name}")
        else:
            # Create collection with schema
            schema = self.client.create_schema(
                auto_id=False,
                enable_dynamic_field=True,
            )
            schema.add_field(
                field_name="id",
                datatype=DataType.VARCHAR,
                max_length=256,
                is_primary=True,
            )
            schema.add_field(
                field_name="vector", datatype=DataType.FLOAT_VECTOR, dim=self.dimension
            )
            schema.add_field(
                field_name="text", datatype=DataType.VARCHAR, max_length=65535
            )
            schema.add_field(
                field_name="document_id", datatype=DataType.VARCHAR, max_length=256
            )
            schema.add_field(field_name="chunk_index", datatype=DataType.INT64)
            schema.add_field(field_name="page_number", datatype=DataType.INT64)
            schema.add_field(
                field_name="category", datatype=DataType.VARCHAR, max_length=256
            )
            schema.add_field(
                field_name="additional_info", datatype=DataType.VARCHAR, max_length=2048
            )
            schema.add_field(
                field_name="filename", datatype=DataType.VARCHAR, max_length=512
            )

            # Create index
            index_params = self.client.prepare_index_params()
            index_params.add_index(
                field_name="vector",
                index_type="IVF_FLAT",
                metric_type="COSINE",
                params={"nlist": 128},
            )

            self.client.create_collection(
                collection_name=name,
                schema=schema,
                index_params=index_params,
            )
            logger.info(f"Created Milvus collection: {name}")

        return name

    def load_text(self, text: str, **kwargs: dict[str, Any]) -> dict[str, str]:
        """
        Load a single text chunk into Milvus.
        """
        document_id = kwargs.get("document_id") or str(uuid4())
        user_metadata = kwargs.get("metadata", {})

        # Generate embedding
        embeddings = self.embeddings.embed_documents([text.strip()])

        doc_id = f"{document_id}_0"
        data = [
            {
                "id": doc_id,
                "vector": self._sanitize_vector(embeddings[0]),
                "text": text.strip(),
                "document_id": document_id,
                "chunk_index": 0,
                "page_number": user_metadata.get("page_number", 0),
                "category": user_metadata.get("category", "other"),
                "additional_info": str(user_metadata.get("additional_info", {})),
                "filename": user_metadata.get("filename", ""),
            }
        ]

        self.client.insert(
            collection_name=self.collection_name,
            data=data,
        )

        logger.info(f"Inserted text into Milvus collection '{self.collection_name}'")
        return {"ids": [doc_id]}

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
        documents: list[Any],
    ) -> list[str]:
        """
        Process and load a list of documents into Milvus.
        """
        if not documents:
            return []

        # Generate embeddings
        embeddings = self.embeddings.embed_documents(
            [self._clean_text(doc.page_content) for doc in documents]
        )

        # Prepare data for Milvus
        data = []
        ids = []
        for idx, (doc, vector) in enumerate(zip(documents, embeddings)):
            doc_id = f"{doc.id}_{idx}"
            ids.append(doc_id)

            data.append(
                {
                    "id": doc_id,
                    "vector": self._sanitize_vector(vector),
                    "text": doc.page_content,
                    "document_id": doc.id,
                    "chunk_index": idx,
                    "page_number": doc.metadata.get("page_number", 0),
                    "category": doc.metadata.get("category", "other"),
                    "additional_info": str(doc.metadata.get("additional_info", {})),
                    "filename": doc.metadata.get("filename", ""),
                }
            )

        # Load into Milvus
        if data:
            logger.info(f"Loading {len(data)} chunks into Milvus.")
            self.client.insert(
                collection_name=self.collection_name,
                data=data,
            )

        return ids

    def delete_document_from_vectorstore(
        self, document_id: str | None = None, filename: str | None = None
    ) -> bool:
        """
        Delete document from Milvus.
        """
        try:
            if document_id:
                filter_expr = f'document_id == "{document_id}"'
            elif filename:
                filter_expr = f'filename == "{filename}"'
            else:
                raise ValueError("No document_id or filename provided")

            self.client.delete(
                collection_name=self.collection_name,
                filter=filter_expr,
            )

            logger.info(
                f"Deleted document from Milvus collection '{self.collection_name}'"
            )
            return True
        except Exception as e:
            logger.error(f"Error deleting data from Milvus: {e}")
            return False
