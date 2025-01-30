import streamlit as st
from chat import search_chat, list_models
from dataclasses import dataclass
import os
from utils import make_stream
from typing import List, Dict

ollama_base_url = os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')
searx_host = os.environ.get('SEARX_HOST', 'http://localhost:30053')
ollama_default_model = os.environ.get('OLLAMA_DEFAULT_MODEL', 'hermes3:latest')
crawl_for_ai_url = os.environ.get('CRAWL_FOR_AI_URL', 'http://localhost:11235')

st.set_page_config(layout="wide")
st.markdown(
    """
    <style>
    [data-testid="stChatMessageContent"] p{
        font-size: 16px;
    }
    .cursor {
        display: inline-block;
        width: 2px;
        margin-left: 0px;
        animation: blink 1s step-end infinite;
    }

    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0; }
    }
    </style>
    """, unsafe_allow_html=True
)

model_options = list_models(ollama_base_url)
default_index = next((i for i, dic in enumerate(model_options) if dic == ollama_default_model), 0)
selected_model = st.selectbox(
    "Model:",
    options=list(model_options.keys()),
    format_func=lambda x: model_options[x],
    index=default_index,
)

USER = "User"
ASSISTANT = "Ollama"
MESSAGES = "messages"


@dataclass
class Message:
    actor: str
    payload: str
    citations: List[Dict[str, str]] = None

    def __post_init__(self):
        if self.citations is None:
            self.citations = []


# Initialize session state
if MESSAGES not in st.session_state:
    st.session_state[MESSAGES] = []

# Display chat history
msg: Message
for msg in st.session_state[MESSAGES]:
    with st.chat_message(msg.actor):
        st.markdown(msg.payload, unsafe_allow_html=True)
        if msg.citations:
            with st.expander("Sources"):
                for citation in msg.citations:
                    st.markdown(f"[{citation['title']}]({citation['link']})")

# Chat input
prompt: str = st.chat_input("Search something...")

if prompt:
    # Add user message
    st.session_state[MESSAGES].append(Message(actor=USER, payload=prompt))
    st.chat_message(USER).markdown(prompt, unsafe_allow_html=True)

    # Show searching indicator
    container = st.empty()
    make_stream(container, "Searching")

    # Get response with citations
    response = search_chat(
        prompt,
        selected_model,
        searx_host,
        ollama_base_url,
        crawl_for_ai_url
    )

    # Display assistant response
    make_stream(container, str(response['content']))

    # Add assistant message with citations
    assistant_message = Message(
        actor=ASSISTANT,
        payload=response['content'],
        citations=response['citations']
    )
    st.session_state[MESSAGES].append(assistant_message)

    # Display citations in expander
    with st.expander("Sources"):
        for citation in response['citations']:
            st.markdown(f"[{citation['title']}]({citation['link']})")