import gradio as gr
import httpx
import json
from typing import List, Tuple

# API Configuration
API_BASE_URL = "http://127.0.0.1:8000"

# Custom CSS for clean, modern design
custom_css = """
.gradio-container {
    max-width: 1200px !important;
    margin: auto !important;
}

.tab-nav {
    background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
}

.upload-area {
    border: 2px dashed #e0e7ff !important;
    border-radius: 12px !important;
    background: #f8fafc !important;
    transition: all 0.3s ease !important;
}

.upload-area:hover {
    border-color: #4f46e5 !important;
    background: #f1f5f9 !important;
}

.status-success {
    background: #ecfdf5 !important;
    border: 1px solid #86efac !important;
    color: #166534 !important;
    padding: 12px !important;
    border-radius: 8px !important;
}

.status-error {
    background: #fef2f2 !important;
    border: 1px solid #fca5a5 !important;
    color: #991b1b !important;
    padding: 12px !important;
    border-radius: 8px !important;
}

.chat-container {
    max-height: 500px !important;
    overflow-y: auto !important;
}

.button-primary {
    background: linear-gradient(90deg, #4f46e5 0%, #7c3aed 100%) !important;
    border: none !important;
    color: white !important;
    border-radius: 8px !important;
    padding: 10px 20px !important;
    transition: all 0.3s ease !important;
}

.button-primary:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 12px rgba(79, 70, 229, 0.4) !important;
}
"""

