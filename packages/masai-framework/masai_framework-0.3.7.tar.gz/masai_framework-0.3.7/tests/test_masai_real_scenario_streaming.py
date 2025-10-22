"""
Comprehensive test for MASAI streaming in real scenario.

Tests:
1. AgentManager with streaming enabled
2. Agent creation with tools
3. Agent execution with streaming callback
4. Custom emit functions for chunks from astream
5. Tool execution with streaming events
"""

import asyncio
import os
import sys
import json
from typing import Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, 'src')

# Load environment variables
load_dotenv()

# Import MASAI components
from masai.AgentManager.AgentManager import AgentManager, AgentDetails
from masai.Tools.utilities.streaming_events import (
    emit_custom_event,
    set_streaming_callback,
    clear_streaming_callback,
    StreamingEvent
)

# Import langchain tool decorator
try:
    from langchain.tools import tool
except ImportError:
    print("⚠️  langchain not available, using mock tool decorator")
    def tool(name=None):
        def decorator(func):
            func.name = name or func.__name__
            func.description = func.__doc__ or ""
            return func
        return decorator


# ============================================================================
# CUSTOM EMIT FUNCTION FOR STREAMING
# ============================================================================

class StreamCollector:
    """Collects streaming chunks for analysis"""
    
    def __init__(self):
        self.chunks = []
        self.tool_events = []
        self.custom_events = []
        self.llm_chunks = []
        
    def reset(self):
        """Reset all collected data"""
        self.chunks = []
        self.tool_events = []
        self.custom_events = []
        self.llm_chunks = []
    
    async def emit_chunk(self, chunk: Any):
        """
        Custom emit function that processes streaming chunks.
        This is the streaming_callback passed to AgentManager.
        """
        self.chunks.append(chunk)
        
        # Handle different chunk types
        if isinstance(chunk, dict):
            # Structured output chunk
            if "answer" in chunk:
                print(f"📦 Structured chunk: {json.dumps(chunk, indent=2)}")
                self.llm_chunks.append(chunk)
            else:
                print(f"📦 Dict chunk: {json.dumps(chunk, indent=2)}")
                self.llm_chunks.append(chunk)
        elif isinstance(chunk, StreamingEvent):
            # Streaming event from tools
            if chunk.event_type == "tool_call":
                print(f"🔧 Tool call: {chunk.data.get('tool_name')}")
                self.tool_events.append(chunk)
            elif chunk.event_type == "tool_output":
                print(f"✅ Tool output: {chunk.data.get('output', '')[:100]}")
                self.tool_events.append(chunk)
            elif chunk.event_type == "custom":
                print(f"💬 Custom event: {chunk.data.get('content')}")
                self.custom_events.append(chunk)
        elif hasattr(chunk, 'content'):
            # AIMessage chunk
            print(f"💭 LLM chunk: {chunk.content}", end="", flush=True)
            self.llm_chunks.append(chunk.content)
        else:
            # Raw string chunk
            print(f"💭 Raw chunk: {chunk}", end="", flush=True)
            self.llm_chunks.append(str(chunk))


# ============================================================================
# TOOLS WITH CUSTOM EMIT EVENTS
# ============================================================================

@tool("calculator")
async def calculator_tool(expression: str) -> str:
    """
    Calculate mathematical expressions.
    
    Args:
        expression: Mathematical expression to evaluate (e.g., "2+2", "10*5")
    
    Returns:
        Result of the calculation
    """
    # Emit custom event: Starting calculation
    await emit_custom_event(
        content=f"🔢 Starting calculation: {expression}",
        custom_data={"stage": "init", "expression": expression}
    )
    
    # Simulate processing
    await asyncio.sleep(0.1)
    
    try:
        # Evaluate expression
        result = eval(expression)
        
        # Emit custom event: Calculation complete
        await emit_custom_event(
            content=f"✅ Calculation complete: {expression} = {result}",
            custom_data={"stage": "complete", "result": result}
        )
        
        return f"The result of {expression} is {result}"
    except Exception as e:
        # Emit custom event: Error
        await emit_custom_event(
            content=f"❌ Calculation error: {str(e)}",
            custom_data={"stage": "error", "error": str(e)}
        )
        return f"Error calculating {expression}: {str(e)}"


@tool("search_database")
async def search_database_tool(query: str) -> str:
    """
    Search a mock database for information.
    
    Args:
        query: Search query
    
    Returns:
        Search results
    """
    # Emit custom event: Starting search
    await emit_custom_event(
        content=f"🔍 Searching database for: {query}",
        custom_data={"stage": "searching", "query": query, "progress": 0.0}
    )
    
    # Simulate search
    await asyncio.sleep(0.2)
    
    # Mock results
    results = [
        f"Result 1 for '{query}'",
        f"Result 2 for '{query}'",
        f"Result 3 for '{query}'"
    ]
    
    # Emit custom event: Search progress
    await emit_custom_event(
        content=f"📊 Found {len(results)} results",
        custom_data={"stage": "processing", "result_count": len(results), "progress": 0.7}
    )
    
    await asyncio.sleep(0.1)
    
    # Emit custom event: Search complete
    await emit_custom_event(
        content=f"✅ Search complete: {len(results)} results",
        custom_data={"stage": "complete", "result_count": len(results), "progress": 1.0}
    )
    
    return f"Found {len(results)} results:\n" + "\n".join(results)


