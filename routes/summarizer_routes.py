import uuid
import os
from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import StreamingResponse 
from typing import AsyncGenerator
import json

from controllers.GraphState import SummaryGenState
from controllers.SummarizerGenGraphController import stream_summarizer_graph as summarizer_graph
from langgraph.types import Command

router = APIRouter()

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_BASE_PATH = os.path.join(PROJECT_ROOT, "assets")

@router.post("/start_session_streaming")
async def start_summarization_session_streaming(asset_id: str = Body(..., embed=True)) -> StreamingResponse:
    """
    Starts a new summarization session for a given asset_id and streams graph events.
    This endpoint will stream JSON objects representing events from the graph execution.
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

    initial_state = SummaryGenState(
        context=context,
        summary="",
        old_summary="",
        feedback="",
        Main_Points=""
    )

    config = {"configurable": {"thread_id": thread_id}}

    async def event_stream() -> AsyncGenerator[str, None]:

        global_events = ["main_point_summarizer", "summarizer_writer", "summarizer_rewriter"]
        current_global_event = None
        initial_payload = {"thread_id": str(thread_id), "status": "starting_session"} 
        yield f'data: {json.dumps(initial_payload)}\n\n'
        try:            
            async for event in summarizer_graph.astream_events(initial_state, config=config, version="v2"):
               
                event_type = event["event"]
                event_name = event.get("name", "")
                event_data = {}
                if "data" in event:
                    raw_data = event.get("data", {})
                    if isinstance(raw_data, dict):
                        for k, v in raw_data.items():
                            if k == "input" and isinstance(v, Command):
                                event_data[k] = {"resume_value": v.resume if hasattr(v, "resume") else str(v)}
                            elif k == "chunk" and hasattr(v, 'content'):
                                event_data[k] = v
                            elif hasattr(v, "__dict__"):
                                event_data[k] = str(v)
                            else:
                                try:
                                    json.dumps(v)
                                    event_data[k] = v
                                except (TypeError, OverflowError):
                                    event_data[k] = str(v)
                    else:
                        event_data = {"value": str(raw_data)}
                
                payload_to_yield = {"event": event_type, "name": event_name, "thread_id": thread_id}

                # print(f"Processing event: {event_type} - {event_name}\n")
                # print(f"global event: {current_global_event}\n")

                if event_type == "on_chain_start":
                    payload_to_yield["status_update"] = f"Starting: {event_name}"
                    payload_to_yield["data"] = event_data.get("input")

                    if event_name in global_events:
                        current_global_event = event_name

                    yield f'data: {json.dumps(payload_to_yield)}\n\n'

                elif event_type == "on_chat_model_stream" and current_global_event in global_events:
                    chunk = event_data.get("chunk")

                    if chunk and chunk.content:
                        payload_to_yield["event"] = "token" 
                        payload_to_yield["token"] = chunk.content
                        payload_to_yield["status_update"] = current_global_event

                        yield f'data: {json.dumps(payload_to_yield)}\n\n'
                # elif event_type == "on_chain_end":
                #     payload_to_yield["status_update"] = f"Finished: {event_name}"
                #     payload_to_yield["data"] = event_data.get("output")
            
                #     if event_name == "main_point_summarizer" and event_data.get("output") and "Main_Points" in event_data["output"] :
                #         payload_to_yield["main_points"] = event_data["output"]["Main_Points"]                  
                #         print(f"Main Points: {payload_to_yield['main_points']}\n") # Debugging output
                #         yield f'data: {json.dumps(payload_to_yield)}\n\n'
                #     elif event_name == "summarizer_writer" and event_data.get("output") and "summary" in event_data["output"]:
                #         payload_to_yield["summary"] = event_data["output"]["summary"]
                #         print(f"Summary: {payload_to_yield['summary']}\n") # Debugging output
                #         yield f'data: {json.dumps(payload_to_yield)}\n\n'
                #     elif event_name == "summarizer_rewriter" and event_data.get("output") and "summary" in event_data["output"]:
                #         payload_to_yield["summary"] = event_data["output"]["summary"]
                #         payload_to_yield["old_summary"] = event_data["output"].get("old_summary", "")
                #         print(f"Rewritten Summary: {payload_to_yield['summary']}\n") # Debugging output
                #         yield f'data: {json.dumps(payload_to_yield)}\n\n'
                 
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            error_message = f"Error in summarization stream: {str(e)}"
            print(f"Error details: {error_details}")
            
            yield f'data: {json.dumps({
                "event": "error", 
                "thread_id": thread_id, 
                "detail": error_message,
                "error_type": e.__class__.__name__
            })}\n\n'
        finally:
            payload = {"event": "stream_end", "thread_id": str(thread_id), "status_update": "Stream ended"}
            yield f'data: {json.dumps(payload)}\n\n'

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@router.post("/provide_feedback_streaming")
async def provide_feedback_to_summarization_streaming(
    thread_id: str = Body(..., embed=True),
    feedback: str = Body(..., embed=True)
) -> StreamingResponse:
    config = {"configurable": {"thread_id": thread_id}}

    # print(f"Received feedback: {feedback} for thread: {thread_id}")

    async def event_stream() -> AsyncGenerator[str, None]:
        global_events = ["summarizer_rewriter"]
        current_global_event = None
        initial_payload = {"thread_id": thread_id, "status": "resuming_with_feedback"} 
        yield f'data: {json.dumps(initial_payload)}\n\n'
        try:
            resume_command = Command(resume=feedback)  
            async for event in summarizer_graph.astream_events(resume_command, config=config, version="v2"):
                event_type = event["event"]
                event_name = event.get("name", "")
                event_data = {}

                if "data" in event:
                    raw_data = event.get("data", {})
                    if isinstance(raw_data, dict):
                        for k, v in raw_data.items():
                            if k == "input" and isinstance(v, Command):
                                event_data[k] = {"resume_value": v.resume if hasattr(v, "resume") else str(v)}
                            elif k == "chunk" and hasattr(v, 'content'):
                                event_data[k] = v
                            elif hasattr(v, "__dict__"):
                                event_data[k] = str(v)
                            else:
                                try:
                                    json.dumps(v)
                                    event_data[k] = v
                                except (TypeError, OverflowError):
                                    event_data[k] = str(v)
                    else:
                        event_data = {"value": str(raw_data)}
                
                payload_to_yield = {"event": event_type, "name": event_name, "thread_id": thread_id}                
                # print(f"Resume feedback event: {event_type} - {event_name}")
                
                if event_type == "on_chain_start":
                    payload_to_yield["status_update"] = f"Starting: {event_name}"
                    input_data = event_data.get("input")
                    if isinstance(input_data, dict):
                        serializable_input = {}
                        for k, v in input_data.items():
                            try:
                                json.dumps(v)
                                serializable_input[k] = v
                            except (TypeError, OverflowError):
                                serializable_input[k] = str(v)
                        payload_to_yield["data"] = serializable_input
                    else:
                        payload_to_yield["data"] = str(input_data) if input_data is not None else None

                    if event_name in global_events:
                        current_global_event = event_name

                    yield f'data: {json.dumps(payload_to_yield)}\n\n'

                elif event_type == "on_chat_model_stream" and current_global_event in global_events:
                    chunk = event_data.get("chunk")

                    # print(f"Processing chat model stream event: {event_type} - {event_name}\n\n\n\n")

                    if chunk and chunk.content:
                        payload_to_yield["event"] = "token" 
                        payload_to_yield["token"] = chunk.content
                        payload_to_yield["status_update"] = current_global_event

                        yield f'data: {json.dumps(payload_to_yield)}\n\n'    
        
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            error_message = f"Error in feedback stream: {str(e)}"

            print(f"Error details: {error_details}")

            yield f'data: {json.dumps({
                "event": "error", 
                "thread_id": thread_id, 
                "detail": error_message,
                "error_type": e.__class__.__name__
            })}\n\n'
        finally:
            payload = {"event": "stream_end", "thread_id": thread_id, "status_update": "Stream ended"}
            yield f'data: {json.dumps(payload)}\n\n'

    return StreamingResponse(event_stream(), media_type="text/event-stream")