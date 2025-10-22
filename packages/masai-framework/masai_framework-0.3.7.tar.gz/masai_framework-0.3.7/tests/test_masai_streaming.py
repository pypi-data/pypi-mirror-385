"""
Test MASAI astream_response_mas() streaming behavior
Uses actual MASAI MASGenerativeModel with .env configuration
"""

import asyncio
import sys
import os
from datetime import datetime
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import MASAI components
from masai.GenerativeModel.generativeModels import MASGenerativeModel
from masai.pydanticModels.AnswerModel import answermodel
from masai.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, PromptTemplate


# Test schema matching MASAI agent responses
class TestResponse(BaseModel):
    """Test schema for streaming"""
    reasoning: str = Field(description="Step-by-step reasoning process")
    answer: str = Field(description="Final answer to the question")
    satisfied: bool = Field(description="Whether the answer is satisfactory", default=True)


class StreamingCallback:
    """Callback to capture streaming chunks"""
    
    def __init__(self):
        self.chunks = []
        self.start_time = None
        self.chunk_times = []
        
    async def __call__(self, chunk):
        """Called for each streaming chunk"""
        if self.start_time is None:
            self.start_time = datetime.now()
        
        elapsed = (datetime.now() - self.start_time).total_seconds()
        self.chunk_times.append(elapsed)
        self.chunks.append(chunk)
        
        # Print chunk info
        chunk_num = len(self.chunks)
        print(f"\n[Chunk {chunk_num}] @ {elapsed:.2f}s")
        print(f"  Type: {type(chunk).__name__}")
        
        if isinstance(chunk, dict):
            print(f"  Keys: {list(chunk.keys())}")
            if 'reasoning' in chunk:
                print(f"  Reasoning: {len(chunk.get('reasoning', ''))} chars")
            if 'answer' in chunk:
                print(f"  Answer: {len(chunk.get('answer', ''))} chars")
            if 'satisfied' in chunk:
                print(f"  Satisfied: {chunk.get('satisfied', 'N/A')}")
        else:
            print(f"  Content: {str(chunk)[:100]}...")


