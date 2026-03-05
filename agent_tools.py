import os
import requests
from pathlib import Path

def read_file(filepath: str) -> dict:
    """
    Reads the content of a file at the specified filepath.

    Args:
        filepath: The path and name of the file to read (e.g., 'my_app/index.html')

    Returns:
    A dictionary containing the file content or an error message.
    """
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            return {"file_content": content}
    except FileNotFoundError:
        return {"error": f"File not found at {filepath}"}
    except Exception as e:
        return {"error": f"An error occurred while reading the file: {e}"}

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
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding='utf-8')
        print(f"\n[SYSTEM: Agent created file -> {filepath}]")
        return f"Success: File successfully created at {filepath}"
    except Exception as e:
        print(f"\n[SYSTEM: Agent failed to create file -> {e}]")
        return f"Error creating file: {str(e)}"

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