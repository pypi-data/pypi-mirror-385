# Egregore v0.1.2a0

**AI Agent Framework Built on PACT Architecture**

Egregore is a powerful Python framework for building AI agents with **structured, manageable context**. Unlike traditional frameworks that treat context as simple chat logs, Egregore uses the **PACT (Positioned Adaptive Context Tree)** architecture to give you precise control over what the LLM sees and when.

Think of it as a **virtual DOM for AI context** - you can insert, update, delete, and manage individual components with temporal lifecycle control (TTL), precise positioning, and automatic cleanup.

## Why Egregore?

**Traditional Problem:** Context is an opaque black box. You dump messages in and hope the LLM does the right thing.

**Egregore's Solution:** Context is a queryable, manipulable tree structure where:
- Every component has a precise position and lifecycle
- You control what persists, expires, or moves through the context
- Components can be temporary, sticky, cyclic, or permanent
- Real-time debugging shows you exactly what the LLM sees at each turn

## 🚀 Quick Start

```python
from egregore.core.agent import Agent

# Create an agent with tools
def calculator(operation: str, a: float, b: float) -> float:
    """Perform basic math operations."""
    ops = {"add": a + b, "subtract": a - b, "multiply": a * b, "divide": a / b}
    return ops.get(operation, 0)

agent = Agent(
    provider="openai:gpt-4o",
    tools=[calculator],
    instructions="You are a helpful math assistant."
)

# Call the agent
response = agent("What's 25 * 4?")
print(response)  # Uses calculator tool and returns result
```

## 🏗️ Core Architecture

### PACT: Positioned Adaptive Context Tree

Egregore's context system uses **PACT coordinates** for universal addressability:

```python
from egregore.core.context_management import Context
from egregore.core.context_management.pact.components.core import TextContent

context = Context()

# Add messages with precise positioning
context.add_user("What is 2+2?")                    # d0,0,0 - active message
context.pact_insert("d0,0,1", note_component)       # d0,0,1 - annotation at offset 1
context.pact_insert("d0,0,-1", reminder_component)  # d0,0,-1 - pre-context at offset -1

# Components with lifecycle control
temporary = TextContent(content="Expires after 3 turns", ttl=3)
sticky = TextContent(content="Always at same relative position", ttl=1, cadence=1)
permanent = TextContent(content="Never expires", ttl=None)
```

### Component Lifecycle System

**4 Component Types:**
- **Permanent** (`ttl=None`): Never expire
- **Temporary** (`ttl=N`): Expire after N turns, gone forever
- **Sticky** (`ttl=1, cadence=1`): Expire and reappear each turn at same relative position
- **Cyclic** (`ttl=N, cadence=M`): Expire after N turns, reappear every M turns

**Render Lifecycle System:**
Components can move through multiple positions based on lifecycle stages:

```python
from egregore.core.context_management.pact.context.position import Pos

component = TextContent(content="Task alert")
component.render_lifecycle([
    Pos("d0, 0, 1", ttl=2),     # Stage 1: offset 1, for 2 turns
    Pos("d0, 0, -1", ttl=3),    # Stage 2: offset -1, for 3 turns
    Pos("d0, 0, -2")            # Stage 3: offset -2 (permanent)
])

context.pact_insert("d0,0,1", component)
# Component automatically transitions through stages as TTL expires
```

## ✨ Key Features

### 🎯 PACT Context Management
- **Universal Coordinates**: Address any component with `(depth, position, offset)` tuples
- **Temporal Management**: TTL+Cadence lifecycle with 4 component types
- **ODI System**: Overlap Demotion Invariant for automatic depth shifting
- **Render Lifecycle**: Components can move through positions based on TTL stages
- **PACT v0.1 Canonical Compliance**: Full specification compliance with automatic serialization

### 🛠️ Advanced Tool System
- **@tool Decorator**: Automatic parameter extraction and validation
- **@operation Decorator**: Scaffold methods become tools automatically
- **Concurrent Execution**: Parallel tool calls with result aggregation
- **Tool Pair Tracking**: Registry maintains call→result relationships

