import uuid
import os
import json
from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from typing import List, Dict, Any, Union

from controllers.GraphState import QuestionAnswerState
from controllers.QuestionAnswerGraphController import stream_qa_graph as qa_graph

router = APIRouter()

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_BASE_PATH = os.path.join(PROJECT_ROOT, "assets")

def serialize_message(message: BaseMessage) -> Dict[str, Any]:
    msg_dict = {"type": message.type, "content": message.content}
    if hasattr(message, 'additional_kwargs'):
        msg_dict["additional_kwargs"] = message.additional_kwargs
    if hasattr(message, 'name') and message.name is not None:
        msg_dict["name"] = message.name
    return msg_dict


@router.post("/start_session_stream")
async def start_qa_session_stream(asset_id: str = Body(..., embed=True), initial_question: str = Body(..., embed=True)):
    """
    Starts a new question answering session with streaming response
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

    initial_state = QuestionAnswerState(
        messages=[HumanMessage(content=initial_question)],
        relevant_text=[],
        on_topic="",
        context=context,
        conversation_history=[]
    )

    config = {"configurable": {"thread_id": thread_id}}
    
    async def generate():
        yield f"data: {json.dumps({'type': 'metadata', 'thread_id': thread_id, 'asset_id': asset_id})}\n\n"
        
        async for event in qa_graph.astream_events(initial_state, config=config, version="v2"):
            # print(f"Received chunk: {event}\n\n\n\n")

            if event["event"] == "on_chat_model_stream" and event["data"]["chunk"].content:
                # print(f"Streaming event: {event}")
                yield f"data: {json.dumps({'type': 'token', 'content': event['data']['chunk'].content})}\n\n"
            elif event["event"] == "on_chain_stream" and event.get("name", "") == "off_topic_response":
                messages = event["data"]["chunk"]["messages"]
                if messages and isinstance(messages[-1], AIMessage):
                    current_content = messages[-1].content
                    yield f"data: {json.dumps({'type': 'token', 'content': current_content})}\n\n"

        yield f"data: {json.dumps({'type': 'complete'})}\n\n"
    

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

@router.post("/continue_conversation_stream")
async def continue_qa_conversation_stream(
    thread_id: str = Body(..., embed=True),
    next_question: str = Body(..., embed=True)
):
    """
    Continues an existing question answering session with streaming response
    """
    config = {"configurable": {"thread_id": thread_id}}

    try:        
        current_graph_state_dict: Union[Dict[str, Any], None] = qa_graph.get_state(config)
        
        if current_graph_state_dict is None:
            raise HTTPException(status_code=404, detail=f"Session (thread_id: {thread_id}) not found or state is empty. Start a new session.")

        current_graph_state_dict = current_graph_state_dict.values
        previous_messages_raw = current_graph_state_dict.get("messages", [])
        previous_messages: List[BaseMessage] = []
        for msg_data in previous_messages_raw:
            if isinstance(msg_data, BaseMessage):
                previous_messages.append(msg_data)
            elif isinstance(msg_data, dict):
                if msg_data.get("type") == "human":
                    previous_messages.append(HumanMessage(content=msg_data["content"]))
                elif msg_data.get("type") == "ai":
                    previous_messages.append(AIMessage(content=msg_data["content"]))

        new_human_message = HumanMessage(content=next_question)
        updated_messages = previous_messages + [new_human_message]
        payload_for_graph = {
            "messages": updated_messages,
        }

        async def generate():
            yield f"data: {json.dumps({'type': 'metadata', 'thread_id': thread_id})}\n\n"
      
            async for event in qa_graph.astream_events(payload_for_graph, config=config, version="v2"):
                # print(f"Received chunk: {event}\n\n\n\n")

                if event["event"] == "on_chat_model_stream" and event["data"]["chunk"].content:
                    # print(f"Streaming event: {event}")
                    yield f"data: {json.dumps({'type': 'token', 'content': event['data']['chunk'].content})}\n\n"
                elif event["event"] == "on_chain_stream" and  event.get("name", "") == "off_topic_response":
                    yield f"data: {json.dumps({'type': 'token', 'content': event['data']['chunk']['messages'][-1].content})}\n\n"
            yield f"data: {json.dumps({'type': 'complete'})}\n\n"

        return StreamingResponse(
            generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
            }
        )

    except HTTPException as e:
        raise e 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error continuing Q&A conversation: {str(e)}")
