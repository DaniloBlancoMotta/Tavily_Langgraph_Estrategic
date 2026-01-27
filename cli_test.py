import asyncio
import uuid
from langchain_core.messages import HumanMessage
from agent import graph

async def run_chat():
    print("🤖 StratGov AI Agent - CLI Test Mode")
    print("Type 'quit' or 'exit' to stop.\n")
    
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    while True:
        user_input = input("\n👤 You: ")
        if user_input.lower() in ["quit", "exit"]:
            break
            
        initial_state = {
            "messages": [HumanMessage(content=user_input)],
            "model": "groq",
            "temperature": 0.2,
            "max_tokens": 4096,
            "search_domains": [],
            "query": user_input,
            "logs": []
        }
        
        print("\n🤖 AI is thinking...", end="", flush=True)
        
        try:
            async for event in graph.astream(initial_state, config, stream_mode="updates"):
                for node_name, node_data in event.items():
                    # Print logs if available
                    if "logs" in node_data:
                        for log in node_data["logs"]:
                            msg = log.message if hasattr(log, 'message') else str(log)
                            print(f"\n[LOG][{node_name}]: {msg}", end="")
                    
                    if "messages" in node_data:
                        last_msg = node_data["messages"][-1]
                        if last_msg.content:
                            print(f"\n\n🤖 StratGov: {last_msg.content}")
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(run_chat())
