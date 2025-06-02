import uuid
import os
from fastapi import APIRouter, HTTPException, Body
from typing import Literal

from controllers.GraphState import QuestionGenState
from controllers.QuestionGenGraphController import qg_graph 

router = APIRouter()

ASSETS_DIR = "assets" 
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
ASSETS_BASE_PATH = os.path.join(PROJECT_ROOT, ASSETS_DIR)


@router.post("/start_session")
async def start_question_generation_session(
    asset_id: str = Body(..., embed=True),
    question_type: Literal["T/F", "MCQ"] = Body(..., embed=True)
):
    """
    Starts a new question generation session for a given asset_id and question_type.
    Returns the initial state of the graph, typically after the first interrupt for feedback.
    """
    thread_id = str(uuid.uuid4())
    context_file_path = os.path.join(ASSETS_BASE_PATH, asset_id, "extracted_text.txt")

    if not os.path.exists(context_file_path):
        raise HTTPException(status_code=404, detail=f"Asset text file not found for id: {asset_id}")

    try:
        with open(context_file_path, "r", encoding="utf-8") as f:
            context = f.read()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read context file: {str(e)}")

    initial_state = QuestionGenState(
        context=context,
        question_type=question_type,
        question="", # Will be populated by the graph
        options=None, # Will be populated by the graph
        answer="",    # Will be populated by the graph
        explanation="", # Will be populated by the graph
        history=[],
        feedback="" # Will be populated by user or auto-refinement
    )

    config = {"configurable": {"thread_id": thread_id}}

    try:
        current_graph_state = qg_graph.invoke(initial_state, config=config)   # Invoke the graph. It will run until the first interrupt        
        # The HumanFeedback node in QuestionGenGraphController is expected to call interrupt().

        data_for_feedback = {
            "generated_question": current_graph_state.get("question"),
            "options": current_graph_state.get("options"),
            "answer": current_graph_state.get("answer"),
            "explanation": current_graph_state.get("explanation"),
            "message": "Provide feedback or type 'auto' to automatically generate a new question or 'save' to finish" # Default message
        }
        
        return {
            "thread_id": thread_id,
            "status": "interrupted_for_feedback",
            "data_for_feedback": data_for_feedback,
            "current_state": current_graph_state 
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error invoking question generation graph: {str(e)}")


@router.post("/provide_feedback")
async def provide_feedback_to_question_generation(
    thread_id: str = Body(..., embed=True),
    feedback: str = Body(..., embed=True)
):
    """
    Provides feedback to an ongoing question generation session.
    Resumes the graph execution with the given feedback.
    """
    config = {"configurable": {"thread_id": thread_id}}

    resume_input = {"feedback": feedback} # The Router node in QuestionGenGraphController uses state["feedback"].

    try:
        current_graph_state = qg_graph.invoke(resume_input, config=config)

        # After this invoke, the graph might have:
        # 1. Reached another interrupt (e.g., looped back to HumanFeedback).
        # 2. Finished (e.g., user feedback was "save" and Router led to END).

        if feedback.lower() == "save": # 'save' leads to END (maybe add question to database)
            return {
                "thread_id": thread_id,
                "status": "completed",
                "final_state": current_graph_state
            }
        else:
            data_for_feedback = {  # If not "save", it's likely looped back for more feedback or refinement.
                "generated_question": current_graph_state.get("question"),
                "options": current_graph_state.get("options"),
                "answer": current_graph_state.get("answer"),
                "explanation": current_graph_state.get("explanation"),
                "message": "Provide feedback or type 'auto' to automatically generate a new question or 'save' to finish"
            }
            return {
                "thread_id": thread_id,
                "status": "interrupted_for_feedback",
                "data_for_feedback": data_for_feedback,
                "current_state": current_graph_state
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error resuming question generation graph: {str(e)}") 