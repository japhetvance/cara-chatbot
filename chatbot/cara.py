import streamlit as st
import os
import uuid
import re
import getpass
import pandas as pd
import numpy as np
from uuid import uuid4
import nltk
from langchain_community.retrievers import PineconeHybridSearchRetriever
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from pinecone import Pinecone as PineconeClient, ServerlessSpec
from pinecone_text.sparse import BM25Encoder

# Lazy download nltk data only if not already downloaded
if "nltk_data" not in st.session_state:
    nltk.download('punkt')
    st.session_state.nltk_data = True

st.title("Make Every Aviators Life Easier with C.A.R.A Chatbot")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi, I'm Cara, your aviation assistant. How can I assist you today?"}]

# Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

def clear_chat_history():
    st.session_state.messages = [{"role": "assistant", "content": "Hi, I'm Cara, your aviation assistant. How can I assist you today?"}]
    if "session_id" in st.session_state:
        st.session_state.pop("session_id")
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

# Cache heavy operations like loading embeddings
@st.cache_data
def load_embeddings():
    return HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

@st.cache_data
def bm25_encoder():
    return BM25Encoder().default()

@st.cache_data
def initialize_pinecone_client(api_key, index_name):
    pc = PineconeClient(api_key=api_key)
    index = pc.Index(index_name)
    return index

embeddings = load_embeddings()
index = initialize_pinecone_client(os.getenv('PINECONE_API_KEY'), os.getenv('PINECONE_INDEX_NAME'))
bm25_encoder = bm25_encoder()

retriever = PineconeHybridSearchRetriever(embeddings=embeddings, sparse_encoder=bm25_encoder, index=index)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
user_profile = st.session_state.role

# Contextualize question
contextualize_q_system_prompt = """Given a chat history and the latest user question \
which might reference context in the chat history, formulate a standalone question \
which can be understood without the chat history. Do NOT answer the question, \
just reformulate it if needed and otherwise return it as is."""
contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)
history_aware_retriever = create_history_aware_retriever(
    llm, retriever, contextualize_q_prompt
)

if user_profile == "Aviation Expert":
    qa_system_prompt = """You are Cara, an AI assistant specializing in aviation queries. \
    Use the provided context to answer the user's question. Provide all information available to answer the queries \
    If the answer is not in the context, simply state that you don't know and ask for more information, or remind the user to focus on aviation-related queries. \
    CAR and PCAR are the same thing. Sanction Tables is in PCAR Part 1. Experience Requirements Table is in PCAR Part 2. \
    When addressing sensitive queries directly answered by the context, mention "According to PCAR" or a similar phrase, ensuring that "PCAR" is highlighted. But dont mention it for general questions that is not specifically tailored on the context \
    Include source on which part of PCAR it is mentioned and its root context below each answer. For example, "Source: PCAR Part 5 - Airworthiness" \
    Capitalize all abbreviations you use.

    {context}"""

else:
    qa_system_prompt = """You are Cara, an AI assistant specializing in aviation queries. \
    Use the provided context to answer the user's question. \
    If the answer is not in context, just say that you don't know and ask to provide more information or ask aviation related queries only \
    But you can provide general information if the question is not tailored on the context.  CAR and PCAR are the same thing. \
    Do not repeatedly ask for more questions or clarifications . \
    Keep your response concise, five sentences maximum. Use layman's term as much as possible \
    When addressing sensitive queries directly answered by the context, mention "According to PCAR" or a similar phrase, ensuring that "PCAR" is highlighted. But dont mention it for general questions that is not specifically tailored on the context \
    Capitalize all abbreviations you use.

    {context}"""
    
qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", qa_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)
question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

# Statefully manage chat history
store = {}

def get_session_history(session_id: str = None) -> tuple:
    if session_id is None:
        session_id = str(uuid.uuid4())
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return session_id, store[session_id]

def get_current_session_history() -> tuple:
    if "session_id" not in st.session_state or "history" not in st.session_state:
        st.session_state.session_id, st.session_state.history = get_session_history()
    return st.session_state.session_id, st.session_state.history

conversational_rag_chain = RunnableWithMessageHistory(
    rag_chain,
    lambda: get_current_session_history()[1],
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="answer",
)

# Generate a new session ID automatically
session_id, history = get_current_session_history()

# User-provided prompt
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = conversational_rag_chain.invoke(
                {"input": prompt}
            )["answer"]
            st.write(response)
            # st.write("Session ID:", session_id)
    message = {"role": "assistant", "content": response}
    st.session_state.messages.append(message)
