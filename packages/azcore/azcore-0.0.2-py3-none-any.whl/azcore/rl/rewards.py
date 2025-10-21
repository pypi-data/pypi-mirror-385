"""
Reward calculation strategies for Azcore. RL.

This module provides various strategies for computing reward signals
from agent execution results, enabling flexible feedback mechanisms.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging
from langchain_core.messages import BaseMessage

logger = logging.getLogger(__name__)


class RewardCalculator(ABC):
    """
    Abstract base class for reward calculation strategies.
    
    Reward calculators take agent execution results and compute
    a reward signal (typically -1.0 to +1.0) for RL feedback.
    """
    
    @abstractmethod
    def calculate(
        self,
        state: Dict[str, Any],
        result: Any,
        user_query: str,
        **kwargs
    ) -> float:
        """
        Calculate reward from execution result.
        
        Args:
            state: Agent state after execution
            result: Execution result/output
            user_query: Original user query
            **kwargs: Additional context
            
        Returns:
            Reward value (typically -1.0 to +1.0)
        """
        pass


class HeuristicRewardCalculator(RewardCalculator):
    """
    Simple heuristic-based reward calculator.
    
    Uses rule-based checks to determine if execution was successful:
    - Positive reward if output is non-empty and no errors
    - Negative reward if errors detected or empty output
    - Configurable scoring rules
    
    Example:
        >>> calculator = HeuristicRewardCalculator(
        ...     success_reward=1.0,
        ...     failure_reward=-0.5,
        ...     error_patterns=["Error:", "Failed", "Exception"]
        ... )
        >>> reward = calculator.calculate(state, result, query)
    """
    
    def __init__(
        self,
        success_reward: float = 1.0,
        failure_reward: float = -0.5,
        empty_penalty: float = -0.3,
        error_patterns: Optional[list] = None,
        min_content_length: int = 10
    ):
        """
        Initialize heuristic calculator.
        
        Args:
            success_reward: Reward for successful execution
            failure_reward: Reward for failed execution
            empty_penalty: Reward for empty/insufficient output
            error_patterns: List of strings that indicate errors
            min_content_length: Minimum content length for success
        """
        self.success_reward = success_reward
        self.failure_reward = failure_reward
        self.empty_penalty = empty_penalty
        self.error_patterns = error_patterns or [
            "Error:", "error:", "ERROR",
            "Failed", "failed", "FAILED",
            "Exception", "exception",
            "Could not", "could not",
            "Unable to", "unable to"
        ]
        self.min_content_length = min_content_length
    
    def calculate(
        self,
        state: Dict[str, Any],
        result: Any,
        user_query: str,
        **kwargs
    ) -> float:
        """Calculate reward using heuristic rules."""
        # Extract content from result
        content = self._extract_content(result)
        
        # Check for empty content
        if not content or len(content) < self.min_content_length:
            logger.debug("Reward: Empty or insufficient content")
            return self.empty_penalty
        
        # Check for error patterns
        content_lower = content.lower()
        for pattern in self.error_patterns:
            if pattern.lower() in content_lower:
                logger.debug(f"Reward: Error pattern detected: {pattern}")
                return self.failure_reward
        
        # Check for tool call failures in state
        messages = state.get("messages", [])
        if self._has_tool_errors(messages):
            logger.debug("Reward: Tool execution errors detected")
            return self.failure_reward
        
        # Success case
        logger.debug("Reward: Successful execution detected")
        return self.success_reward
    
    def _extract_content(self, result: Any) -> str:
        """Extract text content from various result formats."""
        if isinstance(result, str):
            return result
        
        if isinstance(result, dict):
            # Try common keys
            for key in ["content", "output", "result", "text", "answer"]:
                if key in result:
                    return str(result[key])
            
            # Check for messages
            messages = result.get("messages", [])
            if messages:
                last_msg = messages[-1]
                if isinstance(last_msg, BaseMessage):
                    return last_msg.content
                elif isinstance(last_msg, tuple) and len(last_msg) > 1:
                    return str(last_msg[1])
        
        # Fallback to string representation
        return str(result)
    
    def _has_tool_errors(self, messages: list) -> bool:
        """Check if messages contain tool execution errors."""
        for msg in messages:
            if isinstance(msg, BaseMessage):
                content = msg.content
                if isinstance(content, str):
                    for pattern in self.error_patterns:
                        if pattern.lower() in content.lower():
                            return True
        return False


class LLMRewardCalculator(RewardCalculator):
    """
    LLM-based reward calculator using language models to score responses.
    
    Uses an LLM to evaluate response quality on a scale, then normalizes
    to a reward signal. More sophisticated than heuristics but slower.
    
    Example:
        >>> from langchain_openai import ChatOpenAI
        >>> llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        >>> calculator = LLMRewardCalculator(llm=llm)
        >>> reward = calculator.calculate(state, result, query)
    """
    
    def __init__(
        self,
        llm,
        score_min: int = 0,
        score_max: int = 100,
        reward_min: float = -1.0,
        reward_max: float = 1.0,
        evaluation_prompt_template: Optional[str] = None
    ):
        """
        Initialize LLM-based calculator.
        
        Args:
            llm: Language model for evaluation
            score_min: Minimum score from LLM
            score_max: Maximum score from LLM
            reward_min: Minimum reward value
            reward_max: Maximum reward value
            evaluation_prompt_template: Custom prompt template
        """
        self.llm = llm
        self.score_min = score_min
        self.score_max = score_max
        self.reward_min = reward_min
        self.reward_max = reward_max
        
        self.evaluation_prompt_template = evaluation_prompt_template or """
