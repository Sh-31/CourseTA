from typing import Dict, List, Optional, Any, Callable, Union
import numpy as np
import os
from sentence_transformers import SentenceTransformer, models
from langchain.embeddings.base import Embeddings # Import the base class

class LocalEmbeddingProvider(Embeddings): # Inherit from Embeddings
    def __init__(self, 
                       model_id: str = "sentence-transformers/all-MiniLM-L6-v2",
                       embedding_size: int = 384):

        self.model_id = model_id
        self.embedding_size = embedding_size
        self.embedding_model = self._init_model()
    
    def _init_model(self):
        """Initialize the embedding model."""
        transformer = models.Transformer(self.model_id, max_seq_length=128)
        pooling = models.Pooling(transformer.get_word_embedding_dimension(), pooling_mode="mean")
        normalize = models.Normalize()
        return SentenceTransformer(modules=[transformer, pooling, normalize])
        
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of documents."""
        if not self.embedding_model:
            self.embedding_model = self._init_model()
            
        embeddings = self.embedding_model.encode(texts, convert_to_numpy=True)
        
        return embeddings.tolist()

    def embed_query(self, text: str) -> List[float]:
        """Generate embedding for a single query text."""
        if not self.embedding_model:
            self.embedding_model = self._init_model()
            
        embedding = self.embedding_model.encode(text, convert_to_numpy=True)
        
        return embedding.tolist()

    # Deprecating the old embed_text method or adapting it if used elsewhere.
    # For now, let's comment it out to avoid confusion with Langchain's interface.
    # def embed_text(
    #     self, 
    #     text: Union[str, List[str]], 
    #     document_type: Optional[str] = None,
    #     model: Optional[str] = None
    # ) -> List[List[float]]:
    #     """Generate embeddings for the given texts."""
    #     if self.embedding_model is None:
    #         self.set_embedding_model(model) # This method was removed, adapt to _init_model
            
    #     if isinstance(text, str):
    #         # For a single string, embed_query is more appropriate
    #         # or ensure it's wrapped in a list if processed by embed_documents logic
    #         embeddings = self.embedding_model.encode([text], convert_to_numpy=True)
    #         return embeddings[0].tolist() # Return a single embedding
            
    #     # Generate embeddings for a list of texts
    #     embeddings = self.embedding_model.encode(text, convert_to_numpy=True)
        
    #     return embeddings.tolist()

    # The set_embedding_model method is replaced by initializing in __init__
    # def set_embedding_model(self, model_id: Optional[str] = None, embedding_size: Optional[int] = None):
    #     """Set up the embedding model with the specified parameters."""
    #     if model_id:
    #         self.model_id = model_id
    #     if embedding_size:
    #         self.embedding_size = embedding_size    
    #     self.embedding_model = self._init_model()
