"""
Enhanced Streaming Test for MASAI Framework
Tests structured output streaming with LangChain's astream()
"""

import asyncio
import sys
import os
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import MASAI components
from masai.GenerativeModel.baseGenerativeModel.basegenerativeModel import BaseGenerativeModel


# Test schema matching MASAI agent responses
class AgentResponse(BaseModel):
    """Schema matching MAS-AI agent responses."""
    reasoning: str = Field(description="Step-by-step reasoning process")
    answer: str = Field(description="Final answer to the question")
    satisfied: bool = Field(description="Whether the answer is satisfactory", default=True)


class StreamingTester:
    """Test harness for streaming behavior"""
    
    def __init__(self, model_name: str = "gpt-4o-mini", category: str = "openai"):
        """Initialize with model configuration"""
        self.model_name = model_name
        self.category = category
        self.model = None
        
    def initialize_model(self):
        """Initialize the BaseGenerativeModel"""
        print(f"\n🔧 Initializing {self.category} model: {self.model_name}")
        self.model = BaseGenerativeModel(
            model_name=self.model_name,
            category=self.category,
            temperature=0.7,
            memory=False
        )
        print("✅ Model initialized")
        
    async def test_raw_streaming(self, prompt: str):
        """Test raw streaming without structured output"""
        print("\n" + "="*80)
        print("TEST 1: RAW STREAMING (Baseline)")
        print("="*80)
        print(f"\n📝 Prompt: {prompt[:100]}...")
        print("\n🔄 Streaming chunks:")
        print("-" * 80)
        
        chunk_count = 0
        start_time = datetime.now()
        full_response = ""
        
        try:
            async for chunk in self.model.model.astream(prompt):
                chunk_count += 1
                elapsed = (datetime.now() - start_time).total_seconds()
                
                content = chunk.content if hasattr(chunk, 'content') else str(chunk)
                full_response += content
                
                # Show first 10 chunks and every 20th chunk
                if chunk_count <= 10 or chunk_count % 20 == 0:
                    print(f"[Chunk {chunk_count}] @ {elapsed:.2f}s: '{content}'")
            
            total_time = (datetime.now() - start_time).total_seconds()
            
            print("-" * 80)
            print(f"\n✅ Total chunks: {chunk_count}")
            print(f"⏱️ Total time: {total_time:.2f}s")
            print(f"📊 Avg time per chunk: {total_time/chunk_count:.3f}s")
            
            if chunk_count > 10:
                print("\n✅ PASS: Raw streaming works - many chunks received!")
                return True
            else:
                print("\n⚠️ WARNING: Few chunks received")
                return False
                
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def test_structured_streaming(self, prompt: str, output_structure: type[BaseModel]):
        """Test structured output streaming (MASAI pattern)"""
        print("\n" + "="*80)
        print("TEST 2: STRUCTURED OUTPUT STREAMING (MASAI Pattern)")
        print("="*80)
        print(f"\n📝 Prompt: {prompt[:100]}...")
        print("\n🔄 Streaming chunks:")
        print("-" * 80)
        
        chunk_count = 0
        start_time = datetime.now()
        final_response = None
        
        try:
            # Create structured model (MASAI pattern)
            structured_llm = self.model.model.with_structured_output(output_structure)
            
            print("\n⏳ Waiting for chunks...")
            
            # EXACT MASAI PATTERN from astream_response_mas()
            async for chunk in structured_llm.astream(prompt):
                chunk_count += 1
                elapsed = (datetime.now() - start_time).total_seconds()
                
                print(f"\n[Chunk {chunk_count}] @ {elapsed:.2f}s")
                print(f"  Type: {type(chunk).__name__}")
                
                if hasattr(chunk, 'model_dump'):
                    chunk_dict = chunk.model_dump()
                    print(f"  Keys: {list(chunk_dict.keys())}")
                    print(f"  Reasoning: {len(chunk_dict.get('reasoning', ''))} chars")
                    print(f"  Answer: {len(chunk_dict.get('answer', ''))} chars")
                    print(f"  Satisfied: {chunk_dict.get('satisfied', 'N/A')}")
                else:
                    print(f"  Content: {str(chunk)[:100]}...")
                
                final_response = chunk
            
            total_time = (datetime.now() - start_time).total_seconds()
            
            print("\n" + "-" * 80)
            print(f"\n✅ Total chunks: {chunk_count}")
            print(f"⏱️ Total time: {total_time:.2f}s")
            
            if hasattr(final_response, 'model_dump'):
                response_dict = final_response.model_dump()
                print("\n📄 Final Response:")
                print(f"  Reasoning: {response_dict['reasoning'][:150]}...")
                print(f"  Answer: {response_dict['answer'][:150]}...")
                print(f"  Satisfied: {response_dict['satisfied']}")
            
            # Analysis
            print("\n" + "="*80)
            print("ANALYSIS")
            print("="*80)
            
            if chunk_count == 1:
                print("""
❌ CONFIRMED: Structured output does NOT stream token-by-token!

The with_structured_output() + astream() pattern received only 1 chunk.

This means:
1. LLM generated the complete response
2. Pydantic validated the complete response  
3. ONE complete object was returned

This is NOT real streaming - it's just async execution.

IMPACT:
- Users wait 3-6+ seconds with no feedback
- Frontend shows "Thinking..." with no progress
- Poor user experience for complex reasoning

SOLUTION NEEDED:
Implement hybrid streaming approach in MASAI:
1. Phase 1: Stream reasoning token-by-token (raw astream)
2. Phase 2: Get structured output (with_structured_output)
""")
                return False
            else:
                print(f"""
✅ STREAMING DETECTED: {chunk_count} chunks received!

This suggests token-by-token streaming is working with structured output.
This would be unexpected based on LangChain documentation.

Further investigation needed to understand the streaming behavior.
""")
                return True
                
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def test_json_mode_streaming(self, prompt: str):
        """Test streaming with json_mode instead of structured output"""
        print("\n" + "="*80)
        print("TEST 3: JSON MODE STREAMING (Alternative)")
        print("="*80)
        print(f"\n📝 Prompt: {prompt[:100]}...")
        print("\n🔄 Streaming chunks:")
        print("-" * 80)
        
        chunk_count = 0
        start_time = datetime.now()
        full_response = ""
        
        try:
            # Use json_mode instead of structured output
            json_llm = self.model.model.bind(response_format={"type": "json_object"})
            
            async for chunk in json_llm.astream(prompt):
                chunk_count += 1
                elapsed = (datetime.now() - start_time).total_seconds()
                
                content = chunk.content if hasattr(chunk, 'content') else str(chunk)
                full_response += content
                
                if chunk_count <= 10 or chunk_count % 20 == 0:
                    print(f"[Chunk {chunk_count}] @ {elapsed:.2f}s: '{content[:50]}...'")
            
            total_time = (datetime.now() - start_time).total_seconds()
            
            print("-" * 80)
            print(f"\n✅ Total chunks: {chunk_count}")
            print(f"⏱️ Total time: {total_time:.2f}s")
            
            if chunk_count > 10:
                print("\n✅ PASS: JSON mode streaming works!")
                print("\n💡 INSIGHT: json_mode allows token-by-token streaming")
                print("   Consider using json_mode + manual parsing instead of with_structured_output()")
                return True
            else:
                print("\n⚠️ WARNING: Few chunks received with json_mode")
                return False
                
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return False


