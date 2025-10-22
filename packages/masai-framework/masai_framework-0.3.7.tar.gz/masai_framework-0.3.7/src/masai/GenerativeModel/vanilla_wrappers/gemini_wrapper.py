"""
Google Gemini Chat Model Wrapper using vanilla Google Generative AI SDK.

Drop-in replacement for langchain_google_genai.chat_models.ChatGoogleGenerativeAI
"""

import os
from typing import Any, AsyncGenerator, Dict, List, Optional, Type, Union
from pydantic import BaseModel
import json

try:
    import google.generativeai as genai
except ImportError:
    raise ImportError(
        "Google Generative AI SDK not installed. Install with: pip install google-generativeai>=0.8.5"
    )

from .base_chat_model import BaseChatModel, AIMessage


class ChatGoogleGenerativeAI(BaseChatModel):
    """
    Google Gemini chat model wrapper using vanilla Google Generative AI SDK.
    
    Compatible with LangChain's ChatGoogleGenerativeAI interface:
    - invoke(), ainvoke(), stream(), astream()
    - with_structured_output()
    
    Supports:
    - Gemini 2.5 Pro, Gemini 2.5 Flash
    - Gemini 2.0 Flash, Gemini 1.5 Pro/Flash
    - Structured output via response_schema
    - Thinking models with thinkingBudget
    """
    
    def __init__(
        self,
        model: str = "gemini-2.5-flash",
        temperature: float = 0.7,
        api_key: Optional[str] = None,
        model_kwargs: Optional[Dict[str, Any]] = None,
        verbose: bool = False,
        **kwargs
    ):
        """
        Initialize Google Gemini chat model.
        
        Args:
            model: Model name (gemini-2.5-pro, gemini-2.5-flash, etc.)
            temperature: Sampling temperature
            api_key: Google API key (defaults to GOOGLE_API_KEY env var)
            model_kwargs: Additional model parameters (e.g., thinkingBudget)
            verbose: Enable verbose logging
            **kwargs: Additional parameters
        """
        super().__init__(
            model=model,
            temperature=temperature,
            api_key=api_key or os.getenv("GOOGLE_API_KEY"),
            verbose=verbose,
            **kwargs
        )
        
        self.model_kwargs = model_kwargs or {}

        # Configure Google Generative AI
        genai.configure(api_key=self.api_key)

        # Check if this is a thinking model
        self._is_thinking_model = self._check_thinking_model()

        if self.verbose:
            print(f"✅ Initialized {self.__class__.__name__}(model='{self.model}', thinking={self._is_thinking_model})")
    
    def _check_thinking_model(self) -> bool:
        """Check if the model is a thinking/reasoning model."""
        return (
            self.model.startswith('gemini-2.5') or
            'thinking' in self.model.lower()
        )
    
    def _prepare_generation_config(self) -> Dict[str, Any]:
        """
        Prepare generation configuration for Gemini API.

        Returns:
            Dict of generation config parameters
        """
        config = {
            "temperature": self.temperature,
        }

        # Add thinking budget for thinking models
        if self._is_thinking_model and "thinkingBudget" in self.model_kwargs:
            config["thinking_budget"] = self.model_kwargs["thinkingBudget"]

        # Add structured output configuration
        if self._is_structured_output_enabled():
            # Get raw Pydantic schema (NOT OpenAI-processed schema)
            # OpenAI's _get_json_schema() forces all fields to be required, which we don't want for Gemini
            schema = self._structured_output_schema.model_json_schema()
            cleaned_schema = self._convert_to_gemini_schema(schema)

            # Debug: Print schema being sent (can be disabled in production)
            if self.verbose:
                import json
                print("🔍 DEBUG: Gemini schema being sent:")
                print(json.dumps(cleaned_schema, indent=2))

            config["response_mime_type"] = "application/json"
            config["response_schema"] = cleaned_schema

        # Add any extra model_kwargs (but not thinkingBudget again)
        for key, value in self.model_kwargs.items():
            if key not in ["thinkingBudget"]:
                config[key] = value

        return config
    
    def _convert_to_gemini_schema(self, json_schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert JSON schema to Gemini schema format.

        Gemini uses a slightly different schema format than standard JSON Schema.
        Removes unsupported fields like 'default', 'additionalProperties', etc.
        Handles anyOf/allOf/oneOf by flattening to the first type or merging properties.

        Args:
            json_schema: Standard JSON schema from Pydantic

        Returns:
            Gemini-compatible schema
        """
        import copy

        # Deep copy to avoid modifying original
        cleaned_schema = copy.deepcopy(json_schema)

        # Clean up schema for Gemini compatibility
        def clean_schema(obj):
            """Remove unsupported fields from schema recursively."""
            if isinstance(obj, dict):
                # Handle anyOf/allOf/oneOf (Gemini doesn't support these)
                if 'anyOf' in obj:
                    # Flatten anyOf - prefer string type for flexibility
                    any_of_schemas = obj.pop('anyOf')

                    # Strategy: Find string type first (most flexible for Gemini)
                    # Otherwise use first non-null type
                    string_schema = None
                    first_non_null = None

                    for schema in any_of_schemas:
                        if isinstance(schema, dict):
                            if schema.get('type') == 'string':
                                string_schema = schema
                                break
                            elif schema.get('type') != 'null' and not first_non_null:
                                first_non_null = schema

                    # Prefer string, fallback to first non-null
                    chosen_schema = string_schema or first_non_null
                    if chosen_schema:
                        obj.update(chosen_schema)

                if 'allOf' in obj:
                    # Merge all schemas in allOf
                    all_of_schemas = obj.pop('allOf')
                    for schema in all_of_schemas:
                        if isinstance(schema, dict):
                            # Merge properties
                            if 'properties' in schema:
                                if 'properties' not in obj:
                                    obj['properties'] = {}
                                obj['properties'].update(schema['properties'])
                            # Merge other fields
                            for key, value in schema.items():
                                if key not in ['properties']:
                                    obj[key] = value

                if 'oneOf' in obj:
                    # Flatten oneOf - prefer string type
                    one_of_schemas = obj.pop('oneOf')
                    if one_of_schemas:
                        # Try to find string type first
                        string_schema = next((s for s in one_of_schemas if isinstance(s, dict) and s.get('type') == 'string'), None)
                        obj.update(string_schema or one_of_schemas[0])

                # Gemini requires non-empty properties for OBJECT type
                # If type is object but properties is empty or missing, change to string
                if obj.get('type') == 'object':
                    if 'properties' not in obj or not obj['properties']:
                        # Change to string type (more flexible for Gemini)
                        obj['type'] = 'string'
                        obj.pop('properties', None)
                        obj.pop('required', None)

                # Remove unsupported fields
                unsupported_fields = ['default', 'additionalProperties', 'title', '$defs']
                for field in unsupported_fields:
                    obj.pop(field, None)

                # Recursively clean nested objects
                for value in list(obj.values()):  # Use list() to avoid dict size change during iteration
                    clean_schema(value)
            elif isinstance(obj, list):
                for item in obj:
                    clean_schema(item)

        clean_schema(cleaned_schema)
        return cleaned_schema
    
    def _normalize_messages_to_gemini(
        self,
        messages: List[Dict[str, str]]
    ) -> str:
        """
        Convert message list to Gemini prompt format.

        Gemini's generate_content expects a single prompt string or
        a list of Content objects. For MASAI's use case (single formatted prompt),
        we use a string for simplicity.

        Note: Gemini doesn't natively support system messages. Following LangChain's
        approach, we prepend system content to the first user message.

        MASAI-specific behavior:
        - First message from user has role="user" (from initiate_agent)
        - Subsequent messages use agent names or tool names as roles
        - This preserves multi-agent conversation context

        Args:
            messages: Normalized message list [{"role": "user/assistant/system/<agent_name>/<tool_name>", "content": "..."}]

        Returns:
            Single prompt string suitable for Gemini
        """
        # Handle system message by prepending to first user message (LangChain approach)
        system_content = None
        prompt_parts = []

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if not content:  # Skip empty messages
                continue

            if role == "system":
                # Store system content to prepend to first user message
                system_content = content
            elif role == "user":
                # Prepend system content if present (only once)
                if system_content:
                    prompt_parts.append(f"{system_content}\n\n{content}")
                    system_content = None  # Clear after use
                else:
                    prompt_parts.append(content)
            elif role == "assistant":
                # For multi-turn conversations, label assistant messages
                prompt_parts.append(f"Assistant: {content}")
            else:
                # MASAI uses agent names and tool names as roles
                # Format: "<AgentName>: <content>" or "<ToolName>: <content>"
                # This preserves multi-agent conversation context
                prompt_parts.append(f"{role}: {content}")

        # If only system message exists (edge case), return it as user message
        if not prompt_parts and system_content:
            return system_content

        return "\n\n".join(prompt_parts)
    
    def invoke(self, messages: Union[str, List[Dict[str, str]]]) -> AIMessage:
        """
        Synchronously generate a response.

        Args:
            messages: String prompt or list of message dicts

        Returns:
            Pydantic model if structured output enabled, otherwise AIMessage
        """
        normalized_messages = self._normalize_messages(messages)
        prompt = self._normalize_messages_to_gemini(normalized_messages)
        config = self._prepare_generation_config()

        if self.verbose:
            print(f"🟢 Gemini invoke: {self.model}")

        # Create model instance
        model_instance = genai.GenerativeModel(
            model_name=self.model,
            generation_config=config
        )

        # Make API call
        response = model_instance.generate_content(prompt)

        # Extract content
        content = response.text

        # Parse structured output if enabled
        if self._is_structured_output_enabled():
            # Gemini returns parsed object directly
            if hasattr(response, 'parsed') and response.parsed:
                # Return Pydantic model directly (MASAI expects .model_dump() method)
                return response.parsed
            else:
                # Fallback to manual parsing
                parsed = self._parse_structured_output(content)
                # Return Pydantic model directly (MASAI expects .model_dump() method)
                return parsed

        return AIMessage(content=content)
    
    async def ainvoke(self, messages: Union[str, List[Dict[str, str]]]) -> AIMessage:
        """
        Asynchronously generate a response.
        
        Args:
            messages: String prompt or list of message dicts
        
        Returns:
            AIMessage with response (or Pydantic model if structured output)
        """
        # Note: Google SDK doesn't have native async support yet
        # We'll use asyncio.to_thread to run sync code in async context
        import asyncio
        return await asyncio.to_thread(self.invoke, messages)
    
    def stream(self, messages: Union[str, List[Dict[str, str]]]):
        """
        Synchronously stream response chunks.

        Args:
            messages: String prompt or list of message dicts

        Yields:
            AIMessage chunks with incremental content
        """
        normalized_messages = self._normalize_messages(messages)
        prompt = self._normalize_messages_to_gemini(normalized_messages)
        config = self._prepare_generation_config()

        if self.verbose:
            print(f"🟢 Gemini stream: {self.model}")

        # Create model instance
        model_instance = genai.GenerativeModel(
            model_name=self.model,
            generation_config=config
        )

        # Stream API call
        response_stream = model_instance.generate_content(prompt, stream=True)

        accumulated_content = ""
        for chunk in response_stream:
            if hasattr(chunk, 'text') and chunk.text:
                content = chunk.text
                accumulated_content += content

                # For structured output, yield parsed chunks
                if self._is_structured_output_enabled():
                    # Try to parse accumulated content
                    try:
                        parsed = self._parse_structured_output(accumulated_content)
                        yield AIMessage(content=accumulated_content, parsed=parsed)
                    except:
                        # Not yet complete JSON, yield raw content
                        yield AIMessage(content=content)
                else:
                    yield AIMessage(content=content)
    
    async def astream(self, messages: Union[str, List[Dict[str, str]]]) -> AsyncGenerator[AIMessage, None]:
        """
        Asynchronously stream response chunks.

        Args:
            messages: String prompt or list of message dicts

        Yields:
            AIMessage chunks with incremental content
        """
        normalized_messages = self._normalize_messages(messages)
        prompt = self._normalize_messages_to_gemini(normalized_messages)
        config = self._prepare_generation_config()

        if self.verbose:
            print(f"🟢 Gemini astream: {self.model}")

        # Note: Google SDK doesn't have native async streaming yet
        # We'll use asyncio.to_thread to run sync streaming in async context
        import asyncio

        # Create a queue for chunks
        from queue import Queue
        chunk_queue = Queue()
        done_sentinel = object()

        def stream_worker():
            last_parsed = None
            try:
                # Create model instance
                model_instance = genai.GenerativeModel(
                    model_name=self.model,
                    generation_config=config
                )

                # Stream API call
                response_stream = model_instance.generate_content(prompt, stream=True)

                accumulated_content = ""
                for chunk in response_stream:
                    # Check if chunk has text content
                    if hasattr(chunk, 'text'):
                        try:
                            content = chunk.text
                            accumulated_content += content

                            # For structured output, yield parsed chunks
                            if self._is_structured_output_enabled():
                                try:
                                    parsed = self._parse_structured_output(accumulated_content)
                                    last_parsed = parsed
                                    chunk_queue.put(AIMessage(content=accumulated_content, parsed=parsed))
                                except:
                                    chunk_queue.put(AIMessage(content=content))
                            else:
                                chunk_queue.put(AIMessage(content=content))
                        except ValueError as e:
                            # Gemini blocked response (safety filter or validation error)
                            # finish_reason=1 means SAFETY or other blocking
                            error_msg = f"Gemini blocked response: {str(e)}"
                            if hasattr(chunk, 'candidates') and chunk.candidates:
                                finish_reason = chunk.candidates[0].finish_reason
                                error_msg = f"Gemini finish_reason={finish_reason}: {str(e)}"

                            # Raise exception to be caught by outer try-except
                            raise ValueError(error_msg)

                # For structured output, yield the final Pydantic model instance
                # This is what MASAI expects (has model_dump() method)
                if self._is_structured_output_enabled() and last_parsed:
                    chunk_queue.put(last_parsed)
                elif self._is_structured_output_enabled() and not last_parsed:
                    # No valid parsed response - raise error
                    raise ValueError("No valid structured output received from Gemini")
            finally:
                chunk_queue.put(done_sentinel)

        # Start streaming in background thread
        import threading
        thread = threading.Thread(target=stream_worker)
        thread.start()

        # Yield chunks from queue
        while True:
            chunk = await asyncio.to_thread(chunk_queue.get)
            if chunk is done_sentinel:
                break
            yield chunk

