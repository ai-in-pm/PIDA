import sqlite3
import os
import logging
from typing import Dict, Any, List, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SecureDatabase:
    """A secure database for storing agent data with capability-based access control.
    
    This class provides a secure interface to an SQLite database, enforcing
    capability-based access control for all database operations.
    """
    
    def __init__(self, db_path: str = 'secure_agent.db'):
        """Initialize the secure database.
        
        Args:
            db_path: The path to the SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        
        # Create the database directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        
        # Connect to the database
        self._connect()
        
        # Initialize the database schema
        self._init_schema()
    
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
    
    def _init_schema(self):
        """Initialize the database schema."""
        try:
            # Create the tools table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tools (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Create the tool_capabilities table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tool_capabilities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tool_id INTEGER NOT NULL,
                capability TEXT NOT NULL,
                FOREIGN KEY (tool_id) REFERENCES tools (id) ON DELETE CASCADE,
                UNIQUE (tool_id, capability)
            )
            """)
            
            # Create the execution_log table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS execution_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tool_name TEXT NOT NULL,
                params TEXT,
                result TEXT,
                success BOOLEAN NOT NULL,
                error_message TEXT,
                execution_time REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Create the security_violations table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS security_violations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tool_name TEXT NOT NULL,
                params TEXT,
                policy_name TEXT,
                violation_details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Create the data_nodes table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS data_nodes (
                id TEXT PRIMARY KEY,
                data TEXT,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            # Create the data_node_capabilities table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS data_node_capabilities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                node_id TEXT NOT NULL,
                capability TEXT NOT NULL,
                FOREIGN KEY (node_id) REFERENCES data_nodes (id) ON DELETE CASCADE,
                UNIQUE (node_id, capability)
            )
            """)
            
            # Create the data_node_edges table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS data_node_edges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id TEXT NOT NULL,
                target_id TEXT NOT NULL,
                relationship TEXT,
                FOREIGN KEY (source_id) REFERENCES data_nodes (id) ON DELETE CASCADE,
                FOREIGN KEY (target_id) REFERENCES data_nodes (id) ON DELETE CASCADE,
                UNIQUE (source_id, target_id)
            )
            """)
            
            # Create the queries table
            self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS queries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                pseudo_code TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """)
            
            self.conn.commit()
            logger.info("Database schema initialized")
        except sqlite3.Error as e:
            logger.error(f"Error initializing database schema: {str(e)}")
            raise
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            logger.debug("Database connection closed")
    
    def register_tool(self, name: str, description: str, capabilities: List[str]):
        """Register a tool in the database.
        
        Args:
            name: The name of the tool
            description: A description of the tool
            capabilities: The capabilities required by the tool
        """
        try:
            # Insert the tool
            self.cursor.execute(
                "INSERT OR REPLACE INTO tools (name, description) VALUES (?, ?)",
                (name, description)
            )
            
            # Get the tool ID
            self.cursor.execute("SELECT id FROM tools WHERE name = ?", (name,))
            tool_id = self.cursor.fetchone()[0]
            
            # Delete existing capabilities
            self.cursor.execute("DELETE FROM tool_capabilities WHERE tool_id = ?", (tool_id,))
            
            # Insert new capabilities
            for capability in capabilities:
                self.cursor.execute(
                    "INSERT INTO tool_capabilities (tool_id, capability) VALUES (?, ?)",
                    (tool_id, capability)
                )
            
            self.conn.commit()
            logger.info(f"Tool '{name}' registered with capabilities: {capabilities}")
        except sqlite3.Error as e:
            self.conn.rollback()
            logger.error(f"Error registering tool: {str(e)}")
            raise
    
    def log_execution(self, tool_name: str, params: Dict[str, Any], result: Any, 
                     success: bool, error_message: str = None, execution_time: float = None):
        """Log a tool execution in the database.
        
        Args:
            tool_name: The name of the tool
            params: The parameters passed to the tool
            result: The result of the tool execution
            success: Whether the execution was successful
            error_message: The error message if the execution failed
            execution_time: The time taken to execute the tool
        """
        try:
            # Convert params and result to strings
            params_str = str(params)
            result_str = str(result)
            
            self.cursor.execute(
                """INSERT INTO execution_log 
                (tool_name, params, result, success, error_message, execution_time) 
                VALUES (?, ?, ?, ?, ?, ?)""",
                (tool_name, params_str, result_str, success, error_message, execution_time)
            )
            
            self.conn.commit()
            logger.debug(f"Execution of tool '{tool_name}' logged")
        except sqlite3.Error as e:
            self.conn.rollback()
            logger.error(f"Error logging execution: {str(e)}")
            raise
    
    def log_security_violation(self, tool_name: str, params: Dict[str, Any], 
                              policy_name: str, violation_details: str):
        """Log a security policy violation in the database.
        
        Args:
            tool_name: The name of the tool
            params: The parameters passed to the tool
            policy_name: The name of the violated policy
            violation_details: Details about the violation
        """
        try:
            # Convert params to string
            params_str = str(params)
            
            self.cursor.execute(
                """INSERT INTO security_violations 
                (tool_name, params, policy_name, violation_details) 
                VALUES (?, ?, ?, ?)""",
                (tool_name, params_str, policy_name, violation_details)
            )
            
            self.conn.commit()
            logger.info(f"Security violation of policy '{policy_name}' logged for tool '{tool_name}'")
        except sqlite3.Error as e:
            self.conn.rollback()
            logger.error(f"Error logging security violation: {str(e)}")
            raise
    
    def store_data_node(self, node_id: str, data: Any, source: str, capabilities: List[str]):
        """Store a data node in the database.
        
        Args:
            node_id: The ID of the node
            data: The data to store
            source: The source of the data
            capabilities: The capabilities of the data
        """
        try:
            # Convert data to string
            data_str = str(data)
            
            # Insert the data node
            self.cursor.execute(
                "INSERT OR REPLACE INTO data_nodes (id, data, source) VALUES (?, ?, ?)",
                (node_id, data_str, source)
            )
            
            # Delete existing capabilities
            self.cursor.execute("DELETE FROM data_node_capabilities WHERE node_id = ?", (node_id,))
            
            # Insert new capabilities
            for capability in capabilities:
                self.cursor.execute(
                    "INSERT INTO data_node_capabilities (node_id, capability) VALUES (?, ?)",
                    (node_id, capability)
                )
            
            self.conn.commit()
            logger.debug(f"Data node '{node_id}' stored with capabilities: {capabilities}")
        except sqlite3.Error as e:
            self.conn.rollback()
            logger.error(f"Error storing data node: {str(e)}")
            raise
    
    def store_data_edge(self, source_id: str, target_id: str, relationship: str = None):
        """Store a data edge in the database.
        
        Args:
            source_id: The ID of the source node
            target_id: The ID of the target node
            relationship: The relationship between the nodes
        """
        try:
            self.cursor.execute(
                """INSERT OR REPLACE INTO data_node_edges 
                (source_id, target_id, relationship) 
                VALUES (?, ?, ?)""",
                (source_id, target_id, relationship)
            )
            
            self.conn.commit()
            logger.debug(f"Data edge from '{source_id}' to '{target_id}' stored")
        except sqlite3.Error as e:
            self.conn.rollback()
            logger.error(f"Error storing data edge: {str(e)}")
            raise
    
    def store_query(self, query: str, pseudo_code: str):
        """Store a user query and its pseudo-code in the database.
        
        Args:
            query: The user query
            pseudo_code: The generated pseudo-code
        """
        try:
            self.cursor.execute(
                "INSERT INTO queries (query, pseudo_code) VALUES (?, ?)",
                (query, pseudo_code)
            )
            
            self.conn.commit()
            logger.debug(f"Query stored: {query}")
        except sqlite3.Error as e:
            self.conn.rollback()
            logger.error(f"Error storing query: {str(e)}")
            raise
    
    def get_tool_capabilities(self, tool_name: str) -> List[str]:
        """Get the capabilities required by a tool.
        
        Args:
            tool_name: The name of the tool
            
        Returns:
            A list of capabilities required by the tool
        """
        try:
            self.cursor.execute(
                """SELECT c.capability 
                FROM tool_capabilities c 
                JOIN tools t ON c.tool_id = t.id 
                WHERE t.name = ?""",
                (tool_name,)
            )
            
            rows = self.cursor.fetchall()
            capabilities = [row[0] for row in rows]
            
            return capabilities
        except sqlite3.Error as e:
            logger.error(f"Error getting tool capabilities: {str(e)}")
            raise
    
    def get_data_node_capabilities(self, node_id: str) -> List[str]:
        """Get the capabilities of a data node.
        
        Args:
            node_id: The ID of the node
            
        Returns:
            A list of capabilities of the node
        """
        try:
            self.cursor.execute(
                "SELECT capability FROM data_node_capabilities WHERE node_id = ?",
                (node_id,)
            )
            
            rows = self.cursor.fetchall()
            capabilities = [row[0] for row in rows]
            
            return capabilities
        except sqlite3.Error as e:
            logger.error(f"Error getting data node capabilities: {str(e)}")
            raise
    
    def get_execution_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get the execution log.
        
        Args:
            limit: The maximum number of log entries to return
            
        Returns:
            A list of execution log entries
        """
        try:
            self.cursor.execute(
                "SELECT * FROM execution_log ORDER BY created_at DESC LIMIT ?",
                (limit,)
            )
            
            rows = self.cursor.fetchall()
            log_entries = [dict(row) for row in rows]
            
            return log_entries
        except sqlite3.Error as e:
            logger.error(f"Error getting execution log: {str(e)}")
            raise
    
    def get_security_violations(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get the security violations log.
        
        Args:
            limit: The maximum number of log entries to return
            
        Returns:
            A list of security violation log entries
        """
        try:
            self.cursor.execute(
                "SELECT * FROM security_violations ORDER BY created_at DESC LIMIT ?",
                (limit,)
            )
            
            rows = self.cursor.fetchall()
            log_entries = [dict(row) for row in rows]
            
            return log_entries
        except sqlite3.Error as e:
            logger.error(f"Error getting security violations: {str(e)}")
            raise
    
    def get_queries(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get the queries log.
        
        Args:
            limit: The maximum number of log entries to return
            
        Returns:
            A list of query log entries
        """
        try:
            self.cursor.execute(
                "SELECT * FROM queries ORDER BY created_at DESC LIMIT ?",
                (limit,)
            )
            
            rows = self.cursor.fetchall()
            log_entries = [dict(row) for row in rows]
            
            return log_entries
        except sqlite3.Error as e:
            logger.error(f"Error getting queries: {str(e)}")
            raise
