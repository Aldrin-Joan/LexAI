import streamlit as st
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add code directory to path
sys.path.append(str(Path(__file__).parent / "code"))

from search_engine import SearchEngine, SearchMode
from llm_client import LLMClient
from session_manager import SessionManager

# Page Config
st.set_page_config(
    page_title="AI Legal Research Assistant",
    page_icon="⚖️",
    layout="wide"
)

# Load env variables
load_dotenv()

# Initialize Engine
@st.cache_resource
def init_engine():
    return SearchEngine(), LLMClient(), SessionManager(sessions_dir="sessions")

engine, llm, sessions = init_engine()

# Sidebar
with st.sidebar:
    st.title("⚖️ Legal AI Settings")
    st.markdown("---")
    
    # Session Management
    st.subheader("Sessions")
    if st.button("➕ Start New Chat"):
        new_id = sessions.start_new_session()
        st.success(f"New session: {new_id}")
        st.rerun()
    
    recent = sessions.list_sessions()
    if recent:
        st.write("Recent Chats:")
        for s in recent[:5]:
            if st.button(f"📄 {s['id']} ({s['message_count']} msgs)", key=s['id']):
                sessions.load_session(s['id'])
                st.rerun()

    st.markdown("---")
    st.info("Powered by Hybrid Retrieval (Sparse + Dense + Graph) & Gemini 3 Flash Preview.")

# Main UI
st.title("⚖️ AI Legal Research Assistant")
st.caption("Senior Advocate Persona | Case Citation Enforced | Supreme Court Focused")

# Chat Container
chat_container = st.container()

# Welcome Message
if not sessions.history:
    with chat_container:
        st.chat_message("assistant").write(
            "Welcome. I am your AI Legal Assistant. I can help you search for precedents, "
            "analyze legal issues, and draft case briefs based on our database of 26,000+ judgments."
        )

# Display History
for msg in sessions.history:
    with chat_container:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("metadata", {}).get("precedents"):
                with st.expander("Retrieved Precedents"):
                    for p in msg["metadata"]["precedents"]:
                        st.write(f"- {p}")

# Query Input
if prompt := st.chat_input("Ask a legal question..."):
    with chat_container:
        st.chat_message("user").write(prompt)
        sessions.add_message("user", prompt)
        
        with st.spinner("Searching precedents and synthesizing advice..."):
            # 1. Search
            results = engine.search(prompt, limit=5, mode=SearchMode.HYBRID)
            
            if not results:
                answer = "I could not find any relevant legal precedents in our database to answer this specific query."
                st.chat_message("assistant").write(answer)
                sessions.add_message("assistant", answer)
            else:
                # 2. Prepare Context
                context_docs = [
                    {'title': res['title'], 'text': res.get('text_content', '')}
                    for res in results
                ]
                
                # 3. Generate Answer
                answer = llm.generate_answer(prompt, context_docs, history=sessions.history)
                
                # 4. Display Result
                with st.chat_message("assistant"):
                    st.markdown(answer)
                    with st.expander("📑 Top 5 Relevant Precedents Found"):
                        for i, res in enumerate(results):
                            st.markdown(f"**{i+1}. {res['title']}**")
                            st.write(f"Year: {res['year']} | Relevance: {res['score']:.4f}")
                            if st.button(f"View Content for Case {i+1}", key=f"view_{i}_{res['case_id']}"):
                                st.text_area("Judgment Text Snippet", res.get('text_content', 'No content available'), height=300)

                sessions.add_message("assistant", answer, metadata={"precedents": [r['title'] for r in results]})
