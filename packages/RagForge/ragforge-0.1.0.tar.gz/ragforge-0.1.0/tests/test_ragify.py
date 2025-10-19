# tests/test_ragify.py
import sys
import pathlib
import pytest
import asyncio
from unittest.mock import AsyncMock

#project root
sys.path.append(str(pathlib.Path(__file__).resolve().parent.parent))

from src.core.rag_pipeline import RAGPipeline

class DummyAdapter:
    async def generate_embedding(self, text):
        return [0.1, 0.2, 0.3]

    async def query(self, prompt):
        return f"Dummy response for: {prompt}"

@pytest.mark.asyncio
async def test_rag_pipeline(monkeypatch):
    pipeline = RAGPipeline()

    monkeypatch.setattr(pipeline.retriever_service.embedder_service, "adapter", DummyAdapter())

    dummy_retrieved = {
        "documents": [
            ["Dummy document content line 1", "Dummy document content line 2"]
        ]
    }
    monkeypatch.setattr(
        pipeline.retriever_service,
        "retrieve",
        AsyncMock(return_value=dummy_retrieved)
    )

    response = await pipeline.run("What is RAG?")
    assert response is not None
    assert isinstance(response, str)
