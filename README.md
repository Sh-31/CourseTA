# CourseTA - AI Teaching Assistant

CourseTA is an AI-powered teaching assistant that helps educators process educational content, generate questions, create summaries, and build Q&A systems.

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
   git clone https://github.com/yourusername/CourseTA.git
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
   ollama pull qwen2.5:1.5b
   ```

5. Set up your environment variables (API keys, etc.) in a `.env` file.
 
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

## How to Use

1. **Upload Content**:
   - Go to the "Upload Content" tab
   - Upload a PDF document or audio/video file
   - Copy the generated Asset ID

2. **Generate Questions**:
   - Go to the "Question Generation" tab
   - Paste your Asset ID
   - Choose a question type (T/F or MCQ)
   - Click "Generate Question"
   - Provide feedback to refine the questions

3. **Summarize Content**:
   - Go to the "Content Summarization" tab
   - Paste your Asset ID
   - Click "Generate Summary"
   - View the main points and full summary

4. **Ask Questions**:
   - Go to the "Question Answering" tab
   - Paste your Asset ID
   - Ask questions about your content

## Architecture

CourseTA uses a microservice architecture:

- FastAPI backend for API endpoints
- LangGraph-based processing pipelines
- Gradio frontend for user interface
- LangChain for LLM orchestration