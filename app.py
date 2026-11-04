import hashlib                                     # to recognise a recording that was already sent
import os                                          # to read an environment variable
import uuid                                        # to create the session id
import requests                                    # sends the HTTP requests to the API
import streamlit as st                             # the web page framework

API_BASE = os.getenv("API_BASE", "http://127.0.0.1:8000")   # API address; default = your own computer
REQUEST_TIMEOUT = 90                               # seconds to wait for the API before giving up

st.set_page_config(page_title="Fire Emergency Assistant")   # browser tab title
st.title("Fire Emergency Assistant")               # page heading
st.warning("Supplements the official Brandschutzordnung. In an emergency call 112.")   # permanent notice at the top

if "messages" not in st.session_state:             # first visit in this browser session
    st.session_state.messages = []                 # Streamlit re-runs this file on every click, so the history is kept here
if "session_id" not in st.session_state:           # first visit in this browser session
    st.session_state.session_id = str(uuid.uuid4())    # random id; the API uses it as the agent's thread_id


def get_zones():                                   # asks the API which zones exist
    try:
        return requests.get(f"{API_BASE}/zones", timeout=10).json()   # e.g. ["kitchen", "open_office"]
    except requests.RequestException:              # API not reachable
        return []                                  # the drop-down then only offers "(not set)"


zone_choice = st.sidebar.selectbox("Where are you?", ["(not set)"] + get_zones())   # drop-down in the left sidebar
zone = None if zone_choice == "(not set)" else zone_choice   # None means: no zone chosen


def show(msg):                                     # draws one chat message
    with st.chat_message(msg["role"]):             # a chat bubble for "user" or "assistant"
        if msg.get("safety_steps"):                # only present for fire wording
            st.error("**Fire? Do this first:**\n\n" + "\n\n".join(msg["safety_steps"]))   # red box, always above the answer
        st.markdown(msg["content"])                # the answer or the question text
        if msg.get("sources"):                     # only present for real answers
            names = [s["source_doc"] + (f', p.{s["page"]}' if s["page"] else "") for s in msg["sources"]]   # page only for PDFs
            st.caption("Sources: " + "; ".join(names))   # small grey line


for msg in st.session_state.messages:              # redraw the whole history on each run
    show(msg)

question = st.chat_input("Ask about fire safety...")   # typed question; None until the user sends
audio = st.audio_input("Or ask by voice")          # microphone widget; None until something is recorded
if audio is not None:                              # a recording exists
    audio_bytes = audio.getvalue()                 # the raw recording
    audio_id = hashlib.sha256(audio_bytes).hexdigest()   # fingerprint of this recording
    if audio_id != st.session_state.get("last_audio_id"):   # not sent yet (the widget keeps the recording across re-runs)
        st.session_state.last_audio_id = audio_id  # remember it, so it is sent only once
        try:
            with st.spinner("Transcribing..."):    # spinner while Whisper works
                r = requests.post(f"{API_BASE}/transcribe",
                                  files={"audio": ("question.wav", audio_bytes, "audio/wav")},   # multipart upload
                                  timeout=REQUEST_TIMEOUT)
                r.raise_for_status()               # HTTP errors become exceptions
                question = r.json()["text"]        # the spoken words as text; now handled like a typed question
        except requests.RequestException:
            st.error("Could not transcribe the recording. Please type your question.")

if question:                                       # typed or spoken
    user_msg = {"role": "user", "content": question}   # store the question
    st.session_state.messages.append(user_msg)
    show(user_msg)                                 # draw it immediately
    try:
        with st.spinner("Searching the documents..."):   # shows a spinner while the agent works
            r = requests.post(f"{API_BASE}/ask", json={        # call POST /ask
                "question": question,
                "session_id": st.session_state.session_id,     # same id on every question = memory
                "zone": zone,                                  # None if not chosen
            }, timeout=REQUEST_TIMEOUT)
            r.raise_for_status()                   # turns HTTP errors (500 etc.) into exceptions
            data = r.json()                        # the AskResponse from Day 4
        reply = {                                  # build the assistant message
            "role": "assistant",
            "content": data["answer"],
            "sources": data["sources"],
            "safety_steps": data["safety_steps"],
        }
    except requests.RequestException:              # API down, too slow, or an error status
        reply = {                                  # honest fallback, never an invented answer
            "role": "assistant",
            "content": "The assistant is not reachable. In an emergency call 112 and follow the Brandschutzordnung.",
            "sources": [],
            "safety_steps": [],
        }
    st.session_state.messages.append(reply)        # keep it in the history
    show(reply)                                    # draw it