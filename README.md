# Agentic RAG HR System

An intelligent resume matching and candidate ranking system using LangGraph and DSPy for agentic retrieval-augmented generation.

## System Pipeline

1. **Job Description Retrieval**: Fetch relevant job descriptions from LanceDB based on query
2. **Query Builder**: Extract requirements and apply hard filters (experience, location, etc.)
3. **Vector Search**: Find candidates using semantic similarity
4. **Reranking**: Use Gemini embeddings for candidate reranking
5. **LLM Filtering**: Further refine candidates with LLM-based filtering
6. **Explanation Agent**: Generate explanations for top candidates

## Installation

```bash
# Install dependencies
pip install -e .

# Install development dependencies
pip install -e ".[dev]"
```

## Quick Start with LanceDB

1. **Set up your LanceDB API key**:
   ```bash
   cp env.example .env
   # Edit .env and add your LanceDB API key
   ```

2. **Load your job descriptions**:
   ```bash
   python scripts/load_jobs_to_lancedb.py
   ```

3. **Test the system**:
   ```bash
   python scripts/test_lancedb_search.py --query "design engineer"
   ```

## Usage

```python
from agentic_rag_hr.data.vector_store.lance_vector_store import LanceVectorStore
from agentic_rag_hr.core.agents.lance_job_retrieval_agent import LanceJobRetrievalAgent

# Initialize LanceDB
vector_store = LanceVectorStore(
    api_key="your_lance_api_key",
    database_name="hr_jobs"
)

agent = LanceJobRetrievalAgent(vector_store)

# Search for jobs
results = agent.retrieve_jobs("design engineer", top_k=5)
```