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

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/CourseTA.git
   cd CourseTA
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your environment variables (API keys, etc.) in a `.env` file:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Usage

### Running the Application

Run the all-in-one launcher:

```bash
python run_app.py
```

On Windows, you can also use the PowerShell script:
```powershell
./run.ps1
```

This will start both the backend API server and the Gradio web interface.

- Backend API: http://127.0.0.1:8000
- Gradio UI: http://127.0.0.1:7860

### Alternative: Running Separately

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