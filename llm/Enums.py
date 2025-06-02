from enum import Enum

class LLMEnums(Enum):
    OLLAMA = "OLLAMA"
    GOOGLE_GENAI = "GOOGLE_GENAI"
    GROQ = "GROQ"
    
class EmbeddingEnums(Enum):
    LOCAL_EMBEDDING = "LOCAL_EMBEDDING"
    HUGGINGFACE = "HUGGINGFACE"    

