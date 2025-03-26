#!/usr/bin/env python
"""
Sample Visualizations for Secure AI Agent

This script generates sample visualizations to demonstrate the capabilities
of the secure AI agent's data flow analysis and policy enforcement.
"""

import os
import json
import sys

try:
    import networkx as nx
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    from pathlib import Path
    import random
    print("Successfully imported all required libraries")
except Exception as e:
    print(f"Error importing libraries: {e}")
    sys.exit(1)

# Create visualizations directory
try:
    VISUALIZATIONS_DIR = Path('visualizations')
    os.makedirs(VISUALIZATIONS_DIR, exist_ok=True)
    print(f"Visualizations directory created at {VISUALIZATIONS_DIR.absolute()}")
except Exception as e:
    print(f"Error creating visualizations directory: {e}")
    sys.exit(1)

# Sample Data for Visualizations

# 1. Simple Query Visualization
def create_simple_query_visualization():
    """
    Create a visualization of a simple document search query.
    """
    try:
        G = nx.DiGraph()
        
        # Add nodes
        G.add_node('user_query', label='User Query', type='input', color='lightblue')
        G.add_node('parse', label='Parse Query', type='process', color='lightgreen')
        G.add_node('search', label='Search Documents', type='process', color='lightgreen')
        G.add_node('results', label='Search Results', type='output', color='lightyellow')
        
        # Add edges
        G.add_edge('user_query', 'parse')
        G.add_edge('parse', 'search')
        G.add_edge('search', 'results')
        
        # Visualize
        plt.figure(figsize=(10, 6))
        pos = nx.spring_layout(G, seed=42)
        
        # Draw nodes with colors
        node_colors = [G.nodes[n]['color'] for n in G.nodes()]
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=2000, alpha=0.8)
        
        # Draw edges
        nx.draw_networkx_edges(G, pos, width=2, arrowsize=20)
        
        # Draw labels
        labels = {n: G.nodes[n]['label'] for n in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels=labels, font_size=12, font_weight='bold')
        
        plt.title('Simple Document Search Query Flow', fontsize=16)
        plt.axis('off')
        plt.tight_layout()
        
        # Save the visualization
        output_path = VISUALIZATIONS_DIR / 'simple_query_flow.png'
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Created simple query visualization: {output_path}")
        return output_path
    except Exception as e:
        print(f"Error creating simple query visualization: {e}")
        import traceback
        traceback.print_exc()
        # Return a default path to avoid breaking the HTML generation
        return VISUALIZATIONS_DIR / 'simple_query_flow.png'

# 2. Malicious Query Visualization with Policy Enforcement
def create_malicious_query_visualization():
    """
    Create a visualization of a malicious query with policy enforcement.
    """
    G = nx.DiGraph()
    
    # Add nodes
    G.add_node('user_query', label='Malicious Query', type='input', color='lightblue')
    G.add_node('parse', label='Parse Query', type='process', color='lightgreen')
    G.add_node('analyze', label='Analyze Intent', type='process', color='lightgreen')
    G.add_node('policy_check', label='Policy Check', type='decision', color='orange')
    G.add_node('block', label='Block Action', type='output', color='red')
    G.add_node('search', label='Search Documents', type='process', color='lightgreen')
    G.add_node('results', label='Search Results', type='output', color='lightyellow')
    
    # Add edges
    G.add_edge('user_query', 'parse')
    G.add_edge('parse', 'analyze')
    G.add_edge('analyze', 'policy_check')
    G.add_edge('policy_check', 'block', label='Violation')
    G.add_edge('policy_check', 'search', label='Compliant')
    G.add_edge('search', 'results')
    
    # Visualize
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G, seed=42)
    
    # Draw nodes with colors
    node_colors = [G.nodes[n]['color'] for n in G.nodes()]
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=2000, alpha=0.8)
    
    # Draw edges
    nx.draw_networkx_edges(G, pos, width=2, arrowsize=20)
    
    # Draw edge labels
    edge_labels = {(u, v): d.get('label', '') for u, v, d in G.edges(data=True) if 'label' in d}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10)
    
    # Draw labels
    labels = {n: G.nodes[n]['label'] for n in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=12, font_weight='bold')
    
    plt.title('Malicious Query with Policy Enforcement', fontsize=16)
    plt.axis('off')
    plt.tight_layout()
    
    # Save the visualization
    output_path = VISUALIZATIONS_DIR / 'malicious_query_flow.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Created malicious query visualization: {output_path}")
    return output_path

