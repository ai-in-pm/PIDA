import logging
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SecurityPolicyManager:
    """Manages security policies for the secure agent.
    
    This class provides a centralized way to define, register, and enforce
    security policies for the secure agent.
    """
    
    def __init__(self):
        self.policies = {}
        
    def register_policy(self, policy_name: str, policy_func: callable):
        """Register a security policy with the manager."""
        self.policies[policy_name] = policy_func
        logger.info(f"Registered policy: {policy_name}")
        
    def enforce_policy(self, policy_name: str, params: Dict[str, Any]) -> bool:
        """Enforce a specific security policy.
        
        Args:
            policy_name: The name of the policy to enforce
            params: The parameters to check against the policy
            
        Returns:
            True if the policy is satisfied, False otherwise
        """
        if policy_name in self.policies:
            try:
                result = self.policies[policy_name](params)
                logger.info(f"Policy {policy_name} enforcement result: {result}")
                return result
            except Exception as e:
                logger.error(f"Error enforcing policy {policy_name}: {str(e)}")
                return False
        else:
            logger.warning(f"Unknown policy: {policy_name}")
            return False
        
    def enforce_all_policies(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, bool]:
        """Enforce all policies that apply to a specific tool.
        
        Args:
            tool_name: The name of the tool being called
            params: The parameters being passed to the tool
            
        Returns:
            A dictionary mapping policy names to enforcement results
        """
        results = {}
        
        # Determine which policies apply to this tool
        applicable_policies = self._get_applicable_policies(tool_name)
        
        # Enforce each applicable policy
        for policy_name in applicable_policies:
            results[policy_name] = self.enforce_policy(policy_name, params)
            
        return results
    
    def _get_applicable_policies(self, tool_name: str) -> List[str]:
        """Get the list of policies that apply to a specific tool.
        
        Args:
            tool_name: The name of the tool
            
        Returns:
            A list of policy names that apply to the tool
        """
        # In a real implementation, this would be more sophisticated
        # For now, we'll use a simple mapping
        tool_policy_map = {
            'send_email': ['email_domain_policy', 'attachment_policy'],
            'search_document': ['query_sanitization_policy'],
            # Add more tools and their applicable policies here
        }
        
        return tool_policy_map.get(tool_name, [])

# Example policy functions
def email_domain_policy(params: Dict[str, Any]) -> bool:
    """Enforce that email recipients are from trusted domains.
    
    Args:
        params: The parameters for the email sending operation
        
    Returns:
        True if the recipient is from a trusted domain, False otherwise
    """
    recipient = params.get('recipient', '')
    
    # List of trusted domains
    trusted_domains = ['company.com', 'partner.org']
    
    # Check if the recipient's domain is in the trusted domains list
    if '@' in recipient:
        domain = recipient.split('@')[-1]
        return domain in trusted_domains
    
    return False

def attachment_policy(params: Dict[str, Any]) -> bool:
    """Enforce that email attachments are allowed.
    
    Args:
        params: The parameters for the email sending operation
        
    Returns:
        True if the attachment is allowed, False otherwise
    """
    document = params.get('document', '')
    
    # List of forbidden attachment types
    forbidden_extensions = ['.exe', '.bat', '.sh', '.js']
    
    # Check if the document has a forbidden extension
    for ext in forbidden_extensions:
        if document.lower().endswith(ext):
            return False
    
    return True

def query_sanitization_policy(params: Dict[str, Any]) -> bool:
    """Enforce that search queries are sanitized.
    
    Args:
        params: The parameters for the search operation
        
    Returns:
        True if the query is sanitized, False otherwise
    """
    query = params.get('query', '')
    
    # List of forbidden patterns in queries
    forbidden_patterns = ['DROP TABLE', 'DELETE FROM', 'TRUNCATE TABLE', ';']
    
    # Check if the query contains any forbidden patterns
    for pattern in forbidden_patterns:
        if pattern.lower() in query.lower():
            return False
    
    return True

# Create a global policy manager instance
policy_manager = SecurityPolicyManager()

# Register the example policies
policy_manager.register_policy('email_domain_policy', email_domain_policy)
policy_manager.register_policy('attachment_policy', attachment_policy)
policy_manager.register_policy('query_sanitization_policy', query_sanitization_policy)

# Convenience function for enforcing policies
def enforce_policy(tool_name: str, params: Dict[str, Any]) -> bool:
    """Enforce all policies that apply to a specific tool.
    
    Args:
        tool_name: The name of the tool being called
        params: The parameters being passed to the tool
        
    Returns:
        True if all policies are satisfied, False otherwise
    """
    results = policy_manager.enforce_all_policies(tool_name, params)
    
    # All policies must be satisfied
    return all(results.values())
