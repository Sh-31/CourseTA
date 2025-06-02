from typing import Dict, List, Optional, Any, Callable, Union
from langchain_community.embeddings import HuggingFaceEmbeddings 
from langchain.embeddings.base import Embeddings

class HuggingFaceEmbedding(Embeddings): 
    def __init__(self, 
                       model_id: str = "sentence-transformers/all-MiniLM-L6-v2",
                       device: str = "cpu",
                       normalize_embeddings: bool = False,
                       embedding_size: int = 384):

        self.model_id = model_id
        self.device = device
        self.embedding_model: Optional[HuggingFaceEmbeddings] = None
        self.normalize_embeddings = normalize_embeddings

    def _init_model(self):
        """Initialize the embedding model."""
        hf = HuggingFaceEmbeddings(
            model_name=self.model_id,
            model_kwargs={'device': self.device},
            encode_kwargs={'normalize_embeddings': self.normalize_embeddings}
        )
        return hf
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of documents."""
        if not self.embedding_model:
            self.embedding_model = self._init_model()

        embeddings = [self.embed_query(doc) for doc in texts]

        return embeddings


    def embed_query(self, splites: str) -> List[float]:
        """Generate embedding for a single query text."""
        if not self.embedding_model:
            self.embedding_model = self._init_model()

        embeddings_texts = []   

        if isinstance(splites, str):
            splites = [splites]

        for query in splites:
            embeddings_texts.append(self.embed_query(query))

        return embeddings_texts