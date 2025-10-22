"""
Test all MASAI imports to verify minimal dependencies work
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

print("="*80)
print("MASAI IMPORT TEST - Verifying Minimal Dependencies")
print("="*80)

tests_passed = 0
tests_failed = 0
errors = []

def test_import(module_path, description):
    """Test importing a module"""
    global tests_passed, tests_failed, errors
    try:
        exec(f"from {module_path} import *")
        print(f"✅ {description}")
        tests_passed += 1
        return True
    except Exception as e:
        print(f"❌ {description}")
        print(f"   Error: {str(e)[:100]}")
        tests_failed += 1
        errors.append((description, str(e)))
        return False

print("\n" + "-"*80)
print("Core Generative Models")
print("-"*80)

test_import("masai.GenerativeModel.baseGenerativeModel.basegenerativeModel", 
            "BaseGenerativeModel")
test_import("masai.GenerativeModel.generativeModels", 
            "MASGenerativeModel & GenerativeModel")

print("\n" + "-"*80)
print("Agent Components")
print("-"*80)

test_import("masai.Agents.base_agent", 
            "BaseAgent")
test_import("masai.Agents.singular_agent", 
            "Agent (Singular Agent)")

print("\n" + "-"*80)
print("Agent Management")
print("-"*80)

test_import("masai.AgentManager.AgentManager", 
            "AgentManager")

print("\n" + "-"*80)
print("Multi-Agent Systems")
print("-"*80)

test_import("masai.MultiAgents.MultiAgent", 
            "MultiAgentSystem")
test_import("masai.MultiAgents.TaskManager", 
            "TaskManager")

print("\n" + "-"*80)
print("OMAN (Orchestrated Multi-Agent Network)")
print("-"*80)

test_import("masai.OMAN.oman", 
            "OrchestratedMultiAgentNetwork")

print("\n" + "-"*80)
print("Memory & Storage")
print("-"*80)

test_import("masai.Memory.InMemoryStore", 
            "InMemoryDocStore")

print("\n" + "-"*80)
print("Custom LangGraph Implementation")
print("-"*80)

test_import("masai.langgraph.graph", 
            "StateGraph, END, START")
test_import("masai.langgraph.graph.state", 
            "CompiledStateGraph")

print("\n" + "-"*80)
print("Prompts & Templates")
print("-"*80)

test_import("masai.prompts", 
            "ChatPromptTemplate & PromptTemplate")
test_import("masai.prompts.prompt_templates", 
            "Prompt Templates")

print("\n" + "-"*80)
print("Pydantic Models")
print("-"*80)

test_import("masai.pydanticModels.AnswerModel", 
            "Answer Model")
test_import("masai.pydanticModels.supervisorModels", 
            "Supervisor Models")
test_import("masai.pydanticModels.omanModel", 
            "OMAN Model")

print("\n" + "-"*80)
print("Utilities")
print("-"*80)

test_import("masai.Tools.logging_setup.logger", 
            "Logger Setup")
test_import("masai.Tools.PARSERs.json_parser", 
            "JSON Parser")
test_import("masai.Tools.utilities.streaming_events", 
            "Streaming Events")
test_import("masai.Tools.utilities.enhanced_streaming", 
            "Enhanced Streaming")
test_import("masai.Tools.utilities.cache", 
            "Cache Utilities")
test_import("masai.Tools.utilities.deduplication_utils", 
            "Deduplication Utils")
test_import("masai.Tools.utilities.tokenGenerationTool", 
            "Token Generation Tool")

print("\n" + "-"*80)
print("Schema & Config")
print("-"*80)

test_import("masai.schema.document", 
            "Document Schema")
test_import("masai.Config.config", 
            "Config")

print("\n" + "="*80)
print("SUMMARY")
print("="*80)

print(f"\n✅ Tests Passed: {tests_passed}")
print(f"❌ Tests Failed: {tests_failed}")
print(f"📊 Success Rate: {tests_passed/(tests_passed+tests_failed)*100:.1f}%")

if tests_failed > 0:
    print("\n" + "="*80)
    print("FAILED IMPORTS")
    print("="*80)
    for desc, error in errors:
        print(f"\n❌ {desc}")
        print(f"   {error[:200]}")

if tests_failed == 0:
    print("\n🎉 ALL IMPORTS SUCCESSFUL!")
    print("✅ Minimal dependencies are sufficient for MASAI core functionality")
else:
    print(f"\n⚠️ {tests_failed} imports failed")
    print("   Check if additional dependencies are needed")

print("\n" + "="*80)

