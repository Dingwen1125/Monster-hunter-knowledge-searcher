# Monster Hunter LangGraph RAG Agent

This project builds a custom RAG agent with LangGraph over a small Monster Hunter PDF knowledge base.

## Setup

```bash
source .venv/bin/activate
cp .env.example .env
```

Edit `.env` and set `OPENAI_API_KEY`.

## Run

```bash
python monster_hunter_rag_agent.py "How should I fight Rathalos?"
```

The workflow matches the diagram:

```text
Prepare Query -> Rewrite -> Agent -> Should Retrieve -> Tool -> Check Relevance -> Generate -> Answer
                                      |
                                      No
                                      v
                                   Rewrite -> Agent
```

The agent follows the requested RAG setup:

1. Fetch and preprocess documents in `knowledge_base.py`.
2. Index preprocessed chunks for semantic search and create the retriever tool in `retriever.py`.
3. Build an agentic LangGraph RAG workflow in `graph.py`, where `nodes/agent.py` decides whether to call `nodes/retrieve_tool.py`.

The agent loads `knowledge_base/monster_hunter_field_guide.pdf`, embeds PDF chunks, retrieves relevant context, grades whether the retrieved chunks answer the question, optionally rewrites weak search queries, and generates an answer with citations.

## Project Structure

```text
monster_hunter_rag_agent.py  CLI entry point
graph.py                    LangGraph workflow assembly
state.py                    Shared RagState and Chunk types
config.py                   Model and knowledge-base settings
env.py                      Local .env loader
knowledge_base.py           Fetch and preprocess documents
retriever.py                Index documents and create retriever tool
nodes/agent.py              Agent node and should-retrieve route
nodes/prepare_query.py      Detects answer language
nodes/retrieve_tool.py      Retrieval tool node
nodes/check_relevance.py    Relevance grading node and route
nodes/rewrite_query.py      Query rewrite node
nodes/generate.py           Answer generation node
nodes/no_answer.py          Stops when PDF context is not relevant
```

Models:

- Chat / agent / rewrite / relevance grading / answer generation: `gpt-4.1-mini`
- Embeddings / vector retrieval: `text-embedding-3-small`

Questions in any language are converted to an English search query in the Rewrite
node for the English PDF knowledge base, then answered in the user's language.