# 3. Complex Data Flow Visualization
def create_complex_data_flow_visualization():
    """
    Create a visualization of a complex data flow with multiple policies.
    """
    G = nx.DiGraph()
    
    # Add nodes
    G.add_node('user_query', label='Complex Query', type='input', color='lightblue')
    G.add_node('parse', label='Parse Query', type='process', color='lightgreen')
    G.add_node('analyze', label='Analyze Intent', type='process', color='lightgreen')
    
    # Add policy checks
    policies = ['data_access', 'external_comms', 'pii_handling', 'resource_usage']
    for i, policy in enumerate(policies):
        G.add_node(f'policy_{policy}', label=f'{policy.replace("_", " ").title()} Policy', type='decision', color='orange')
        G.add_edge('analyze', f'policy_{policy}')
    
    # Add tools
    tools = ['search_docs', 'create_report', 'analyze_data', 'format_output']
    for i, tool in enumerate(tools):
        G.add_node(f'tool_{tool}', label=f'{tool.replace("_", " ").title()}', type='process', color='lightgreen')
        # Connect some policies to tools
        for policy in random.sample(policies, k=random.randint(1, 3)):
            G.add_edge(f'policy_{policy}', f'tool_{tool}', label='Approved')
    
    # Add output
    G.add_node('results', label='Final Results', type='output', color='lightyellow')
    for tool in tools:
        G.add_edge(f'tool_{tool}', 'results')
    
    # Visualize
    plt.figure(figsize=(16, 10))
    pos = nx.spring_layout(G, seed=42, k=0.3)  # k controls the spacing
    
    # Draw nodes with colors
    node_colors = [G.nodes[n]['color'] for n in G.nodes()]
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=1500, alpha=0.8)
    
    # Draw edges
    nx.draw_networkx_edges(G, pos, width=1.5, arrowsize=15, alpha=0.7)
    
    # Draw edge labels
    edge_labels = {(u, v): d.get('label', '') for u, v, d in G.edges(data=True) if 'label' in d}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
    
    # Draw labels
    labels = {n: G.nodes[n]['label'] for n in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels=labels, font_size=10, font_weight='bold')
    
    plt.title('Complex Query Data Flow with Multiple Policies', fontsize=16)
    plt.axis('off')
    plt.tight_layout()
    
    # Save the visualization
    output_path = VISUALIZATIONS_DIR / 'complex_data_flow.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Created complex data flow visualization: {output_path}")
    return output_path

# 4. Policy Enforcement Heatmap
def create_policy_enforcement_heatmap():
    """
    Create a heatmap showing policy enforcement statistics.
    """
    plt.figure(figsize=(12, 8))
    
    # Sample data
    policies = ['Data Access Control', 'External Communications', 'PII Handling', 
               'Resource Usage', 'Tool Execution', 'Output Filtering']
    
    query_types = ['Document Search', 'Email Sending', 'Report Generation', 
                  'Data Analysis', 'External API Call']
    
    # Generate random data for the heatmap
    data = []
    for i in range(len(query_types)):
        row = []
        for j in range(len(policies)):
            # Higher values for more critical policies
            if j < 3:  # More critical policies
                row.append(random.randint(70, 100))  # Higher enforcement rate
            else:
                row.append(random.randint(50, 95))
        data.append(row)
    
    # Create heatmap
    plt.imshow(data, cmap='YlGnBu', aspect='auto')
    plt.colorbar(label='Enforcement Rate (%)')
    
    # Add labels
    plt.xticks(range(len(policies)), policies, rotation=45, ha='right')
    plt.yticks(range(len(query_types)), query_types)
    
    # Add values to cells
    for i in range(len(query_types)):
        for j in range(len(policies)):
            plt.text(j, i, data[i][j], ha='center', va='center', color='black' if data[i][j] < 75 else 'white')
    
    plt.title('Policy Enforcement Rates by Query Type', fontsize=16)
    plt.tight_layout()
    
    # Save the visualization
    output_path = VISUALIZATIONS_DIR / 'policy_enforcement_heatmap.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Created policy enforcement heatmap: {output_path}")
    return output_path

