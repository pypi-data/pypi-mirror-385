"""Chain of Thought reasoning module for Dinnovos Agent"""

from typing import List, Dict, Any, Optional, Iterator
from ..llms.base import BaseLLM


class ChainOfThought:
    """
    Implements Chain of Thought (CoT) reasoning patterns.
    
    This class enables step-by-step reasoning for complex problems,
    allowing the LLM to break down tasks and think through solutions
    methodically.
    """
    
    def __init__(self, llm: BaseLLM):
        """
        Initialize Chain of Thought with an LLM.
        
        Args:
            llm: Any LLM instance (OpenAI, Anthropic, Google)
        """
        self.llm = llm
    
    def reason(
        self,
        problem: str,
        context: Optional[str] = None,
        steps: int = 3,
        temperature: float = 0.7,
        strategy: str = "explicit"
    ) -> Dict[str, Any]:
        """
        Perform step-by-step reasoning on a problem.
        
        Args:
            problem: The problem or question to reason about
            context: Optional additional context
            steps: Number of reasoning steps to perform
            temperature: Temperature for generation
            strategy: Reasoning strategy - "explicit", "implicit", or "verification"
        
        Returns:
            Dict with 'steps' (list of reasoning steps), 'conclusion', and 'full_reasoning'
        """
        if strategy == "explicit":
            return self._explicit_reasoning(problem, context, steps, temperature)
        elif strategy == "implicit":
            return self._implicit_reasoning(problem, context, temperature)
        elif strategy == "verification":
            return self._verification_reasoning(problem, context, steps, temperature)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
    
    def reason_stream(
        self,
        problem: str,
        context: Optional[str] = None,
        steps: int = 3,
        temperature: float = 0.7,
        strategy: str = "explicit"
    ) -> Iterator[Dict[str, Any]]:
        """
        Stream step-by-step reasoning on a problem.
        
        Args:
            problem: The problem or question to reason about
            context: Optional additional context
            steps: Number of reasoning steps to perform
            temperature: Temperature for generation
            strategy: Reasoning strategy
        
        Yields:
            Dict with 'type' ('step_start', 'step_content', 'step_end', 'conclusion')
            and relevant content
        """
        if strategy == "explicit":
            yield from self._explicit_reasoning_stream(problem, context, steps, temperature)
        elif strategy == "implicit":
            yield from self._implicit_reasoning_stream(problem, context, temperature)
        elif strategy == "verification":
            yield from self._verification_reasoning_stream(problem, context, steps, temperature)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
    
    def _explicit_reasoning(
        self,
        problem: str,
        context: Optional[str],
        steps: int,
        temperature: float
    ) -> Dict[str, Any]:
        """Explicit step-by-step reasoning where each step is clearly defined."""
        reasoning_steps = []
        accumulated_reasoning = ""
        
        system_prompt = """You are an expert problem solver who thinks step by step.
For each step, clearly explain your reasoning process.
Be thorough and methodical in your analysis."""
        
        context_text = f"\n\nContext: {context}" if context else ""
        
        for step_num in range(1, steps + 1):
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"""Problem: {problem}{context_text}

{accumulated_reasoning}

Now, provide Step {step_num} of your reasoning process. Think carefully and explain your thought process for this step."""}
            ]
            
            step_response = self.llm.call(messages, temperature=temperature)
            
            reasoning_steps.append({
                "step": step_num,
                "content": step_response
            })
            
            accumulated_reasoning += f"\nStep {step_num}: {step_response}\n"
        
        # Get final conclusion
        conclusion_messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"""Problem: {problem}{context_text}

{accumulated_reasoning}

Based on all the reasoning steps above, provide your final conclusion and answer to the problem."""}
        ]
        
        conclusion = self.llm.call(conclusion_messages, temperature=temperature)
        
        return {
            "steps": reasoning_steps,
            "conclusion": conclusion,
            "full_reasoning": accumulated_reasoning,
            "strategy": "explicit"
        }
    
    def _explicit_reasoning_stream(
        self,
        problem: str,
        context: Optional[str],
        steps: int,
        temperature: float
    ) -> Iterator[Dict[str, Any]]:
        """Stream explicit step-by-step reasoning."""
        accumulated_reasoning = ""
        
        system_prompt = """You are an expert problem solver who thinks step by step.
For each step, clearly explain your reasoning process.
Be thorough and methodical in your analysis."""
        
        context_text = f"\n\nContext: {context}" if context else ""
        
        for step_num in range(1, steps + 1):
            yield {
                "type": "step_start",
                "step": step_num,
                "content": f"Starting step {step_num}..."
            }
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"""Problem: {problem}{context_text}

{accumulated_reasoning}

Now, provide Step {step_num} of your reasoning process. Think carefully and explain your thought process for this step."""}
            ]
            
            step_content = ""
            for chunk in self.llm.call_stream(messages, temperature=temperature):
                step_content += chunk
                yield {
                    "type": "step_content",
                    "step": step_num,
                    "content": chunk
                }
            
            accumulated_reasoning += f"\nStep {step_num}: {step_content}\n"
            
            yield {
                "type": "step_end",
                "step": step_num,
                "content": step_content
            }
        
        # Stream final conclusion
        yield {
            "type": "conclusion_start",
            "content": "Generating final conclusion..."
        }
        
        conclusion_messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"""Problem: {problem}{context_text}

{accumulated_reasoning}

Based on all the reasoning steps above, provide your final conclusion and answer to the problem."""}
        ]
        
        conclusion_content = ""
        for chunk in self.llm.call_stream(conclusion_messages, temperature=temperature):
            conclusion_content += chunk
            yield {
                "type": "conclusion_content",
                "content": chunk
            }
        
        yield {
            "type": "conclusion_end",
            "content": conclusion_content,
            "full_reasoning": accumulated_reasoning
        }
    
    def _implicit_reasoning(
        self,
        problem: str,
        context: Optional[str],
        temperature: float
    ) -> Dict[str, Any]:
        """Implicit reasoning using a single prompt that encourages step-by-step thinking."""
        system_prompt = """You are an expert problem solver. When given a problem, think through it step by step before providing your answer.

Use this format:
1. First, analyze what the problem is asking
2. Break down the problem into smaller parts
3. Solve each part systematically
4. Combine your findings into a final answer

Show your reasoning process clearly."""
        
        context_text = f"\n\nContext: {context}" if context else ""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Problem: {problem}{context_text}"}
        ]
        
        response = self.llm.call(messages, temperature=temperature)
        
        steps = self._parse_steps_from_text(response)
        
        return {
            "steps": steps,
            "conclusion": response,
            "full_reasoning": response,
            "strategy": "implicit"
        }
    
    def _implicit_reasoning_stream(
        self,
        problem: str,
        context: Optional[str],
        temperature: float
    ) -> Iterator[Dict[str, Any]]:
        """Stream implicit reasoning."""
        system_prompt = """You are an expert problem solver. When given a problem, think through it step by step before providing your answer.

Use this format:
1. First, analyze what the problem is asking
2. Break down the problem into smaller parts
3. Solve each part systematically
4. Combine your findings into a final answer

Show your reasoning process clearly."""
        
        context_text = f"\n\nContext: {context}" if context else ""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Problem: {problem}{context_text}"}
        ]
        
        full_response = ""
        for chunk in self.llm.call_stream(messages, temperature=temperature):
            full_response += chunk
            yield {
                "type": "reasoning_content",
                "content": chunk
            }
        
        steps = self._parse_steps_from_text(full_response)
        
        yield {
            "type": "reasoning_complete",
            "steps": steps,
            "full_reasoning": full_response
        }
    
    def _verification_reasoning(
        self,
        problem: str,
        context: Optional[str],
        steps: int,
        temperature: float
    ) -> Dict[str, Any]:
        """Reasoning with verification - each step is verified before proceeding."""
        reasoning_steps = []
        accumulated_reasoning = ""
        
        system_prompt = """You are an expert problem solver who thinks step by step and verifies each step.
For each step, explain your reasoning and then verify if it's correct."""
        
        context_text = f"\n\nContext: {context}" if context else ""
        
        for step_num in range(1, steps + 1):
            # Generate step
            step_messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"""Problem: {problem}{context_text}

{accumulated_reasoning}

Provide Step {step_num} of your reasoning. Explain your thought process."""}
            ]
            
            step_response = self.llm.call(step_messages, temperature=temperature)
            
            # Verify step
            verify_messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"""Problem: {problem}{context_text}

{accumulated_reasoning}

Step {step_num}: {step_response}

Now verify this step. Is the reasoning correct? Are there any errors or improvements needed?"""}
            ]
            
            verification = self.llm.call(verify_messages, temperature=temperature)
            
            reasoning_steps.append({
                "step": step_num,
                "content": step_response,
                "verification": verification
            })
            
            accumulated_reasoning += f"\nStep {step_num}: {step_response}\nVerification: {verification}\n"
        
        # Final conclusion
        conclusion_messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"""Problem: {problem}{context_text}

{accumulated_reasoning}

Based on all verified reasoning steps, provide your final conclusion."""}
        ]
        
        conclusion = self.llm.call(conclusion_messages, temperature=temperature)
        
        return {
            "steps": reasoning_steps,
            "conclusion": conclusion,
            "full_reasoning": accumulated_reasoning,
            "strategy": "verification"
        }
    
    def _verification_reasoning_stream(
        self,
        problem: str,
        context: Optional[str],
        steps: int,
        temperature: float
    ) -> Iterator[Dict[str, Any]]:
        """Stream reasoning with verification."""
        accumulated_reasoning = ""
        
        system_prompt = """You are an expert problem solver who thinks step by step and verifies each step.
For each step, explain your reasoning and then verify if it's correct."""
        
        context_text = f"\n\nContext: {context}" if context else ""
        
        for step_num in range(1, steps + 1):
            yield {
                "type": "step_start",
                "step": step_num,
                "content": f"Generating step {step_num}..."
            }
            
            step_messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"""Problem: {problem}{context_text}

{accumulated_reasoning}

Provide Step {step_num} of your reasoning. Explain your thought process."""}
            ]
            
            step_content = ""
            for chunk in self.llm.call_stream(step_messages, temperature=temperature):
                step_content += chunk
                yield {
                    "type": "step_content",
                    "step": step_num,
                    "content": chunk
                }
            
            yield {
                "type": "verification_start",
                "step": step_num,
                "content": f"Verifying step {step_num}..."
            }
            
            verify_messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"""Problem: {problem}{context_text}

{accumulated_reasoning}

Step {step_num}: {step_content}

Now verify this step. Is the reasoning correct? Are there any errors or improvements needed?"""}
            ]
            
            verification_content = ""
            for chunk in self.llm.call_stream(verify_messages, temperature=temperature):
                verification_content += chunk
                yield {
                    "type": "verification_content",
                    "step": step_num,
                    "content": chunk
                }
            
            accumulated_reasoning += f"\nStep {step_num}: {step_content}\nVerification: {verification_content}\n"
            
            yield {
                "type": "step_complete",
                "step": step_num,
                "step_content": step_content,
                "verification": verification_content
            }
        
        yield {
            "type": "conclusion_start",
            "content": "Generating final conclusion..."
        }
        
        conclusion_messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"""Problem: {problem}{context_text}

{accumulated_reasoning}

Based on all verified reasoning steps, provide your final conclusion."""}
        ]
        
        conclusion_content = ""
        for chunk in self.llm.call_stream(conclusion_messages, temperature=temperature):
            conclusion_content += chunk
            yield {
                "type": "conclusion_content",
                "content": chunk
            }
        
        yield {
            "type": "conclusion_end",
            "content": conclusion_content,
            "full_reasoning": accumulated_reasoning
        }
    
    def _parse_steps_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Parse reasoning steps from text that may contain numbered steps."""
        steps = []
        lines = text.split('\n')
        current_step = None
        current_content = []
        
        for line in lines:
            stripped = line.strip()
            if stripped and stripped[0].isdigit() and ('.' in stripped[:3] or ')' in stripped[:3]):
                if current_step is not None:
                    steps.append({
                        "step": current_step,
                        "content": '\n'.join(current_content).strip()
                    })
                
                try:
                    step_num = int(stripped.split('.')[0].split(')')[0])
                    current_step = step_num
                    current_content = [stripped]
                except:
                    current_content.append(line)
            else:
                if current_step is not None:
                    current_content.append(line)
        
        if current_step is not None:
            steps.append({
                "step": current_step,
                "content": '\n'.join(current_content).strip()
            })
        
        if not steps:
            steps = [{"step": 1, "content": text}]
        
        return steps
