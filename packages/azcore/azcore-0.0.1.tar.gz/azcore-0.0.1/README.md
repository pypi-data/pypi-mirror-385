# 🌟 Arc Framework

[![PyPI - Version](https://img.shields.io/pypi/v/azcore)](https://pypi.org/project/azcore/)
[![PyPI - License](https://img.shields.io/pypi/l/azcore)](https://github.com/Azrienlabs/Arc/blob/main/LICENSE)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/azcore)](https://pypi.org/project/azcore/)

> **Arc** - A professional hierarchical multi-agent framework built on Python

To help you ship Arc-powered apps to production faster, check out our comprehensive agent orchestration and workflow management capabilities.

## Quick Install

```bash
pip install azcore
```

## 🤔 What is this?

**Arc** is the easiest way to start building hierarchical multi-agent systems and autonomous applications powered by LLMs. With under 10 lines of code, you can create sophisticated agent teams that collaborate, reason, and solve complex problems. Arc provides pre-built agent architectures, orchestration patterns, and workflow management to help you get started quickly and seamlessly incorporate intelligent agents into your applications.

We recommend you use Arc if you want to:
- **Quickly build multi-agent systems** with hierarchical coordination
- **Implement advanced reasoning patterns** like ReAct, Reflexion, and Self-Consistency
- **Create autonomous agent teams** with built-in collaboration and routing
- **Build production-ready agent applications** with persistence, caching, and monitoring

Arc supports multiple agent patterns and workflows including:
- 🎯 **Agent Patterns**: ReAct, Reflexion, Reasoning Duo, Self-Consistency
- 🌲 **Workflow Types**: Sequential, Concurrent, Hierarchical, Forest Swarm, Graph-based
- 🤝 **Team Coordination**: Agent routing, pattern matching, group chat, mixture of agents
- 🔄 **Advanced Features**: Reinforcement learning, state management, agent persistence

## 🚀 Features

- **Multiple Agent Architectures**: Choose from ReAct, Reflexion, and custom agent patterns
- **Hierarchical Organization**: Build complex agent hierarchies with supervisors and coordinators
- **Flexible Workflows**: Sequential, concurrent, graph-based, and swarm workflows
- **Agent Routing**: Intelligent routing based on patterns, capabilities, and context
- **State Management**: Robust state tracking and persistence across agent interactions
- **MCP Integration**: Support for Model Context Protocol team building
- **Reinforcement Learning**: Built-in RL manager for agent optimization
- **Caching & Performance**: Smart caching for LLM calls and conversation history
- **Production Ready**: Comprehensive logging, error handling, and monitoring

## 📖 Documentation

For full documentation, see the [API reference](https://github.com/Azrienlabs/Arc).

## 🎯 Quick Start

```python
from azcore.agents import AgentFactory
from azcore.core import Orchestrator
from azcore.workflows import SequentialWorkflow

# Create agents
agent_factory = AgentFactory()
researcher = agent_factory.create_agent("react", name="Researcher")
analyst = agent_factory.create_agent("reasoning_duo", name="Analyst")

# Build workflow
workflow = SequentialWorkflow([researcher, analyst])

# Execute
orchestrator = Orchestrator(workflow)
result = orchestrator.execute("Analyze market trends for Q4 2025")
```

## 📦 Installation Options

### Basic Installation
```bash
pip install azcore
```

### With Development Tools
```bash
pip install azcore[dev]
```

### With MCP Support
```bash
pip install azcore[mcp]
```

## 🏗️ Architecture

Arc is built with a modular architecture:

- **Agents**: Core agent implementations (ReAct, Reflexion, etc.)
- **Core**: Orchestrator, executor, and state management
- **Workflows**: Pre-built workflow patterns for common use cases
- **Nodes**: Specialized nodes for planning, coordination, and generation
- **RL**: Reinforcement learning components for agent optimization
- **Utils**: Utilities for caching, logging, persistence, and more

## 📕 Releases & Versioning

See our [Releases](https://github.com/Azrienlabs/Arc/releases) and Versioning policies.

## 💁 Contributing

As an open-source project in a rapidly developing field, we are extremely open to contributions, whether it be in the form of a new feature, improved infrastructure, or better documentation.

For detailed information on how to contribute, see the [Contributing Guide](https://github.com/Azrienlabs/Arc/blob/main/CONTRIBUTING.md).

## 📄 License

Arc is released under the [MIT License](LICENSE).

## 🔗 Links

- **GitHub**: [https://github.com/Azrienlabs/Arc](https://github.com/Azrienlabs/Arc)
- **Issues**: [https://github.com/Azrienlabs/Arc/issues](https://github.com/Azrienlabs/Arc/issues)
- **PyPI**: [https://pypi.org/project/azcore/](https://pypi.org/project/azcore/)

## 🙏 Acknowledgments

Built with ❤️ by the Azrienlabs team.

---

**Ready to build the next generation of AI agents?** Start with Arc today!
