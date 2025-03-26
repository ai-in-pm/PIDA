import sqlite3
import argparse
import os
import logging
import json
from typing import Dict, Any, List, Optional
from tabulate import tabulate

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseManager:
    """A utility for managing the secure agent's database."""
    
    def __init__(self, db_path: str):
        """Initialize the database manager.
        
        Args:
            db_path: The path to the SQLite database file
        """
        self.db_path = db_path
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
    
    def list_tables(self):
        """List all tables in the database."""
        try:
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in self.cursor.fetchall()]
            
            print("\nDatabase Tables:")
            for table in tables:
                self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = self.cursor.fetchone()[0]
                print(f"- {table}: {count} rows")
        except sqlite3.Error as e:
            logger.error(f"Error listing tables: {str(e)}")
            raise
    
    def show_table_schema(self, table_name: str):
        """Show the schema of a table.
        
        Args:
            table_name: The name of the table
        """
        try:
            self.cursor.execute(f"PRAGMA table_info({table_name})")
            columns = self.cursor.fetchall()
            
            if not columns:
                print(f"\nTable '{table_name}' not found.")
                return
            
            print(f"\nSchema for table '{table_name}':")
            headers = ["ID", "Name", "Type", "NotNull", "DefaultValue", "PrimaryKey"]
            rows = [[col[0], col[1], col[2], col[3], col[4], col[5]] for col in columns]
            print(tabulate(rows, headers=headers, tablefmt="grid"))
        except sqlite3.Error as e:
            logger.error(f"Error showing table schema: {str(e)}")
            raise
    
    def show_table_data(self, table_name: str, limit: int = 10):
        """Show the data in a table.
        
        Args:
            table_name: The name of the table
            limit: The maximum number of rows to show
        """
        try:
            self.cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
            rows = self.cursor.fetchall()
            
            if not rows:
                print(f"\nNo data found in table '{table_name}'.")
                return
            
            print(f"\nData in table '{table_name}' (limited to {limit} rows):")
            headers = [column[0] for column in self.cursor.description]
            data = [[row[col] for col in range(len(headers))] for row in rows]
            print(tabulate(data, headers=headers, tablefmt="grid"))
        except sqlite3.Error as e:
            logger.error(f"Error showing table data: {str(e)}")
            raise
    
    def execute_query(self, query: str):
        """Execute a custom SQL query.
        
        Args:
            query: The SQL query to execute
        """
        try:
            self.cursor.execute(query)
            
            # Check if the query returns data
            if self.cursor.description:
                rows = self.cursor.fetchall()
                
                if not rows:
                    print("\nQuery executed successfully, but no data was returned.")
                    return
                
                print("\nQuery results:")
                headers = [column[0] for column in self.cursor.description]
                data = [[row[col] for col in range(len(headers))] for row in rows]
                print(tabulate(data, headers=headers, tablefmt="grid"))
            else:
                self.conn.commit()
                print("\nQuery executed successfully.")
        except sqlite3.Error as e:
            logger.error(f"Error executing query: {str(e)}")
            print(f"\nError executing query: {str(e)}")
    
    def export_data(self, output_file: str):
        """Export all data from the database to a JSON file.
        
        Args:
            output_file: The path to the output JSON file
        """
        try:
            # Get all tables
            self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in self.cursor.fetchall()]
            
            # Export data from each table
            data = {}
            for table in tables:
                self.cursor.execute(f"SELECT * FROM {table}")
                rows = self.cursor.fetchall()
                
                headers = [column[0] for column in self.cursor.description]
                table_data = []
                
                for row in rows:
                    row_data = {}
                    for i, header in enumerate(headers):
                        row_data[header] = row[i]
                    table_data.append(row_data)
                
                data[table] = table_data
            
            # Write data to JSON file
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"\nData exported to {output_file}")
        except sqlite3.Error as e:
            logger.error(f"Error exporting data: {str(e)}")
            raise
        except IOError as e:
            logger.error(f"Error writing to file: {str(e)}")
            raise
    
    def import_data(self, input_file: str):
        """Import data from a JSON file into the database.
        
        Args:
            input_file: The path to the input JSON file
        """
        try:
            # Read data from JSON file
            with open(input_file, 'r') as f:
                data = json.load(f)
            
            # Import data into each table
            for table, table_data in data.items():
                # Check if the table exists
                self.cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
                if not self.cursor.fetchone():
                    print(f"\nTable '{table}' not found in the database. Skipping.")
                    continue
                
                # Get the table schema
                self.cursor.execute(f"PRAGMA table_info({table})")
                columns = [col[1] for col in self.cursor.fetchall()]
                
                # Import data
                for row_data in table_data:
                    # Filter out keys that don't correspond to columns
                    filtered_data = {k: v for k, v in row_data.items() if k in columns}
                    
                    # Generate the SQL query
                    placeholders = ', '.join(['?'] * len(filtered_data))
                    columns_str = ', '.join(filtered_data.keys())
                    query = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})"
                    
                    # Execute the query
                    self.cursor.execute(query, list(filtered_data.values()))
            
            self.conn.commit()
            print(f"\nData imported from {input_file}")
        except sqlite3.Error as e:
            self.conn.rollback()
            logger.error(f"Error importing data: {str(e)}")
            raise
        except IOError as e:
            logger.error(f"Error reading from file: {str(e)}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON: {str(e)}")
            raise
    
    def clear_table(self, table_name: str):
        """Clear all data from a table.
        
        Args:
            table_name: The name of the table
        """
        try:
            self.cursor.execute(f"DELETE FROM {table_name}")
            self.conn.commit()
            print(f"\nTable '{table_name}' cleared.")
        except sqlite3.Error as e:
            self.conn.rollback()
            logger.error(f"Error clearing table: {str(e)}")
            raise
    
    def vacuum_database(self):
        """Vacuum the database to reclaim unused space."""
        try:
            self.cursor.execute("VACUUM")
            print("\nDatabase vacuumed.")
        except sqlite3.Error as e:
            logger.error(f"Error vacuuming database: {str(e)}")
            raise

