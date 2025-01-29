import streamlit as st
from chat import search_chat, list_models
from dataclasses import dataclass
import os

ollama_base_url = os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')
searx_host = os.environ.get('SEARX_HOST', 'http://localhost:30053')
ollama_default_model = os.environ.get('OLLAMA_DEFAULT_MODEL', 'hermes3:latest')
crawl_for_ai_url = os.environ.get('CRAWL_FOR_AI_URL', 'http://localhost:11235/crawl')

st.set_page_config(layout="wide")
st.markdown(
    """
    <style>
    [data-testid="stChatMessageContent"] p{
        font-size: 16px;
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

tool_options = [
    {"id": "search_internet_tool", "name": "Search the web"},
    {"id": "system_info", "name": "System Information"},
    {"id": "latest_rss_news", "name": "Latest RSS News"},
]
selected_tools = st.multiselect(
    "Tools:",
    options=tool_options,
    format_func=lambda x: x["name"],
    default=[tool_options[0]],
)

debug_container = st.container()
with debug_container:
    st.subheader("Debug Information")


@dataclass
class Message:
    actor: str
    payload: str


USER = "User"
ASSISTANT = "Ollama"

MESSAGES = "messages"
if MESSAGES not in st.session_state:
    st.session_state[MESSAGES] = [Message(actor=ASSISTANT, payload="Search something...")]

msg: Message
for msg in st.session_state[MESSAGES]:
    st.chat_message(msg.actor).write(msg.payload)

prompt: str = st.chat_input("Search something...")

if st.button('Reset Chat'):
    st.session_state.messages = []
    st.rerun()

if prompt:
    st.session_state[MESSAGES].append(Message(actor=USER, payload=prompt))
    st.chat_message(USER).markdown(prompt, unsafe_allow_html=True)
    response = search_chat(
        prompt,
        debug_container,
        selected_model,
        [option["id"] for option in selected_tools],
        searx_host,
        ollama_base_url,
        crawl_for_ai_url
    )
    st.session_state[MESSAGES].append(Message(actor=ASSISTANT, payload=response))
    st.chat_message(ASSISTANT).markdown(response, unsafe_allow_html=True)
