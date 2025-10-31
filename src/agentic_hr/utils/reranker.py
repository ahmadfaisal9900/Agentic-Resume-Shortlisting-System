import numpy as np

# Assume the Google Gemini API client/model is initialized elsewhere and imported as `client` and EMBEDDINGS_MODEL_ID.


def _embed_batch(texts, client, EMBEDDINGS_MODEL_ID):
    # Gemini batch embed; returns array shape [N, D]
    resp = client.models.embed_content(
        model=EMBEDDINGS_MODEL_ID,
        contents=texts,
    )
    embs = resp.embeddings
    return np.vstack([np.asarray(e.values, dtype=np.float32) for e in embs])


def _cosine_sim_matrix(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    A = A / (np.linalg.norm(A, axis=1, keepdims=True) + 1e-12)
    B = B / (np.linalg.norm(B, axis=1, keepdims=True) + 1e-12)
    return A @ B.T


def rerank_with_gemini(
    query: str, docs: list[str], client, EMBEDDINGS_MODEL_ID, top_k: int | None = None
):
    if not docs:
        return [], []
    q_vec = _embed_batch([query], client, EMBEDDINGS_MODEL_ID)  # shape [1, d]
    d_vecs = _embed_batch(docs, client, EMBEDDINGS_MODEL_ID)  # [N, d]
    sims = _cosine_sim_matrix(d_vecs, q_vec)  # [N, 1]
    scores = sims[:, 0]
    order = np.argsort(-scores)
    if top_k is not None:
        order = order[:top_k]
    return order.tolist(), scores[order].tolist()
