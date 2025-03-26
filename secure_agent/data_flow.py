import logging
import uuid
from typing import Dict, Any, List, Set, Optional, Tuple
import networkx as nx

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataFlowTracker:
    """Tracks data flow through the system and enforces capability restrictions.
    
    This class is responsible for tracking how data flows through the system,
    annotating data with capabilities, and enforcing restrictions on data usage.
    """
    
    def __init__(self):
        self.data_graph = nx.DiGraph()
        self.data_nodes = {}
        
    def create_data_node(self, data: Any, source: str, capabilities: List[str]) -> str:
        """Create a new data node in the graph.
        
        Args:
            data: The data to store in the node
            source: The source of the data (e.g., 'user_input', 'system', 'tool_output')
            capabilities: The capabilities that apply to this data
            
        Returns:
            The ID of the created node
        """
        node_id = str(uuid.uuid4())
        
        self.data_graph.add_node(
            node_id,
            data=data,
            source=source,
            capabilities=set(capabilities)
        )
        
        self.data_nodes[node_id] = {
            'data': data,
            'source': source,
            'capabilities': set(capabilities)
        }
        
        logger.debug(f"Created data node {node_id} with source {source} and capabilities {capabilities}")
        return node_id
    
    def create_derived_data_node(self, data: Any, parent_ids: List[str], transformation: str) -> str:
        """Create a new data node derived from existing nodes.
        
        Args:
            data: The derived data
            parent_ids: The IDs of the parent nodes
            transformation: The transformation applied to derive the data
            
        Returns:
            The ID of the created node
        """
        node_id = str(uuid.uuid4())
        
        # Calculate the intersection of parent capabilities
        parent_capabilities = None
        for parent_id in parent_ids:
            if parent_id in self.data_nodes:
                parent_caps = self.data_nodes[parent_id]['capabilities']
                if parent_capabilities is None:
                    parent_capabilities = set(parent_caps)
                else:
                    parent_capabilities &= set(parent_caps)
        
        # If no parents or no common capabilities, use empty set
        if parent_capabilities is None:
            parent_capabilities = set()
        
        self.data_graph.add_node(
            node_id,
            data=data,
            source='derived',
            capabilities=parent_capabilities,
            transformation=transformation
        )
        
        self.data_nodes[node_id] = {
            'data': data,
            'source': 'derived',
            'capabilities': parent_capabilities,
            'transformation': transformation
        }
        
        # Add edges from parents to this node
        for parent_id in parent_ids:
            if parent_id in self.data_nodes:
                self.data_graph.add_edge(parent_id, node_id)
        
        logger.debug(f"Created derived data node {node_id} with capabilities {parent_capabilities}")
        return node_id
    
    def add_capability(self, node_id: str, capability: str) -> bool:
        """Add a capability to a data node.
        
        Args:
            node_id: The ID of the node
            capability: The capability to add
            
        Returns:
            True if the capability was added, False otherwise
        """
        if node_id in self.data_nodes:
            self.data_nodes[node_id]['capabilities'].add(capability)
            self.data_graph.nodes[node_id]['capabilities'].add(capability)
            logger.debug(f"Added capability {capability} to node {node_id}")
            return True
        else:
            logger.warning(f"Cannot add capability to unknown node: {node_id}")
            return False
    
    def remove_capability(self, node_id: str, capability: str) -> bool:
        """Remove a capability from a data node.
        
        Args:
            node_id: The ID of the node
            capability: The capability to remove
            
        Returns:
            True if the capability was removed, False otherwise
        """
        if node_id in self.data_nodes:
            if capability in self.data_nodes[node_id]['capabilities']:
                self.data_nodes[node_id]['capabilities'].remove(capability)
                self.data_graph.nodes[node_id]['capabilities'].remove(capability)
                logger.debug(f"Removed capability {capability} from node {node_id}")
                return True
            else:
                logger.debug(f"Capability {capability} not present in node {node_id}")
                return False
        else:
            logger.warning(f"Cannot remove capability from unknown node: {node_id}")
            return False
    
    def has_capability(self, node_id: str, capability: str) -> bool:
        """Check if a data node has a specific capability.
        
        Args:
            node_id: The ID of the node
            capability: The capability to check
            
        Returns:
            True if the node has the capability, False otherwise
        """
        if node_id in self.data_nodes:
            return capability in self.data_nodes[node_id]['capabilities']
        else:
            logger.warning(f"Cannot check capability of unknown node: {node_id}")
            return False
    
    def get_data(self, node_id: str) -> Optional[Any]:
        """Get the data stored in a node.
        
        Args:
            node_id: The ID of the node
            
        Returns:
            The data stored in the node, or None if the node doesn't exist
        """
        if node_id in self.data_nodes:
            return self.data_nodes[node_id]['data']
        else:
            logger.warning(f"Cannot get data from unknown node: {node_id}")
            return None
    
    def get_capabilities(self, node_id: str) -> Set[str]:
        """Get the capabilities of a node.
        
        Args:
            node_id: The ID of the node
            
        Returns:
            The set of capabilities for the node, or empty set if the node doesn't exist
        """
        if node_id in self.data_nodes:
            return self.data_nodes[node_id]['capabilities']
        else:
            logger.warning(f"Cannot get capabilities of unknown node: {node_id}")
            return set()
    
    def check_operation_allowed(self, node_id: str, operation: str, required_capabilities: List[str]) -> bool:
        """Check if an operation is allowed on a data node.
        
        Args:
            node_id: The ID of the node
            operation: The operation to perform
            required_capabilities: The capabilities required for the operation
            
        Returns:
            True if the operation is allowed, False otherwise
        """
        if node_id in self.data_nodes:
            node_capabilities = self.data_nodes[node_id]['capabilities']
            
            # Check if the node has all required capabilities
            for capability in required_capabilities:
                if capability not in node_capabilities:
                    logger.warning(f"Operation {operation} on node {node_id} denied: missing capability {capability}")
                    return False
            
            logger.debug(f"Operation {operation} on node {node_id} allowed")
            return True
        else:
            logger.warning(f"Cannot check operation on unknown node: {node_id}")
            return False
    
    def get_provenance(self, node_id: str) -> List[Dict[str, Any]]:
        """Get the provenance of a data node.
        
        This function traces the lineage of a data node back to its sources.
        
        Args:
            node_id: The ID of the node
            
        Returns:
            A list of dictionaries describing the provenance of the node
        """
        if node_id not in self.data_nodes:
            logger.warning(f"Cannot get provenance of unknown node: {node_id}")
            return []
        
        provenance = []
        visited = set()
        
        def dfs(current_id, path):
            if current_id in visited:
                return
            
            visited.add(current_id)
            
            if current_id in self.data_nodes:
                node_info = self.data_nodes[current_id].copy()
                node_info['id'] = current_id
                node_info['path'] = path
                
                # Convert set to list for serialization
                if 'capabilities' in node_info:
                    node_info['capabilities'] = list(node_info['capabilities'])
                
                provenance.append(node_info)
                
                # Recursively visit predecessors
                for pred in self.data_graph.predecessors(current_id):
                    dfs(pred, path + [current_id])
        
        dfs(node_id, [])
        return provenance
    
    def visualize_graph(self, output_file: str = 'data_flow_graph.png') -> None:
        """Visualize the data flow graph.
        
        Args:
            output_file: The file to save the visualization to
        """
        try:
            import matplotlib.pyplot as plt
            from networkx.drawing.nx_agraph import graphviz_layout
            
            plt.figure(figsize=(12, 8))
            
            # Create a copy of the graph with simplified labels
            G = self.data_graph.copy()
            
            # Add labels to nodes
            labels = {}
            for node in G.nodes:
                source = G.nodes[node].get('source', 'unknown')
                caps = G.nodes[node].get('capabilities', set())
                labels[node] = f"{source}\n{', '.join(caps)}"
            
            # Draw the graph
            pos = graphviz_layout(G, prog='dot')
            nx.draw(G, pos, with_labels=False, node_size=300, node_color='lightblue', 
                   font_size=10, font_weight='bold', arrows=True)
            nx.draw_networkx_labels(G, pos, labels=labels, font_size=8)
            
            plt.title('Data Flow Graph')
            plt.axis('off')
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            logger.info(f"Data flow graph visualization saved to {output_file}")
        except ImportError as e:
            logger.warning(f"Cannot visualize graph: {str(e)}")
            logger.warning("Install matplotlib and pygraphviz for visualization support")
