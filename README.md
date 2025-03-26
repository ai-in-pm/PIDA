# Secure AI Agent with Prompt Injection Defense

This project implements a secure AI agent with robust defenses against prompt injection attacks. The implementation follows a defense-by-design approach based on the algorithm described in the research literature.


## Core Defense Strategy

The algorithm embodies a robust defense strategy by following these steps:

1. **User Query Parsing and Control Flow Extraction**:
   - The agent uses a simulated privileged language model to convert natural language queries into pseudo-code.
   - This pseudo-code captures the intended sequence of tool calls (control flow) and isolates it from untrusted data sources that could be manipulated through prompt injections.

2. **Data Flow Tracking and Capability Annotation**:
   - Each argument or data element in the pseudo-code is annotated with capabilities that detail its provenance and permitted usage.
   - This tracking ensures that even if untrusted data is injected, it cannot alter critical parameters—preventing attacks analogous to SQL injections.

3. **Security Policy Enforcement with a Custom Interpreter**:
   - Before any tool call is executed, a custom interpreter constructs a data flow dependency graph and checks each action against explicit security policies.
   - For example, for email sending operations, the policy allows execution only if the recipient is within a trusted domain.
   - This mechanism stops adversaries from redirecting sensitive data to unintended recipients.

4. **Real-Time Execution and Feedback**:
   - Once the plan is verified, the agent executes the actions.
   - Should any security policy be violated, execution is halted or flagged for explicit user confirmation.
   - This feedback loop ensures that even subtle prompt injections—those attempting to transform data flow into control flow—are detected and blocked in real-time.

## Project Structure

```
secure_agent/
├── agent.py           # Main agent implementation
├── policies.py        # Security policy definitions and enforcement
├── data_flow.py       # Data flow tracking and capability annotation
├── interpreter.py     # Custom interpreter for secure execution
├── main.py            # Main application entry point
├── test_agent.py      # Unit tests for the agent
└── web_demo/          # Web-based demo for interactive testing
    ├── index.html      # Main interface for the web demo
    ├── styles.css      # Styling for the web interface
    └── demo.js         # JavaScript code powering the interactive demo
```

## Installation

1. Create and activate a virtual environment:

```bash
python -m venv venv
venv\Scripts\activate  # On Windows
source venv/bin/activate  # On Unix/Linux
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

To run the agent with a default query:

```bash
python secure_agent/main.py
```

To specify a custom query:

```bash
python secure_agent/main.py --query "Can you search for documents about project schedules?"
```

### Demo Mode

To run a demonstration with multiple queries, including some injection attempts:

```bash
python secure_agent/main.py --demo
```

### Verbose Mode

To enable verbose logging for debugging:

```bash
python secure_agent/main.py --verbose
```

### Running the Web Demo

To run the web demo, simply open the `web_demo/index.html` file in a web browser. The demo allows you to:

1. Select from predefined queries or create custom ones
2. Run the query through the secure agent pipeline
3. View the step-by-step processing:
   - Query parsing and pseudo-code generation
   - Data flow analysis
   - Security policy enforcement
   - Tool execution (or blocking if security violations are detected)
4. Track statistics on queries processed, security violations, tools executed, and data nodes

## Running Tests

To run the unit tests:

```bash
python -m unittest secure_agent/test_agent.py
```

Or using pytest:

```bash
pytest secure_agent/test_agent.py
```

## Key Components

### SecureAgent (agent.py)

The main agent class that orchestrates the entire secure processing pipeline:

- Extracts control flow from user queries
- Builds and annotates dependency graphs
- Enforces security policies
- Executes validated plans

### SecurityPolicyManager (policies.py)

Manages and enforces security policies:

- Email domain policy: Ensures email recipients are from trusted domains
- Attachment policy: Prevents sending dangerous file types
- Query sanitization policy: Blocks SQL injection attempts

### DataFlowTracker (data_flow.py)

Tracks data flow and enforces capability restrictions:

- Creates and manages data nodes with capability annotations
- Tracks data provenance and transformations
- Enforces capability-based access control

### SecureInterpreter (interpreter.py)

Securely interprets pseudo-code with policy enforcement:

- Parses pseudo-code into tool calls
- Builds dependency graphs
- Enforces security policies
- Executes validated plans

## Visualizations

The project includes a comprehensive set of visualizations to help understand the secure AI agent's architecture, data flow, and security mechanisms:

### Available Visualizations

1. **Data Flow Visualizations**:
   - Simple Query Flow: Illustrates the basic flow of a simple document search query.
   - Complex Data Flow: Shows a more complex data flow involving multiple security policies and tools.
   - Secure Agent Data Flow: Provides a comprehensive view of the secure AI agent's data flow architecture.

2. **Policy Enforcement Visualizations**:
   - Malicious Query with Policy Enforcement: Demonstrates how the secure AI agent handles potentially malicious queries.
   - Policy Enforcement Rates: A heatmap showing the enforcement rates of different security policies across various query types.

3. **Security Analysis Visualizations**:
   - Security Violation Types: A pie chart showing the distribution of different types of security violations detected and prevented.

4. **Database Schema Visualization**:
   - Database Schema: Shows the database schema of the secure AI agent, illustrating the tables and their relationships.

### Viewing Visualizations

To view the visualizations:

```bash
python open_dashboard.py
```

This will open the visualization dashboard in your default web browser.

Alternatively, you can:

1. Open `visualizations/dashboard.html` directly in your web browser.
2. View individual visualization files in the `visualizations/` directory.
3. Use the Visualizations tab in the web demo.

### Generating New Visualizations

To generate new visualizations:

```bash
python sample_visualizations.py  # Generate sample visualizations
python secure_agent_data_flow.py  # Generate data flow visualizations based on the database schema
```

## Extending the Agent

### Adding New Tools

To add a new tool to the agent, define a function and register it with the agent:

```python
def new_tool(param1, param2):
    """Tool documentation"""
    # Tool implementation
    return result

agent.register_tool('new_tool', new_tool, ['required_capability1', 'required_capability2'])
```

### Adding New Policies

To add a new security policy, define a policy function and register it with the policy manager:

```python
def new_policy(params):
    """Policy documentation"""
    # Policy implementation
    return is_allowed

policy_manager.register_policy('new_policy', new_policy)
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

This implementation is based on research in prompt injection defenses and secure AI agent design.
