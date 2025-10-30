from langgraph.graph import StateGraph, END
from .rag_state import RAGState
from .nodes import node_retrieve, node_plan_from_jd, node_pool_candidates, node_rerank, node_generate


def build_rag_graph():
    graph = StateGraph(RAGState)
    graph.add_node("retrieve", node_retrieve)
    graph.add_node("plan_from_jd", node_plan_from_jd)
    graph.add_node("pool_candidates", node_pool_candidates)
    graph.add_node("rerank", node_rerank)
    graph.add_node("generate", node_generate)

    graph.set_entry_point("retrieve")
    graph.add_edge("retrieve", "plan_from_jd")
    graph.add_edge("plan_from_jd", "pool_candidates")
    graph.add_edge("pool_candidates", "rerank")
    graph.add_edge("rerank", "generate")
    graph.add_edge("generate", END)
    return graph.compile()
