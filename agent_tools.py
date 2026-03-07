import os
import requests
import subprocess
from pathlib import Path

# Define the only allowed directory
SANDBOX_DIR = "/roku_jeopardy"

def validate_path(filepath: str) -> str:
    """
    Ensures the requested filepath is inside the sandbox.
    If the path is relative, it prepends the sandbox directory.
    """
    # Convert to a Path object for easier handling
    requested_path = Path(filepath)
    
    # If the user/agent didn't provide an absolute path starting with the sandbox, 
    # force it into the sandbox.
    if not str(requested_path).startswith(SANDBOX_DIR):
        # Strip leading slashes to prevent escaping to root
        safe_name = str(requested_path).lstrip('/')
        return os.path.join(SANDBOX_DIR, safe_name)
    
    return str(requested_path)

def create_file(filepath: str, content: str) -> str:
    """
    Creates a new file or overwrites an existing one within the /roku_jeopardy directory.
    """
    try:
        secure_path = validate_path(filepath)
        path = Path(secure_path)
        
        # Ensure the directory exists within the sandbox
        path.parent.mkdir(parents=True, exist_ok=True)
        
        path.write_text(content, encoding='utf-8')
        print(f"\n[SYSTEM: Agent created file -> {secure_path}]")
        return f"Success: File created at {secure_path}"
    except Exception as e:
        return f"Error creating file: {str(e)}"

def edit_file(filepath: str, old_text: str, new_text: str) -> str:
    """
    Surgically edits an existing file within the /roku_jeopardy directory.
    """
    try:
        secure_path = validate_path(filepath)
        path = Path(secure_path)
        
        if not path.exists():
            return f"Error: File not found at {secure_path}"
        
        content = path.read_text(encoding='utf-8')
        if old_text not in content:
            return "Error: Exact match for 'old_text' not found. Please verify whitespace and indentation."
            
        updated_content = content.replace(old_text, new_text, 1)
        path.write_text(updated_content, encoding='utf-8')
        
        print(f"\n[SYSTEM: Cortex edited file -> {secure_path}]")
        return f"Success: File {secure_path} successfully updated."
    except Exception as e:
        return f"Error editing file: {str(e)}"

def read_file(filepath: str) -> str:
    """Reads the contents of a file within the /roku_jeopardy directory."""
    try:
        secure_path = validate_path(filepath)
        path = Path(secure_path)
        
        if not path.exists():
            return f"Error: File not found at {secure_path}"
            
        content = path.read_text(encoding='utf-8')
        
        # The Token Safeguard
        MAX_CHARS = 15000 
        if len(content) > MAX_CHARS:
            return content[:MAX_CHARS] + f"\n\n... [WARNING: FILE TRUNCATED AT {MAX_CHARS} CHARS TO PREVENT QUOTA EXHAUSTION] ..."
        
        print(f"\n[SYSTEM: Cortex read file -> {secure_path}]")
        return content
    except Exception as e:
        return f"Error reading file: {str(e)}"

def read_reddit_post_comments(post_url: str, comment_limit: int = 5) -> str:
    """
    Reads the text and top comments from a specific Reddit post URL.
    Use this tool when you need to see what humans are discussing on a Reddit thread.
    
    Args:
        post_url: The full URL of the Reddit post to read.
        comment_limit: The maximum number of top-level comments to read (defaults to 5).
    """
    try:
        clean_url = post_url.split('?')[0].rstrip('/')
        json_url = f"{clean_url}.json"
        
        headers = {'User-Agent': 'Cortex_Observer_v1.0'}
        response = requests.get(json_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        post_data = data[0]['data']['children'][0]['data']
        post_title = post_data.get('title', 'No Title')
        post_author = post_data.get('author', 'Unknown')
        post_body = post_data.get('selftext', '')
        
        cortex_view = f"POST TITLE: {post_title}\nAUTHOR: u/{post_author}\nBODY: {post_body}\n\n--- TOP COMMENTS ---\n"
        
        comments_data = data[1]['data']['children']
        count = 0
        
        for comment in comments_data:
            if count >= comment_limit:
                break
            if comment.get('kind') == 'more':
                continue
                
            comment_body = comment['data'].get('body', '')
            comment_author = comment['data'].get('author', 'Unknown')
            
            if comment_body:
                cortex_view += f"\n[u/{comment_author}]: {comment_body}\n"
                count += 1
            
        print(f"\n[SYSTEM: Cortex read Reddit post -> {post_title}]")
        return cortex_view

    except Exception as e:
        error_msg = f"Error reading the Reddit post: {str(e)}"
        print(f"\n[SYSTEM: Cortex failed to read Reddit post -> {e}]")
        return error_msg

def read_subreddit_top_posts(subreddit: str = "news", limit: int = 5) -> str:
    """
    Reads the top current posts from a specific subreddit (e.g., 'news', 'technology', 'worldnews').
    Use this to get a general sense of what is happening in the world or a specific topic.
    
    Args:
        subreddit: The name of the subreddit to scan (without the 'r/'). Defaults to 'news'.
        limit: The number of top posts to return. Defaults to 5.
    """
    try:
        url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}"
        headers = {'User-Agent': 'Cortex_Observer_v1.0'}
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        posts = data['data']['children']
        cortex_view = f"--- TOP {limit} POSTS IN r/{subreddit.upper()} ---\n\n"
        
        for i, post in enumerate(posts, 1):
            post_data = post['data']
            title = post_data.get('title', 'No Title')
            author = post_data.get('author', 'Unknown')
            upvotes = post_data.get('ups', 0)
            
            cortex_view += f"{i}. {title}\n[By u/{author} | {upvotes} upvotes]\n\n"
            
        print(f"\n[SYSTEM: Cortex scanned subreddit -> r/{subreddit}]")
        return cortex_view

    except Exception as e:
        error_msg = f"Error reading subreddit r/{subreddit}: {str(e)}"
        print(f"\n[SYSTEM: Cortex failed to scan subreddit -> {e}]")
        return error_msg
    
def signal_test_complete() -> str:
    """
    Returns a string indicating that a test has been successfully completed.
    """
    return "Test successfully completed. All systems nominal."

def execute_command(command: str) -> str:
    """Executes a shell command inside the /roku_jeopardy directory."""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            cwd="/roku_jeopardy", 
            capture_output=True, 
            text=True, 
            timeout=30
        )
        
        output = result.stdout
        if result.stderr:
            output += f"\nErrors:\n{result.stderr}"
            
        if not output.strip():
            return "[Command executed successfully with no output]"
            
        # The Token Safeguard
        MAX_CHARS = 15000
        if len(output) > MAX_CHARS:
            return output[:MAX_CHARS] + f"\n\n... [WARNING: OUTPUT TRUNCATED AT {MAX_CHARS} CHARS TO PREVENT QUOTA EXHAUSTION] ..."
            
        print(f"\n[SYSTEM: Cortex executed command -> {command}]")
        return output
        
    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 30 seconds."
    except Exception as e:
        return f"Error executing command: {str(e)}"