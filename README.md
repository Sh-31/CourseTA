# CourseTA - AI Teaching Assistant

CourseTA is an Agentic AI-powered teaching assistant that helps educators process educational content, generate questions, create summaries, and build Q&A systems.

## Features

- **File Upload**: Upload PDF documents or audio/video files for automatic text extraction
- **Question Generation**: Create True/False or Multiple Choice questions from your content
- **Content Summarization**: Extract main points and generate comprehensive summaries
- **Question Answering**: Ask questions and get answers specific to your uploaded content

## Requirements

- Python 3.9+
- Dependencies listed in `requirements.txt`
- FFmpeg (for audio/video processing)
- Ollama (optional, for local LLM support)

## Installation

1. Clone this repository:
   ```bash
   https://github.com/Sh-31/CourseTA.git
   cd CourseTA
   ```

2. Install FFmpeg:
   
   **Linux (Ubuntu/Debian):**
   ```bash
   sudo apt update
   sudo apt install ffmpeg
   ```

3. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

4. (Optional) Install Ollama for local LLM support:
   
   **Windows/macOS/Linux:**
   - Download and install from https://ollama.ai/
   - Or use the installation script:
   ```bash
   curl -fsSL https://ollama.ai/install.sh | sh
   ```
   
   **Pull the recommended model:**
   ```bash
   ollama pull qwen3:4b
   ```

5. Set up your environment variables (API keys, etc.) in a `.env` file.

   **Update `.env` with your credentials:**
   ```
   cp .env.example .env
   ```
## Usage

### Running the Application

1. Start the FastAPI backend:
   ```bash
   python main.py
   ```

2. In a separate terminal, start the Gradio UI:
   ```bash
   python gradio_ui.py
   ```

## Architecture

CourseTA uses a microservice architecture with agent-based workflows:

- **FastAPI backend** for API endpoints
- **LangChain-based processing pipelines** with multi-agent workflows
- **LangGraph** for LLM orchestration

### Agent Graph Architecture

CourseTA implements three main agent graphs, each designed with specific nodes, loops, and reflection mechanisms:

#### 1. Question Generation Graph
![Question Generation Graph](docs/question_generation_graph.png)

The Question Generation agent follows a human-in-the-loop pattern with reflection capabilities:

**Nodes:**
- **QuestionGenerator**: Initial question creation from content
- **HumanFeedback**: Human interaction node with interrupt mechanism
- **Router**: Decision node that routes based on feedback type
- **QuestionRefiner**: Automatic refinement using AI feedback
- **QuestionRewriter**: Manual refinement based on human feedback

**Flow:**
[Question Generation Graph Flow (LangGraph Studio)](docs/question_generation_graph_flow.mp4)
- Starts with question generation
- Enters human feedback loop with interrupt
- Router decides: `save` (END), `auto` (refiner), or `feedback` (rewriter)
- Both refiner and rewriter loop back to human feedback for continuous improvement

#### 2. Content Summarization Graph
![Summarization Graph](docs/summarization_graph.png)

The Summarization agent uses a two-stage approach with iterative refinement:

**Nodes:**
- **SummarizerMainPointNode**: Extracts key points and creates table of contents
- **SummarizerWriterNode**: Generates detailed summary from main points
- **UserFeedbackNode**: Human review and feedback collection
- **SummarizerRewriterNode**: Refines summary based on feedback
- **Router**: Routes to save or continue refinement

**Flow:**
[Summarization Graph Flow (LangGraph Studio)](docs/summarization_graph_flow.mp4)
- Sequential processing: Main Points → Summary Writer → User Feedback
- Feedback loop: Router directs to rewriter or completion
- Rewriter loops back to user feedback for iterative improvement

#### 3. Question Answering Graph
![Question Answer Graph](docs/question_answer_graph.png)

The Q&A agent implements intelligent topic classification and retrieval:

**Nodes:**
- **QuestionClassifier**: Analyzes question relevance and retrieves context
- **OnTopicRouter**: Routes based on question relevance to content
- **Retrieve**: Fetches relevant document chunks using semantic search
- **GenerateAnswer**: Creates contextual answers from retrieved content
- **OffTopicResponse**: Handles questions outside the content scope

**Flow:**
[Question Answer Graph Flow (LangGraph Studio)](docs/question_answer_graph_flow.mp4)

- Question classification with embedding-based relevance scoring
- Conditional routing: on-topic questions go through retrieval pipeline
- Off-topic questions receive appropriate redirect responses
- No loops - single-pass processing for efficiency

### Key Architectural Features

**Human-in-the-Loop Design:**
- Strategic interrupt points for human feedback
- Continuous refinement loops in generation and summarization
- User control over when to complete or continue refining

**Reflection Agent Architecture:**
- Feedback incorporation mechanisms
- History tracking for context preservation
- Iterative improvement through dedicated refiner/rewriter nodes

### Async API Architecture

CourseTA implements a comprehensive async API architecture that supports both synchronous and streaming responses, providing real-time user experiences and efficient resource utilization.

## API Documentation

### File Processing APIs

#### 1. Upload File
Upload PDF documents or audio/video files for text extraction and processing.

**URL:** `/upload_file/`

**Method:** `POST`

**Content-Type:** `multipart/form-data`

