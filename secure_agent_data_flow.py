#!/usr/bin/env python
"""
Secure Agent Data Flow Visualization

This script generates a visualization of the data flow in the secure AI agent
based on the actual database structure.
"""

import os
import json
import sys
import sqlite3
from pathlib import Path

try:
    import networkx as nx
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
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

# Database path
DB_PATH = Path('data') / 'secure_agent.db'

class SecureAgentDataFlowVisualizer:
    """
    Visualizer for the secure agent data flow based on the database structure.
    """
    
    def __init__(self, db_path):
        """
        Initialize the visualizer.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        
        # Connect to the database if it exists
        if os.path.exists(db_path):
            self._connect()
        else:
            print(f"Database file not found: {db_path}")
            print("Will generate sample data flow instead")
    
    def _connect(self):
        """
        Connect to the SQLite database.
        """
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            print(f"Connected to database: {self.db_path}")
        except Exception as e:
            print(f"Error connecting to database: {e}")
            self.conn = None
            self.cursor = None
    
    def close(self):
        """
        Close the database connection.
        """
        if self.conn:
            self.conn.close()
            print("Database connection closed")
    
    def get_database_schema(self):
        """
        Get the database schema.
        
        Returns:
            A dictionary with table names as keys and column information as values
        """
        schema = {}
        
        if not self.conn:
            return schema
        
        try:
            # Get all tables
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = self.cursor.fetchall()
            
            for table in tables:
                table_name = table[0]
                
                # Get columns for each table
                self.cursor.execute(f"PRAGMA table_info({table_name})")
                columns = self.cursor.fetchall()
                
                schema[table_name] = [
                    {
                        'name': col[1],
                        'type': col[2],
                        'primary_key': bool(col[5])
                    }
                    for col in columns
                ]
            
            print(f"Retrieved schema for {len(schema)} tables")
            return schema
        except Exception as e:
            print(f"Error getting database schema: {e}")
            return {}
    
    def visualize_schema(self, output_file='database_schema.png'):
        """
        Visualize the database schema.
        
        Args:
            output_file: File to save visualization to
        """
        schema = self.get_database_schema()
        
        if not schema:
            print("No schema available. Generating sample schema.")
            schema = self._generate_sample_schema()
        
        try:
            G = nx.DiGraph()
            
            # Add nodes for tables
            for table_name, columns in schema.items():
                # Create label with table name and columns
                label = f"{table_name}\n" + "\n".join(
                    [f"- {col['name']} ({col['type']})" for col in columns[:5]]
                )
                if len(columns) > 5:
                    label += f"\n... ({len(columns) - 5} more)"
                
                G.add_node(table_name, label=label, type='table', color='lightblue')
            
            # Add edges based on foreign key relationships or naming conventions
            for table_name, columns in schema.items():
                for col in columns:
                    # Check if column name suggests a foreign key relationship
                    if col['name'].endswith('_id') and not col['primary_key']:
                        # Extract the referenced table name
                        ref_table = col['name'][:-3]  # Remove '_id'
                        
                        # Check if the referenced table exists
                        if ref_table in schema:
                            G.add_edge(table_name, ref_table, label=col['name'])
            
            # Visualize
            plt.figure(figsize=(14, 10))
            pos = nx.spring_layout(G, seed=42, k=0.3)  # k controls the spacing
            
            # Draw nodes with colors
            node_colors = [G.nodes[n]['color'] for n in G.nodes()]
            nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=3000, alpha=0.8)
            
            # Draw edges
            nx.draw_networkx_edges(G, pos, width=1.5, arrowsize=15, alpha=0.7)
            
            # Draw edge labels
            edge_labels = {(u, v): d.get('label', '') for u, v, d in G.edges(data=True) if 'label' in d}
            nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
            
            # Draw labels
            labels = {n: G.nodes[n]['label'] for n in G.nodes()}
            nx.draw_networkx_labels(G, pos, labels=labels, font_size=8, font_weight='bold', verticalalignment='top')
            
            plt.title('Secure Agent Database Schema', fontsize=16)
            plt.axis('off')
            plt.tight_layout()
            
            # Save the visualization
            output_path = VISUALIZATIONS_DIR / output_file
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"Created database schema visualization: {output_path}")
            return output_path
        except Exception as e:
            print(f"Error creating database schema visualization: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _generate_sample_schema(self):
        """
        Generate a sample schema for visualization when the database is not available.
        
        Returns:
            A dictionary with table names as keys and column information as values
        """
        schema = {
            'users': [
                {'name': 'id', 'type': 'INTEGER', 'primary_key': True},
                {'name': 'username', 'type': 'TEXT', 'primary_key': False},
                {'name': 'email', 'type': 'TEXT', 'primary_key': False},
                {'name': 'created_at', 'type': 'TIMESTAMP', 'primary_key': False},
            ],
            'queries': [
                {'name': 'id', 'type': 'INTEGER', 'primary_key': True},
                {'name': 'user_id', 'type': 'INTEGER', 'primary_key': False},
                {'name': 'query_text', 'type': 'TEXT', 'primary_key': False},
                {'name': 'created_at', 'type': 'TIMESTAMP', 'primary_key': False},
            ],
            'policy_checks': [
                {'name': 'id', 'type': 'INTEGER', 'primary_key': True},
                {'name': 'query_id', 'type': 'INTEGER', 'primary_key': False},
                {'name': 'policy_name', 'type': 'TEXT', 'primary_key': False},
                {'name': 'passed', 'type': 'BOOLEAN', 'primary_key': False},
                {'name': 'created_at', 'type': 'TIMESTAMP', 'primary_key': False},
            ],
            'documents': [
                {'name': 'id', 'type': 'INTEGER', 'primary_key': True},
                {'name': 'title', 'type': 'TEXT', 'primary_key': False},
                {'name': 'content', 'type': 'TEXT', 'primary_key': False},
                {'name': 'created_at', 'type': 'TIMESTAMP', 'primary_key': False},
            ],
            'search_results': [
                {'name': 'id', 'type': 'INTEGER', 'primary_key': True},
                {'name': 'query_id', 'type': 'INTEGER', 'primary_key': False},
                {'name': 'document_id', 'type': 'INTEGER', 'primary_key': False},
                {'name': 'relevance_score', 'type': 'REAL', 'primary_key': False},
                {'name': 'created_at', 'type': 'TIMESTAMP', 'primary_key': False},
            ],
            'policies': [
                {'name': 'id', 'type': 'INTEGER', 'primary_key': True},
                {'name': 'name', 'type': 'TEXT', 'primary_key': False},
                {'name': 'description', 'type': 'TEXT', 'primary_key': False},
                {'name': 'created_at', 'type': 'TIMESTAMP', 'primary_key': False},
            ],
        }
        
        return schema
    
    def visualize_data_flow(self, output_file='secure_agent_data_flow.png'):
        """
        Visualize the data flow in the secure agent.
        
        Args:
            output_file: File to save visualization to
        """
        try:
            G = nx.DiGraph()
            
            # Add nodes
            G.add_node('user', label='User', type='external', color='lightblue')
            G.add_node('query_parser', label='Query Parser', type='process', color='lightgreen')
            G.add_node('intent_analyzer', label='Intent Analyzer', type='process', color='lightgreen')
            G.add_node('policy_engine', label='Policy Engine', type='process', color='orange')
            G.add_node('document_search', label='Document Search', type='process', color='lightgreen')
            G.add_node('result_formatter', label='Result Formatter', type='process', color='lightgreen')
            G.add_node('database', label='Secure Database', type='storage', color='lightyellow')
            G.add_node('policy_store', label='Policy Store', type='storage', color='lightyellow')
            G.add_node('document_store', label='Document Store', type='storage', color='lightyellow')
            
            # Add edges
            G.add_edge('user', 'query_parser', label='Query')
            G.add_edge('query_parser', 'intent_analyzer', label='Parsed Query')
            G.add_edge('intent_analyzer', 'policy_engine', label='Query Intent')
            G.add_edge('policy_engine', 'policy_store', label='Fetch Policies')
            G.add_edge('policy_store', 'policy_engine', label='Policy Rules')
            G.add_edge('policy_engine', 'document_search', label='Approved Query')
            G.add_edge('document_search', 'document_store', label='Search Request')
            G.add_edge('document_store', 'document_search', label='Matching Documents')
            G.add_edge('document_search', 'result_formatter', label='Search Results')
            G.add_edge('result_formatter', 'user', label='Formatted Results')
            G.add_edge('query_parser', 'database', label='Log Query')
            G.add_edge('policy_engine', 'database', label='Log Policy Checks')
            G.add_edge('document_search', 'database', label='Log Search Results')
            
            # Add policy violation path
            G.add_edge('policy_engine', 'user', label='Policy Violation')
            
            # Visualize
            plt.figure(figsize=(14, 10))
            pos = nx.spring_layout(G, seed=42, k=0.3)  # k controls the spacing
            
            # Draw nodes with colors
            node_colors = [G.nodes[n]['color'] for n in G.nodes()]
            nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=2000, alpha=0.8)
            
            # Draw edges
            nx.draw_networkx_edges(G, pos, width=1.5, arrowsize=15, alpha=0.7)
            
            # Draw edge labels
            edge_labels = {(u, v): d.get('label', '') for u, v, d in G.edges(data=True) if 'label' in d}
            nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
            
            # Draw labels
            labels = {n: G.nodes[n]['label'] for n in G.nodes()}
            nx.draw_networkx_labels(G, pos, labels=labels, font_size=10, font_weight='bold')
            
            plt.title('Secure Agent Data Flow', fontsize=16)
            plt.axis('off')
            plt.tight_layout()
            
            # Save the visualization
            output_path = VISUALIZATIONS_DIR / output_file
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"Created data flow visualization: {output_path}")
            return output_path
        except Exception as e:
            print(f"Error creating data flow visualization: {e}")
            import traceback
            traceback.print_exc()
            return None

def main():
    """
    Main function to create visualizations.
    """
    try:
        print("Generating secure agent data flow visualizations...")
        
        # Initialize the visualizer
        visualizer = SecureAgentDataFlowVisualizer(DB_PATH)
        
        # Create visualizations
        schema_path = visualizer.visualize_schema()
        data_flow_path = visualizer.visualize_data_flow()
        
        # Close the database connection
        visualizer.close()
        
        # Create an HTML file to display the visualizations
        if schema_path and data_flow_path:
            html_content = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Secure Agent Data Flow Visualizations</title>
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
                    <h1>Secure Agent Data Flow Visualizations</h1>
                    <p>The following visualizations show the data flow and database schema of the secure AI agent.</p>
                    
                    <div class="visualization">
                        <h2>Secure Agent Data Flow</h2>
                        <img src="{data_flow_path.name}" alt="Data Flow Diagram">
                        <div class="description">
                            <p>This visualization shows the data flow in the secure AI agent. It illustrates how queries are processed, how policy checks are performed, and how search results are returned to the user.</p>
                        </div>
                    </div>
                    
                    <div class="visualization">
                        <h2>Database Schema</h2>
                        <img src="{schema_path.name}" alt="Database Schema">
                        <div class="description">
                            <p>This visualization shows the database schema of the secure AI agent. It illustrates the tables and their relationships in the database.</p>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Save the HTML file
            html_path = VISUALIZATIONS_DIR / 'secure_agent_data_flow.html'
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
