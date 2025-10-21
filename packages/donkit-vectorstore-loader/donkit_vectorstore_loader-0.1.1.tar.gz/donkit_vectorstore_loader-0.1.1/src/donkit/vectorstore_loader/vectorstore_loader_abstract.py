from abc import ABC
from abc import abstractmethod
from typing import Any
from uuid import UUID


class VectorstoreLoaderAbstract(ABC):
    @abstractmethod
    def load_text(self, text: str, **kwargs: dict[str, Any]) -> dict[str, str]:
        raise NotImplementedError

    @abstractmethod
    def load_documents(
        self,
        task_id: UUID,
        documents: list[Any],
    ) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def delete_document_from_vectorstore(
        self, document_id: str | None = None, filename: str | None = None
    ) -> bool:
        raise NotImplementedError