class GradioUI:
    def __init__(self):
        self.question_session_state = {}
        self.summary_session_state = {}
        self.qa_session_state = {}    
    def upload_file(self, file) -> Tuple[str, str]:
        """Upload file and return asset ID and status message"""
        if file is None:
            return "", "❌ Please select a file to upload"
        
        try:
            # Set timeout for large file uploads (5 minutes)
            timeout = httpx.Timeout(300.0, connect=60.0)
            
            with httpx.Client(timeout=timeout) as client:
                with open(file.name, "rb") as f:
                    files = {"file": (file.name.split("/")[-1], f, "application/octet-stream")}
                    response = client.post(f"{API_BASE_URL}/upload_file/", files=files)
            
            if response.status_code == 200:
                result = response.json()
                asset_id = result["id"]
                return asset_id, f"✅ File uploaded successfully!\n📁 Asset ID: {asset_id}\n📄 File: {file.name.split('/')[-1]}"
            else:
                return "", f"❌ Upload failed: {response.text}"
                
        except httpx.TimeoutException:
            return "", "❌ Upload timed out. Please try with a smaller file or check your connection."
        except httpx.ConnectError:
            return "", "❌ Cannot connect to the API server. Please ensure the server is running."
        except Exception as e:
            return "", f"❌ Error uploading file: {str(e)}"    
    def start_question_session(self, asset_id: str, question_type: str) -> Tuple[str, str, str, str, str]:
        """Start a question generation session"""
        if not asset_id.strip():
            return "", "", "", "", "❌ Please enter an Asset ID"
        
        try:
            payload = {"asset_id": asset_id.strip(), "question_type": question_type}
            timeout = httpx.Timeout(60.0, connect=10.0)
            with httpx.Client(timeout=timeout) as client:
                response = client.post(f"{API_BASE_URL}/api/v1/graph/qg/start_session", json=payload)
         
            if response.status_code == 200:
                result = response.json()
                # print(f"Response from question generation: {result}")
                state = result

                # Store session state
                self.question_session_state = {
                    "thread_id": state["thread_id"],
                    "asset_id": asset_id.strip(),
                    "question_type": question_type
                }
                
                question = state["data_for_feedback"].get("generated_question", "")
                options = state["data_for_feedback"].get("options", [])
                answer = state["data_for_feedback"].get("answer", "")
                explanation = state["data_for_feedback"].get("explanation", "")

                # Format options for display
                options_text = "\n".join([f"{chr(65+i)}. {opt}" for i, opt in enumerate(options)]) if options else ""

                status = f"✅ Question generated successfully!\n🎯 Type: {question_type}\n🔗 Session ID: {state['thread_id']}..."
                return question, options_text, answer, explanation, status
            else:
                return "", "", "", "", f"❌ Failed to generate question: {response.text}"
                
        except httpx.TimeoutException:
            return "", "", "", "", "❌ Request timed out. Please try again."
        except httpx.ConnectError:
            return "", "", "", "", "❌ Cannot connect to the API server. Please ensure the server is running."       
        except Exception as e:
            return "", "", "", "", f"❌ Error generating question: {str(e)}"
    
    def update_question(self, feedback: str) -> Tuple[str, str, str, str, str]:
        """Update question based on feedback"""
        if not self.question_session_state:
            return "", "", "", "", "❌ No active session. Please start a new session first."
        
        if not feedback.strip():
            return "", "", "", "", "❌ Please provide feedback for the question"
        
        try:
            payload = {
                "thread_id": self.question_session_state["thread_id"],
                "feedback": feedback.strip()
            }
            timeout = httpx.Timeout(60.0, connect=10.0)
            with httpx.Client(timeout=timeout) as client:
                response = client.post(f"{API_BASE_URL}/api/v1/graph/qg/provide_feedback", json=payload)

            if response.status_code == 200:
                result = response.json()
                # print(f"Response from question update: {result}")
                state = result

                question = state["data_for_feedback"].get("generated_question", "")
                options = state["data_for_feedback"].get("options", [])
                answer = state["data_for_feedback"].get("answer", "")
                explanation = state["data_for_feedback"].get("explanation", "")

                options_text = "\n".join([f"{chr(65+i)}. {opt}" for i, opt in enumerate(options)]) if options else ""
                
                status = "✅ Question updated based on your feedback!"
                return question, options_text, answer, explanation, status
            else:
                return "", "", "", "", f"❌ Failed to update question: {response.text}"
                
        except httpx.TimeoutException:
            return "", "", "", "", "❌ Request timed out. Please try again."
        except httpx.ConnectError:
            return "", "", "", "", "❌ Cannot connect to the API server. Please ensure the server is running."
        except Exception as e:
            return "", "", "", "", f"❌ Error updating question: {str(e)}"
    def start_summary_session(self, asset_id: str):
        """Start a summary generation session with streaming"""
        if not asset_id.strip():
            return "", "", "❌ Please enter an Asset ID"
        
        try:
            payload = {"asset_id": asset_id.strip()}

            # Use streaming endpoint
            with httpx.Client(timeout=httpx.Timeout(300.0)) as client:
                with client.stream("POST", f"{API_BASE_URL}/api/v1/graph/summarizer/start_session_streaming", json=payload) as response:
                    if response.status_code != 200:
                        return "", "", f"❌ Failed to start summary session: {response.text}"
                    
                    main_points = ""
                    summary = ""
                    thread_id = ""
                    
                    for chunk in response.iter_text():
                        if chunk.strip():
                            if chunk.startswith("data: "):
                                chunk = chunk[6:]  # Remove 'data: ' prefix
                            
                            try:
                                event = json.loads(chunk)

                                if event.get("thread_id"):
                                    thread_id = event["thread_id"]
                                    self.summary_session_state = {
                                        "thread_id": thread_id,
                                        "asset_id": asset_id.strip()
                                    }
                                
                                if event.get("event") == "token" and event.get("status_update") == "main_point_summarizer":
                                    main_points += event["token"]
                                    yield main_points, summary, "🔄 Generating main points..."
                                
                                elif event.get("event") == "token" and event.get("status_update") == "summarizer_writer":
                                    summary += event["token"]
                                    yield main_points, summary, "🔄 Generating detailed summary..."

                            except json.JSONDecodeError as e:
                                print(f"JSON decode error: {e}, chunk: {chunk}")
                                continue

                    status = f"✅ Summary generated successfully!\n🔗 Session ID: {thread_id[:8]}..."
                    yield main_points, summary, status
                
        except Exception as e:
            yield "", "", f"❌ Error generating summary: {str(e)}"

    def update_summary(self, feedback: str):
        """Update summary based on feedback"""
        if not self.summary_session_state:
            yield "", "❌ No active session. Please start a new session first."
            return
        
        if not feedback.strip():
            yield "", "❌ Please provide feedback for the summary"
            return
        
        try:
            payload = {
                "thread_id": self.summary_session_state["thread_id"],
                "feedback": feedback.strip()
            }
            with httpx.Client(timeout=httpx.Timeout(300.0)) as client:
                with client.stream("POST", f"{API_BASE_URL}/api/v1/graph/summarizer/provide_feedback_streaming", json=payload) as response:
                    if response.status_code != 200:
                        yield "", f"❌ Failed to update summary: {response.text}"
                        return
                    summary = ""
                    
                    for chunk in response.iter_text():
                        if chunk.strip():                            
                            if chunk.startswith("data: "):
                                chunk = chunk[6:]
                            try:
                                event = json.loads(chunk)
                                
                                if event.get("event") == "token" and event.get("status_update") == "summarizer_rewriter":
                                    summary += event["token"]
                                    yield summary, "🔄 Updating summary based on feedback..."

                            except json.JSONDecodeError:
                                continue
                    
                    status = "✅ Summary updated based on your feedback!"
                    yield summary, status

        except Exception as e:
            yield "", f"❌ Error updating summary: {str(e)}"

    def start_qa_session_streaming(self, asset_id: str, question: str):
        """Start a Q&A session with streaming response"""
        if not asset_id.strip():
            yield [], "❌ Please enter an Asset ID"
            return
        
        if not question.strip():
            yield [], "❌ Please enter a question"
            return
        
        try:
            payload = {"asset_id": asset_id.strip(), "initial_question": question.strip()}
            
            with httpx.Client(timeout=httpx.Timeout(300.0)) as client:
                with client.stream("POST", f"{API_BASE_URL}/api/v1/graph/qa/start_session_stream", json=payload) as response:
                    if response.status_code != 200:
                        yield [], f"❌ Failed to start Q&A session: {response.text}"
                        return
                    
                    thread_id = ""
                    ai_response = ""
                    for chunk in response.iter_text():
                        if chunk.strip():
                            if chunk.startswith("data: "):
                                chunk = chunk[6:]  # Remove 'data: ' prefix
                            
                            try:
                                event = json.loads(chunk)

                                if event.get("type") == "metadata":
                                    thread_id = event.get("thread_id", "")
                                    self.qa_session_state = {
                                        "thread_id": thread_id,
                                        "asset_id": asset_id.strip()
                                    }
                                    yield [], f"🔄 Starting Q&A session... ID: {thread_id[:8]}..."
                                
                                elif event.get("type") == "token":
                                    ai_response += event.get("content", "")
                                    chat_history = [(question.strip(), ai_response)]
                                    yield chat_history, f"🔄 Generating response..."
                                
                                elif event.get("type") == "complete":
                                    chat_history = [(question.strip(), ai_response)]
                                    yield chat_history, f"✅ Q&A session started! ID: {thread_id[:8]}..."
                                
                                elif event.get("type") == "error":
                                    yield [], f"❌ Error: {event.get('content', 'Unknown error')}"
                                    return
                                    
                            except json.JSONDecodeError:
                                continue

        except Exception as e:
            yield [], f"❌ Error starting Q&A session: {str(e)}"

    def continue_qa_chat_streaming(self, message: str, history: List[Tuple[str, str]]):
        """Continue the Q&A conversation with streaming"""
        if not self.qa_session_state:
            yield history, "❌ No active session. Please start a new session first."
            return
        
        if not message.strip():
            yield history, "❌ Please enter a message"
            return
        
        try:
            payload = {
                "thread_id": self.qa_session_state["thread_id"],
                "next_question": message.strip()
            }
            
            with httpx.Client(timeout=httpx.Timeout(300.0)) as client:
                with client.stream("POST", f"{API_BASE_URL}/api/v1/graph/qa/continue_conversation_stream", json=payload) as response:
                    if response.status_code != 200:
                        yield history, f"❌ Failed to get response: {response.text}"
                        return
                    
                    ai_response = ""
                    for chunk in response.iter_text():
                        if chunk.strip():
                            if chunk.startswith("data: "):
                                chunk = chunk[6:]  # Remove 'data: ' prefix

                            try:
                                event = json.loads(chunk)

                                if event.get("type") == "token":
                                    ai_response += event.get("content", "")
                                    new_history = history + [(message.strip(), ai_response)]
                                    yield new_history, "🔄 Generating response..."
                                
                                elif event.get("type") == "complete":
                                    new_history = history + [(message.strip(), ai_response)]
                                    yield new_history, "✅ Response complete"
                                
                                elif event.get("type") == "error":
                                    yield history, f"❌ Error: {event.get('content', 'Unknown error')}"
                                    return
                                    
                            except json.JSONDecodeError:
                                continue

        except Exception as e:
            yield history, f"❌ Error in conversation: {str(e)}"

