from typing import TypedDict

from langchain_core.documents import Document


class RAGState(TypedDict):
    query: str
    docs: list[Document]
    context: str
    answer: str
    plan: dict
    candidate_ids: list[str]
    candidates_context: str
    candidate_snippets: list[str]
    ranked_ids: list[str]
    ranked_scores: list[float]
