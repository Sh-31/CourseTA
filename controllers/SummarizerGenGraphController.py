import os
import sys
sys.path.append(os.path.dirname(os.path.dirname( os.path.abspath(__file__))))

from helper import get_settings
from llm import LLMProviderFactory
from chains import SummarizerGenPrompt, SummarizerRewriterPrompt, SummarizerMainPointPrompt

from .GraphState import SummaryGenState
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt 

config = get_settings()

def SummarizerMainPointNode(state: SummaryGenState) -> SummaryGenState:
    llm = LLMProviderFactory(config).create(
        config.SUMMARIZER_MAINPOINT_PROVIDER, 
        config.SUMMARIZER_MAINPOINT_MODEL_ID, 
        config.SUMMARIZER_MAINPOINT_TEMPERATURE
    )
    summarizer_main_point_llm = SummarizerMainPointPrompt | llm
    response = summarizer_main_point_llm.invoke({"context": state["context"]})

    state["Main_Points"] = response

    return state


async def SummarizerMainPointNodeStream(state: SummaryGenState) -> SummaryGenState:

    llm = LLMProviderFactory(config).create(
        config.SUMMARIZER_MAINPOINT_PROVIDER, 
        config.SUMMARIZER_MAINPOINT_MODEL_ID, 
        config.SUMMARIZER_MAINPOINT_TEMPERATURE
    )
    summarizer_main_point_llm = SummarizerMainPointPrompt | llm
    response = await summarizer_main_point_llm.ainvoke({"context": state["context"]})

    state["Main_Points"] = response.content if hasattr(response, 'content') else str(response)

    return state

def SummarizerWriterNode(state: SummaryGenState) -> SummaryGenState:
    llm = LLMProviderFactory(config).create(
        config.SUMMARIZER_WRITER_PROVIDER, 
        config.SUMMARIZER_WRITER_MODEL_ID, 
        config.SUMMARIZER_WRITER_TEMPERATURE
    )
    summarizer_writer_llm = SummarizerGenPrompt | llm
    response = summarizer_writer_llm.invoke({"context": state["context"], "table_of_contents": state["Main_Points"]})

    state["summary"] = response

    return state

async def SummarizerWriterNodeStream(state: SummaryGenState) -> SummaryGenState:

    llm = LLMProviderFactory(config).create(
        config.SUMMARIZER_WRITER_PROVIDER, 
        config.SUMMARIZER_WRITER_MODEL_ID, 
        config.SUMMARIZER_WRITER_TEMPERATURE
    )
    summarizer_writer_llm = SummarizerGenPrompt | llm
    response = await summarizer_writer_llm.ainvoke({"context": state["context"], "table_of_contents": state["Main_Points"]})

    state["summary"] = response.content if hasattr(response, 'content') else str(response)

    return state

def UserFeedbackNode(state: SummaryGenState) -> SummaryGenState:
    interrupt_payload = {
        "table_of_contents": state["Main_Points"],
        "summary": state["summary"],
        "message": "Provide feedback or type 'save' to finish",
        "waiting_for_input": True
    }
 
    user_input = interrupt(interrupt_payload)
    
    state["feedback"] = user_input
    
    return state

async def UserFeedbackNodeStream(state: SummaryGenState) -> SummaryGenState:
    print("DEBUG: UserFeedbackNode entered. Preparing interrupt_payload.") 
    interrupt_payload = {
        "table_of_contents": state["Main_Points"],
        "summary": state["summary"],
        "message": "Provide feedback or type 'save' to finish",
        "waiting_for_input": True
    }
    # print(f"DEBUG: Calling interrupt() with payload: {interrupt_payload}")
    
    # The interrupt function pauses execution and returns the value used to resume
    # when provide_feedback_streaming endpoint is called
    user_input = interrupt(interrupt_payload)
    
    # This next log should only appear AFTER the graph is successfully resumed
    # print(f"DEBUG: UserFeedbackNode resumed. Received feedback: {user_input}")
    state["feedback"] = user_input
    
    return state

def Router(state: SummaryGenState): 
    if state.get("feedback", "").lower() == "save":
        return  "save"
    else:
        return "feedback"

def SummarizerRewriterNode(state: SummaryGenState) -> SummaryGenState:
    state["old_summary"] = state["summary"] 

    llm = LLMProviderFactory(config).create(
        config.SUMMARIZER_REWRITER_PROVIDER, 
        config.SUMMARIZER_REWRITER_MODEL_ID, 
        config.SUMMARIZER_REWRITER_TEMPERATURE
    )
    summarizer_rewriter_llm = SummarizerRewriterPrompt | llm
    response = summarizer_rewriter_llm.invoke({
        "context": state["context"], 
        "original_summary": state["old_summary"],
        "user_feedback": state["feedback"]
    })
    
    state["summary"] = response.content if hasattr(response, 'content') else str(response)

    return state

async def SummarizerRewriterNodeStream(state: SummaryGenState) -> SummaryGenState:
    state["old_summary"] = state["summary"] 

    llm = LLMProviderFactory(config).create(
        config.SUMMARIZER_REWRITER_PROVIDER, 
        config.SUMMARIZER_REWRITER_MODEL_ID, 
        config.SUMMARIZER_REWRITER_TEMPERATURE
    )
    summarizer_rewriter_llm = SummarizerRewriterPrompt | llm
    response = await summarizer_rewriter_llm.ainvoke({
        "context": state["context"], 
        "original_summary": state["old_summary"],
        "user_feedback": state["feedback"]
    })
    
    state["summary"] = response.content if hasattr(response, 'content') else str(response)

    return state

stream_graph = StateGraph(SummaryGenState)

stream_graph.add_node("main_point_summarizer", SummarizerMainPointNodeStream)
stream_graph.add_node("summarizer_writer", SummarizerWriterNodeStream)
stream_graph.add_node("user_feedback", UserFeedbackNodeStream)
stream_graph.add_node("summarizer_rewriter", SummarizerRewriterNodeStream)

stream_graph.add_edge(START, "main_point_summarizer")
stream_graph.add_edge("main_point_summarizer", "summarizer_writer")
stream_graph.add_edge("summarizer_writer", "user_feedback")
stream_graph.add_conditional_edges("user_feedback", Router, {"save": END, "feedback": "summarizer_rewriter"})
stream_graph.add_edge("summarizer_rewriter", "user_feedback")

checkpointer = MemorySaver()
stream_summarizer_graph = stream_graph.compile(checkpointer=checkpointer)

graph = StateGraph(SummaryGenState)
graph.add_node("main_point_summarizer", SummarizerMainPointNode)
graph.add_node("summarizer_writer", SummarizerWriterNode)
graph.add_node("user_feedback", UserFeedbackNode)
graph.add_node("summarizer_rewriter", SummarizerRewriterNode)

graph.add_edge(START, "main_point_summarizer")
graph.add_edge("main_point_summarizer", "summarizer_writer")
graph.add_edge("summarizer_writer", "user_feedback")
graph.add_conditional_edges("user_feedback", Router, {"save": END, "feedback": "summarizer_rewriter"})
graph.add_edge("summarizer_rewriter", "user_feedback")

summarizer_graph = graph.compile()

# from IPython.display import display, Image
# display(Image(summarizer_graph.get_graph().draw_mermaid_png()))