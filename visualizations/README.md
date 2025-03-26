# Secure AI Agent Visualizations

## Overview

This directory contains visualizations that demonstrate the capabilities of the secure AI agent. These visualizations help users understand how the agent processes queries, enforces security policies, and protects sensitive data.

## Visualization Types

### Data Flow Visualizations

- **Simple Query Flow** (`simple_query_flow.png`): Illustrates the basic flow of a simple document search query through the secure AI agent.
- **Secure Agent Data Flow** (`secure_agent_data_flow.png`): Shows a comprehensive view of the secure AI agent's data flow architecture.
- **Complex Data Flow** (`complex_data_flow.png`): Demonstrates a more complex data flow involving multiple security policies and tools.

### Policy Enforcement Visualizations

- **Malicious Query with Policy Enforcement** (`malicious_query_flow.png`): Shows how the secure AI agent handles potentially malicious queries.
- **Policy Enforcement Rates** (`policy_enforcement_heatmap.png`): A heatmap showing the enforcement rates of different security policies across various query types.

### Security Analysis Visualizations

- **Security Violation Types** (`security_violations_pie.png`): A pie chart showing the distribution of different types of security violations detected and prevented by the secure AI agent.

### Database Schema Visualization

- **Database Schema** (`database_schema.png`): Shows the database schema of the secure AI agent, illustrating the tables and their relationships.

## Viewing the Visualizations

You can view the visualizations in several ways:

1. **Individual Files**: Open the PNG files directly to view each visualization.

2. **HTML Summary Pages**:
   - `secure_agent_visualizations.html`: Contains all the sample visualizations with descriptions.
   - `secure_agent_data_flow.html`: Contains the data flow and database schema visualizations.

3. **Dashboard** (`dashboard.html`): A comprehensive dashboard that combines all visualizations with navigation and detailed descriptions.

## Generating New Visualizations

To generate new visualizations, you can use the following scripts:

- `sample_visualizations.py`: Generates sample visualizations to demonstrate the capabilities of the secure AI agent.
- `secure_agent_data_flow.py`: Generates visualizations based on the actual database structure of the secure AI agent.

Run these scripts from the root directory of the project:

```bash
python sample_visualizations.py
python secure_agent_data_flow.py
```

## Customizing Visualizations

You can customize the visualizations by modifying the scripts. Each visualization function can be adjusted to change colors, layouts, or data sources.

## Dependencies

The visualization scripts require the following Python packages:

- networkx
- matplotlib
- numpy

Install these dependencies using pip:

```bash
pip install networkx matplotlib numpy
```

## Integration with the Web Demo

These visualizations can be integrated into the web demo by adding them to the appropriate sections of the demo interface. This helps users understand how the secure AI agent works and builds trust in its security features.
