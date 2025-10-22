"""
OpenAI Chat Model Wrapper using vanilla OpenAI SDK.

Drop-in replacement for langchain_openai.chat_models.ChatOpenAI
"""

import os
from typing import Any, AsyncGenerator, Dict, List, Optional, Type, Union
from pydantic import BaseModel
import json

try:
    from openai import OpenAI, AsyncOpenAI
except ImportError:
    raise ImportError(
        "OpenAI SDK not installed. Install with: pip install openai>=2.6.0"
    )

from .base_chat_model import BaseChatModel, AIMessage


class ChatOpenAI(BaseChatModel):
    """
    OpenAI chat model wrapper using vanilla OpenAI SDK.
    
    Compatible with LangChain's ChatOpenAI interface:
    - invoke(), ainvoke(), stream(), astream()
    - with_structured_output()
    
    Supports:
    - GPT-4o, GPT-4o-mini, GPT-4-turbo
    - GPT-5, o1, o3, o4 (reasoning models with reasoning_effort)
    - Structured output via response_format
    - Streaming with structured output
    """
    
    def __init__(
        self,
        model: str = "gpt-4o-mini",
        temperature: float = 0.7,
        api_key: Optional[str] = None,
        reasoning_effort: Optional[str] = None,
        verbose: bool = False,
        **kwargs
    ):
        """
        Initialize OpenAI chat model.
        
        Args:
            model: Model name (gpt-4o, gpt-4o-mini, gpt-5, o1, etc.)
            temperature: Sampling temperature (ignored for reasoning models)
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            reasoning_effort: For reasoning models: "low", "medium", "high"
            verbose: Enable verbose logging
            **kwargs: Additional OpenAI parameters
        """
        super().__init__(
            model=model,
            temperature=temperature,
            api_key=api_key or os.getenv("OPENAI_API_KEY"),
            verbose=verbose,
            **kwargs
        )
        
        self.reasoning_effort = reasoning_effort
        
        # Initialize OpenAI clients
        self.client = OpenAI(api_key=self.api_key)
        self.async_client = AsyncOpenAI(api_key=self.api_key)
        
        # Check if this is a reasoning model
        self._is_reasoning_model = self._check_reasoning_model()
        
        if self.verbose:
            print(f"✅ Initialized {self.__class__.__name__}(model='{self.model}', reasoning={self._is_reasoning_model})")
    
    def _check_reasoning_model(self) -> bool:
        """Check if the model is a reasoning model."""
        reasoning_prefixes = ['gpt-5', 'o1', 'o3', 'o4', 'gpt-4.1']
        return any(self.model.startswith(prefix) for prefix in reasoning_prefixes)

    def _normalize_roles_for_openai(self, messages: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Normalize roles for OpenAI API.

        OpenAI only accepts: "system", "user", "assistant", "tool", "function"
        MASAI uses agent names and tool names as roles in chat history.

        This method maps custom roles to OpenAI-compatible roles:
        - "user" → "user"
        - "system" → "system"
        - "assistant" → "assistant"
        - Any other role (agent names, tool names) → "assistant"

        Args:
            messages: Normalized message list with potentially custom roles

        Returns:
            Message list with OpenAI-compatible roles
        """
        openai_messages = []
        valid_roles = {"system", "user", "assistant", "tool", "function"}

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role in valid_roles:
                # Keep valid OpenAI roles as-is
                openai_messages.append({"role": role, "content": content})
            else:
                # Map custom roles (agent names, tool names) to "assistant"
                # Prepend the original role name to preserve context
                openai_messages.append({
                    "role": "assistant",
                    "content": f"[{role}]: {content}"
                })

        return openai_messages

    def _prepare_request_params(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        """
        Prepare parameters for OpenAI API request.

        Args:
            messages: Normalized message list (may contain custom roles like agent names)

        Returns:
            Dict of parameters for client.chat.completions.create()
        """
        # Normalize roles for OpenAI (convert agent names to "assistant")
        openai_messages = self._normalize_roles_for_openai(messages)

        params = {
            "model": self.model,
            "messages": openai_messages,
        }
        
        # Add temperature (not for reasoning models)
        if not self._is_reasoning_model:
            params["temperature"] = self.temperature
        
        # Add reasoning_effort for reasoning models
        if self._is_reasoning_model and self.reasoning_effort:
            params["reasoning_effort"] = self.reasoning_effort
        
        # Add structured output configuration
        if self._is_structured_output_enabled():
            schema = self._get_json_schema()
            
            if self._structured_output_method == "json_mode":
                # JSON mode: response_format with json_schema
                params["response_format"] = {
                    "type": "json_schema",
                    "json_schema": {
                        "name": self._structured_output_schema.__name__,
                        "schema": schema,
                        "strict": True
                    }
                }
            else:
                # Function calling mode (alternative)
                params["response_format"] = {"type": "json_object"}
        
        # Add any extra kwargs
        params.update(self.extra_kwargs)
        
        return params
    
    def invoke(self, messages: Union[str, List[Dict[str, str]]]) -> AIMessage:
        """
        Synchronously generate a response.

        Args:
            messages: String prompt or list of message dicts

        Returns:
            Pydantic model if structured output enabled, otherwise AIMessage
        """
        normalized_messages = self._normalize_messages(messages)
        params = self._prepare_request_params(normalized_messages)

        if self.verbose:
            print(f"🔵 OpenAI invoke: {self.model}")

        # Make API call
        response = self.client.chat.completions.create(**params)

        # Extract content
        content = response.choices[0].message.content

        # Parse structured output if enabled
        if self._is_structured_output_enabled():
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
            Pydantic model if structured output enabled, otherwise AIMessage
        """
        normalized_messages = self._normalize_messages(messages)
        params = self._prepare_request_params(normalized_messages)

        if self.verbose:
            print(f"🔵 OpenAI ainvoke: {self.model}")

        # Make async API call
        response = await self.async_client.chat.completions.create(**params)

        # Extract content
        content = response.choices[0].message.content

        # Parse structured output if enabled
        if self._is_structured_output_enabled():
            parsed = self._parse_structured_output(content)
            # Return Pydantic model directly (MASAI expects .model_dump() method)
            return parsed

        return AIMessage(content=content)
    
    def stream(self, messages: Union[str, List[Dict[str, str]]]):
        """
        Synchronously stream response chunks.
        
        Args:
            messages: String prompt or list of message dicts
        
        Yields:
            AIMessage chunks with incremental content
        """
        normalized_messages = self._normalize_messages(messages)
        params = self._prepare_request_params(normalized_messages)
        params["stream"] = True
        
        if self.verbose:
            print(f"🔵 OpenAI stream: {self.model}")
        
        # Stream API call
        stream = self.client.chat.completions.create(**params)
        
        accumulated_content = ""
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
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
            AIMessage chunks with incremental content (or Pydantic model for final structured output)
        """
        normalized_messages = self._normalize_messages(messages)
        params = self._prepare_request_params(normalized_messages)
        params["stream"] = True

        if self.verbose:
            print(f"🔵 OpenAI astream: {self.model}")

        # Async stream API call
        stream = await self.async_client.chat.completions.create(**params)

        accumulated_content = ""
        last_parsed = None
        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                accumulated_content += content

                # For structured output, yield parsed chunks
                if self._is_structured_output_enabled():
                    # Try to parse accumulated content
                    try:
                        parsed = self._parse_structured_output(accumulated_content)
                        last_parsed = parsed
                        yield AIMessage(content=accumulated_content, parsed=parsed)
                    except:
                        # Not yet complete JSON, yield raw content
                        yield AIMessage(content=content)
                else:
                    yield AIMessage(content=content)

        # For structured output, yield the final Pydantic model instance
        # This is what MASAI expects (has model_dump() method)
        if self._is_structured_output_enabled() and last_parsed:
            yield last_parsed

