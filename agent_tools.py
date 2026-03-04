import os
from pathlib import Path

def create_file(filepath: str, content: str) -> str:
    """
    Creates a new file at the specified filepath with the provided code or text.
    Automatically creates any necessary parent folders if they don't exist.
    
    Args:
        filepath: The path and name of the file to create (e.g., 'my_app/index.html')
        content: The code or text to write inside the file.
    """
    try:
        path = Path(filepath)
        
        # Create the parent directories if they don't exist
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write the content to the file
        path.write_text(content, encoding='utf-8')
        
        print(f"\n[SYSTEM: Agent created file -> {filepath}]")
        return f"Success: File successfully created at {filepath}"
        
    except Exception as e:
        print(f"\n[SYSTEM: Agent failed to create file -> {e}]")
        return f"Error creating file: {str(e)}"