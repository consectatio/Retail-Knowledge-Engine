# Retail Knowledge Engine
>This project was made for learning purposes, as I wanted to try to make a graph database and practice my embedding and RAG skills.

A local Graph RAG system for querying retail data using a graph + vector search + LLM pipeline, running entirely on-device via Ollama.

The system was built around this dataset (https://www.kaggle.com/datasets/vijayuv/onlineretail)

## Architecture
```
CSV Data → Graph (NetworkX) → Vector Embeddings → Query → LLM Answer
```

## How It Works

1. Reads `data/online_retail.csv` into a DataFrame
2. Builds a knowledge graph from the data
3. Prompts you to select a language model and embedding model from your local Ollama installs
4. Embeds the graph nodes into a vector database
5. Enters a query loop — type questions, get answers

## File Overview

- **`graph.py`** — Builds a NetworkX graph where nodes represent invoices, products, customers, and countries. Edges capture purchase/return relationships, quantities, and prices. The `traverse()` function walks from a product node outward to collect stats like average price, quantity, return rate, and buyer countries.
- **`embedding.py`** — Embeds graph node data using the chosen Ollama embedding model and stores vectors locally for semantic search.
- **`LLM.py`** — Handles model selection (language + embedding) from your Ollama installs, and sends graph traversal context + your query to the LLM with a retail analyst system prompt.
- **`engine.py`** — Orchestrates the full pipeline: read → build graph → embed → query loop.
- **`run.py`** — Entry point.

## Requirements

- [Ollama](https://ollama.com/) running locally with at least:
  - One language model (e.g. `llama3`)
  - One embedding model (e.g. `nomic-embed-text`)

## Setup
```
pip install pandas networkx matplotlib tqdm ollama
python run.py
```
