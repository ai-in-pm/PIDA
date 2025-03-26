import ast, networkx as nx
import uuid
import logging
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SecureAgent:
    """A secure AI agent that defends against prompt injection attacks.
    
    This agent implements a defense-by-design approach by:
    1. Separating control flow from untrusted data
    2. Tracking data flow with capability annotations
    3. Enforcing security policies before execution
    4. Providing real-time feedback during execution
    """
    
    def __init__(self):
        self.tool_registry = {}
        self.policies = {}
        self.execution_log = []
    
    def register_tool(self, tool_name: str, tool_func: callable, required_capabilities: List[str]):
        """Register a tool with the agent and its required capabilities."""
        self.tool_registry[tool_name] = {
            'function': tool_func,
            'required_capabilities': required_capabilities
        }
        logger.info(f"Registered tool: {tool_name} with capabilities: {required_capabilities}")
    
    def register_policy(self, policy_name: str, policy_func: callable):
        """Register a security policy with the agent."""
        self.policies[policy_name] = policy_func
        logger.info(f"Registered policy: {policy_name}")
    
    def extract_control_flow(self, query: str) -> str:
        """Simulate a privileged LLM converting natural language query into pseudo-Python code.
        
        This function represents the first layer of defense by isolating the intended
        control flow (sequence of tool calls) from untrusted data sources.
        
        Args:
            query: The natural language query from the user
            
        Returns:
            A string containing pseudo-Python code representing the intended tool calls
        """
        logger.info(f"Extracting control flow from query: {query}")
        
        # In a real implementation, this would call a privileged LLM
        # Here we simulate the behavior with simple pattern matching
        pseudo_code = f"# Generated pseudo-code from query: {query}\n"
        pseudo_code += "tool_calls = []\n"
        
        # Simple pattern matching to detect intents
        if "send" in query.lower() and ("bob" in query.lower() or "document" in query.lower()):
            pseudo_code += ("tool_calls.append({'tool': 'send_email', 'params': "
                          "{'recipient': 'bob@company.com', 'document': 'confidential.txt', "
                          "'capability': 'trusted_email'}}))\n")
        elif "search" in query.lower() or "find" in query.lower():
            pseudo_code += ("tool_calls.append({'tool': 'search_document', 'params': "
                          "{'query': query, 'capability': 'user_query'}}))\n")
        else:
            pseudo_code += "# No specific tool calls detected\n"
            
        logger.debug(f"Generated pseudo-code:\n{pseudo_code}")
        return pseudo_code
    
    def build_dependency_graph(self, code: str) -> nx.DiGraph:
        """Build a data flow dependency graph from the pseudo-code.
        
        This function creates a graph representation of data dependencies between
        tool calls, which is essential for tracking how data flows through the system
        and enforcing security policies.
        
        Args:
            code: The pseudo-code generated from the user query
            
        Returns:
            A directed graph representing data dependencies
        """
        logger.info("Building dependency graph from pseudo-code")
        G = nx.DiGraph()
        
        # Parse the pseudo-code to extract tool calls and their dependencies
        tool_calls = []
        for line in code.splitlines():
            if "tool_calls.append" in line:
                # Extract the tool call information
                node_id = str(uuid.uuid4())
                G.add_node(node_id, command=line.strip())
                
                # In a real implementation, we would parse the AST to extract
                # data dependencies between tool calls
                # For simplicity, we're just adding nodes without edges here
                
        logger.debug(f"Dependency graph created with {len(G.nodes)} nodes")
        return G
    
    def annotate_capabilities(self, graph: nx.DiGraph) -> nx.DiGraph:
        """Annotate the dependency graph with capability information.
        
        This function adds capability annotations to each node in the graph,
        indicating what operations are permitted on the data.
        
        Args:
            graph: The dependency graph to annotate
            
        Returns:
            The annotated dependency graph
        """
        logger.info("Annotating dependency graph with capabilities")
        
        for node in graph.nodes:
            command = graph.nodes[node].get('command', '')
            
            # Extract capability information from the command
            if "'capability':" in command:
                # Extract the capability string
                capability_start = command.find("'capability':")
                capability_end = command.find("}", capability_start)
                capability = command[capability_start:capability_end].split(":")[1].strip().strip("'")
                
                # Annotate the node with the capability
                graph.nodes[node]['capability'] = capability
                logger.debug(f"Node {node} annotated with capability: {capability}")
            else:
                # Default capability is 'untrusted'
                graph.nodes[node]['capability'] = 'untrusted'
                logger.debug(f"Node {node} annotated with default capability: untrusted")
                
        return graph
    
    def enforce_policies(self, graph: nx.DiGraph) -> Dict[str, bool]:
        """Enforce security policies on the annotated dependency graph.
        
        This function checks each node in the graph against the registered
        security policies to ensure that the intended operations comply with
        the security requirements.
        
        Args:
            graph: The annotated dependency graph
            
        Returns:
            A dictionary mapping node IDs to policy compliance results
        """
        logger.info("Enforcing security policies on dependency graph")
        
        policy_results = {}
        
        for node in graph.nodes:
            command = graph.nodes[node].get('command', '')
            capability = graph.nodes[node].get('capability', 'untrusted')
            
            # Extract tool name and parameters
            if "'tool':" in command:
                tool_start = command.find("'tool':")
                tool_end = command.find(",", tool_start)
                tool_name = command[tool_start:tool_end].split(":")[1].strip().strip("'")
                
                params_start = command.find("'params':")
                params_end = command.find("})", params_start)
                params_str = command[params_start:params_end].split(":", 1)[1].strip()
                
                # Convert params string to dictionary (simplified)
                params = {}
                for param_pair in params_str.strip("{").strip("}").split(","):
                    if ':' in param_pair:
                        key, value = param_pair.split(":", 1)
                        params[key.strip().strip("'")] = value.strip().strip("'")
                
                # Check if the tool exists in the registry
                if tool_name in self.tool_registry:
                    # Check if the required capabilities are satisfied
                    required_capabilities = self.tool_registry[tool_name]['required_capabilities']
                    
                    # For simplicity, we're just checking if the capability is in the required list
                    # In a real implementation, this would be more sophisticated
                    if capability in required_capabilities:
                        policy_results[node] = True
                        logger.debug(f"Node {node} ({tool_name}) passed capability check")
                    else:
                        policy_results[node] = False
                        logger.warning(f"Node {node} ({tool_name}) failed capability check: {capability} not in {required_capabilities}")
                else:
                    policy_results[node] = False
                    logger.warning(f"Node {node} references unknown tool: {tool_name}")
            else:
                policy_results[node] = True  # Non-tool nodes are allowed by default
                
        return policy_results
    
    def execute_plan(self, graph: nx.DiGraph, policy_results: Dict[str, bool]) -> List[str]:
        """Execute the validated plan by checking each tool call against security policies.
        
        This function executes the tool calls in the dependency graph, but only if
        they comply with the security policies.
        
        Args:
            graph: The annotated dependency graph
            policy_results: The results of policy enforcement
            
        Returns:
            A list of execution results
        """
        logger.info("Executing validated plan")
        
        result_log = []
        
        for node in graph.nodes:
            command = graph.nodes[node].get('command', '')
            
            # Check if the node passed policy enforcement
            if policy_results.get(node, False):
                # Extract tool name and parameters
                if "'tool':" in command:
                    tool_start = command.find("'tool':")
                    tool_end = command.find(",", tool_start)
                    tool_name = command[tool_start:tool_end].split(":")[1].strip().strip("'")
                    
                    params_start = command.find("'params':")
                    params_end = command.find("})", params_start)
                    params_str = command[params_start:params_end].split(":", 1)[1].strip()
                    
                    # Convert params string to dictionary (simplified)
                    params = {}
                    for param_pair in params_str.strip("{").strip("}").split(","):
                        if ':' in param_pair:
                            key, value = param_pair.split(":", 1)
                            params[key.strip().strip("'")] = value.strip().strip("'")
                    
                    # Remove capability from params before execution
                    if 'capability' in params:
                        del params['capability']
                    
                    # Execute the tool
                    if tool_name in self.tool_registry:
                        try:
                            tool_func = self.tool_registry[tool_name]['function']
                            result = tool_func(**params)
                            result_log.append(f"Successfully executed {tool_name}: {result}")
                            logger.info(f"Successfully executed {tool_name}")
                        except Exception as e:
                            result_log.append(f"Error executing {tool_name}: {str(e)}")
                            logger.error(f"Error executing {tool_name}: {str(e)}")
                    else:
                        result_log.append(f"Unknown tool: {tool_name}")
                        logger.warning(f"Unknown tool: {tool_name}")
            else:
                # Node failed policy enforcement
                result_log.append(f"Security policy violation: {command}")
                logger.warning(f"Security policy violation: {command}")
                
        return result_log
    
    def process_query(self, query: str) -> List[str]:
        """Process a user query through the secure agent pipeline.
        
        This function orchestrates the entire secure agent pipeline, from
        extracting control flow to executing the validated plan.
        
        Args:
            query: The natural language query from the user
            
        Returns:
            A list of execution results
        """
        logger.info(f"Processing query: {query}")
        
        # Step 1: Extract control flow from the query
        pseudo_code = self.extract_control_flow(query)
        
        # Step 2: Build dependency graph from the pseudo-code
        dependency_graph = self.build_dependency_graph(pseudo_code)
        
        # Step 3: Annotate the graph with capabilities
        annotated_graph = self.annotate_capabilities(dependency_graph)
        
        # Step 4: Enforce security policies on the annotated graph
        policy_results = self.enforce_policies(annotated_graph)
        
        # Step 5: Execute the validated plan
        execution_results = self.execute_plan(annotated_graph, policy_results)
        
        # Log the results
        self.execution_log.extend(execution_results)
        
        return execution_results

# Example tool functions
def send_email(recipient: str, document: str) -> str:
    """Send an email to the specified recipient with the specified document."""
    return f"Email sent to {recipient} with document: {document}"

def search_document(query: str) -> str:
    """Search for documents matching the specified query."""
    return f"Found 3 documents matching query: {query}"

# Main function for demonstration
def main():
    # Create a secure agent
    agent = SecureAgent()
    
    # Register tools with their required capabilities
    agent.register_tool('send_email', send_email, ['trusted_email'])
    agent.register_tool('search_document', search_document, ['user_query'])
    
    # Process a user query
    query = "Can you send Bob the document he requested in our last meeting?"
    results = agent.process_query(query)
    
    # Print the results
    print("Execution Results:")
    for result in results:
        print(f"- {result}")

if __name__ == "__main__":
    main()