async def main():
    """Run all streaming tests"""
    
    print("="*80)
    print("MASAI STREAMING BEHAVIOR TEST SUITE")
    print("="*80)
    print("\nThis test suite validates streaming behavior with:")
    print("  1. Raw streaming (baseline)")
    print("  2. Structured output streaming (current MASAI pattern)")
    print("  3. JSON mode streaming (alternative approach)")
    print("="*80)
    
    # Initialize tester
    tester = StreamingTester(model_name="gpt-4o-mini", category="openai")
    tester.initialize_model()
    
    # Test prompt
    prompt = """You are a helpful assistant. Respond in JSON format.

Question: Explain why the sky is blue in simple terms.

Provide your response with:
- reasoning: Step-by-step explanation (at least 100 words)
- answer: Final answer (at least 50 words)
- satisfied: true"""
    
    # Run tests
    results = {}
    
    # Test 1: Raw streaming
    results['raw'] = await tester.test_raw_streaming(prompt)
    
    # Test 2: Structured streaming
    results['structured'] = await tester.test_structured_streaming(prompt, AgentResponse)
    
    # Test 3: JSON mode streaming
    results['json_mode'] = await tester.test_json_mode_streaming(prompt)
    
    # Final summary
    print("\n" + "="*80)
    print("FINAL SUMMARY")
    print("="*80)
    print(f"\n✅ Raw streaming: {'PASS' if results['raw'] else 'FAIL'}")
    print(f"{'✅' if results['structured'] else '❌'} Structured streaming: {'PASS' if results['structured'] else 'FAIL'}")
    print(f"✅ JSON mode streaming: {'PASS' if results['json_mode'] else 'FAIL'}")
    
    print("\n" + "="*80)
    print("RECOMMENDATIONS")
    print("="*80)
    
    if not results['structured'] and results['json_mode']:
        print("""
🎯 RECOMMENDED SOLUTION: Hybrid Streaming with JSON Mode

Current Issue:
- with_structured_output() blocks until complete response
- No token-by-token streaming
- Poor user experience

Proposed Solution:
1. Use json_mode for streaming: model.bind(response_format={"type": "json_object"})
2. Stream tokens in real-time to frontend
3. Parse final JSON into Pydantic model after streaming completes
4. Provides immediate feedback while maintaining type safety

Implementation:
- Modify astream_response_mas() to use json_mode
- Stream reasoning tokens as they arrive
- Parse complete JSON at the end
- Best of both worlds: streaming + structured output
""")
    elif results['structured']:
        print("""
✅ UNEXPECTED: Structured output streaming appears to work!

This is surprising based on LangChain documentation.
Further investigation needed to understand the behavior.
""")
    else:
        print("""
⚠️ WARNING: All streaming methods failed

Check:
1. API key configuration
2. Network connectivity
3. Model availability
""")


if __name__ == "__main__":
    asyncio.run(main())

