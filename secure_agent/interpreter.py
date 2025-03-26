import ast
import logging
from typing import Dict, Any, List, Optional, Tuple, Set
import networkx as nx

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SecureInterpreter:
    """A secure interpreter for executing pseudo-code with security policy enforcement.
    
    This interpreter constructs a data flow dependency graph from pseudo-code and
    checks each action against explicit security policies before execution.
    """
    
    def __init__(self, tool_registry: Dict[str, Dict[str, Any]], policy_manager):
        self.tool_registry = tool_registry
        self.policy_manager = policy_manager
        self.execution_log = []
        
    def parse_pseudo_code(self, code: str) -> List[Dict[str, Any]]:
        """Parse pseudo-code into a list of tool calls.
        
        Args:
            code: The pseudo-code to parse
            
        Returns:
            A list of dictionaries representing tool calls
        """
        logger.info("Parsing pseudo-code into tool calls")
        
        tool_calls = []
        
        # Simple parsing for our specific pseudo-code format
        # In a real implementation, this would use a proper parser
        for line in code.splitlines():
            if "tool_calls.append" in line:
                # Extract the tool call information
                try:
                    # Find the start and end of the tool call dictionary
                    dict_start = line.find("{") 
                    dict_end = line.rfind("})") 
                    
                    if dict_start != -1 and dict_end != -1:
                        # Extract the dictionary string
                        dict_str = line[dict_start:dict_end+1]
                        
                        # Parse the tool name
                        tool_start = dict_str.find("'tool':") 
                        tool_end = dict_str.find(",", tool_start)
                        tool_name = dict_str[tool_start:tool_end].split(":")[1].strip().strip("'")
                        
                        # Parse the parameters
                        params_start = dict_str.find("'params':") 
                        params_end = dict_str.find("}", params_start)
                        params_str = dict_str[params_start:params_end+1].split(":", 1)[1].strip()
                        
                        # Convert params string to dictionary
                        params = {}
                        for param_pair in params_str.strip("{").strip("}").split(","):
                            if ':' in param_pair:
                                key, value = param_pair.split(":", 1)
                                params[key.strip().strip("'")] = value.strip().strip("'")
                        
                        # Create the tool call dictionary
                        tool_call = {
                            'tool': tool_name,
                            'params': params
                        }
                        
                        tool_calls.append(tool_call)
                        logger.debug(f"Parsed tool call: {tool_call}")
                except Exception as e:
                    logger.error(f"Error parsing tool call: {str(e)}")
        
        return tool_calls
    
    def build_dependency_graph(self, tool_calls: List[Dict[str, Any]]) -> nx.DiGraph:
        """Build a data flow dependency graph from tool calls.
        
        Args:
            tool_calls: The list of tool calls
            
        Returns:
            A directed graph representing data dependencies
        """
        logger.info("Building dependency graph from tool calls")
        
        G = nx.DiGraph()
        
        # Add nodes for each tool call
        for i, tool_call in enumerate(tool_calls):
            node_id = f"tool_{i}"
            G.add_node(node_id, **tool_call)
            
            # In a real implementation, we would analyze data dependencies
            # between tool calls and add edges accordingly
            # For simplicity, we're just adding nodes without edges here
        
        logger.debug(f"Dependency graph created with {len(G.nodes)} nodes")
        return G
    
    def annotate_capabilities(self, graph: nx.DiGraph) -> nx.DiGraph:
        """Annotate the dependency graph with capability information.
        
        Args:
            graph: The dependency graph to annotate
            
        Returns:
            The annotated dependency graph
        """
        logger.info("Annotating dependency graph with capabilities")
        
        for node in graph.nodes:
            tool_name = graph.nodes[node].get('tool', '')
            params = graph.nodes[node].get('params', {})
            
            # Extract capability information from the parameters
            capability = params.get('capability', 'untrusted')
            
            # Annotate the node with the capability
            graph.nodes[node]['capability'] = capability
            logger.debug(f"Node {node} annotated with capability: {capability}")
                
        return graph
    
    def enforce_policies(self, graph: nx.DiGraph) -> Dict[str, bool]:
        """Enforce security policies on the annotated dependency graph.
        
        Args:
            graph: The annotated dependency graph
            
        Returns:
            A dictionary mapping node IDs to policy compliance results
        """
        logger.info("Enforcing security policies on dependency graph")
        
        policy_results = {}
        
        for node in graph.nodes:
            tool_name = graph.nodes[node].get('tool', '')
            params = graph.nodes[node].get('params', {})
            capability = graph.nodes[node].get('capability', 'untrusted')
            
            # Check if the tool exists in the registry
            if tool_name in self.tool_registry:
                # Check if the required capabilities are satisfied
                required_capabilities = self.tool_registry[tool_name].get('required_capabilities', [])
                
                # For simplicity, we're just checking if the capability is in the required list
                if capability in required_capabilities:
                    # Now check the security policies
                    if self.policy_manager.enforce_policy(tool_name, params):
                        policy_results[node] = True
                        logger.debug(f"Node {node} ({tool_name}) passed policy check")
                    else:
                        policy_results[node] = False
                        logger.warning(f"Node {node} ({tool_name}) failed policy check")
                else:
                    policy_results[node] = False
                    logger.warning(f"Node {node} ({tool_name}) failed capability check: {capability} not in {required_capabilities}")
            else:
                policy_results[node] = False
                logger.warning(f"Node {node} references unknown tool: {tool_name}")
                
        return policy_results
    
    def execute_plan(self, graph: nx.DiGraph, policy_results: Dict[str, bool]) -> List[str]:
        """Execute the validated plan by checking each tool call against security policies.
        
        Args:
            graph: The annotated dependency graph
            policy_results: The results of policy enforcement
            
        Returns:
            A list of execution results
        """
        logger.info("Executing validated plan")
        
        result_log = []
        
        for node in graph.nodes:
            tool_name = graph.nodes[node].get('tool', '')
            params = graph.nodes[node].get('params', {}).copy()  # Make a copy to avoid modifying the original
            
            # Check if the node passed policy enforcement
            if policy_results.get(node, False):
                # Remove capability from params before execution
                if 'capability' in params:
                    del params['capability']
                
                # Execute the tool
                if tool_name in self.tool_registry:
                    try:
                        tool_func = self.tool_registry[tool_name].get('function')
                        if tool_func:
                            result = tool_func(**params)
                            result_log.append(f"Successfully executed {tool_name}: {result}")
                            logger.info(f"Successfully executed {tool_name}")
                        else:
                            result_log.append(f"No function defined for tool: {tool_name}")
                            logger.warning(f"No function defined for tool: {tool_name}")
                    except Exception as e:
                        result_log.append(f"Error executing {tool_name}: {str(e)}")
                        logger.error(f"Error executing {tool_name}: {str(e)}")
                else:
                    result_log.append(f"Unknown tool: {tool_name}")
                    logger.warning(f"Unknown tool: {tool_name}")
            else:
                # Node failed policy enforcement
                result_log.append(f"Security policy violation: {tool_name} with params {params}")
                logger.warning(f"Security policy violation: {tool_name} with params {params}")
                
        return result_log
    
    def interpret(self, code: str) -> List[str]:
        """Interpret pseudo-code with security policy enforcement.
        
        Args:
            code: The pseudo-code to interpret
            
        Returns:
            A list of execution results
        """
        logger.info(f"Interpreting pseudo-code")
        
        # Step 1: Parse the pseudo-code into tool calls
        tool_calls = self.parse_pseudo_code(code)
        
        # Step 2: Build dependency graph from the tool calls
        dependency_graph = self.build_dependency_graph(tool_calls)
        
        # Step 3: Annotate the graph with capabilities
        annotated_graph = self.annotate_capabilities(dependency_graph)
        
        # Step 4: Enforce security policies on the annotated graph
        policy_results = self.enforce_policies(annotated_graph)
        
        # Step 5: Execute the validated plan
        execution_results = self.execute_plan(annotated_graph, policy_results)
        
        # Log the results
        self.execution_log.extend(execution_results)
        
        return execution_results