### 🧠 Context Scaffolds
- **Persistent Memory**: Agent state that survives across sessions
- **IPC System**: Inter-scaffold communication with source tracking
- **Reactive Rendering**: Automatic re-rendering on context changes
- **@operation Methods**: Scaffold methods exposed as tools

### 🔧 Agent Hook System
Decorator-based lifecycle hooks for observing and modifying behavior:

```python
@agent.hooks.tool.pre_call
def before_tool(ctx: ToolExecContext):
    print(f"Calling tool: {ctx.tool_name}")

@agent.hooks.context.before_change
def validate_change(ctx: ContextExecContext):
    # Cancel operation by raising exception
    if ctx.operation_type == "delete" and ctx.component.critical:
        raise ValueError("Cannot delete critical component")

@agent.hooks.streaming.on_chunk
def process_chunk(ctx: StreamExecContext):
    print(f"Chunk: {ctx.chunk_data}")
```

### 🌊 Unified Streaming
- Consistent streaming interface across all providers
- Real-time token processing and tool call accumulation
- Streaming hooks for chunk-level control

### 📊 Analytics & Debugging
- **ContextExplorer**: Interactive REPL-like debugger for step-by-step execution
- **ContextViewer**: Static snapshots with tree, text, XML, and provider-specific views
- **Episode Management**: Proper TTL testing with `explorer.step("render")`

### 🔗 Workflow System
- **Node-based Execution**: Declarative workflow composition
- **Native Agent Discovery**: Automatic agent detection in workflows
- **Parallel Processing**: Dictionary-based result aggregation from terminal nodes
- **Parameter Mapping**: Intelligent parameter flow between nodes

### 🔌 Universal Provider Interface
- **30+ Providers**: OpenAI, Anthropic, Google, and more
- **Standardized API**: Consistent interface across all providers
- **Universal Token Counting**: Multi-tokenizer support
- **OAuth Interceptors**: Premium model access

## 📦 Installation

```bash
# Clone repository
git clone https://github.com/yourusername/egregore-v2.git
cd egregore-v2

# Install with Poetry
poetry install

# Or with pip
pip install -e .
```

## 🎯 Real-World Examples

### Example 1: Context Debugging with ContextExplorer

```python
from egregore.analytics.context_explorer import ContextExplorer
from egregore.core.agent import Agent

def my_tool(text: str) -> str:
    return f"Processed: {text}"

agent = Agent(provider="openai", tools=[my_tool])
explorer = ContextExplorer(agent)

# Step through conversation
explorer.step("user_message", "Test message")
explorer.print("tree")  # See context structure

# Simulate LLM tool call
from egregore.core.messaging import ProviderResponse, ProviderToolCall
explorer.step("seal", ProviderResponse(content=[
    ProviderToolCall(
        tool_name="my_tool",
        tool_call_id="call_123",
        parameters={"text": "test"}
    )
]))

# Execute tools
explorer.step("execute_tools")

# Verify execution
tool_results = explorer.context.select(".tool_result")
print(f"Results: {tool_results[0].content}")
```

### Example 2: TTL Component Lifecycle

```python
from egregore.analytics.context_explorer import ContextExplorer
from egregore.core.context_management.pact.components.core import TextContent

explorer = ContextExplorer()
explorer.step("user_message", "Test")

# Component that expires after 2 turns
component = TextContent(content="Important note", ttl=2)
explorer.context.pact_insert("d0,0,1", component)

# Advance episodes
explorer.step("render")  # TTL=2, age=1
explorer.step("render")  # TTL=2, age=2, component expires

# Verify removal
assert explorer.context[0, 0, 1] is None
```

### Example 3: Agent with Context Hooks

```python
from egregore.core.agent import Agent

agent = Agent(provider="openai")

@agent.hooks.context.before_change
def log_changes(ctx):
    print(f"About to {ctx.operation_type} at {ctx.selector}")

@agent.hooks.context.after_change
def track_changes(ctx):
    print(f"Modified: {ctx.component}")

response = agent("Analyze this data")
# Hooks fire on every context operation
```

### Example 4: Scaffold with Operations