You are an expert evaluator. Rate the quality of the assistant's response.

User Query: {query}

Assistant Response: {response}

Evaluate the response on a scale of {score_min} to {score_max} based on:
- Relevance to the query
- Accuracy and correctness
- Completeness of the answer
- Clarity and usefulness

Respond with ONLY a number between {score_min} and {score_max}.
Score:"""
    
    def calculate(
        self,
        state: Dict[str, Any],
        result: Any,
        user_query: str,
        **kwargs
    ) -> float:
        """Calculate reward using LLM evaluation."""
        try:
            # Extract response content
            response = self._extract_response(result)
            
            # Build evaluation prompt
            prompt = self.evaluation_prompt_template.format(
                query=user_query,
                response=response,
                score_min=self.score_min,
                score_max=self.score_max
            )
            
            # Get LLM score
            llm_response = self.llm.invoke(prompt)
            
            # Extract numeric score
            score_text = llm_response.content if hasattr(llm_response, 'content') else str(llm_response)
            score = self._parse_score(score_text)
            
            # Normalize to reward range
            reward = self._normalize_score(score)
            
            logger.info(f"LLM Reward: score={score}/{self.score_max}, reward={reward:.3f}")
            return reward
            
        except Exception as e:
            logger.error(f"Error calculating LLM reward: {e}")
            # Return neutral reward on error
            return 0.0
    
    def _extract_response(self, result: Any) -> str:
        """Extract response text from result."""
        if isinstance(result, str):
            return result
        
        if isinstance(result, dict):
            messages = result.get("messages", [])
            if messages:
                last_msg = messages[-1]
                if isinstance(last_msg, BaseMessage):
                    return last_msg.content
                elif isinstance(last_msg, tuple) and len(last_msg) > 1:
                    return str(last_msg[1])
        
        return str(result)
    
    def _parse_score(self, text: str) -> float:
        """Parse numeric score from LLM response."""
        import re
        
        # Try to find a number in the text
        numbers = re.findall(r'\d+\.?\d*', text.strip())
        if numbers:
            try:
                score = float(numbers[0])
                # Clamp to valid range
                return max(self.score_min, min(self.score_max, score))
            except ValueError:
                pass
        
        # Default to middle score if parsing fails
        logger.warning(f"Could not parse score from: {text}")
        return (self.score_min + self.score_max) / 2
    
    def _normalize_score(self, score: float) -> float:
        """Normalize score to reward range."""
        # Linear mapping from [score_min, score_max] to [reward_min, reward_max]
        score_range = self.score_max - self.score_min
        reward_range = self.reward_max - self.reward_min
        
        normalized = (
            (score - self.score_min) / score_range * reward_range + self.reward_min
        )
        
        return max(self.reward_min, min(self.reward_max, normalized))


class UserFeedbackRewardCalculator(RewardCalculator):
    """
    Reward calculator based on explicit user feedback.
    
    Converts user feedback (thumbs up/down, ratings, etc.) into
    reward signals. Useful for human-in-the-loop RL.
    
    Example:
        >>> calculator = UserFeedbackRewardCalculator()
        >>> reward = calculator.calculate(
        ...     state, result, query,
        ...     user_feedback="positive"
        ... )
    """
    
    def __init__(
        self,
        positive_reward: float = 1.0,
        negative_reward: float = -1.0,
        neutral_reward: float = 0.0,
        use_rating_scale: bool = False,
        rating_min: int = 1,
        rating_max: int = 5
    ):
        """
        Initialize user feedback calculator.
        
        Args:
            positive_reward: Reward for positive feedback
            negative_reward: Reward for negative feedback
            neutral_reward: Reward when no feedback provided
            use_rating_scale: Whether to use numeric ratings
            rating_min: Minimum rating value
            rating_max: Maximum rating value
        """
        self.positive_reward = positive_reward
        self.negative_reward = negative_reward
        self.neutral_reward = neutral_reward
        self.use_rating_scale = use_rating_scale
        self.rating_min = rating_min
        self.rating_max = rating_max
    
    def calculate(
        self,
        state: Dict[str, Any],
        result: Any,
        user_query: str,
        user_feedback: Optional[Any] = None,
        **kwargs
    ) -> float:
        """Calculate reward from user feedback."""
        if user_feedback is None:
            logger.debug("No user feedback provided, using neutral reward")
            return self.neutral_reward
        
        # Handle boolean feedback
        if isinstance(user_feedback, bool):
            return self.positive_reward if user_feedback else self.negative_reward
        
        # Handle string feedback
        if isinstance(user_feedback, str):
            feedback_lower = user_feedback.lower()
            
            positive_keywords = ["positive", "good", "yes", "like", "helpful", "correct"]
            negative_keywords = ["negative", "bad", "no", "dislike", "wrong", "unhelpful"]
            
            if any(kw in feedback_lower for kw in positive_keywords):
                return self.positive_reward
            elif any(kw in feedback_lower for kw in negative_keywords):
                return self.negative_reward
        
        # Handle numeric ratings
        if isinstance(user_feedback, (int, float)) and self.use_rating_scale:
            # Normalize rating to reward range
            rating_range = self.rating_max - self.rating_min
            reward_range = self.positive_reward - self.negative_reward
            
            normalized = (
                (user_feedback - self.rating_min) / rating_range * reward_range
                + self.negative_reward
            )
            
            return max(self.negative_reward, min(self.positive_reward, normalized))
        
        logger.warning(f"Unknown feedback format: {user_feedback}, using neutral")
        return self.neutral_reward


class CompositeRewardCalculator(RewardCalculator):
    """
    Combines multiple reward calculators with weights.
    
    Useful for combining heuristic, LLM, and user feedback signals.
    
    Example:
        >>> calculator = CompositeRewardCalculator([
        ...     (HeuristicRewardCalculator(), 0.3),
        ...     (LLMRewardCalculator(llm), 0.5),
        ...     (UserFeedbackRewardCalculator(), 0.2)
        ... ])
    """
    
    def __init__(self, calculators: list):
        """
        Initialize composite calculator.
        
        Args:
            calculators: List of (calculator, weight) tuples
        """
        self.calculators = calculators
        
        # Normalize weights
        total_weight = sum(weight for _, weight in calculators)
        self.calculators = [
            (calc, weight / total_weight) for calc, weight in calculators
        ]
    
    def calculate(
        self,
        state: Dict[str, Any],
        result: Any,
        user_query: str,
        **kwargs
    ) -> float:
        """Calculate weighted combination of rewards."""
        total_reward = 0.0
        
        for calculator, weight in self.calculators:
            try:
                reward = calculator.calculate(state, result, user_query, **kwargs)
                total_reward += reward * weight
            except Exception as e:
                logger.error(f"Error in calculator {calculator.__class__.__name__}: {e}")
        
        logger.debug(f"Composite reward: {total_reward:.3f}")
        return total_reward
