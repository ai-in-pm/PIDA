"""Visualization module for the secure AI agent."""

import os
import json
import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path
from typing import Dict, List, Any, Optional
import argparse
import logging
import sqlite3

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Try to import optional dependencies
try:
    import pygraphviz
    HAS_PYGRAPHVIZ = True
except ImportError:
    HAS_PYGRAPHVIZ = False

try:
    import pydot
    HAS_PYDOT = True
except ImportError:
    HAS_PYDOT = False

class DataFlowVisualizer:
    """Visualizer for data flow graphs."""
    
    def __init__(self, db_path: str, output_dir: Optional[str] = None):
        """Initialize the visualizer.
        
        Args:
            db_path: Path to the SQLite database file
            output_dir: Directory to save visualizations to
        """
        self.db_path = db_path
        self.output_dir = output_dir or str(Path(__file__).parent.parent / 'visualizations')
        os.makedirs(self.output_dir, exist_ok=True)
        self.conn = None
        self.cursor = None
        
        # Check if the database file exists
        if not os.path.exists(db_path):
            logger.error(f"Database file not found: {db_path}")
            raise FileNotFoundError(f"Database file not found: {db_path}")
        
        # Connect to the database
        self._connect()
    
    def _connect(self):
        """Connect to the SQLite database."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries
            self.cursor = self.conn.cursor()
            logger.debug(f"Connected to database: {self.db_path}")
        except sqlite3.Error as e:
            logger.error(f"Error connecting to database: {str(e)}")
            raise
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            logger.debug("Database connection closed")
    
    def load_data_flow_graph(self) -> Dict[str, Any]:
        """Load the data flow graph from the database.
        
        Returns:
            A dictionary representing the data flow graph
        """
        try:
            # Create a dictionary to store the data flow graph
            data_flow = {'data_nodes': [], 'data_edges': []}
            
            # Load nodes
            self.cursor.execute("SELECT id, data, source FROM data_nodes")
            nodes = self.cursor.fetchall()
            
            for node in nodes:
                node_id = node[0]
                data = node[1]
                source = node[2]
                
                # Load node capabilities
                self.cursor.execute(
                    "SELECT capability FROM data_node_capabilities WHERE node_id = ?",
                    (node_id,)
                )
                capabilities = [row[0] for row in self.cursor.fetchall()]
                
                # Add node to the data flow graph
                data_flow['data_nodes'].append({
                    'id': node_id,
                    'type': source,
                    'value': data,
                    'capabilities': capabilities
                })
            
            # Load edges
            self.cursor.execute(
                "SELECT source_id, target_id, relationship FROM data_node_edges"
            )
            edges = self.cursor.fetchall()
            
            for edge in edges:
                source_id = edge[0]
                target_id = edge[1]
                relationship = edge[2]
                
                # Add edge to the data flow graph
                data_flow['data_edges'].append({
                    'source': source_id,
                    'target': target_id,
                    'type': relationship
                })
            
            return data_flow
        except sqlite3.Error as e:
            logger.error(f"Error loading data flow graph: {str(e)}")
            raise
    
    def visualize_data_flow(self, output_file: str = 'data_flow.png'):
        """Visualize the data flow graph from the database.
        
        Args:
            output_file: File to save visualization to
        """
        try:
            # Load the graph
            data_flow = self.load_data_flow_graph()
            
            # Check if the graph is empty
            if len(data_flow['data_nodes']) == 0:
                print("No data flow nodes found in the database.")
                return
            
            # Visualize the graph
            self._visualize_data_flow(data_flow, output_file)
        except Exception as e:
            logger.error(f"Error visualizing data flow: {str(e)}")
            raise
    
    def _visualize_data_flow(self, data_flow: Dict[str, Any], output_file: str):
        """Visualize a data flow graph.
        
        Args:
            data_flow: Data flow graph to visualize
            output_file: File to save visualization to
        """
        # Create a directed graph
        G = nx.DiGraph()
        
        # Add nodes
        for node in data_flow.get('data_nodes', []):
            node_id = node.get('id')
            node_type = node.get('type')
            node_value = node.get('value')
            capabilities = node.get('capabilities', [])
            
            G.add_node(node_id, type=node_type, value=node_value, capabilities=capabilities)
        
        # Add edges
        for edge in data_flow.get('data_edges', []):
            source = edge.get('source')
            target = edge.get('target')
            edge_type = edge.get('type')
            
            G.add_edge(source, target, type=edge_type)
        
        # Save visualization
        output_path = os.path.join(self.output_dir, output_file)
        self._save_visualization(G, output_path)
        
        return output_path
    
    def _save_visualization(self, G: nx.DiGraph, output_path: str):
        """Save a visualization of a graph.
        
        Args:
            G: Graph to visualize
            output_path: Path to save visualization to
        """
        # Try different visualization methods based on available dependencies
        if HAS_PYGRAPHVIZ and output_path.endswith(('.png', '.pdf', '.svg')):
            self._save_with_pygraphviz(G, output_path)
        elif HAS_PYDOT and output_path.endswith(('.png', '.pdf', '.svg')):
            self._save_with_pydot(G, output_path)
        elif output_path.endswith('.json'):
            self._save_as_json(G, output_path)
        else:
            # Fall back to matplotlib
            self._save_with_matplotlib(G, output_path)
    
    def _save_with_pygraphviz(self, G: nx.DiGraph, output_path: str):
        """Save a visualization using pygraphviz.
        
        Args:
            G: Graph to visualize
            output_path: Path to save visualization to
        """
        A = nx.nx_agraph.to_agraph(G)
        
        # Set node attributes
        for node in A.nodes():
            node_data = G.nodes[node]
            node_type = node_data.get('type', 'unknown')
            
            # Set node color based on type
            if node_type == 'input':
                node.attr['fillcolor'] = '#AED6F1'  # Light blue
            elif node_type == 'process':
                node.attr['fillcolor'] = '#D5F5E3'  # Light green
            elif node_type == 'output':
                node.attr['fillcolor'] = '#FADBD8'  # Light red
            else:
                node.attr['fillcolor'] = '#F5EEF8'  # Light purple
            
            node.attr['style'] = 'filled'
            node.attr['shape'] = 'box'
            node.attr['label'] = f"{node}\n{node_data.get('value', '')}\n{node_data.get('capabilities', [])}"  # noqa
        
        # Set edge attributes
        for edge in A.edges():
            edge_data = G.get_edge_data(edge[0], edge[1])
            edge_type = edge_data.get('type', 'unknown')
            
            edge.attr['label'] = edge_type
        
        # Set graph attributes
        A.graph_attr['rankdir'] = 'LR'
        A.graph_attr['splines'] = 'ortho'
        
        # Draw and save
        A.draw(output_path, prog='dot')
    
    def _save_with_pydot(self, G: nx.DiGraph, output_path: str):
        """Save a visualization using pydot.
        
        Args:
            G: Graph to visualize
            output_path: Path to save visualization to
        """
        P = nx.nx_pydot.to_pydot(G)
        
        # Set graph attributes
        P.set('rankdir', 'LR')
        P.set('splines', 'ortho')
        
        # Save
        if output_path.endswith('.png'):
            P.write_png(output_path)
        elif output_path.endswith('.pdf'):
            P.write_pdf(output_path)
        elif output_path.endswith('.svg'):
            P.write_svg(output_path)
        else:
            P.write_png(output_path)
    
    def _save_with_matplotlib(self, G: nx.DiGraph, output_path: str):
        """Save a visualization using matplotlib.
        
        Args:
            G: Graph to visualize
            output_path: Path to save visualization to
        """
        plt.figure(figsize=(12, 8))
        
        # Create node colors based on type
        node_colors = []
        for node in G.nodes():
            node_type = G.nodes[node].get('type', 'unknown')
            
            if node_type == 'input':
                node_colors.append('#AED6F1')  # Light blue
            elif node_type == 'process':
                node_colors.append('#D5F5E3')  # Light green
            elif node_type == 'output':
                node_colors.append('#FADBD8')  # Light red
            else:
                node_colors.append('#F5EEF8')  # Light purple
        
        # Create node labels
        node_labels = {}
        for node in G.nodes():
            node_data = G.nodes[node]
            node_labels[node] = f"{node}\n{node_data.get('value', '')}"  # noqa
        
        # Create edge labels
        edge_labels = {}
        for u, v in G.edges():
            edge_data = G.get_edge_data(u, v)
            edge_labels[(u, v)] = edge_data.get('type', '')
        
        # Draw
        pos = nx.spring_layout(G)
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=500, alpha=0.8)
        nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5, edge_color='gray')
        nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=8)
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
        
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
    
    def _save_as_json(self, G: nx.DiGraph, output_path: str):
        """Save a graph as JSON.
        
        Args:
            G: Graph to save
            output_path: Path to save JSON to
        """
        data = nx.node_link_data(G)
        
        with open(output_path, 'w') as f:
            json.dump(data, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description='Secure Agent Data Flow Visualizer')
    parser.add_argument('--db-path', type=str, help='Path to the SQLite database file',
                        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'secure_agent.db'))
    parser.add_argument('--output', type=str, help='Path to the output image file (optional)')
    
    args = parser.parse_args()
    
    # Create database directory if it doesn't exist
    os.makedirs(os.path.dirname(args.db_path), exist_ok=True)
    
    # Check if the database file exists
    if not os.path.exists(args.db_path):
        print(f"Database file not found: {args.db_path}")
        return
    
    # Initialize the data flow visualizer
    visualizer = DataFlowVisualizer(args.db_path)
    
    try:
        # Visualize the data flow
        visualizer.visualize_data_flow(args.output)
    finally:
        # Close the database connection
        visualizer.close()

if __name__ == '__main__':
    main()