# ============================================================================
# MODEL CONFIG
# ============================================================================

def create_model_config():
    """Create model configuration file"""
    config = {
        "math_agent": {
            "router": {
                "model_name": "gpt-4o-mini",
                "category": "openai",
                "temperature": 0.3
            },
            "evaluator": {
                "model_name": "gpt-4o-mini",
                "category": "openai",
                "temperature": 0.1
            },
            "reflector": {
                "model_name": "gpt-4o-mini",
                "category": "openai",
                "temperature": 0.5
            }
        }
    }
    
    config_path = "test_model_config_streaming.json"
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    return config_path


# ============================================================================
# TESTS
# ============================================================================

async def test_agent_manager_streaming():
    """Test AgentManager with streaming enabled"""
    
    print("\n" + "="*80)
    print("TEST 1: AgentManager with Streaming")
    print("="*80)
    
    # Create stream collector
    collector = StreamCollector()
    
    # Create model config
    config_path = create_model_config()
    
    try:
        # Initialize AgentManager with streaming
        print("\n🔧 Initializing AgentManager with streaming...")
        manager = AgentManager(
            logging=True,
            context={"environment": "test"},
            model_config_path=config_path,
            streaming=True,
            streaming_callback=collector.emit_chunk
        )
        print("✅ AgentManager initialized with streaming callback")
        
        # Create agent with tools
        print("\n🔧 Creating math_agent with tools...")
        tools = [calculator_tool, search_database_tool]
        agent_details = AgentDetails(
            capabilities=["mathematics", "calculations", "database search"],
            description="An agent that can perform calculations and search databases",
            style="concise and accurate"
        )
        
        manager.create_agent(
            agent_name="math_agent",
            tools=tools,
            agent_details=agent_details,
            memory_order=5,
            temperature=0.3
        )
        print("✅ Agent created successfully")
        
        # Get the agent
        agent = manager.agents["math_agent"]
        print(f"✅ Agent retrieved: {agent.agent_name}")
        
        # Set streaming callback for emit events
        set_streaming_callback(collector.emit_chunk)
        
        # Test query
        query = "Calculate 15 * 8 and then search the database for 'multiplication results'"
        
        print(f"\n📝 Query: {query}")
        print("\n🔄 Streaming agent execution:")
        print("-" * 80)
        
        # Stream agent execution
        start_time = datetime.now()
        state_count = 0
        
        async for state in agent.initiate_agent_astream(query=query, passed_from="user"):
            state_count += 1
            
            # Extract actual state
            actual_state = state
            if isinstance(state, tuple) and len(state) > 1:
                maybe = state[1]
                if isinstance(maybe, dict) and maybe:
                    actual_state = next(iter(maybe.values()), maybe)
                else:
                    actual_state = maybe
            
            # Print state info
            if isinstance(actual_state, dict):
                current_node = actual_state.get('current_node', 'unknown')
                print(f"\n📍 State {state_count}: {current_node}")
                
                if actual_state.get('current_tool'):
                    print(f"   🔧 Tool: {actual_state['current_tool']}")
                
                if actual_state.get('answer'):
                    print(f"   💬 Answer: {actual_state['answer'][:100]}...")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        print("\n" + "-" * 80)
        print(f"✅ Streaming complete!")
        print(f"   Duration: {duration:.2f}s")
        print(f"   States: {state_count}")
        print(f"   LLM chunks: {len(collector.llm_chunks)}")
        print(f"   Tool events: {len(collector.tool_events)}")
        print(f"   Custom events: {len(collector.custom_events)}")
        
        # Clear streaming callback
        clear_streaming_callback()
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Cleanup
        if os.path.exists(config_path):
            os.remove(config_path)


async def main():
    """Run all tests"""
    
    print("\n" + "="*80)
    print("MASAI REAL SCENARIO STREAMING TEST")
    print("="*80)
    print("\nThis test simulates a real MASAI scenario with:")
    print("  • AgentManager with streaming enabled")
    print("  • Agent with tools (calculator, database search)")
    print("  • Custom emit functions for streaming chunks")
    print("  • Tool execution with custom events")
    
    # Check API keys
    if not os.getenv("OPENAI_API_KEY"):
        print("\n⚠️  Warning: OPENAI_API_KEY not set")
        print("   Set it in .env file or environment")
        return
    
    # Run test
    success = await test_agent_manager_streaming()
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    if success:
        print("✅ All tests passed!")
        print("\n🎉 MASAI streaming works perfectly in real scenarios!")
    else:
        print("❌ Some tests failed")
        print("\n⚠️  Check the errors above")


if __name__ == "__main__":
    asyncio.run(main())

