# Agentic HR (Production Structure)

This directory contains the production-ready implementation of the Agentic HR (Retrieval-Augmented Generation) system, ported from the research notebook.

## Directory Structure

- `agentic_hr/` — Main package for core source code.
    - `utils/` — Utilities: environment loading, LanceDB setup, vector store management, chunking, doc reconstructions, etc.
    - `components/` — Data loading and ingestion components (e.g., JD loader, candidate ingestion, etc.)
    - `graphs/` — Graph definitions and node logic (DSPy, LangGraph integration, RAG pipeline nodes, etc.)
    - `pipeline/` — Scripts and logic to initialize and run the pipeline end-to-end.
- `scripts/` — Entry points, CLI tools, and orchestration scripts for training, serving, etc.
- `config/` — YAML, environment, and external configuration files.
- `data/` — Place to store local input/output data files (not persisted in git).
- `tests/` — Unittests and validation scripts.

## Setup

- Install dependencies: `pip install -r requirements.txt`
- Place `.env` with secret keys and config in project root or env.
- Main environment/config handled by `utils/env.py`.

## Migration

All research prototype logic previously in `HR_RAG_System.ipynb` is now split into:
- Modular utility and pipeline files
- Production-grade layout for easier extension, testing, and deployment
