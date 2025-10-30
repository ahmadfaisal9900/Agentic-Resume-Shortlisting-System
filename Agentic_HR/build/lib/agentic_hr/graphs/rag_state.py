from typing import List, TypedDict
from langchain.schema import Document

class RAGState(TypedDict):
    query: str
    docs: List[Document]
    context: str
    answer: str
    plan: dict
    candidate_ids: List[str]
    candidates_context: str
    candidate_snippets: List[str]
    ranked_ids: List[str]
    ranked_scores: List[float]