async def test_astream_response_mas():
    """Test the actual MASAI astream_response_mas() method"""
    
    print("="*80)
    print("MASAI astream_response_mas() STREAMING TEST")
    print("="*80)
    print("\nThis test uses the actual MASAI MASGenerativeModel")
    print("Testing: astream_response_mas() method")
    print("="*80)
    
    # Initialize streaming callback
    callback = StreamingCallback()

    # Create prompt template (required for MASGenerativeModel)
    system_template = SystemMessagePromptTemplate(
        prompt=PromptTemplate(
            template="You are a helpful assistant. Respond in JSON format with reasoning, answer, and satisfied fields."
        )
    )
    human_template = HumanMessagePromptTemplate(
        prompt=PromptTemplate(
            template="""<USEFUL INFO>:{useful_info}</USEFUL INFO>

<CURRENT TIME>:{current_time}</CURRENT TIME>

<QUESTION>:{question}</QUESTION>

<HISTORY>:{history}</HISTORY>

<SCHEMA>:{schema}</SCHEMA>

<COWORKING AGENTS INFO>:{coworking_agents_info}</COWORKING AGENTS INFO>

Provide your response in JSON format matching the schema.""",
            input_variables=["useful_info", "current_time", "question", "history", "schema", "coworking_agents_info"]
        )
    )
    prompt_template = ChatPromptTemplate.from_messages([system_template, human_template])

    # Initialize MASGenerativeModel with streaming
    print("\n🔧 Initializing MASGenerativeModel...")
    print("   Model: gpt-4o-mini")
    print("   Category: openai")
    print("   Streaming: ENABLED")

    # Get model from environment or use default
    model_name = os.getenv("TEST_MODEL_NAME", "gpt-4o-mini")
    category = os.getenv("TEST_MODEL_CATEGORY", "openai")

    try:
        model = MASGenerativeModel(
            model_name=model_name,
            category=category,
            temperature=0.7,
            memory_order=5,
            prompt_template=prompt_template,
            streaming=True,
            streaming_callback=callback
        )
        print(f"✅ Model initialized successfully: {model_name} ({category})")
    except Exception as e:
        print(f"❌ Failed to initialize model: {e}")
        return False
    
    # Test prompt
    prompt = "Explain why the sky is blue in simple terms. Provide a detailed explanation with step-by-step reasoning."
    
    print(f"\n📝 Prompt: {prompt[:100]}...")
    print("\n🔄 Starting streaming...")
    print("-" * 80)
    
    start_time = datetime.now()
    
    try:
        # Call astream_response_mas (EXACT MASAI PATTERN)
        response = await model.astream_response_mas(
            prompt=prompt,
            output_structure=TestResponse,
            agent_name="test_agent"
        )
        
        total_time = (datetime.now() - start_time).total_seconds()
        
        print("\n" + "-" * 80)
        print(f"\n⏱️ Total time: {total_time:.2f}s")
        print(f"📊 Total chunks received: {len(callback.chunks)}")
        
        if len(callback.chunks) > 0:
            print(f"⚡ Avg time per chunk: {total_time/len(callback.chunks):.3f}s")
            print(f"🎯 First chunk at: {callback.chunk_times[0]:.3f}s")
            print(f"🎯 Last chunk at: {callback.chunk_times[-1]:.3f}s")
        
        print("\n📄 Final Response:")
        if isinstance(response, dict):
            print(f"  Reasoning: {response.get('reasoning', '')[:150]}...")
            print(f"  Answer: {response.get('answer', '')[:150]}...")
            print(f"  Satisfied: {response.get('satisfied', 'N/A')}")
        else:
            print(f"  {str(response)[:200]}...")
        
        # Analysis
        print("\n" + "="*80)
        print("ANALYSIS")
        print("="*80)
        
        if len(callback.chunks) == 1:
            print("""
❌ CONFIRMED: astream_response_mas() does NOT stream token-by-token!

Only 1 chunk was received, meaning:
1. LLM generated the complete response
2. Pydantic validated the complete response  
3. ONE complete object was returned to the callback

This is NOT real streaming - it's just async execution.

IMPACT:
- Users wait {:.1f}+ seconds with no feedback
- Frontend shows "Thinking..." with no progress
- Poor user experience for complex reasoning

SOLUTION NEEDED:
Implement hybrid streaming in astream_response_mas():
1. Phase 1: Stream reasoning token-by-token (raw astream)
2. Phase 2: Get structured output (with_structured_output)
3. Provide immediate feedback while maintaining type safety
""".format(total_time))
            return False
            
        elif len(callback.chunks) > 10:
            print(f"""
✅ STREAMING DETECTED: {len(callback.chunks)} chunks received!

This suggests token-by-token streaming is working!

Chunk distribution:
- First chunk: {callback.chunk_times[0]:.3f}s
- Last chunk: {callback.chunk_times[-1]:.3f}s
- Average interval: {(callback.chunk_times[-1] - callback.chunk_times[0]) / (len(callback.chunks) - 1):.3f}s

This is REAL streaming - tokens are arriving incrementally.
""")
            return True
        else:
            print(f"""
⚠️ PARTIAL STREAMING: {len(callback.chunks)} chunks received

This is better than 1 chunk, but still not ideal.
May indicate chunked delivery rather than token-by-token streaming.
""")
            return False
            
    except Exception as e:
        print(f"\n❌ Error during streaming: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_raw_model_streaming():
    """Test raw model streaming for comparison"""
    
    print("\n" + "="*80)
    print("BASELINE: RAW MODEL STREAMING (WITHOUT STRUCTURED OUTPUT)")
    print("="*80)
    
    print("\n🔧 Initializing raw model...")
    
    try:
        model = MASGenerativeModel(
            model_name="gpt-4o-mini",
            category="openai",
            temperature=0.7,
            memory_order=5,
            streaming=False  # No streaming callback for raw test
        )
        print("✅ Model initialized")
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return False
    
    prompt = "Explain why the sky is blue in simple terms."
    
    print(f"\n📝 Prompt: {prompt}")
    print("\n🔄 Streaming chunks:")
    print("-" * 80)
    
    chunk_count = 0
    start_time = datetime.now()
    
    try:
        async for chunk in model.model.astream(prompt):
            chunk_count += 1
            elapsed = (datetime.now() - start_time).total_seconds()
            
            if chunk_count <= 10 or chunk_count % 20 == 0:
                content = chunk.content if hasattr(chunk, 'content') else str(chunk)
                print(f"[Chunk {chunk_count}] @ {elapsed:.2f}s: '{content}'")
        
        total_time = (datetime.now() - start_time).total_seconds()
        
        print("-" * 80)
        print(f"\n✅ Total chunks: {chunk_count}")
        print(f"⏱️ Total time: {total_time:.2f}s")
        
        if chunk_count > 10:
            print("\n✅ PASS: Raw streaming works perfectly!")
            return True
        else:
            print("\n⚠️ WARNING: Few chunks received")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    
    print("="*80)
    print("MASAI STREAMING BEHAVIOR TEST SUITE")
    print("="*80)
    print("\nEnvironment:")
    print(f"  OPENAI_API_KEY: {'✅ Set' if os.getenv('OPENAI_API_KEY') else '❌ Not set'}")
    print("="*80)
    
    if not os.getenv('OPENAI_API_KEY'):
        print("\n❌ ERROR: OPENAI_API_KEY not set in environment")
        print("   Please set it in .env file or environment variables")
        return
    
    # Test 1: MASAI astream_response_mas
    result_masai = await test_astream_response_mas()
    
    # Test 2: Raw streaming baseline
    result_raw = await test_raw_model_streaming()
    
    # Final summary
    print("\n" + "="*80)
    print("FINAL SUMMARY")
    print("="*80)
    print(f"\n{'✅' if result_masai else '❌'} MASAI astream_response_mas: {'PASS' if result_masai else 'FAIL'}")
    print(f"✅ Raw model streaming: {'PASS' if result_raw else 'FAIL'}")
    
    print("\n" + "="*80)
    print("CONCLUSION")
    print("="*80)
    
    if not result_masai and result_raw:
        print("""
🎯 CONFIRMED ISSUE: Structured output blocks streaming

- Raw streaming works perfectly (many chunks)
- astream_response_mas() returns only 1 chunk
- with_structured_output() waits for complete response

RECOMMENDATION:
Implement hybrid streaming in astream_response_mas():
1. Stream reasoning tokens in real-time
2. Parse final JSON into Pydantic model
3. Provide immediate user feedback
""")
    elif result_masai:
        print("""
✅ UNEXPECTED: astream_response_mas() appears to stream!

This is surprising and needs further investigation.
The streaming callback received multiple chunks.
""")
    else:
        print("""
⚠️ WARNING: Both tests failed

Check:
1. API key configuration
2. Network connectivity
3. Model availability
""")


if __name__ == "__main__":
    asyncio.run(main())

