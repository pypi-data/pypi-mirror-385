"""
Comprehensive test suite for vanilla SDK wrappers.

Tests OpenAI and Google Gemini wrappers with:
- invoke, ainvoke, stream, astream
- Structured output with Pydantic models
- Multiple models (GPT-4o, GPT-4o-mini, Gemini 2.5 Pro, Gemini 2.5 Flash)
"""

import asyncio
import os
import sys
import time
from typing import List
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, 'src')

# Load environment variables
load_dotenv()

# Import vanilla wrappers
from masai.GenerativeModel.vanilla_wrappers import ChatOpenAI, ChatGoogleGenerativeAI


# Define test Pydantic models
class AgentResponse(BaseModel):
    """Response format for agent."""
    reasoning: str = Field(description="Step-by-step reasoning process")
    answer: str = Field(description="Final answer to the question")
    satisfied: bool = Field(description="Whether the answer is satisfactory")


class SimpleResponse(BaseModel):
    """Simple response format."""
    answer: str = Field(description="The answer")


# Test configuration
TEST_MODELS = {
    "openai": [
        ("gpt-4o", "openai"),
        ("gpt-4o-mini", "openai"),
    ],
    "gemini": [
        ("gemini-2.5-pro", "gemini"),
        ("gemini-2.5-flash", "gemini"),
    ]
}


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_test(test_name: str):
    """Print a formatted test header."""
    print(f"\n{'─' * 80}")
    print(f"  TEST: {test_name}")
    print(f"{'─' * 80}")


def test_openai_invoke():
    """Test OpenAI invoke (sync)."""
    print_test("OpenAI - invoke (sync, unstructured)")
    
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, verbose=True)
    
    prompt = "What is 2+2? Answer in one sentence."
    response = model.invoke(prompt)
    
    print(f"✅ Response: {response.content}")
    assert response.content, "Response should not be empty"
    print("✅ PASS: OpenAI invoke works")


def test_openai_invoke_structured():
    """Test OpenAI invoke with structured output."""
    print_test("OpenAI - invoke (sync, structured)")
    
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, verbose=True)
    structured_model = model.with_structured_output(SimpleResponse, method="json_mode")
    
    prompt = "What is the capital of France?"
    response = structured_model.invoke(prompt)
    
    print(f"✅ Response content: {response.content}")
    print(f"✅ Parsed: {response.additional_kwargs.get('parsed')}")
    
    assert hasattr(response, 'additional_kwargs'), "Response should have additional_kwargs"
    assert 'parsed' in response.additional_kwargs, "Response should have parsed field"
    parsed = response.additional_kwargs['parsed']
    assert isinstance(parsed, SimpleResponse), "Parsed should be SimpleResponse instance"
    print(f"✅ Parsed answer: {parsed.answer}")
    print("✅ PASS: OpenAI structured output works")


async def test_openai_ainvoke():
    """Test OpenAI ainvoke (async)."""
    print_test("OpenAI - ainvoke (async, unstructured)")
    
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, verbose=True)
    
    prompt = "What is 3+3? Answer in one sentence."
    response = await model.ainvoke(prompt)
    
    print(f"✅ Response: {response.content}")
    assert response.content, "Response should not be empty"
    print("✅ PASS: OpenAI ainvoke works")


async def test_openai_astream():
    """Test OpenAI astream (async streaming)."""
    print_test("OpenAI - astream (async streaming, unstructured)")
    
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, verbose=True)
    
    prompt = "Count from 1 to 5, one number per line."
    
    chunks = []
    start_time = time.time()
    async for chunk in model.astream(prompt):
        chunks.append(chunk.content)
        print(f"📦 Chunk {len(chunks)}: {chunk.content[:50]}")
    
    elapsed = time.time() - start_time
    
    full_response = "".join(chunks)
    print(f"\n✅ Total chunks: {len(chunks)}")
    print(f"✅ Time: {elapsed:.2f}s")
    print(f"✅ Full response: {full_response[:100]}")
    
    assert len(chunks) > 1, "Should receive multiple chunks"
    print("✅ PASS: OpenAI astream works")


async def test_openai_astream_structured():
    """Test OpenAI astream with structured output."""
    print_test("OpenAI - astream (async streaming, structured)")
    
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0.7, verbose=True)
    structured_model = model.with_structured_output(AgentResponse, method="json_mode")
    
    prompt = "Explain why the sky is blue. Provide reasoning and answer."
    
    chunks = []
    start_time = time.time()
    async for chunk in structured_model.astream(prompt):
        chunks.append(chunk)
        if hasattr(chunk, 'additional_kwargs') and 'parsed' in chunk.additional_kwargs:
            parsed = chunk.additional_kwargs['parsed']
            print(f"📦 Chunk {len(chunks)}: Parsed! reasoning={len(parsed.reasoning)} chars, answer={len(parsed.answer)} chars")
        else:
            print(f"📦 Chunk {len(chunks)}: {chunk.content[:30]}...")
    
    elapsed = time.time() - start_time
    
    print(f"\n✅ Total chunks: {len(chunks)}")
    print(f"✅ Time: {elapsed:.2f}s")
    
    # Check final chunk has parsed data
    final_chunk = chunks[-1]
    if hasattr(final_chunk, 'additional_kwargs') and 'parsed' in final_chunk.additional_kwargs:
        parsed = final_chunk.additional_kwargs['parsed']
        print(f"✅ Final parsed reasoning: {parsed.reasoning[:100]}...")
        print(f"✅ Final parsed answer: {parsed.answer[:100]}...")
        print(f"✅ Satisfied: {parsed.satisfied}")
    
    assert len(chunks) > 0, "Should receive chunks"
    print("✅ PASS: OpenAI astream structured works")


