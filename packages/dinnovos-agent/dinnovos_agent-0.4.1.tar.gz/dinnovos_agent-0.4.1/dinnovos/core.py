"""Core Dinnovos Agent implementation"""

from typing import List, Dict, Optional, Iterator, Any
from .llms.base import BaseLLM


class Agent:
    """
    Agent - Agile and intelligent conversational agent

    An agent that can use any LLM (OpenAI, Anthropic, Google)
    and maintains conversations with context memory.
    """
    
    def __init__(
        self, 
        llm: BaseLLM,
        system_prompt: Optional[str] = None,
        max_history: int = 10
    ):
        """
        Args:
            llm: LLM interface to use (OpenAI, Anthropic or Google)
            system_prompt: System instructions for the agent
            max_history: Maximum number of messages to keep in memory
        """
        self.llm = llm
        self.system_prompt = system_prompt or "You are a helpful and concise assistant."
        self.max_history = max_history
        self.messages: List[Dict[str, str]] = [
            {"role": "system", "content": self.system_prompt}
        ]
    
    def chat(
        self, 
        content: str = None, 
        temperature: float = 0.7,
        format: str = 'text',
        schema: Optional[Dict[str, Any]] = None,
        history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Sends a message to the agent and gets a response.
        
        Args:
            user_message: User's message
            temperature: Temperature for generation
            history: Optional list of previous messages to use as context.
                     Format: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
                     If provided, these messages will be used instead of the internal history.
        
        Returns:
            Agent's response
        """
        # If history is provided, use it instead of internal messages
        if history is not None:
            # Build messages with system prompt + provided history + new user message
            messages_to_send = [
                {"role": "system", "content": self.system_prompt}
            ] + history
            
            # Add user message if provided
            if content is not None:
                messages_to_send.append({"role": "user", "content": content})
        else:
            # Use internal message history
            self.messages.append({"role": "user", "content": content})
            messages_to_send = self.messages
        
        # Get LLM response
        response = self.llm.call(messages_to_send, temperature=temperature, format=format, schema=schema)
        
        # Only update internal history if no external history was provided
        if history is None:
            # Add assistant response
            self.messages.append({"role": "assistant", "content": response})
            
            # Keep only the last N messages (+ system prompt)
            if len(self.messages) > self.max_history + 1:
                # Keep system prompt + last max_history messages
                self.messages = [self.messages[0]] + self.messages[-(self.max_history):]
        
        return response
    
    def chat_stream(
        self, 
        content: str = None, 
        temperature: float = 0.7,
        format: str = 'text',
        history: Optional[List[Dict[str, str]]] = None
    ) -> Iterator[str]:
        """
        Sends a message to the agent and streams the response.
        
        Args:
            content: User's message
            temperature: Temperature for generation
            history: Optional list of previous messages to use as context.
                     Format: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
                     If provided, these messages will be used instead of the internal history.
        
        Yields:
            Chunks of the agent's response
        """
        # If history is provided, use it instead of internal messages
        if history is not None:
            # Build messages with system prompt + provided history + new user message
            messages_to_send = [
                {"role": "system", "content": self.system_prompt}
            ] + history
            
            # Add user message if provided
            if content is not None:
                messages_to_send.append({"role": "user", "content": content})
        else:
            # Use internal message history
            self.messages.append({"role": "user", "content": content})
            messages_to_send = self.messages
        
        # Stream LLM response
        full_response = ""
        
        for chunk in self.llm.call_stream(messages_to_send, temperature=temperature, format=format):
            full_response += chunk
            yield chunk
        
        # Only update internal history if no external history was provided
        if history is None:
            # Add assistant response
            self.messages.append({"role": "assistant", "content": full_response})
            
            # Keep only the last N messages (+ system prompt)
            if len(self.messages) > self.max_history + 1:
                # Keep system prompt + last max_history messages
                self.messages = [self.messages[0]] + self.messages[-(self.max_history):]
    
    def reset(self):
        """Resets the conversation"""
        self.messages = [{"role": "system", "content": self.system_prompt}]
    
    def get_history(self) -> List[Dict[str, str]]:
        """Gets message history"""
        return self.messages.copy()
    
    def set_system_prompt(self, new_prompt: str):
        """Changes the system prompt and resets the conversation"""
        self.system_prompt = new_prompt
        self.reset()
    
    def reason(
        self,
        problem: str,
        context: Optional[str] = None,
        steps: int = 3,
        temperature: float = 0.7,
        strategy: str = "explicit"
    ) -> Dict[str, Any]:
        """
        Perform Chain of Thought reasoning on a problem.
        
        Args:
            problem: The problem or question to reason about
            context: Optional additional context
            steps: Number of reasoning steps (for explicit/verification strategies)
            temperature: Temperature for generation
            strategy: Reasoning strategy - "explicit", "implicit", or "verification"
        
        Returns:
            Dict with reasoning steps, conclusion, and full reasoning process
        """
        from .utils.chain_of_thought import ChainOfThought
        
        cot = ChainOfThought(self.llm)
        return cot.reason(problem, context, steps, temperature, strategy)
    
    def reason_stream(
        self,
        problem: str,
        context: Optional[str] = None,
        steps: int = 3,
        temperature: float = 0.7,
        strategy: str = "explicit"
    ) -> Iterator[Dict[str, Any]]:
        """
        Stream Chain of Thought reasoning on a problem.
        
        Args:
            problem: The problem or question to reason about
            context: Optional additional context
            steps: Number of reasoning steps (for explicit/verification strategies)
            temperature: Temperature for generation
            strategy: Reasoning strategy - "explicit", "implicit", or "verification"
        
        Yields:
            Dict chunks with reasoning progress
        """
        from .utils.chain_of_thought import ChainOfThought
        
        cot = ChainOfThought(self.llm)
        yield from cot.reason_stream(problem, context, steps, temperature, strategy)