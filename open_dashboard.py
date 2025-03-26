import os
import webbrowser
import sys

def open_dashboard():
    """Open the visualization dashboard in the default web browser."""
    try:
        # Get the absolute path to the dashboard HTML file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        dashboard_path = os.path.join(script_dir, 'visualizations', 'dashboard.html')
        
        # Convert to file URI format
        if sys.platform.startswith('win'):
            dashboard_uri = f'file:///{dashboard_path.replace("\\", "/")}'
        else:
            dashboard_uri = f'file://{dashboard_path}'
        
        print(f"Opening dashboard at: {dashboard_uri}")
        
        # Open in the default web browser
        webbrowser.open(dashboard_uri)
        
        print("Dashboard opened in your default web browser.")
        print("If the browser didn't open automatically, you can manually open this file:")
        print(dashboard_path)
        
    except Exception as e:
        print(f"Error opening dashboard: {e}")
        print("You can manually open the dashboard by navigating to:")
        print("visualizations/dashboard.html")

if __name__ == "__main__":
    open_dashboard()
