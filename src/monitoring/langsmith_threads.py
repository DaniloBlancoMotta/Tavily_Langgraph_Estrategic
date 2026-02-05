"""
LangSmith Conversation History Manager

Manages conversation threads and history using LangSmith for long-running chats.
Integrates with the Strategic_Agent monitoring system.
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from langsmith import traceable, Client
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
import langsmith as ls

class ConversationHistoryManager:
    """
    Manages conversation threads using LangSmith for persistence and retrieval.
    """
    
    def __init__(self, project_name: str = "Strategic_Agent"):
        """
        Initialize the conversation history manager.
        
        Args:
            project_name: LangSmith project name for storing conversations
        """
        self.client = Client()
        self.project_name = project_name
    
    def get_thread_history(
        self, 
        thread_id: str, 
        max_messages: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve conversation history for a specific thread.
        
        Args:
            thread_id: Unique identifier for the conversation thread
            max_messages: Maximum number of messages to retrieve (None = all)
        
        Returns:
            List of message dictionaries with role and content
        """
        try:
            # Filter runs by thread ID in metadata
            filter_string = (
                f'and(in(metadata_key, ["session_id", "conversation_id", "thread_id"]), '
                f'eq(metadata_value, "{thread_id}"))'
            )
            
            # Get all LLM runs for this thread
            runs = [
                r for r in self.client.list_runs(
                    project_name=self.project_name,
                    filter=filter_string,
                    run_type="llm"
                )
            ]
            
            if not runs:
                return []
            
            # Sort by start time (oldest first for chronological order)
            runs = sorted(runs, key=lambda run: run.start_time)
            
            # Reconstruct conversation history
            messages = []
            for run in runs:
                # Get input messages
                if "messages" in run.inputs:
                    input_msgs = run.inputs["messages"]
                    # Skip system messages to avoid duplication
                    for msg in input_msgs:
                        if isinstance(msg, dict):
                            if msg.get("role") != "system":
                                messages.append(msg)
                        elif hasattr(msg, "type") and msg.type != "system":
                            messages.append({
                                "role": msg.type if msg.type != "ai" else "assistant",
                                "content": msg.content
                            })
                
                # Get output message
                if "outputs" in run.outputs:
                    output = run.outputs["outputs"]
                    if isinstance(output, dict) and "choices" in output:
                        response_msg = output["choices"][0]["message"]
                        messages.append(response_msg)
                elif hasattr(run.outputs, "content"):
                    messages.append({
                        "role": "assistant",
                        "content": run.outputs.content
                    })
            
            # Deduplicate messages (keep unique based on content and order)
            unique_messages = []
            seen = set()
            for msg in messages:
                key = (msg["role"], msg["content"][:100])  # Use first 100 chars as key
                if key not in seen:
                    unique_messages.append(msg)
                    seen.add(key)
            
            # Apply max_messages limit if specified
            if max_messages:
                unique_messages = unique_messages[-max_messages:]
            
            return unique_messages
            
        except Exception as e:
            print(f"Error retrieving thread history: {e}")
            return []
    
    def get_thread_summary(self, thread_id: str) -> Dict[str, Any]:
        """
        Get summary statistics for a conversation thread.
        
        Args:
            thread_id: Unique identifier for the conversation thread
        
        Returns:
            Dictionary with thread statistics
        """
        try:
            filter_string = (
                f'and(in(metadata_key, ["session_id", "conversation_id", "thread_id"]), '
                f'eq(metadata_value, "{thread_id}"))'
            )
            
            runs = list(self.client.list_runs(
                project_name=self.project_name,
                filter=filter_string
            ))
            
            if not runs:
                return {
                    "thread_id": thread_id,
                    "total_runs": 0,
                    "total_messages": 0,
                    "first_interaction": None,
                    "last_interaction": None,
                    "total_llm_calls": 0
                }
            
            runs_sorted = sorted(runs, key=lambda r: r.start_time)
            llm_runs = [r for r in runs if r.run_type == "llm"]
            
            return {
                "thread_id": thread_id,
                "total_runs": len(runs),
                "total_messages": len(self.get_thread_history(thread_id)),
                "first_interaction": runs_sorted[0].start_time.isoformat(),
                "last_interaction": runs_sorted[-1].start_time.isoformat(),
                "total_llm_calls": len(llm_runs),
                "run_types": {run.run_type: len([r for r in runs if r.run_type == run.run_type]) for run in runs}
            }
            
        except Exception as e:
            print(f"Error retrieving thread summary: {e}")
            return {"error": str(e)}
    
    def list_active_threads(self, hours: int = 24) -> List[str]:
        """
        List all active conversation threads from the last N hours.
        
        Args:
            hours: Number of hours to look back
        
        Returns:
            List of unique thread IDs
        """
        try:
            # Get all recent runs
            runs = list(self.client.list_runs(
                project_name=self.project_name,
                limit=1000  # Adjust based on your needs
            ))
            
            # Extract unique thread IDs from metadata
            thread_ids = set()
            for run in runs:
                if run.extra and "metadata" in run.extra:
                    metadata = run.extra["metadata"]
                    for key in ["session_id", "conversation_id", "thread_id"]:
                        if key in metadata:
                            thread_ids.add(metadata[key])
            
            return sorted(list(thread_ids))
            
        except Exception as e:
            print(f"Error listing active threads: {e}")
            return []
    
    def delete_thread_history(self, thread_id: str) -> bool:
        """
        Delete all runs associated with a thread (use with caution).
        
        Args:
            thread_id: Thread ID to delete
        
        Returns:
            True if successful, False otherwise
        """
        try:
            filter_string = (
                f'and(in(metadata_key, ["session_id", "conversation_id", "thread_id"]), '
                f'eq(metadata_value, "{thread_id}"))'
            )
            
            runs = list(self.client.list_runs(
                project_name=self.project_name,
                filter=filter_string
            ))
            
            for run in runs:
                self.client.delete_run(run.id)
            
            return True
            
        except Exception as e:
            print(f"Error deleting thread history: {e}")
            return False


