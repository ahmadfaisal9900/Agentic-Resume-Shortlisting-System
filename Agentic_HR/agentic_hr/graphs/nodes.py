from .rag_state import RAGState
from agentic_hr.utils.doc_reconstruct import reconstruct_full_docs
from agentic_hr.utils.vector_store import LanceDBManager
from agentic_hr.utils.env import LANCE_URI, LANCE_API_KEY, LANCE_REGION, GEMINI_API_KEY
from agentic_hr.utils.reranker import rerank_with_gemini
import os

CAND_TABLE = "candidates_meta"
TEXT_TABLE = "candidate_texts"
TOPK_RERANK = 10

lancedb_mgr = LanceDBManager(LANCE_URI, LANCE_API_KEY, LANCE_REGION)
db = lancedb_mgr.get_connection()
embeddings = lancedb_mgr.get_embeddings()

# Gemini/Google LLM client (API key from env)
from google import genai
client = genai.Client(api_key=GEMINI_API_KEY)
EMBEDDINGS_MODEL_ID = "gemini-embedding-001"

# To be implemented: import DSPy, helpers, reranker functions, etc.

# Node: Retrieve

def node_retrieve(state: RAGState) -> dict:
    from langchain_community.vectorstores import LanceDB as LC_LanceDB
    lancedb_mgr = LanceDBManager(LANCE_URI, LANCE_API_KEY, LANCE_REGION)
    db = lancedb_mgr.get_connection()
    embeddings = lancedb_mgr.get_embeddings()
    vector_store = LC_LanceDB(
        connection=db,
        embedding=embeddings,
        table_name="job_descriptions",
        api_key=LANCE_API_KEY,
        region=LANCE_REGION,
        uri=LANCE_URI
    )
    retriever = vector_store.as_retriever(
        search_kwargs={"k": 10, "fetch_k": 20}
    )
    q = state["query"]
    # Use .invoke() for compatibility with newer LangChain versions
    docs = retriever.invoke(q)
    from agentic_hr.utils.doc_reconstruct import reconstruct_full_docs
    full_docs = reconstruct_full_docs(docs)
    context = full_docs[0] if full_docs else "No relevant document found."
    return {"docs": docs, "context": context}

# Node: Plan from JD

def node_plan_from_jd(state: RAGState) -> dict:
    jd_text = state.get("context") or ""
    plan = {
        "jd_embedding": embeddings.embed_query(jd_text),
        "k_candidates": 30,
        "indexes": ["candidates_meta"],
    }
    return {"plan": plan}

# Node: Placeholder, more to fill in as utils are split

def _quote(vals):
    return ", ".join(repr(str(v)) for v in vals if v is not None and str(v) != "")

def _fetch_texts_by_ids(resume_ids):
    if not resume_ids:
        return []
    tbl = db.open_table(TEXT_TABLE)
    id_filter = f"resume_id IN ({_quote(resume_ids)})"
    rows = (
        tbl.search()
           .where(id_filter)
           .select(["resume_id", "text"])
           .limit(len(resume_ids) * 2)
           .to_list()
    )
    id_to_text = {}
    for r in rows:
        rid = str(r.get("resume_id", "")).strip()
        txt = (r.get("text") or "").strip()
        if rid and rid not in id_to_text:
            id_to_text[rid] = txt
    return [id_to_text.get(str(rid), "") for rid in resume_ids]

def node_pool_candidates(state: RAGState) -> dict:
    plan = state["plan"]
    k = int(plan.get("k_candidates", 30))
    jd_vec = plan["jd_embedding"]

    from langchain_community.vectorstores import LanceDB as LC_LanceDB
    cand_store = LC_LanceDB(connection=db, embedding=embeddings, table_name=CAND_TABLE,
                         api_key=LANCE_API_KEY, region=LANCE_REGION, uri=LANCE_URI)
    hits = cand_store.similarity_search_by_vector(jd_vec, k=k)

    ids, meta_lines = [], []
    for h in hits:
        md = h.metadata or {}
        rid = str(md.get("resume_id", "")).strip()
        name = (md.get("candidate_name") or "").strip()
        title = (md.get("job_title") or "").strip()
        uni = (md.get("university") or "").strip()
        ids.append(rid or f"{name}|{title}")
        meta_lines.append(f"- {name} | {title} | {uni} | id={rid or 'n/a'}")

    resume_texts = _fetch_texts_by_ids(ids)
    snippets = [(t[:4000] if len(t) > 4000 else t) for t in resume_texts]

    return {
        "candidate_ids": ids,
        "candidate_snippets": snippets,
        "candidates_context": "\n".join(meta_lines[:100]) if meta_lines else "No matching candidates found."
    }

def node_rerank(state: RAGState) -> dict:
    q = state["query"]
    snippets = state.get("candidate_snippets", []) or []
    idxs, scores = rerank_with_gemini(q, snippets, client, EMBEDDINGS_MODEL_ID, top_k=TOPK_RERANK)
    ids = state.get("candidate_ids", [])
    ranked_ids = [ids[i] for i in idxs] if ids else []
    ranked_snippets = [snippets[i][:1200] for i in idxs]
    return {
        "ranked_ids": ranked_ids,
        "ranked_scores": scores,
        "candidates_context": "\n\n---\n\n".join(ranked_snippets) if ranked_snippets else ""
    }

# DSPy integration: placeholder AnswerJD signature and predict module
try:
    import dspy
except ImportError:
    dspy = None
    AnswerJD = None

def node_generate(state: RAGState) -> dict:
    # Set up DSPy Gemini LM (every call OK, idempotent)
    import dspy
    dspy.configure(lm=dspy.LM("gemini/gemini-2.5-flash", api_key=GEMINI_API_KEY))
    # Get top candidates and their scores
    top_ids = state.get("ranked_ids", [])[:3]
    top_scores = state.get("ranked_scores", [])[:3]
    snippets = state.get("candidate_snippets", [])
    context_lines = []
    for i, (candidate_id, score) in enumerate(zip(top_ids, top_scores)):
        if i < len(snippets):
            context_lines.append(f"Candidate {i+1} (Score: {score:.3f}): {snippets[i]}")
    context = "\n".join([
        "Top Candidates for Your Review:",
        "--------------------------------",
        *context_lines,
        "\nQuery: " + state["query"]
    ])
    class AnswerJD(dspy.Signature):
        context: str = dspy.InputField(desc="Candidate information and their scores")
        query: str = dspy.InputField(desc="Query about candidate recommendations")
        answer: str = dspy.OutputField(desc="Structured answer explaining top candidates and reasoning")
    dspy_module = dspy.Predict(AnswerJD)
    pred = dspy_module(
        context=context,
        query="Analyze these candidates and recommend the best match, explaining why. Consider their roles, experience, and match scores."
    )
    answer = getattr(pred, "answer", "").strip()
    return {"answer": answer}
