from agentic_hr.utils.chunker import chunk_job_descriptions
from langchain.schema import Document

def test_chunk_job_descriptions():
    docs = [Document(page_content="A" * 1200, metadata={"id": "doc1", "title": "Fake JD"})]
    chunks = chunk_job_descriptions(docs, chunk_size=500, chunk_overlap=100)
    assert len(chunks) >= 2  # should split into at least two chunks
    assert all(isinstance(c, Document) for c in chunks)
    # Check overlap: first chunk and second chunk should share some content
    assert chunks[0].page_content[-100:] == chunks[1].page_content[:100]
