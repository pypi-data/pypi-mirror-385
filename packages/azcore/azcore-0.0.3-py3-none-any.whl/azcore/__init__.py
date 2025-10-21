"""
Azcore - A Professional Multi-Agent Framework

A comprehensive framework for building hierarchical multi-agent systems with LangGraph,
featuring coordinator-planner-supervisor architecture, team management, and flexible
agent orchestration with improved error handling and validation.

Version: 0.0.3
Author: Arc  Team
License: MIT
"""

# Suppress LangGraph deprecation warnings (internal library warnings)
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning, module='langgraph')

__version__ = "0.0.3"
__author__ = "Arc Team"

from azcore.core.base import BaseAgent, BaseTeam, BaseNode
from azcore.core.state import State, StateManager
from azcore.core.supervisor import Supervisor
from azcore.agents.team_builder import TeamBuilder
from azcore.agents.agent_factory import AgentFactory
from azcore.nodes.coordinator import CoordinatorNode
from azcore.nodes.planner import PlannerNode
from azcore.nodes.generator import ResponseGeneratorNode
from azcore.config.config import Config, load_config
from azcore.core.orchestrator import GraphOrchestrator
from azcore.utils.logging import setup_logging, get_logger
from azcore import exceptions
from azcore.config import validation
from azcore.utils import retry

__all__ = [
    # Core classes
    "BaseAgent",
    "BaseTeam",
    "BaseNode",
    "State",
    "StateManager",
    "Supervisor",
    
    # Agent classes
    "TeamBuilder",
    "AgentFactory",
    
    # Node classes
    "CoordinatorNode",
    "PlannerNode",
    "ResponseGeneratorNode",
    
    # Configuration
    "Config",
    "load_config",
    
    # Orchestration
    "GraphOrchestrator",
    
    # Utilities
    "setup_logging",
    "get_logger",
    
    # New modules
    "exceptions",
    "validation",
    "retry",
    
    # Version
    "__version__",
    "__author__",
]
