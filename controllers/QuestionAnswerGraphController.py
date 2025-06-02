import os
import sys
sys.path.append(os.path.dirname(os.path.dirname( os.path.abspath(__file__))))

from helper import get_settings, text_splitter
from llm import LLMProviderFactory, EmbeddingProviderFactory

from chains import GradeQuestion, GradeQuestionPrompt
from .GraphState import QuestionAnswerState

from langchain_community.vectorstores import Chroma
from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.prompts import ChatPromptTemplate

config = get_settings()

def question_classifier(state: QuestionAnswerState) -> QuestionAnswerState: 
    if hasattr(state["messages"][-1], 'content'):
        question = state["messages"][-1].content
    else:    
        question = state["messages"][-1]["content"]

    if "conversation_history" not in state:
        state["conversation_history"] = []

    embedding = EmbeddingProviderFactory(config).create(config.EMBEDDING_MODEL_PROVIDER)

    texts = text_splitter(
        state["context"], 
        chunk_size=int(os.getenv("CHUNK_SIZE", 350)), 
        chunk_overlap=int(os.getenv("CHUNK_OVERLAP", 50))
    )

    retriever = Chroma.from_texts(
        texts, 
        embedding, 
    ).as_retriever(search_type="mmr", search_kwargs={"k": 5})

    state["relevant_text"] = retriever.invoke(question) 

    docs = "\n".join([doc.page_content for doc in state["relevant_text"]])
    llm = LLMProviderFactory(config).create(
        config.GRADE_QA_PROVIDER, 
        config.GRADE_QA_MODEL_ID, 
        config.GRADE_QA_TEMPERATURE
    )

    structured_llm = llm.with_structured_output(GradeQuestion)
    grader_llm = GradeQuestionPrompt | structured_llm
    result = grader_llm.invoke({"question": question, "docs": docs})
    
    state["on_topic"] = result.score

    return state

def on_topic_router(state: QuestionAnswerState): 
    on_topic = state["on_topic"]
    if on_topic.lower() == "yes":
        return "on_topic"
    return "off_topic"

def retrieve(state: QuestionAnswerState):
    return state

def generate_answer(state: QuestionAnswerState): 
    
    if hasattr(state["messages"][-1], 'content'):
        question = state["messages"][-1].content
    else:    
        question = state["messages"][-1]["content"]
    documents = state["relevant_text"] 

    if "conversation_history" not in state:
        state["conversation_history"] = []
    
    # Use conversation history for better context
    chat_history = state.get("conversation_history", [])

    template = """ 
Answer the question based only on the following context: {context},
chat history: {chat_history},
Question: {question}
"""

    prompt = ChatPromptTemplate.from_template(template)
    llm = LLMProviderFactory(config).create(
        config.QUESTION_ANSWERER_PROVIDER, 
        config.QUESTION_ANSWERER_MODEL_ID, 
        config.QUESTION_ANSWERER_TEMPERATURE
    )

    rag_chain = prompt | llm

    generation =  rag_chain.invoke({"context": documents, "chat_history": chat_history, "question": question})
    state["messages"].append(generation)
    
    state["conversation_history"] = state.get("conversation_history", []) + [
        state["messages"][-2],  
        generation              
    ]
    
    return state

async def generate_answer_streaming(state: QuestionAnswerState): 
    question = state["messages"][-1].content
    documents = state["relevant_text"] 
    
    if "conversation_history" not in state:
        state["conversation_history"] = []
    
    # Use conversation history for better context
    chat_history = state.get("conversation_history", [])

    template = """ 
Answer the question based only on the following context: {context},
chat history: {chat_history},
Question: {question}
"""

    prompt = ChatPromptTemplate.from_template(template)
    llm = LLMProviderFactory(config).create(
        config.QUESTION_ANSWERER_PROVIDER, 
        config.QUESTION_ANSWERER_MODEL_ID, 
        config.QUESTION_ANSWERER_TEMPERATURE
    )

    rag_chain = prompt | llm
    
    full_response = ""
    
    # Add empty AI message to start streaming
    state["messages"].append(AIMessage(content=""))
    

    try:
        async for chunk in rag_chain.astream({"context": documents, "chat_history": chat_history, "question": question}):
            if hasattr(chunk, 'content') and chunk.content:
                full_response += chunk.content
                state["messages"][-1] = AIMessage(content=full_response)
                yield state
    
    except Exception as e:
        print(f"Error in streaming: {e}")
      
    if state["messages"] and isinstance(state["messages"][-1], AIMessage):
        final_ai_message = state["messages"][-1]
        state["conversation_history"] = state.get("conversation_history", []) + [
            state["messages"][-2],  # The user's question
            final_ai_message        # The AI's response
        ]
    
    yield state

def off_topic_response(state: QuestionAnswerState): 
    state["messages"].append(AIMessage(content="I'm sorry! I cannot answer this question!"))
    return state

async def off_topic_response_streaming(state: QuestionAnswerState):
    """Streaming version of off-topic response"""
    response_text = "I'm sorry! I cannot answer this question!"
    state["messages"].append(AIMessage(content=""))
    
    print("Streaming off-topic response...")
    # Stream the off-topic message character by character
    for i, char in enumerate(response_text):
        state["messages"][-1] = AIMessage(content=response_text[i])
        yield state
    
    yield state


stream_graph = StateGraph(QuestionAnswerState)

stream_graph.add_node("topic_decision", question_classifier)
stream_graph.add_node("off_topic_response", off_topic_response_streaming)
stream_graph.add_node("retrieve", retrieve)
stream_graph.add_node("generate_answer_streaming", generate_answer_streaming)

stream_graph.add_conditional_edges(
    "topic_decision", 
    on_topic_router, 
    {
        "on_topic": "retrieve", 
        "off_topic": "off_topic_response"
    }
)

stream_graph.add_edge("retrieve", "generate_answer_streaming")
stream_graph.add_edge("generate_answer_streaming", END)
stream_graph.add_edge("off_topic_response", END)
stream_graph.add_edge(START, "topic_decision")

checkpointer = MemorySaver()
stream_qa_graph = stream_graph.compile(checkpointer=checkpointer)

qa_graph = StateGraph(QuestionAnswerState)

qa_graph.add_node("topic_decision", question_classifier)
qa_graph.add_node("off_topic_response", off_topic_response)
qa_graph.add_node("retrieve", retrieve)
qa_graph.add_node("generate_answer", generate_answer)

qa_graph.add_conditional_edges(
    "topic_decision", 
    on_topic_router, 
    {
        "on_topic": "retrieve", 
        "off_topic": "off_topic_response"
    }
)

qa_graph.add_edge("retrieve", "generate_answer")
qa_graph.add_edge("generate_answer", END)
qa_graph.add_edge("off_topic_response", END)
qa_graph.add_edge(START, "topic_decision")

qa_graph = qa_graph.compile()

# from IPython.display import display, Image
# display(Image(qa_graph.get_graph().draw_mermaid_png()))