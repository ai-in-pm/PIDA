/**
 * Visualizations module for the Secure AI Agent web demo.
 * This module provides functions to display visualizations in the web demo.
 */

// Base path to visualizations
const VISUALIZATIONS_PATH = '../visualizations/';

// Visualization categories and their associated files
const visualizations = {
    dataFlow: [
        {
            id: 'simple-query-flow',
            title: 'Simple Query Flow',
            file: 'simple_query_flow.png',
            description: 'A basic flow showing how a simple document search query is processed through the secure AI agent.'
        },
        {
            id: 'secure-agent-data-flow',
            title: 'Secure Agent Data Flow',
            file: 'secure_agent_data_flow.png',
            description: 'A comprehensive view of the secure AI agent\'s data flow architecture.'
        },
        {
            id: 'complex-data-flow',
            title: 'Complex Data Flow',
            file: 'complex_data_flow.png',
            description: 'A more complex data flow involving multiple security policies and tools.'
        }
    ],
    policyEnforcement: [
        {
            id: 'malicious-query-flow',
            title: 'Malicious Query with Policy Enforcement',
            file: 'malicious_query_flow.png',
            description: 'How the secure AI agent handles potentially malicious queries.'
        },
        {
            id: 'policy-enforcement-heatmap',
            title: 'Policy Enforcement Rates',
            file: 'policy_enforcement_heatmap.png',
            description: 'Enforcement rates of different security policies across various query types.'
        }
    ],
    securityAnalysis: [
        {
            id: 'security-violations-pie',
            title: 'Security Violation Types',
            file: 'security_violations_pie.png',
            description: 'Distribution of different types of security violations detected and prevented.'
        }
    ],
    databaseSchema: [
        {
            id: 'database-schema',
            title: 'Database Schema',
            file: 'database_schema.png',
            description: 'The database schema of the secure AI agent, illustrating tables and their relationships.'
        }
    ]
};

/**
 * Initialize the visualizations tab in the web demo.
 * @param {string} containerId - The ID of the container element to populate with visualizations.
 */
function initVisualizations(containerId = 'visualizations-container') {
    const container = document.getElementById(containerId);
    if (!container) {
        console.error(`Container element with ID '${containerId}' not found.`);
        return;
    }

    // Create tabs for visualization categories
    const tabsContainer = document.createElement('div');
    tabsContainer.className = 'visualization-tabs';
    container.appendChild(tabsContainer);

    // Create content container
    const contentContainer = document.createElement('div');
    contentContainer.className = 'visualization-content';
    container.appendChild(contentContainer);

    // Add tabs and populate content
    const categories = {
        dataFlow: 'Data Flow',
        policyEnforcement: 'Policy Enforcement',
        securityAnalysis: 'Security Analysis',
        databaseSchema: 'Database Schema'
    };

    // Create tabs
    Object.entries(categories).forEach(([key, label], index) => {
        const tab = document.createElement('button');
        tab.className = 'visualization-tab' + (index === 0 ? ' active' : '');
        tab.textContent = label;
        tab.dataset.category = key;
        tab.onclick = () => switchVisualizationCategory(key);
        tabsContainer.appendChild(tab);
    });

    // Show the first category by default
    showVisualizationCategory('dataFlow');
}

/**
 * Switch to a different visualization category.
 * @param {string} category - The category to switch to.
 */
function switchVisualizationCategory(category) {
    // Update active tab
    const tabs = document.querySelectorAll('.visualization-tab');
    tabs.forEach(tab => {
        tab.classList.toggle('active', tab.dataset.category === category);
    });

    // Show the selected category
    showVisualizationCategory(category);
}

/**
 * Show visualizations for a specific category.
 * @param {string} category - The category to show.
 */
function showVisualizationCategory(category) {
    const contentContainer = document.querySelector('.visualization-content');
    if (!contentContainer) return;

    // Clear existing content
    contentContainer.innerHTML = '';

    // Get visualizations for the selected category
    const categoryVisualizations = visualizations[category] || [];

    // Create visualization cards
    categoryVisualizations.forEach(viz => {
        const card = document.createElement('div');
        card.className = 'visualization-card';
        card.innerHTML = `
            <h3>${viz.title}</h3>
            <div class="visualization-image">
                <img src="${VISUALIZATIONS_PATH}${viz.file}" alt="${viz.title}" />
            </div>
            <div class="visualization-description">
                <p>${viz.description}</p>
            </div>
        `;
        contentContainer.appendChild(card);
    });

    // If no visualizations in this category
    if (categoryVisualizations.length === 0) {
        contentContainer.innerHTML = '<p class="no-visualizations">No visualizations available for this category.</p>';
    }
}

/**
 * Show a specific visualization in a modal.
 * @param {string} vizId - The ID of the visualization to show.
 */
function showVisualizationModal(vizId) {
    // Find the visualization by ID
    let visualization = null;
    for (const category in visualizations) {
        const found = visualizations[category].find(viz => viz.id === vizId);
        if (found) {
            visualization = found;
            break;
        }
    }

    if (!visualization) {
        console.error(`Visualization with ID '${vizId}' not found.`);
        return;
    }

    // Create modal
    const modal = document.createElement('div');
    modal.className = 'visualization-modal';
    modal.innerHTML = `
        <div class="visualization-modal-content">
            <span class="close-modal">&times;</span>
            <h2>${visualization.title}</h2>
            <div class="modal-image">
                <img src="${VISUALIZATIONS_PATH}${visualization.file}" alt="${visualization.title}" />
            </div>
            <div class="modal-description">
                <p>${visualization.description}</p>
            </div>
        </div>
    `;

    // Add modal to the document
    document.body.appendChild(modal);

    // Close modal when clicking the close button or outside the modal
    const closeBtn = modal.querySelector('.close-modal');
    closeBtn.onclick = () => document.body.removeChild(modal);
    modal.onclick = (event) => {
        if (event.target === modal) {
            document.body.removeChild(modal);
        }
    };
}

// Export functions for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initVisualizations,
        switchVisualizationCategory,
        showVisualizationModal
    };
} else {
    // For browser use
    window.secureAgentVisualizations = {
        initVisualizations,
        switchVisualizationCategory,
        showVisualizationModal
    };
}
