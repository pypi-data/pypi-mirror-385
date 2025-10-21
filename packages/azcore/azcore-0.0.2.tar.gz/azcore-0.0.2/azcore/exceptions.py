"""
Custom exceptions for the Azcore..

This module provides a comprehensive exception hierarchy for better
error handling and debugging throughout the framework.
"""


class AzCoreException(Exception):
    """
    Base exception for all Azcore. errors.
    
    All custom exceptions in the framework inherit from this class,
    allowing for easy catching of all framework-specific errors.
    """
    
    def __init__(self, message: str, details: dict = None):
        """
        Initialize the exception.
        
        Args:
            message: Human-readable error message
            details: Optional dictionary with additional error context
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
    def __str__(self) -> str:
        if self.details:
            details_str = ", ".join(f"{k}={v}" for k, v in self.details.items())
            return f"{self.message} ({details_str})"
        return self.message


class ConfigurationError(AzCoreException):
    """
    Configuration-related errors.
    
    Raised when:
    - Configuration file is missing or invalid
    - Required configuration keys are missing
    - Configuration values are out of valid range
    - Environment variables are not set
    """
    pass


class ValidationError(AzCoreException):
    """
    Input/output validation errors.
    
    Raised when:
    - Input parameters fail validation
    - Output format is invalid
    - Schema validation fails
    - Type checking fails
    """
    pass


class LLMError(AzCoreException):
    """
    LLM invocation and response errors.
    
    Raised when:
    - LLM API call fails
    - Response parsing fails
    - Rate limits are exceeded
    - Model is unavailable
    """
    pass


class LLMTimeoutError(LLMError):
    """
    LLM request timeout error.
    
    Raised when an LLM request exceeds the configured timeout.
    """
    pass


class LLMRateLimitError(LLMError):
    """
    LLM rate limit exceeded error.
    
    Raised when LLM API rate limits are exceeded.
    """
    pass


class NodeExecutionError(AzCoreException):
    """
    Node execution errors.
    
    Raised when:
    - Node execution fails
    - Node returns invalid output
    - Node exceeds execution timeout
    - Node state is invalid
    """
    pass


class ToolExecutionError(AzCoreException):
    """
    Tool execution errors.
    
    Raised when:
    - Tool execution fails
    - Tool returns invalid output
    - Tool not found
    - Tool permission denied
    """
    pass


class ToolNotFoundError(ToolExecutionError):
    """
    Tool not found error.
    
    Raised when attempting to use a tool that doesn't exist.
    """
    pass


class StateError(AzCoreException):
    """
    State management errors.
    
    Raised when:
    - State is invalid or corrupted
    - State update fails
    - State validation fails
    - State size exceeds limits
    """
    pass


class SupervisorError(AzCoreException):
    """
    Supervisor routing and decision errors.
    
    Raised when:
    - Supervisor routing fails
    - Invalid routing decision
    - No valid route available
    - Supervisor response is malformed
    """
    pass


class TeamError(AzCoreException):
    """
    Team building and execution errors.
    
    Raised when:
    - Team building fails
    - Team execution fails
    - Team configuration is invalid
    - Required team component is missing
    """
    pass


class GraphError(AzCoreException):
    """
    Graph orchestration errors.
    
    Raised when:
    - Graph compilation fails
    - Graph execution fails
    - Invalid graph structure
    - Cycle detected in graph
    """
    pass


class GraphCycleError(GraphError):
    """
    Graph cycle detection error.
    
    Raised when a cycle is detected in the execution graph.
    """
    pass


class MaxIterationsExceededError(GraphError):
    """
    Maximum iterations exceeded error.
    
    Raised when graph execution exceeds the maximum iteration limit.
    """
    pass


class RLError(AzCoreException):
    """
    Reinforcement learning errors.
    
    Raised when:
    - RL manager initialization fails
    - Q-table loading/saving fails
    - Reward calculation fails
    - Invalid RL configuration
    """
    pass


class EmbeddingError(RLError):
    """
    Embedding generation and similarity errors.
    
    Raised when:
    - Embedding model loading fails
    - Embedding generation fails
    - Similarity computation fails
    """
    pass


class RewardCalculationError(RLError):
    """
    Reward calculation error.
    
    Raised when reward calculation fails for any reward calculator.
    """
    pass


class AgentError(AzCoreException):
    """
    Agent creation and execution errors.
    
    Raised when:
    - Agent initialization fails
    - Agent execution fails
    - Agent configuration is invalid
    """
    pass


class TimeoutError(AzCoreException):
    """
    Generic timeout error.
    
    Raised when an operation exceeds its configured timeout.
    """
    pass


# Convenience function for creating detailed exceptions
def create_detailed_error(
    exception_class: type,
    message: str,
    **details
) -> AzCoreException:
    """
    Create an exception with detailed context.
    
    Args:
        exception_class: Exception class to instantiate
        message: Error message
        **details: Additional context as keyword arguments
        
    Returns:
        Exception instance with message and details
        
    Example:
        >>> raise create_detailed_error(
        ...     ConfigurationError,
        ...     "Invalid temperature value",
        ...     key="llm.temperature",
        ...     value=2.5,
        ...     valid_range="0.0-2.0"
        ... )
    """
    return exception_class(message, details=details)
