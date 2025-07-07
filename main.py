from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from routes import file_processing_routes
from routes import question_gen_routes
from routes import summarizer_routes
from routes import qa_routes
from dotenv import load_dotenv

load_dotenv() 
app = FastAPI(
    title="CourseTA API",
    version="1.0.0",
    description="API for CourseTA agentic system including preprocessing and graph-based agents."
)

# Add CORS middleware to allow requests from Gradio frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_v1_router = APIRouter(prefix="/api/v1")

# --- Direct Routes (no prefix) --- #
# Making the file_processing_routes accessible directly for easier Gradio integration
app.include_router(
    file_processing_routes.router,
    tags=["File Processing"]
)

# --- Preprocessing Routes --- #
api_v1_router.include_router(
    file_processing_routes.router, 
    prefix="/preprocessing", 
    tags=["Preprocessing"]
)

# --- Graph Agent Routes --- # 
graph_base_router = APIRouter(prefix="/graph", tags=["Graph Agents"])

graph_base_router.include_router(
    question_gen_routes.router,
    prefix="/qg",
    tags=["Question Generation Agent"]
)
graph_base_router.include_router(
    summarizer_routes.router,
    prefix="/summarizer",
    tags=["Summarization Agent"]
)
graph_base_router.include_router(
    qa_routes.router,
    prefix="/qa",
    tags=["Question Answering Agent"]
)

api_v1_router.include_router(graph_base_router)
app.include_router(api_v1_router)


@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to CourseTA API."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
