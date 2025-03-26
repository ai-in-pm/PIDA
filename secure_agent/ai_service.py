"""AI service module for interacting with OpenAI API."""

import openai
from typing import Dict, List, Any, Optional
from . import config

# Configure OpenAI API
openai.api_key = config.OPENAI_API_KEY

class AIService:
    """Service for interacting with OpenAI API."""
    
    @staticmethod
    def parse_query(query: str) -> Dict[str, Any]:
        """Parse a natural language query into pseudo-code.
        
        Args:
            query: The natural language query from the user
            
        Returns:
            A dictionary containing the parsed query information
        """
        try:
            # In a real implementation, this would call the OpenAI API
            # For the demo, we'll simulate the response
            return {
                'pseudo_code': f"# Processing query: {query}\nresult = process_query('{query}')",
                'intent': 'information_retrieval',
                'tools': ['process_query']
            }
        except Exception as e:
            return {
                'error': str(e),
                'pseudo_code': '# Error processing query',
                'intent': 'unknown'
            }
    
    @staticmethod
    def analyze_data_flow(pseudo_code: str) -> Dict[str, Any]:
        """Analyze the data flow in the pseudo-code.
        
        Args:
            pseudo_code: The pseudo-code to analyze
            
        Returns:
            A dictionary containing the data flow analysis
        """
        try:
            # In a real implementation, this would use OpenAI to analyze the data flow
            # For the demo, we'll simulate the response
            return {
                'data_nodes': [
                    {'id': 'input_1', 'type': 'input', 'value': 'user_query', 'capabilities': ['user_input']},
                    {'id': 'process_1', 'type': 'process', 'value': 'process_query', 'capabilities': ['execution']},
                    {'id': 'output_1', 'type': 'output', 'value': 'result', 'capabilities': ['result']}
                ],
                'data_edges': [
                    {'source': 'input_1', 'target': 'process_1', 'type': 'data_flow'},
                    {'source': 'process_1', 'target': 'output_1', 'type': 'data_flow'}
                ]
            }
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def check_security_policies(data_flow: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Check security policies against the data flow.
        
        Args:
            data_flow: The data flow analysis
            query: The original query
            
        Returns:
            A dictionary containing the security policy check results
        """
        try:
            # In a real implementation, this would use OpenAI to check security policies
            # For the demo, we'll simulate the response
            policies = {
                'email_domain': {'result': 'pass', 'message': 'No email domains detected'},
                'sql_injection': {'result': 'pass', 'message': 'No SQL injection detected'},
                'capability_access': {'result': 'pass', 'message': 'All capability requirements satisfied'}
            }
            
            # Check for SQL injection patterns
            if any(pattern in query.lower() for pattern in ['drop table', 'delete from', ';', '--']):
                policies['sql_injection'] = {
                    'result': 'fail',
                    'message': 'Potential SQL injection detected'
                }
            
            # Check for email domains
            if '@' in query:
                email_parts = query.split('@')
                for i in range(1, len(email_parts)):
                    domain = email_parts[i].split()[0].strip('.,;:"\'')
                    if domain not in config.TRUSTED_EMAIL_DOMAINS and any(c in domain for c in ['.com', '.org', '.net']):
                        policies['email_domain'] = {
                            'result': 'fail',
                            'message': f'Untrusted email domain: {domain}'
                        }
                        break
            
            return {'policies': policies}
        except Exception as e:
            return {'error': str(e)}