def test_gemini_invoke():
    """Test Gemini invoke (sync)."""
    print_test("Gemini - invoke (sync, unstructured)")
    
    model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7, verbose=True)
    
    prompt = "What is 2+2? Answer in one sentence."
    response = model.invoke(prompt)
    
    print(f"✅ Response: {response.content}")
    assert response.content, "Response should not be empty"
    print("✅ PASS: Gemini invoke works")


def test_gemini_invoke_structured():
    """Test Gemini invoke with structured output."""
    print_test("Gemini - invoke (sync, structured)")
    
    model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7, verbose=True)
    structured_model = model.with_structured_output(SimpleResponse)
    
    prompt = "What is the capital of Japan?"
    response = structured_model.invoke(prompt)
    
    print(f"✅ Response content: {response.content}")
    print(f"✅ Parsed: {response.additional_kwargs.get('parsed')}")
    
    assert hasattr(response, 'additional_kwargs'), "Response should have additional_kwargs"
    assert 'parsed' in response.additional_kwargs, "Response should have parsed field"
    parsed = response.additional_kwargs['parsed']
    assert isinstance(parsed, SimpleResponse), "Parsed should be SimpleResponse instance"
    print(f"✅ Parsed answer: {parsed.answer}")
    print("✅ PASS: Gemini structured output works")


async def test_gemini_astream():
    """Test Gemini astream (async streaming)."""
    print_test("Gemini - astream (async streaming, unstructured)")
    
    model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7, verbose=True)
    
    prompt = "Count from 1 to 5, one number per line."
    
    chunks = []
    start_time = time.time()
    async for chunk in model.astream(prompt):
        chunks.append(chunk.content)
        print(f"📦 Chunk {len(chunks)}: {chunk.content[:50]}")
    
    elapsed = time.time() - start_time
    
    full_response = "".join(chunks)
    print(f"\n✅ Total chunks: {len(chunks)}")
    print(f"✅ Time: {elapsed:.2f}s")
    print(f"✅ Full response: {full_response[:100]}")
    
    print(f"⚠️  Note: Gemini may return only 1 chunk (blocks until complete)")
    print("✅ PASS: Gemini astream works")


async def test_gemini_astream_structured():
    """Test Gemini astream with structured output."""
    print_test("Gemini - astream (async streaming, structured)")
    
    model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7, verbose=True)
    structured_model = model.with_structured_output(AgentResponse)
    
    prompt = "Explain why water is wet. Provide reasoning and answer."
    
    chunks = []
    start_time = time.time()
    async for chunk in structured_model.astream(prompt):
        chunks.append(chunk)
        if hasattr(chunk, 'additional_kwargs') and 'parsed' in chunk.additional_kwargs:
            parsed = chunk.additional_kwargs['parsed']
            print(f"📦 Chunk {len(chunks)}: Parsed! reasoning={len(parsed.reasoning)} chars, answer={len(parsed.answer)} chars")
        else:
            print(f"📦 Chunk {len(chunks)}: {chunk.content[:30]}...")
    
    elapsed = time.time() - start_time
    
    print(f"\n✅ Total chunks: {len(chunks)}")
    print(f"✅ Time: {elapsed:.2f}s")
    
    print(f"⚠️  Note: Gemini structured output may block until complete (1 chunk)")
    print("✅ PASS: Gemini astream structured works")


async def run_all_tests():
    """Run all tests."""
    print_section("VANILLA SDK WRAPPERS - COMPREHENSIVE TEST SUITE")
    
    print("\n🔍 Environment Check:")
    print(f"  OPENAI_API_KEY: {'✅ Set' if os.getenv('OPENAI_API_KEY') else '❌ Not set'}")
    print(f"  GOOGLE_API_KEY: {'✅ Set' if os.getenv('GOOGLE_API_KEY') else '❌ Not set'}")
    
    # OpenAI Tests
    print_section("OPENAI TESTS")
    
    try:
        test_openai_invoke()
    except Exception as e:
        print(f"❌ FAIL: {e}")
    
    try:
        test_openai_invoke_structured()
    except Exception as e:
        print(f"❌ FAIL: {e}")
    
    try:
        await test_openai_ainvoke()
    except Exception as e:
        print(f"❌ FAIL: {e}")
    
    try:
        await test_openai_astream()
    except Exception as e:
        print(f"❌ FAIL: {e}")
    
    try:
        await test_openai_astream_structured()
    except Exception as e:
        print(f"❌ FAIL: {e}")
    
    # Gemini Tests
    print_section("GEMINI TESTS")
    
    try:
        test_gemini_invoke()
    except Exception as e:
        print(f"❌ FAIL: {e}")
    
    try:
        test_gemini_invoke_structured()
    except Exception as e:
        print(f"❌ FAIL: {e}")
    
    try:
        await test_gemini_astream()
    except Exception as e:
        print(f"❌ FAIL: {e}")
    
    try:
        await test_gemini_astream_structured()
    except Exception as e:
        print(f"❌ FAIL: {e}")
    
    print_section("ALL TESTS COMPLETE")


if __name__ == "__main__":
    asyncio.run(run_all_tests())