def create_gradio_interface():
    ui = GradioUI()
    
    with gr.Blocks(css=custom_css, title="CourseTA - AI Teaching Assistant", theme=gr.themes.Soft()) as app:
        gr.Markdown(
            """
            # 🎓 CourseTA - AI Teaching Assistant
            ### Upload content, generate questions, create summaries, and ask questions about your educational materials
            """,
            elem_classes="header"
        )
        
        with gr.Tabs():
            # Tab 1: File Upload
            with gr.Tab("📁 Upload Content", elem_id="upload-tab"):
                gr.Markdown("### Upload PDF documents or audio/video files for processing")
                
                with gr.Row():
                    with gr.Column(scale=2):
                        file_input = gr.File(
                            label="Select File",
                            file_types=[".pdf", ".mp3", ".mp4", ".wav", ".avi", ".mov", ".mkv", ".flv"],
                            elem_classes="upload-area"
                        )
                        upload_btn = gr.Button("🚀 Upload File", variant="primary", elem_classes="button-primary")
                    
                    with gr.Column(scale=1):
                        asset_id_display = gr.Textbox(
                            label="Generated Asset ID",
                            placeholder="Asset ID will appear here after upload...",
                            interactive=True,
                            lines=1
                        )
                        upload_status = gr.Markdown("📋 Ready to upload files")
                  # Event handlers for upload tab
                upload_btn.click(
                    fn=ui.upload_file,
                    inputs=[file_input],
                    outputs=[asset_id_display, upload_status]
                )
            
            # Tab 2: Question Generation
            with gr.Tab("❓ Question Generation", elem_id="question-tab"):
                gr.Markdown("### Generate questions from your uploaded content")
                
                with gr.Row():
                    with gr.Column(scale=1):
                        q_asset_id = gr.Textbox(
                            label="Asset ID",
                            placeholder="Enter or paste your Asset ID here...",
                            lines=1
                        )
                        question_type = gr.Radio(
                            choices=["T/F", "MCQ"],
                            label="Question Type",
                            value="MCQ"
                        )
                        generate_q_btn = gr.Button("🎯 Generate Question", variant="primary", elem_classes="button-primary")
                    
                    with gr.Column(scale=2):
                        question_display = gr.Textbox(
                            label="Generated Question",
                            lines=3,
                            interactive=False
                        )
                        options_display = gr.Textbox(
                            label="Answer Options",
                            lines=4,
                            interactive=False
                        )
                        answer_display = gr.Textbox(
                            label="Correct Answer",
                            lines=1,
                            interactive=False
                        )
                        explanation_display = gr.Textbox(
                            label="Explanation",
                            lines=3,
                            interactive=False
                        )
                
                with gr.Row():
                    feedback_input = gr.Textbox(
                        label="Feedback",
                        placeholder="Provide feedback to improve the question...",
                        lines=2
                    )
                    update_q_btn = gr.Button("🔄 Update Question", variant="secondary")
                
                q_status = gr.Markdown("📋 Ready to generate questions")
                  # Event handlers for question generation
                generate_q_btn.click(
                    fn=ui.start_question_session,
                    inputs=[q_asset_id, question_type],
                    outputs=[question_display, options_display, answer_display, explanation_display, q_status]
                )
                
                update_q_btn.click(
                    fn=ui.update_question,
                    inputs=[feedback_input],
                    outputs=[question_display, options_display, answer_display, explanation_display, q_status]
                )
            
            # Tab 3: Summarization
            with gr.Tab("📝 Content Summarization", elem_id="summary-tab"):
                gr.Markdown("### Create summaries and main points from your content")
                
                with gr.Row():
                    with gr.Column(scale=1):
                        s_asset_id = gr.Textbox(
                            label="Asset ID",
                            placeholder="Enter or paste your Asset ID here...",
                            lines=1
                        )
                        generate_s_btn = gr.Button("📊 Generate Summary", variant="primary", elem_classes="button-primary")
                        
                        summary_feedback = gr.Textbox(
                            label="Feedback",
                            placeholder="Provide feedback to improve the summary...",
                            lines=3
                        )
                        update_s_btn = gr.Button("🔄 Update Summary", variant="secondary")
                    
                    with gr.Column(scale=2):
                        main_points_display = gr.Textbox(
                            label="Main Points",
                            lines=6,
                            interactive=False
                        )
                        summary_display = gr.Textbox(
                            label="Detailed Summary",
                            lines=8,
                            interactive=False
                        )
                
                s_status = gr.Markdown("📋 Ready to generate summaries")
                  # Event handlers for summarization
                generate_s_btn.click(
                    fn=ui.start_summary_session,
                    inputs=[s_asset_id],
                    outputs=[main_points_display, summary_display, s_status]
                )
                
                update_s_btn.click(
                    fn=ui.update_summary,
                    inputs=[summary_feedback],
                    outputs=[summary_display, s_status]
                )
            
            # Tab 4: Question Answering Chat
            with gr.Tab("💬 Question Answering", elem_id="qa-tab"):
                gr.Markdown("### Ask questions about your uploaded content")
                
                with gr.Row():
                    with gr.Column(scale=1):
                        qa_asset_id = gr.Textbox(
                            label="Asset ID",
                            placeholder="Enter or paste your Asset ID here...",
                            lines=1
                        )
                        initial_question = gr.Textbox(
                            label="Initial Question",
                            placeholder="Ask your first question about the content...",
                            lines=2
                        )
                        start_qa_btn = gr.Button("🚀 Start Q&A Session", variant="primary", elem_classes="button-primary")
                        
                        qa_status = gr.Markdown("📋 Ready to start Q&A session")
                    
                    with gr.Column(scale=2):
                        chatbot = gr.Chatbot(
                            label="Conversation",
                            height=400,
                            elem_classes="chat-container"
                        )
                        
                        with gr.Row():
                            msg_input = gr.Textbox(
                                label="Your Message",
                                placeholder="Continue the conversation...",
                                lines=1,
                                scale=4
                            )
                            send_btn = gr.Button("📤 Send", variant="secondary", scale=1)                  # Event handlers for Q&A
                start_qa_btn.click(
                    fn=ui.start_qa_session_streaming,
                    inputs=[qa_asset_id, initial_question],
                    outputs=[chatbot, qa_status]
                )
                
                send_btn.click(
                    fn=ui.continue_qa_chat_streaming,
                    inputs=[msg_input, chatbot],
                    outputs=[chatbot, qa_status]
                ).then(
                    lambda: "",
                    outputs=[msg_input]
                )
                
                # Allow Enter key to send messages
                msg_input.submit(
                    fn=ui.continue_qa_chat_streaming,
                    inputs=[msg_input, chatbot],
                    outputs=[chatbot, qa_status]
                ).then(
                    lambda: "",
                    outputs=[msg_input]
                )
        
        gr.Markdown(
            """
            ---
            ### 💡 How to Use:
            1. **Upload**: Upload your PDF or video files to get an Asset ID
            2. **Questions**: Use the Asset ID to generate and refine questions
            3. **Summary**: Create main points and detailed summaries
            4. **Chat**: Have interactive conversations about your content
            """
        )
    
    return app

if __name__ == "__main__":
    app = create_gradio_interface()
    app.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        show_error=True
    )