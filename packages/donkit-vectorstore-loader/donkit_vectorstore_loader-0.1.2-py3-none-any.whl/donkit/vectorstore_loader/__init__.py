from langchain_core.embeddings import Embeddings

from .chroma_loader import ChromaVectorstoreLoader
from .milvus_loader import MilvusVectorstoreLoader
from .qdrant_loader import QdrantVectorstoreLoader
from .vectorstore_loader_abstract import VectorstoreLoaderAbstract

__all__ = [
    "VectorstoreLoaderAbstract",
    "ChromaVectorstoreLoader",
    "MilvusVectorstoreLoader",
    "QdrantVectorstoreLoader",
    "create_vectorstore_loader",
]


def create_vectorstore_loader(
    db_type: str,
    embeddings: Embeddings,
    collection_name: str = "my_collection",
    database_uri: str | None = None,
) -> VectorstoreLoaderAbstract:
    """
    Factory function to create a vectorstore loader based on database type.

    Args:
        db_type: Type of database ("qdrant", "milvus", "chroma")
        collection_name: Name of the collection
        embeddings: Embeddings instance
        database_uri: Database URI (optional, uses defaults if not provided)

    Returns:
        VectorstoreLoaderAbstract: Instance of the appropriate loader

    Raises:
        ValueError: If db_type is not supported

    Examples:
        >>> loader = create_vectorstore_loader(
        ...     db_type="qdrant",
        ...     collection_name="my_docs",
        ...     embeddings=embeddings,
        ...     database_uri="http://localhost:6333"
        ... )
    """
    if not db_type:
        raise ValueError("db_type cannot be None or empty")

    db_type = db_type

    match db_type:
        case "qdrant":
            return QdrantVectorstoreLoader(
                collection_name=collection_name,
                embeddings=embeddings,
                database_uri=database_uri or "http://localhost:6333",
            )
        case "milvus":
            return MilvusVectorstoreLoader(
                collection_name=collection_name,
                embeddings=embeddings,
                database_uri=database_uri or "http://localhost:19530",
            )
        case "chroma":
            return ChromaVectorstoreLoader(
                collection_name=collection_name,
                embeddings=embeddings,
                database_uri=database_uri or "http://localhost:8000",
            )
        case _:
            raise ValueError(
                f"Unsupported database type: {db_type}. "
                f"Supported types: 'qdrant', 'milvus', 'chroma'"
            )
