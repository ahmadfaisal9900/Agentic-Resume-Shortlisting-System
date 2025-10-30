def reconstruct_full_docs(chunks):
    docs_map = {}
    for chunk in chunks:
        doc_id = chunk.metadata['id']
        if doc_id not in docs_map:
            docs_map[doc_id] = []
        docs_map[doc_id].append(chunk.page_content)
    return [" ".join(chunks) for chunks in docs_map.values()]