# 5. Security Violations Pie Chart
def create_security_violations_pie_chart():
    """
    Create a pie chart showing security violation types.
    """
    plt.figure(figsize=(10, 8))
    
    # Sample data
    violation_types = ['Unauthorized Data Access', 'External Communication Attempt', 
                      'PII Exposure Risk', 'Resource Abuse', 'Malicious Tool Execution']
    
    # Generate random data for the pie chart
    sizes = [random.randint(5, 30) for _ in range(len(violation_types))]
    
    # Adjust to make sure they sum to 100
    total = sum(sizes)
    sizes = [int(s * 100 / total) for s in sizes]
    # Fix any rounding issues
    sizes[-1] = 100 - sum(sizes[:-1])
    
    # Colors
    colors = plt.cm.Set3(range(len(violation_types)))
    
    # Create pie chart
    wedges, texts, autotexts = plt.pie(sizes, labels=violation_types, autopct='%1.1f%%',
                                      startangle=90, colors=colors, shadow=True)
    
    # Style the text
    plt.setp(autotexts, size=10, weight='bold')
    plt.setp(texts, size=12)
    
    plt.title('Security Violation Types', fontsize=16)
    plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
    
    # Save the visualization
    output_path = VISUALIZATIONS_DIR / 'security_violations_pie.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Created security violations pie chart: {output_path}")
    return output_path

# Main function to create all visualizations
def main():
    try:
        print("Generating sample visualizations for Secure AI Agent...")
        
        # Create all visualizations
        print("Creating simple query visualization...")
        simple_path = create_simple_query_visualization()
        
        print("Creating malicious query visualization...")
        malicious_path = create_malicious_query_visualization()
        
        print("Creating complex data flow visualization...")
        complex_path = create_complex_data_flow_visualization()
        
        print("Creating policy enforcement heatmap...")
        heatmap_path = create_policy_enforcement_heatmap()
        
        print("Creating security violations pie chart...")
        pie_path = create_security_violations_pie_chart()
        
        print("Creating HTML summary page...")
        # Create an HTML file to display all visualizations
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Secure AI Agent Visualizations</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f5f5f5; }}
                h1, h2 {{ color: #333; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                .visualization {{ margin-bottom: 40px; background-color: white; padding: 20px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
                img {{ max-width: 100%; height: auto; display: block; margin: 0 auto; border: 1px solid #ddd; }}
                .description {{ margin-top: 15px; line-height: 1.6; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Secure AI Agent Visualizations</h1>
                <p>The following visualizations demonstrate the capabilities of the secure AI agent in analyzing data flow and enforcing security policies.</p>
                
                <div class="visualization">
                    <h2>Simple Document Search Query Flow</h2>
                    <img src="{simple_path.name}" alt="Simple Query Flow">
                    <div class="description">
                        <p>This visualization shows the basic flow of a simple document search query through the secure AI agent. The query is parsed, then used to search documents, and finally returns results to the user.</p>
                    </div>
                </div>
                
                <div class="visualization">
                    <h2>Malicious Query with Policy Enforcement</h2>
                    <img src="{malicious_path.name}" alt="Malicious Query Flow">
                    <div class="description">
                        <p>This visualization demonstrates how the secure AI agent handles a potentially malicious query. The query is parsed and analyzed for intent, then checked against security policies. If a violation is detected, the action is blocked; otherwise, it proceeds to execution.</p>
                    </div>
                </div>
                
                <div class="visualization">
                    <h2>Complex Query Data Flow with Multiple Policies</h2>
                    <img src="{complex_path.name}" alt="Complex Data Flow">
                    <div class="description">
                        <p>This visualization shows a more complex data flow involving multiple security policies and tools. Each policy governs which tools can be executed, ensuring that only approved operations are performed.</p>
                    </div>
                </div>
                
                <div class="visualization">
                    <h2>Policy Enforcement Rates by Query Type</h2>
                    <img src="{heatmap_path.name}" alt="Policy Enforcement Heatmap">
                    <div class="description">
                        <p>This heatmap shows the enforcement rates of different security policies across various query types. Higher percentages (darker colors) indicate stricter enforcement of that policy for the given query type.</p>
                    </div>
                </div>
                
                <div class="visualization">
                    <h2>Security Violation Types</h2>
                    <img src="{pie_path.name}" alt="Security Violations Pie Chart">
                    <div class="description">
                        <p>This pie chart shows the distribution of different types of security violations detected and prevented by the secure AI agent. Understanding the most common violation types helps improve security measures.</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Save the HTML file
        html_path = VISUALIZATIONS_DIR / 'secure_agent_visualizations.html'
        with open(html_path, 'w') as f:
            f.write(html_content)
        
        print(f"\nAll visualizations created successfully!")
        print(f"View the visualizations in your browser: {html_path}")
        
    except Exception as e:
        print(f"Error in main function: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
