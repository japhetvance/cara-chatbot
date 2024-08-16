import streamlit as st
import os
import uuid
from uuid import uuid4
import re
import getpass
import pandas as pd
import numpy as np
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
nltk.download('punkt')

st.title("Make Every Aviatiors Life Easier with C.A.R.A Chatbot")

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

# Initialize the retriever and language model
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
# Initialize Pinecone
pc = PineconeClient(api_key=os.getenv('PINECONE_API_KEY'))
index = pc.Index(os.getenv('PINECONE_INDEX_NAME'))
bm25_encoder = BM25Encoder().default()

# Create the retriever with the BM25 encoder
retriever = PineconeHybridSearchRetriever(embeddings=embeddings, sparse_encoder=bm25_encoder, index=index)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

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

# Answer question
qa_system_prompt = """You are Cara, an AI assistant specializing in aviation queries. \
Use the provided context to answer the user's question. \
If the answer is not in context, just say that you don't know and ask to provide more information or ask aviation related queries only \
But you can provide general information if the question is not tailored on the context. \
Do not repeatedly ask for more questions or clarifications . \
Keep your response concise, limited to three sentences if possible. \
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