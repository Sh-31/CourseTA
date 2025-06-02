from pydantic_settings import BaseSettings

class Settings(BaseSettings): 
    # API keys and tokens
    GROQ_API_KEY: str = None
    GOOGLE_API_KEY: str = None
    TAVILY_API_KEY: str = None
    HUGGING_FACE_HUB_TOKEN: str = None

    # LangSmith configuration
    LANGSMITH_TRACING: bool = False
    LANGSMITH_ENDPOINT: str = None
    LANGSMITH_API_KEY: str = None
    LANGSMITH_PROJECT: str = None

    # Question Generation Agent configuration
    QUESTION_GENERATER_PROVIDER: str
    QUESTION_GENERATER_MODEL_ID: str
    QUESTION_GENERATER_TEMPERATURE: float

    QUESTION_REFINER_PROVIDER: str
    QUESTION_REFINER_MODEL_ID: str
    QUESTION_REFINER_TEMPERATURE: float

    QUESTION_REWRITER_PROVIDER: str
    QUESTION_REWRITER_MODEL_ID: str
    QUESTION_REWRITER_TEMPERATURE: float

    # Summarizer Agent configuration
    SUMMARIZER_MAINPOINT_PROVIDER: str
    SUMMARIZER_MAINPOINT_MODEL_ID: str
    SUMMARIZER_MAINPOINT_TEMPERATURE: float

    SUMMARIZER_WRITER_PROVIDER: str
    SUMMARIZER_WRITER_MODEL_ID: str
    SUMMARIZER_WRITER_TEMPERATURE: float

    SUMMARIZER_REWRITER_PROVIDER: str
    SUMMARIZER_REWRITER_MODEL_ID: str
    SUMMARIZER_REWRITER_TEMPERATURE: float

    # Question Answering Agent configuration
    GRADE_QA_PROVIDER: str
    GRADE_QA_MODEL_ID: str
    GRADE_QA_TEMPERATURE: float

    QUESTION_ANSWERER_PROVIDER: str
    QUESTION_ANSWERER_MODEL_ID: str
    QUESTION_ANSWERER_TEMPERATURE: float

    EMBEDDING_MODEL_ID: str
    EMBEDDING_MODEL_PROVIDER: str
    CHUNK_SIZE: int
    CHUNK_OVERLAP: int

    class Config:
        env_file = ".env"

def get_settings():
    return Settings()

def print_env_variables():
    settings = get_settings()
    for key, value in settings:
        print(f"{key}: {value}")