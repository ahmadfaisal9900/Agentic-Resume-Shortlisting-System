import logging
from agentic_hr.utils.env import LANCE_URI, LANCE_API_KEY, LANCE_REGION, DOCS_FOLDER, META_JSON_DIR, RESUME_CSV
from agentic_hr.components.jd_loader import load_job_descriptions
from agentic_hr.components.candidate_ingest import load_meta_docs, build_text_rows, CAND_TABLE, TEXT_TABLE
from agentic_hr.utils.chunker import chunk_job_descriptions
from agentic_hr.utils.vector_store import LanceDBManager
from agentic_hr.graphs.rag_graph import build_rag_graph
from langchain.schema import Document
from pathlib import Path
import pyarrow as pa

logging.basicConfig(level=logging.INFO)

def main():
    # 1. Load job descriptions from PDFs
    jobs = load_job_descriptions(Path(DOCS_FOLDER))
    docs = [Document(page_content=j["description"], metadata={"id": j["id"], "title": j["title"]}) for j in jobs]
    # 2. Chunk job descriptions
    chunks = chunk_job_descriptions(docs)
    logging.info(f"Split into {len(chunks)} chunks")
    # 3. Set up LanceDB and tables
    lancedb_mgr = LanceDBManager(LANCE_URI, LANCE_API_KEY, LANCE_REGION)
    db = lancedb_mgr.get_connection()
    embeddings = lancedb_mgr.get_embeddings()
    # (Re)create JD vector table
    if "job_descriptions" in db.table_names():
        db.drop_table("job_descriptions")
    from langchain_community.vectorstores import LanceDB as LC_LanceDB
    LC_LanceDB.from_documents(
        documents=chunks,
        embedding=embeddings,
        connection=db,
        table_name="job_descriptions",
        api_key=LANCE_API_KEY,
        region=LANCE_REGION,
        uri=LANCE_URI,
    )
    # (Re)create candidate metadata table
    meta_docs = load_meta_docs(META_JSON_DIR)
    print(f"Loaded {len(meta_docs)} metadata documents")
    if CAND_TABLE in db.table_names():
        db.drop_table(CAND_TABLE)
    LC_LanceDB.from_documents(
        documents=meta_docs,
        embedding=embeddings,
        connection=db,
        table_name=CAND_TABLE,
        mode="overwrite",
        api_key=LANCE_API_KEY,
        region=LANCE_REGION,
        uri=LANCE_URI,
    )
    # (Re)create resume text table
    text_rows = build_text_rows(RESUME_CSV)
    if TEXT_TABLE in db.table_names():
        db.drop_table(TEXT_TABLE)
    schema = pa.schema([
        pa.field("resume_id", pa.string()),
        pa.field("text", pa.large_string()),
    ])
    db.create_table(TEXT_TABLE, data=text_rows, schema=schema, mode="overwrite")
    # 4. Build and run the RAG graph
    app = build_rag_graph()
    user_query = input("Enter your HR/candidate matching query: ")
    rag_in = {"query": user_query}
    result_state = app.invoke(rag_in)
    print("Recommendation:\n", result_state.get("answer", "No answer."))
    print("Top IDs:", result_state.get("ranked_ids", [])[:5])
    print("Top scores:", [round(s, 4) for s in result_state.get("ranked_scores", [])[:5]])

if __name__ == "__main__":
    main()
