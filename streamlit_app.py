import streamlit as st
import asyncio
import uuid
import json
from langchain_core.messages import HumanMessage, AIMessage
from agent import graph

# Page Config
st.set_page_config(page_title="StratGov Agent Test", page_icon="🤖", layout="wide")

st.title("🤖 StratGov AI Agent - Test Interface")

# Sidebar Configuration
with st.sidebar:
    st.header("Configuration")
    model = st.selectbox("Model", ["groq", "llama", "mixtral", "kimi"], index=0)
    temperature = st.slider("Temperature", 0.0, 1.0, 0.2)
    max_tokens = st.number_input("Max Tokens", 500, 8000, 4096)
    use_search = st.toggle("Enable Search", value=True)
    
    st.divider()
    if st.button("Reset Conversation"):
        st.session_state.messages = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()

# Session State Initialization
if "messages" not in st.session_state:
    st.session_state.messages = []
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "logs" in msg and msg["logs"]:
            with st.expander("View Logs"):
                for log in msg["logs"]:
                    st.text(f"[{log['type']}] {log['message']}")

# Chat Input
if prompt := st.chat_input("Ask your strategic question..."):
    # Add User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Prepare AI Response Container
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        status_placeholder = st.status("Thinking...", expanded=True)
        
        full_response = ""
        current_logs = []
        
        # Prepare Config
        config = {"configurable": {"thread_id": st.session_state.thread_id}}
        initial_state = {
            "messages": [HumanMessage(content=prompt)],
            "model": model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "search_domains": [] if use_search else ["none"], # Hack to disable
            "query": prompt,
            "logs": []
        }

        # Run Graph Async Wrapper
        async def run_agent():
            nonlocal full_response
            try:
                async for event in graph.astream(initial_state, config, stream_mode="updates"):
                    for node_name, node_data in event.items():
                        
                        # Process Logs
                        if "logs" in node_data:
                            for log in node_data["logs"]:
                                log_msg = log.message if hasattr(log, 'message') else str(log)
                                log_type = log.type if hasattr(log, 'type') else "info"
                                status_placeholder.write(f"**{node_name}**: {log_msg}")
                                current_logs.append({"type": log_type, "message": log_msg})

                        # Process Resources (Search Results)
                        if "resources" in node_data and node_data["resources"]:
                            status_placeholder.markdown("---")
                            status_placeholder.write(f"📚 Found {len(node_data['resources'])} resources")

                        # Process Final Answer
                        if "messages" in node_data:
                            last_msg = node_data["messages"][-1]
                            if isinstance(last_msg, AIMessage) and last_msg.content:
                                full_response = last_msg.content
                                message_placeholder.markdown(full_response)
                                
            except Exception as e:
                status_placeholder.error(f"Error: {str(e)}")
                full_response = f"Error: {str(e)}"

        # Run the async loop
        asyncio.run(run_agent())
        
        status_placeholder.update(label="Complete", state="complete", expanded=False)
        
        # Save to history
        st.session_state.messages.append({
            "role": "assistant", 
            "content": full_response,
            "logs": current_logs
        })
