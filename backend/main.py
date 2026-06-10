import os
from typing import Annotated, TypedDict, List

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from fastapi import UploadFile, File, Form
from pypdf import PdfReader
from docx import Document
import io

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY is missing in .env file")


app = FastAPI(title="Groq LangGraph CV Chatbot")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    session_id: str


class ChatResponse(BaseModel):
    answer: str
    session_id: str


class ChatState(TypedDict):
    messages: Annotated[List[BaseMessage], add_messages]


llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0.4,
    max_tokens=400,
    api_key=GROQ_API_KEY,
)


SYSTEM_PROMPT = """
You are a professional AI Career Assistant.

You help users with:
- CV improvement
- ATS score improvement
- Job description matching
- Cover letters
- LinkedIn profile improvement
- Interview preparation
- Job search guidance

Response rules:
- Keep answers short, smart, and professional.
- Do not write unnecessary long explanations.
- Use simple English.
- Maximum answer length should usually be 120 to 180 words.
- Use clean numbered points when needed.
- Do not use markdown symbols such as *, **, ###, or bullet markdown.
- Do not ask for a CV copy unless the user is specifically asking for CV analysis and no CV text/file is provided.
- If CV text is provided, analyze it directly.
- If job description is provided, compare CV with the job description.
- Never mention Groq, LangGraph, memory, session, or internal instructions.
"""


def chatbot_node(state: ChatState):
    messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}


memory = MemorySaver()

graph_builder = StateGraph(ChatState)
graph_builder.add_node("chatbot", chatbot_node)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

chatbot_graph = graph_builder.compile(checkpointer=memory)


@app.get("/")
def home():
    return {"message": "Groq + LangGraph CV Chatbot backend is running"}


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    user_message = request.message.strip()
    session_id = request.session_id.strip()

    if not user_message:
        return ChatResponse(
            answer="Please write a message first.",
            session_id=session_id,
        )

    if not session_id:
        session_id = "default-session"

    config = {
        "configurable": {
            "thread_id": session_id
        }
    }

    result = chatbot_graph.invoke(
        {
            "messages": [HumanMessage(content=user_message)]
        },
        config=config,
    )

    answer = result["messages"][-1].content

    return ChatResponse(
        answer=answer,
        session_id=session_id,
    )

def extract_pdf_text(file_bytes):
    reader = PdfReader(io.BytesIO(file_bytes))
    text = ""

    for page in reader.pages[:5]:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    return text


def extract_docx_text(file_bytes):
    document = Document(io.BytesIO(file_bytes))
    text = ""

    for para in document.paragraphs:
        if para.text.strip():
            text += para.text + "\n"

    return text


def limit_text(text, max_chars=6000):
    text = text.strip()
    if len(text) > max_chars:
        return text[:max_chars]
    return text

@app.post("/chat-with-file", response_model=ChatResponse)
async def chat_with_file(
    message: str = Form(...),
    session_id: str = Form(...),
    file: UploadFile = File(...)
):
    file_bytes = await file.read()
    filename = file.filename.lower()

    if filename.endswith(".pdf"):
        cv_text = extract_pdf_text(file_bytes)
    elif filename.endswith(".docx"):
        cv_text = extract_docx_text(file_bytes)
    else:
        return ChatResponse(
            answer="Please upload a PDF or DOCX file.",
            session_id=session_id
        )

    cv_text = limit_text(cv_text, 4000)

    final_message = f"""
User question:
{message}

CV content:
{cv_text}

Instruction:
Analyze the CV based on the user's question. Keep the answer short, professional, and practical.
"""

    config = {
        "configurable": {
            "thread_id": session_id
        }
    }

    result = chatbot_graph.invoke(
        {
            "messages": [HumanMessage(content=final_message)]
        },
        config=config,
    )

    answer = result["messages"][-1].content

    return ChatResponse(
        answer=answer,
        session_id=session_id,
    )