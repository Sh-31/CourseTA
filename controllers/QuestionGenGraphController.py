import os
import sys
sys.path.append(os.path.dirname(os.path.dirname( os.path.abspath(__file__))))

from helper import get_settings
from llm import LLMProviderFactory
from chains import QuestionGenPrompt, QuestionRefinerPrompt, QuestionRewriterPrompt
from chains import Question, Feedback

from .GraphState import QuestionGenState

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import interrupt

config = get_settings()

def QuestionGenerator(state: QuestionGenState) -> QuestionGenState:

    llm = LLMProviderFactory(config).create(
        config.QUESTION_GENERATER_PROVIDER, 
        config.QUESTION_GENERATER_MODEL_ID, 
        config.QUESTION_GENERATER_TEMPERATURE
    )

    llm = llm.with_structured_output(Question)
    question_generation_llm = QuestionGenPrompt | llm
    response = question_generation_llm.invoke({"context": state["context"], "question_type": state["question_type"]})

    state["question"] = response.question
    state["options"] = response.options
    state["answer"] = response.answer
    state["explanation"] = response.explanation
    
    if state.get("history") is None:
        state["history"] = []

    return state

def HumanFeedback(state: QuestionGenState) -> QuestionGenState:
    
    human_feedback = interrupt(
        {
            "gernerated_question": state["question"],
            "options": state["options"],
            "answer": state["answer"],
            "explanation": state["explanation"],
            "message": "Provide feedback or type 'auto' to automatically generate a new question or 'save' to finish"
        }
    )
    
    state["feedback"] = human_feedback

    return state
    
def Router(state: QuestionGenState) -> str:
    if state["feedback"].lower() == "save":
        return "save"
    elif state["feedback"].lower() == "auto":
        return "auto"
    else:
        return "feedback"
    
def QuestionRefiner(state: QuestionGenState) -> QuestionGenState:

    llm = LLMProviderFactory(config).create(
        config.QUESTION_REFINER_PROVIDER,
        config.QUESTION_REFINER_MODEL_ID,
        config.QUESTION_REFINER_TEMPERATURE
    )

    llm = llm.with_structured_output(Feedback)
    question_refiner_llm = QuestionRefinerPrompt | llm
    response = question_refiner_llm.invoke({"context": state["context"], "question_type": state["question_type"], "question": state["question"], "options": state["options"], "answer": state["answer"], "explanation": state["explanation"]})

    state["feedback"] = response.feedback
    return state

def QuestionRewriter(state: QuestionGenState) -> QuestionGenState:

    llm = LLMProviderFactory(config).create(
        config.QUESTION_REWRITER_PROVIDER,
        config.QUESTION_REWRITER_MODEL_ID,
        config.QUESTION_REWRITER_TEMPERATURE
    )

    llm = llm.with_structured_output(Question)
    question_rewriter_llm = QuestionRewriterPrompt | llm

    GeneratedQuestionFormat = """Question_Type: {Question_Type}, Transcript: {Context}, Question: {Question}\nOptions: {Options}\nAnswer: {Answer}\nExplanation: {Explanation}"""
    NewQuestionFormat = """Question_Type: {Question_Type}, Question: {Question}\nOptions: {Options}\nAnswer: {Answer}\nExplanation: {Explanation}"""

    Original_Question = GeneratedQuestionFormat.format(
        Question_Type=state["question_type"],
        Context=state["context"],
        Question=state["question"],
        Options=state["options"],
        Answer=state["answer"],
        Explanation=state["explanation"]
    )
    
    response = question_rewriter_llm.invoke({"history": state["history"], "original_question": Original_Question, "feedback": state["feedback"]})
    
    state["question"] = response.question
    state["options"] = response.options
    state["answer"] = response.answer
    state["explanation"] = response.explanation

    New_Question = NewQuestionFormat.format(
        Question_Type=response.question_type,
        Question=response.question,
        Options=response.options,
        Answer=response.answer,
        Explanation=response.explanation
    )

    if len(state["history"]) > 0:
        state["history"].append(f"Orginal Question: {Original_Question}\n Feedback: {state['feedback']}\n New question: {New_Question}\n Generate only new question\n")
    else:
        state["history"].append(f"Feedback: {state['feedback']}\n New question: {New_Question}\n Generate only new question\n")
    
    return state

graph = StateGraph(QuestionGenState)

graph.add_node("question_gen", QuestionGenerator)
graph.add_node("question_refiner", QuestionRefiner)
graph.add_node("question_rewriter", QuestionRewriter)
graph.add_node("human_feedback", HumanFeedback)

graph.add_edge(START, "question_gen")
graph.add_edge("question_gen", "human_feedback")
graph.add_conditional_edges("human_feedback", Router, {"save": END, "auto": "question_refiner", "feedback": "question_rewriter"})

graph.add_edge("question_refiner", "question_rewriter")
graph.add_edge("question_rewriter", "human_feedback")

checkpointer = MemorySaver()
qg_graph = graph.compile(checkpointer=checkpointer)

graph = graph.compile() # for langgraph dev 
# from IPython.display import Image, display
# display(Image(graph.get_graph().draw_mermaid_png()))