def main():
    parser = argparse.ArgumentParser(description='Secure Agent Database Manager')
    parser.add_argument('--db-path', type=str, help='Path to the SQLite database file',
                        default=os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'secure_agent.db'))
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # List tables command
    subparsers.add_parser('list-tables', help='List all tables in the database')
    
    # Show table schema command
    schema_parser = subparsers.add_parser('show-schema', help='Show the schema of a table')
    schema_parser.add_argument('table', type=str, help='Name of the table')
    
    # Show table data command
    data_parser = subparsers.add_parser('show-data', help='Show the data in a table')
    data_parser.add_argument('table', type=str, help='Name of the table')
    data_parser.add_argument('--limit', type=int, default=10, help='Maximum number of rows to show')
    
    # Execute query command
    query_parser = subparsers.add_parser('query', help='Execute a custom SQL query')
    query_parser.add_argument('sql', type=str, help='SQL query to execute')
    
    # Export data command
    export_parser = subparsers.add_parser('export', help='Export all data to a JSON file')
    export_parser.add_argument('output', type=str, help='Path to the output JSON file')
    
    # Import data command
    import_parser = subparsers.add_parser('import', help='Import data from a JSON file')
    import_parser.add_argument('input', type=str, help='Path to the input JSON file')
    
    # Clear table command
    clear_parser = subparsers.add_parser('clear', help='Clear all data from a table')
    clear_parser.add_argument('table', type=str, help='Name of the table')
    
    # Vacuum database command
    subparsers.add_parser('vacuum', help='Vacuum the database to reclaim unused space')
    
    args = parser.parse_args()
    
    # Create database directory if it doesn't exist
    os.makedirs(os.path.dirname(args.db_path), exist_ok=True)
    
    # Check if the database file exists
    if not os.path.exists(args.db_path):
        print(f"Database file not found: {args.db_path}")
        return
    
    # Initialize the database manager
    manager = DatabaseManager(args.db_path)
    
    try:
        # Execute the command
        if args.command == 'list-tables':
            manager.list_tables()
        elif args.command == 'show-schema':
            manager.show_table_schema(args.table)
        elif args.command == 'show-data':
            manager.show_table_data(args.table, args.limit)
        elif args.command == 'query':
            manager.execute_query(args.sql)
        elif args.command == 'export':
            manager.export_data(args.output)
        elif args.command == 'import':
            manager.import_data(args.input)
        elif args.command == 'clear':
            manager.clear_table(args.table)
        elif args.command == 'vacuum':
            manager.vacuum_database()
        else:
            print("No command specified. Use --help to see available commands.")
    finally:
        # Close the database connection
        manager.close()

if __name__ == '__main__':
    main()
