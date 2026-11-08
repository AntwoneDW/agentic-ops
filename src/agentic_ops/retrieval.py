from pathlib import Path

from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings


RUNBOOK_PATH = Path("../../data/runbooks/checkout.md")


def load_runbook_documents() -> list[Document]:
    """
    Loads the local operations runbook into retrieval documents.

    The initial implementation uses manually defined sections so retrieval
    behavior remains explicit before introducing generalized text splitting.
    """
    runbook_text = RUNBOOK_PATH.read_text(encoding="utf-8")

    sections = [
        section.strip()
        for section in runbook_text.split("## ")
        if section.strip()
    ]

    return [
        Document(
            page_content=section,
            metadata={
                "source": str(RUNBOOK_PATH),
                "section_index": index,
            },
        )
        for index, section in enumerate(sections)
    ]


def build_runbook_store() -> InMemoryVectorStore:
    """
    Builds an in-memory semantic index over the operations runbook.

    The vector store is intentionally local for the first implementation.
    A persistent vector database can replace it later without changing the
    retrieval contract used by the agent.
    """
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small"
    )

    vector_store = InMemoryVectorStore(embeddings)

    vector_store.add_documents(
        documents=load_runbook_documents()
    )

    return vector_store


def search_runbook(query: str, k: int = 2) -> list[Document]:
    """
    Returns the runbook sections most semantically relevant to the query.
    """
    vector_store = build_runbook_store()

    return vector_store.similarity_search(
        query=query,
        k=k,
    )