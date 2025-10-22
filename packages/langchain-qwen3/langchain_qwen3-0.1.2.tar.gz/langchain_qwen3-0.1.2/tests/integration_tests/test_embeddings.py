"""Test Qwen3 embeddings."""

from typing import Type

from langchain_qwen3.embeddings import Qwen3Embeddings
from langchain_tests.integration_tests import EmbeddingsIntegrationTests


class TestQwen3EmbeddingsIntegration(EmbeddingsIntegrationTests):
    @property
    def embeddings_class(self) -> Type[Qwen3Embeddings]:
        return Qwen3Embeddings

    @property
    def embedding_model_params(self) -> dict:
        return {'model': 'Qwen/Qwen3-Embedding-0.6B', 'use_modelscope': True}
