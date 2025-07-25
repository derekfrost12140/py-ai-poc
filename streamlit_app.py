import streamlit as st
import requests

API_URL = "http://localhost:8000/query"

st.set_page_config(page_title="MCP Agent (Streamlit)", page_icon="🤖", layout="centered")

# --- Dark mode toggle ---
if 'dark_mode' not in st.session_state:
    st.session_state['dark_mode'] = False

def set_dark_mode():
    st.session_state['dark_mode'] = not st.session_state['dark_mode']

with st.sidebar:
    st.title("⚙️ Settings")
    dark = st.checkbox("🌙 Dark Mode", value=st.session_state['dark_mode'], on_change=set_dark_mode)
    st.markdown("---")
    st.markdown("**Try these examples:**")
    st.button("Weather in Paris", on_click=lambda: st.session_state.update(user_input="What is the weather in Paris?"))
    st.button("List Users", on_click=lambda: st.session_state.update(user_input="Show all users in the database"))
    st.button("SpaceX Launches", on_click=lambda: st.session_state.update(user_input="What were the last 3 SpaceX launches?"))
    st.button("User Count", on_click=lambda: st.session_state.update(user_input="How many users are in the system?"))
    st.button("Tokyo Weather", on_click=lambda: st.session_state.update(user_input="What is the temperature in Tokyo?"))

# --- Chat history ---
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

st.markdown(f"<h1 style='text-align:center;'>{'🤖 MCP Agent'}</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align:center; color:#764ba2; font-size:1.2em;'>AI-powered tool orchestration system</p>", unsafe_allow_html=True)

# --- User input ---
user_input = st.text_input("Type your message...", key="user_input")
col1, col2 = st.columns([1,1])
send_clicked = col1.button("Send", use_container_width=True)
clear_clicked = col2.button("Clear Chat", use_container_width=True)

if clear_clicked:
    st.session_state['chat_history'] = []
    st.session_state['user_input'] = ""
    st.experimental_rerun()

# --- Send query and update chat history ---
if send_clicked and user_input.strip():
    with st.spinner("Thinking..."):
        try:
            response = requests.post(API_URL, json={"query": user_input})
            if response.ok:
                data = response.json()
                agent_reply = data.get("result", "No result")
            else:
                agent_reply = f"Error: {response.status_code}"
        except Exception as e:
            agent_reply = f"Connection error: {e}"
    st.session_state['chat_history'].append((user_input, agent_reply))
    st.session_state['user_input'] = ""
    st.experimental_rerun()

# --- Display chat history ---
chat_bg = "#232946" if st.session_state['dark_mode'] else "#f6f7fb"
user_bg = "#667eea" if not st.session_state['dark_mode'] else "#353a5a"
agent_bg = "#fff" if not st.session_state['dark_mode'] else "#232946"
user_color = "#fff" if not st.session_state['dark_mode'] else "#eaeaea"
agent_color = "#333" if not st.session_state['dark_mode'] else "#eaeaea"

st.markdown(f"<div style='background:{chat_bg};padding:18px 12px 18px 12px;border-radius:16px;min-height:300px;'>", unsafe_allow_html=True)
for user_msg, agent_msg in st.session_state['chat_history']:
    st.markdown(f"<div style='background:{user_bg};color:{user_color};padding:10px 16px;border-radius:12px 12px 4px 12px;margin-bottom:6px;max-width:80%;margin-left:auto;text-align:right;'><b>🧑 You:</b> {user_msg}</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='background:{agent_bg};color:{agent_color};padding:10px 16px;border-radius:12px 12px 12px 4px;margin-bottom:18px;max-width:80%;margin-right:auto;text-align:left;'><b>🤖 MCP Agent:</b> {agent_msg}</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True) 
