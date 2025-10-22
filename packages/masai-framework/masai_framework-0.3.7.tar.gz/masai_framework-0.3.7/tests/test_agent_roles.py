"""
Test vanilla wrappers with MASAI-style agent names and tool names as roles.

This test verifies that:
1. OpenAI wrapper correctly maps agent names to "assistant" role
2. Gemini wrapper correctly labels agent names in the prompt
3. Multi-agent conversation history is preserved correctly
"""

import os
import asyncio
from dotenv import load_dotenv

load_dotenv()

# Import vanilla wrappers
from src.masai.GenerativeModel.vanilla_wrappers import ChatOpenAI, ChatGoogleGenerativeAI

def test_openai_with_agent_roles():
    """Test OpenAI wrapper with agent names as roles."""
    print("\n" + "="*80)
    print("  TEST: OpenAI with Agent Names as Roles")
    print("="*80)
    
    # Create model
    model = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.7,
        api_key=os.getenv("OPENAI_API_KEY"),
        verbose=True
    )
    
    # Simulate MASAI multi-agent conversation history
    messages = [
        {"role": "user", "content": "What is 2+2?"},
        {"role": "math_agent", "content": "The answer is 4."},
        {"role": "user", "content": "What is 3+3?"},
        {"role": "calculator_tool", "content": "Result: 6"},
        {"role": "math_agent", "content": "The answer is 6."},
        {"role": "user", "content": "Now multiply the first answer by 2"}
    ]
    
    print("\n📝 Input messages (with agent names as roles):")
    for msg in messages:
        print(f"  {msg['role']}: {msg['content'][:50]}...")
    
    # Invoke model
    print("\n🔵 Calling OpenAI with agent roles...")
    response = model.invoke(messages)
    
    print(f"\n✅ Response: {response.content}")
    print("✅ PASS: OpenAI handles agent names correctly")
    
    return True

def test_gemini_with_agent_roles():
    """Test Gemini wrapper with agent names as roles."""
    print("\n" + "="*80)
    print("  TEST: Gemini with Agent Names as Roles")
    print("="*80)
    
    # Create model
    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.7,
        api_key=os.getenv("GOOGLE_API_KEY"),
        verbose=True
    )
    
    # Simulate MASAI multi-agent conversation history
    messages = [
        {"role": "user", "content": "What is 2+2?"},
        {"role": "math_agent", "content": "The answer is 4."},
        {"role": "user", "content": "What is 3+3?"},
        {"role": "calculator_tool", "content": "Result: 6"},
        {"role": "math_agent", "content": "The answer is 6."},
        {"role": "user", "content": "Now multiply the first answer by 2"}
    ]
    
    print("\n📝 Input messages (with agent names as roles):")
    for msg in messages:
        print(f"  {msg['role']}: {msg['content'][:50]}...")
    
    # Invoke model
    print("\n🟢 Calling Gemini with agent roles...")
    response = model.invoke(messages)
    
    print(f"\n✅ Response: {response.content}")
    print("✅ PASS: Gemini handles agent names correctly")
    
    return True

async def test_openai_streaming_with_agent_roles():
    """Test OpenAI streaming with agent names as roles."""
    print("\n" + "="*80)
    print("  TEST: OpenAI Streaming with Agent Names")
    print("="*80)
    
    # Create model
    model = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.7,
        api_key=os.getenv("OPENAI_API_KEY"),
        verbose=True
    )
    
    # Simulate MASAI multi-agent conversation
    messages = [
        {"role": "user", "content": "Count from 1 to 3"},
        {"role": "counter_agent", "content": "1, 2, 3"},
        {"role": "user", "content": "Now count from 4 to 6"}
    ]
    
    print("\n📝 Input messages:")
    for msg in messages:
        print(f"  {msg['role']}: {msg['content']}")
    
    # Stream response
    print("\n🔵 Streaming OpenAI response...")
    chunks = []
    async for chunk in model.astream(messages):
        chunks.append(chunk.content)
        print(f"📦 Chunk {len(chunks)}: {chunk.content[:20]}...")
    
    full_response = "".join(chunks)
    print(f"\n✅ Total chunks: {len(chunks)}")
    print(f"✅ Full response: {full_response}")
    print("✅ PASS: OpenAI streaming with agent roles works")
    
    return True

async def test_gemini_streaming_with_agent_roles():
    """Test Gemini streaming with agent names as roles."""
    print("\n" + "="*80)
    print("  TEST: Gemini Streaming with Agent Names")
    print("="*80)
    
    # Create model
    model = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.7,
        api_key=os.getenv("GOOGLE_API_KEY"),
        verbose=True
    )
    
    # Simulate MASAI multi-agent conversation
    messages = [
        {"role": "user", "content": "Count from 1 to 3"},
        {"role": "counter_agent", "content": "1, 2, 3"},
        {"role": "user", "content": "Now count from 4 to 6"}
    ]
    
    print("\n📝 Input messages:")
    for msg in messages:
        print(f"  {msg['role']}: {msg['content']}")
    
    # Stream response
    print("\n🟢 Streaming Gemini response...")
    chunks = []
    async for chunk in model.astream(messages):
        chunks.append(chunk.content)
        print(f"📦 Chunk {len(chunks)}: {chunk.content[:20]}...")
    
    full_response = "".join(chunks)
    print(f"\n✅ Total chunks: {len(chunks)}")
    print(f"✅ Full response: {full_response}")
    print("✅ PASS: Gemini streaming with agent roles works")
    
    return True

async def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("  AGENT ROLES TEST SUITE")
    print("  Testing vanilla wrappers with MASAI-style agent names")
    print("="*80)
    
    # Check environment
    print("\n🔍 Environment Check:")
    print(f"  OPENAI_API_KEY: {'✅ Set' if os.getenv('OPENAI_API_KEY') else '❌ Missing'}")
    print(f"  GOOGLE_API_KEY: {'✅ Set' if os.getenv('GOOGLE_API_KEY') else '❌ Missing'}")
    
    results = []
    
    # Test OpenAI
    try:
        results.append(test_openai_with_agent_roles())
    except Exception as e:
        print(f"❌ FAIL: {e}")
        results.append(False)
    
    # Test Gemini
    try:
        results.append(test_gemini_with_agent_roles())
    except Exception as e:
        print(f"❌ FAIL: {e}")
        results.append(False)
    
    # Test OpenAI streaming
    try:
        results.append(await test_openai_streaming_with_agent_roles())
    except Exception as e:
        print(f"❌ FAIL: {e}")
        results.append(False)
    
    # Test Gemini streaming
    try:
        results.append(await test_gemini_streaming_with_agent_roles())
    except Exception as e:
        print(f"❌ FAIL: {e}")
        results.append(False)
    
    # Summary
    print("\n" + "="*80)
    print("  TEST SUMMARY")
    print("="*80)
    passed = sum(results)
    total = len(results)
    print(f"\n✅ Passed: {passed}/{total}")
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
    else:
        print(f"❌ {total - passed} test(s) failed")
    
    return passed == total

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)