@traceable(name="chat_with_history", run_type="chain")
def chat_with_history(
    messages: List[Dict[str, str]],
    thread_id: str,
    project_name: str = "Strategic_Agent",
    get_chat_history: bool = True,
    max_history_messages: int = 20
) -> Dict[str, Any]:
    """
    Chat function with conversation history management.
    
    Args:
        messages: New messages to add to the conversation
        thread_id: Unique thread identifier for this conversation
        project_name: LangSmith project name
        get_chat_history: Whether to retrieve and include conversation history
        max_history_messages: Maximum number of historical messages to include
    
    Returns:
        Dictionary with full conversation including history and new response
    """
    history_manager = ConversationHistoryManager(project_name)
    
    # Get conversation history if requested
    if get_chat_history:
        history_messages = history_manager.get_thread_history(
            thread_id, 
            max_messages=max_history_messages
        )
        
        if history_messages:
            print(f"📚 Retrieved {len(history_messages)} messages from thread {thread_id}")
        
        # Combine history with new messages
        all_messages = history_messages + messages
    else:
        all_messages = messages
    
    return {
        "messages": all_messages,
        "thread_id": thread_id,
        "history_loaded": get_chat_history,
        "history_message_count": len(all_messages) - len(messages) if get_chat_history else 0
    }


def create_langsmith_metadata(
    thread_id: str,
    session_id: Optional[str] = None,
    user_id: Optional[str] = None,
    additional_metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create standardized metadata for LangSmith tracking.
    
    Args:
        thread_id: Conversation thread identifier
        session_id: Optional session identifier
        user_id: Optional user identifier
        additional_metadata: Any additional metadata to include
    
    Returns:
        Metadata dictionary for LangSmith
    """
    metadata = {
        "thread_id": thread_id,
        "conversation_id": thread_id,  # Alias for compatibility
        "session_id": session_id or thread_id,
        "timestamp": datetime.now().isoformat()
    }
    
    if user_id:
        metadata["user_id"] = user_id
    
    if additional_metadata:
        metadata.update(additional_metadata)
    
    return metadata


# Example usage
if __name__ == "__main__":
    print("=" * 80)
    print("🔗 CONVERSATION HISTORY MANAGER - DEMO")
    print("=" * 80)
    print()
    
    # Initialize manager
    manager = ConversationHistoryManager("Strategic_Agent")
    
    # Example: Get thread history
    thread_id = "demo_thread_001"
    
    print(f"📚 Retrieving history for thread: {thread_id}")
    history = manager.get_thread_history(thread_id, max_messages=10)
    
    if history:
        print(f"✅ Found {len(history)} messages:")
        for i, msg in enumerate(history, 1):
            role = msg.get("role", "unknown")
            content = msg.get("content", "")[:100]
            print(f"   {i}. [{role.upper()}]: {content}...")
    else:
        print("   No history found (this is expected for new threads)")
    print()
    
    # Example: Get thread summary
    print(f"📊 Thread Summary:")
    summary = manager.get_thread_summary(thread_id)
    for key, value in summary.items():
        print(f"   {key}: {value}")
    print()
    
    # Example: List active threads
    print("🔍 Active Threads:")
    threads = manager.list_active_threads(hours=24)
    if threads:
        for thread in threads[:10]:  # Show first 10
            print(f"   • {thread}")
    else:
        print("   No active threads found")
    print()
    
    print("=" * 80)
    print("💡 Usage Example:")
    print("=" * 80)
    print("""
from src.langsmith_threads import chat_with_history, create_langsmith_metadata

# Create metadata
metadata = create_langsmith_metadata(
    thread_id="user_123_session_456",
    user_id="user_123",
    additional_metadata={"source": "streamlit_ui"}
)

# Chat with history
messages = [{"role": "user", "content": "What are AI trends for 2024?"}]

result = chat_with_history(
    messages=messages,
    thread_id="user_123_session_456",
    get_chat_history=True,
    langsmith_extra={
        "project_name": "Strategic_Agent",
        "metadata": metadata
    }
)

print(f"Total messages in conversation: {len(result['messages'])}")
print(f"History messages loaded: {result['history_message_count']}")
    """)
    print("=" * 80)