**Request Body:**
```
file: Upload file (PDF, audio, or video format)
```

**Response:**
```json
{
  "message": "File processed successfully",
  "id": "uuid-string",
  "text_path": "path/to/extracted_text.txt",
  "original_file_path": "path/to/original_file"
}
```

**Supported Formats:**
- **PDF**: `.pdf` files
- **Audio**: `.mp3`, `.wav` formats
- **Video**: `.mp4`, `.avi`, `.mov`, `.mkv`, `.flv` formats

---

#### 2. Get Extracted Text
Retrieve the processed text content for a given asset ID.

**URL:** `/get_extracted_text/{asset_id}`

**Method:** `GET`

**Path Parameters:**
- `asset_id`: The unique identifier returned from file upload

**Response:**
```json
{
  "asset_id": "uuid-string",
  "extracted_text": "Full text content..."
}
```

---

### Question Generation APIs

#### 3. Start Question Generation Session
Generate questions from uploaded content with human-in-the-loop feedback.

**URL:** `/api/v1/graph/qg/start_session`

**Method:** `POST`

**Request Body:**
```json
{
  "asset_id": "uuid-string",
  "question_type": "T/F" | "MCQ"
}
```

**Parameters:**
- `asset_id`: Asset ID from file upload (required)
- `question_type`: Question type - "T/F" for True/False or "MCQ" for Multiple Choice (required)

**Response:**
```json
{
  "thread_id": "uuid-string",
  "status": "interrupted_for_feedback",
  "data_for_feedback": {
    "generated_question": "string",
    "options": ["string"] | null,
    "answer": "string",
    "explanation": "string",
    "message": "string"
  },
  "current_state": {...}
}
```

---

#### 4. Provide Question Feedback
Provide feedback to refine generated questions or save the current question.

**URL:** `/api/v1/graph/qg/provide_feedback`

**Method:** `POST`

**Request Body:**
```json
{
  "thread_id": "uuid-string",
  "feedback": "string"
}
```

**Parameters:**
- `thread_id`: Session ID from start_session (required)
- `feedback`: Feedback text, "auto" for automatic refinement, or "save" to finish (required)

**Response:**
```json
{
  "thread_id": "uuid-string",
  "status": "completed" | "interrupted_for_feedback",
  "final_state": {...} | null
}
```

---

### Content Summarization APIs

#### 5. Start Summarization Session (Streaming)
Generate content summaries with real-time streaming output.

**URL:** `/api/v1/graph/summarizer/start_session_streaming`

**Method:** `POST`

**Content-Type:** `text/event-stream`

**Request Body:**
```json
{
  "asset_id": "uuid-string"
}
```

**Parameters:**
- `asset_id`: Asset ID from file upload (required)

**Streaming Response Events:**
```
data: {"thread_id": "uuid", "status": "starting_session"}
data: {"event": "token", "token": "text", "status_update": "main_point_summarizer"}
data: {"event": "token", "token": "text", "status_update": "summarizer_writer"}
data: {"event": "stream_end", "thread_id": "uuid", "status_update": "Stream ended"}
```

---

#### 6. Provide Summarization Feedback (Streaming)
Refine summaries based on user feedback with streaming responses.

**URL:** `/api/v1/graph/summarizer/provide_feedback_streaming`

**Method:** `POST`

**Content-Type:** `text/event-stream`

**Request Body:**
```json
{
  "thread_id": "uuid-string",
  "feedback": "string"
}
```

**Parameters:**
- `thread_id`: Session ID from start_session_streaming (required)
- `feedback`: Feedback text or "save" to finish (required)

**Streaming Response Events:**
```
data: {"thread_id": "uuid", "status": "resuming_with_feedback"}
data: {"event": "token", "token": "text", "status_update": "summarizer_rewriter"}
data: {"event": "stream_end", "thread_id": "uuid", "status_update": "Stream ended"}
```

---

### Question Answering APIs

#### 7. Start Q&A Session (Streaming)
Answer questions based on uploaded content with streaming responses.

**URL:** `/api/v1/graph/qa/start_session_stream`

**Method:** `POST`

**Content-Type:** `text/event-stream`

**Request Body:**
```json
{
  "asset_id": "uuid-string",
  "initial_question": "string"
}
```

**Parameters:**
- `asset_id`: Asset ID from file upload (required)
- `initial_question`: The first question to ask about the content (required)

**Streaming Response Events:**
```
data: {"type": "metadata", "thread_id": "uuid", "asset_id": "uuid"}
data: {"type": "token", "content": "answer text..."}
data: {"type": "complete"}
```

---

#### 8. Continue Q&A Conversation (Streaming)
Continue an existing Q&A session with follow-up questions.

**URL:** `/api/v1/graph/qa/continue_conversation_stream`

**Method:** `POST`

**Content-Type:** `text/event-stream`

**Request Body:**
```json
{
  "thread_id": "uuid-string",
  "next_question": "string"
}
```
**Streaming Response Events:**
```
data: {"type": "metadata", "thread_id": "uuid"}
data: {"type": "token", "content": "answer text..."}
data: {"type": "complete"}
```

---

### Headers for Streaming APIs

**Required Headers:**
```
Accept: text/event-stream
Cache-Control: no-cache
Connection: keep-alive
```