// API service for the web demo
// This file provides functions to interact with the secure AI agent backend

// In a real implementation, these functions would make API calls to a backend server
// For this demo, we'll simulate the responses using the predefined query definitions

class SecureAgentAPI {
    constructor() {
        this.apiKey = null;
        this.baseUrl = '/api'; // Would be a real endpoint in production
    }

    // Set the API key
    setApiKey(apiKey) {
        if (!apiKey || apiKey.trim() === '') {
            console.error('Invalid API key provided');
            return false;
        }

        // Basic validation for OpenAI API key format (starts with 'sk-')
        if (!apiKey.startsWith('sk-')) {
            console.warn('API key does not match expected OpenAI format (should start with sk-)');
            // We'll still set it but return false to indicate it might not be valid
            this.apiKey = apiKey.trim();
            return false;
        }

        this.apiKey = apiKey.trim();
        console.log('API key set successfully');
        return true;
    }

    // Check if API key is set
    hasApiKey() {
        return !!this.apiKey;
    }

    // Validate the API key format
    validateApiKeyFormat() {
        if (!this.apiKey) return false;
        return this.apiKey.startsWith('sk-') && this.apiKey.length > 20;
    }

    // Process a query (simulated for demo)
    async processQuery(query, queryType = null) {
        // Check if API key is set
        if (!this.hasApiKey()) {
            return {
                success: false,
                error: 'API key is not configured. Please set your API key first.'
            };
        }

        // In a real implementation, this would make an API call to the backend
        // For the demo, we'll use the predefined query definitions
        
        console.log(`Processing query: ${query}`);
        
        // Simulate API call delay
        await new Promise(resolve => setTimeout(resolve, 500));
        
        if (queryType && queryDefinitions[queryType]) {
            return {
                success: true,
                queryDef: queryDefinitions[queryType]
            };
        }
        
        // For custom queries, analyze and return appropriate response
        const customResponse = this.analyzeCustomQuery(query);
        return {
            success: true,
            queryDef: customResponse
        };
    }
    
    // Analyze a custom query (simulated for demo)
    analyzeCustomQuery(query) {
        // Create a custom query definition based on the query content
        const customDef = JSON.parse(JSON.stringify(queryDefinitions.custom)); // Deep clone
        customDef.query = query;
        
        // Generate pseudo-code
        customDef.pseudoCode = `# Processing custom query\nparse_query("${escapeHtml(query)}")\nanalyze_intent()\nexecute_tools()`;
        
        // Check for potential security issues
        const hasSqlInjection = /drop|delete|;|--/i.test(query);
        const hasEmailDomain = /@[\w.-]+\.(com|org|net)/i.test(query);
        const hasUntrustedEmail = /@(?!company\.com|trusted-partner\.com)[\w.-]+\.(com|org|net)/i.test(query);
        
        // Set policies based on analysis
        customDef.policies = {
            emailDomain: hasEmailDomain ? 
                (hasUntrustedEmail ? 
                    { result: 'fail', message: 'Untrusted email domain detected' } : 
                    { result: 'pass', message: 'Email domain is trusted' }) : 
                { result: 'na', message: 'No email domains in query' },
            
            sqlInjection: hasSqlInjection ? 
                { result: 'fail', message: 'Potential SQL injection detected' } : 
                { result: 'pass', message: 'No SQL injection detected' },
            
            dataFlow: { result: 'pass', message: 'Data flow is valid' },
            capability: hasUntrustedEmail ? 
                { result: 'fail', message: 'Data lacks required capability: trusted_email' } : 
                { result: 'pass', message: 'Required capabilities are satisfied' }
        };
        
        // Set results based on policies
        const policyFailed = Object.values(customDef.policies).some(p => p.result === 'fail');
        
        if (policyFailed) {
            const failedPolicies = Object.entries(customDef.policies)
                .filter(([_, p]) => p.result === 'fail')
                .map(([key, p]) => `${formatPolicyName(key)}: ${p.message}`);
            
            customDef.results = [
                { type: 'error', message: `Security policy violation: ${failedPolicies.join(', ')}` }
            ];
        } else {
            customDef.results = [
                { type: 'success', message: `Successfully processed query: ${query}` }
            ];
        }
        
        // Generate simple data flow
        customDef.dataFlow = [
            { id: 'input_1', label: 'User Query', data: query, capabilities: ['user_input'] },
            { id: 'process_1', label: 'Process Query', data: 'process_query', capabilities: ['execution'] },
            { id: 'result_1', label: 'Query Result', data: 'Results', capabilities: ['result'] },
            { source: 'input_1', target: 'process_1', label: 'input' },
            { source: 'process_1', target: 'result_1', label: 'output' }
        ];
        
        return customDef;
    }
}

// Create and export API instance
const secureAgentAPI = new SecureAgentAPI();

// Helper function to escape HTML
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// Helper function to format policy names
function formatPolicyName(policyKey) {
    const policyNames = {
        emailDomain: 'Email Domain Policy',
        sqlInjection: 'SQL Injection Protection',
        dataFlow: 'Data Flow Validation',
        capability: 'Capability Access Control'
    };
    return policyNames[policyKey] || policyKey;
}