```python
from egregore.core.context_scaffolds import BaseContextScaffold
from egregore.core.context_scaffolds.decorators import operation

class TaskManager(BaseContextScaffold):
    def __init__(self):
        super().__init__()
        self.tasks = []

    @operation
    def add_task(self, description: str, priority: str = "medium") -> str:
        """Add a new task to the task list."""
        self.tasks.append({"description": description, "priority": priority})
        return f"Added task: {description}"

    @operation
    def list_tasks(self) -> list:
        """List all current tasks."""
        return self.tasks

# Operations automatically become tools the agent can use
agent = Agent(provider="openai", scaffolds=[TaskManager()])
agent("Add a high priority task to implement authentication")
```

## 📚 Documentation

Comprehensive documentation in the [`docs/`](docs/) directory:

### Architecture
- [**PACT Overview**](docs/PACT/README.md) - Core PACT architecture and concepts
- [**Context Management**](docs/architecture/context/overview.md) - PACT context tree system
- [**Context Lifecycle**](docs/architecture/context-lifecycle.md) - TTL, cadence, and ODI
- [**Scaffolds**](docs/architecture/scaffolds/index.md) - Persistent agent capabilities

### Guides
- [**Analytics Module**](docs/analytics-module.md) - ContextExplorer and ContextViewer
- [**Agent Hooks System**](docs/agent-hooks-system.md) - Lifecycle hooks
- [**Workflow System**](docs/workflow-system.md) - Node-based orchestration
- [**Modifying Tool Outputs**](docs/guides/modifying-tool-outputs.md) - Tool result transformation
- [**Component Triggers**](docs/guides/component-triggers.md) - Reactive context management

### Testing & Contributing
- [**Testing Guide**](docs/contributing/testing.md) - Universal testing strategy
- [**Provider Development**](docs/contributing/providers.md) - Adding new providers

### Internal (Development)
- [**Plans**](internal/plans/index.md) - Feature roadmap and implementation plans
- [**Reports**](internal/reports/index.md) - Analysis and audit reports

## 🧪 Testing

```bash
# Run all tests
poetry run pytest

# Run specific test categories
poetry run pytest tests/core/context_management/
poetry run pytest tests/analytics/

# With coverage
poetry run pytest --cov=egregore --cov-report=html
```

## 🔑 Key Concepts

### PACT Coordinates
- **Depth** (`d`): Message turn position (0=active, 1+=history)
- **Position** (`p`): Container within depth (0=message, 1+=components)
- **Offset** (`o`): Relative positioning within container
- **Examples**: `d0,0,0` (active message), `d0,0,1` (component at offset 1), `d1,0,0` (previous turn)

### PACT Selectors
CSS-like syntax for querying context:

```python
context.select("+tool_call")           # All tool calls (by tag)
context.select(".tool_result")         # All tool results (by type)
context.select("scaffold[memory]")     # Memory scaffolds
context.select("*[ttl<5]")            # Components expiring soon
```

### MessageContainer Pattern
Clean separation of message content from context components. Messages live at `dN,0`, components attach at `dN,1+`.

### ODI (Overlap Demotion Invariant)
Automatic depth shifting when message count changes:
- Message count increases → increment depths by difference
- Message count decreases → decrement depths by difference
- Maintains relative positions of permanent/sticky components

## 🛣️ Roadmap

Current focus areas:

- ✅ **PACT v0.1 Canonical Compliance** - Full specification compliance
- ✅ **Render Lifecycle System** - Dynamic component positioning
- ✅ **Agent Hook System** - Comprehensive lifecycle hooks
- ✅ **Context Explorer** - Interactive debugging tool
- 🔄 **Observability CLI** - Production debugging and monitoring (planned)
- 🔄 **Context History Snapshots** - Session persistence and replay (planned)

See [internal/plans/index.md](internal/plans/index.md) for detailed roadmap.

## 🤝 Contributing

We welcome contributions! Key areas:

1. **Testing**: Expand test coverage for edge cases
2. **Providers**: Add new LLM provider integrations
3. **Documentation**: Improve examples and guides
4. **Features**: Implement planned features from roadmap

See [docs/contributing/index.md](docs/contributing/index.md) for details.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built on the PACT specification for structured AI context
- Inspired by the need for predictable, debuggable AI agents
- Thanks to all contributors making this framework possible

---

**Current Version**: v0.1.2a0
**Last Updated**: October 2025
**Status**: Alpha - Active Development
