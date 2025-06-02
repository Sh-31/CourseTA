from langchain_huggingface import HuggingFaceEmbeddings
from .providers.LocalEmbeddingProvider import LocalEmbeddingProvider
from .Enums import EmbeddingEnums

class EmbeddingProviderFactory:
    def __init__(self, config: dict):
        self.config = config

    def create(self, provider: str, model_name: str = None):
        if provider == EmbeddingEnums.LOCAL_EMBEDDING.value:
            return LocalEmbeddingProvider()
        elif provider == EmbeddingEnums.HUGGINGFACE.value:
            return HuggingFaceEmbeddings(model_name=model_name)
        return None
