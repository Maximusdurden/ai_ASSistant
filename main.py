import os
import sys
import json
import re
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse  # <-- Add this!
from pydantic import BaseModel
import uvicorn
from contextlib import asynccontextmanager

import memory_manager 
import agent_tools

# Load environment variables from .env file
load_dotenv()

# Initialize the Gemini client
try:
    client = genai.Client()
except Exception as e:
    print(f"Failed to initialize client. Make sure GEMINI_API_KEY is in your .env file. Error: {e}")
    sys.exit(1)

def load_soul() -> str:
    """Reads the system prompt and injects existing persistent memories."""
    soul_path = Path("your_essence/SOUL.md")
    try:
        base_prompt = soul_path.read_text(encoding="utf-8")
        saved_memories = memory_manager.get_all_memories()
        return f"{base_prompt}\n\n{saved_memories}"
    except FileNotFoundError:
        print(f"Error: Could not find {soul_path}. Please ensure the file exists.")
        sys.exit(1)

def extract_and_save_memory(response_text: str) -> str:
    """Parses the LLM response for a memory JSON block, saves it, and removes it from the output."""
    ticks = '`' * 3
    pattern = rf'{ticks}json\n({{\s*"action":\s*"save_memory".*?}})\n{ticks}'
    match = re.search(pattern, response_text, re.DOTALL)
    
    if match:
        try:
            memory_data = json.loads(match.group(1))
            category = memory_data.get("category", "general")
            content = memory_data.get("content", "")
            
            if content:
                memory_manager.add_memory(category, content)
                print(f"\n[SYSTEM: Saved new '{category}' memory to SQLite database (via JSON fallback)]")
                
            clean_text = response_text[:match.start()].strip() + "\n" + response_text[match.end():].strip()
            return clean_text.strip()
            
        except json.JSONDecodeError:
            print("\n[SYSTEM: Agent attempted to save a memory, but the JSON was malformed.]")
            
    return response_text

def create_memory(category: str, content: str) -> str:
    """
    Saves a permanent memory to the SQLite database. Use this tool whenever the user 
    shares a fact, preference, or architectural detail that should be remembered permanently,
    or when saving your own name.
    
    Args:
        category: The category of the memory (e.g., 'agent_name', 'user_preference', 'project_context').
        content: The specific detail or fact to remember.
    """
    memory_manager.add_memory(category, content)
    print(f"\n[SYSTEM: Saved new '{category}' memory to SQLite database via Tool]")
    return "Memory successfully saved."

# --- FastAPI Server Setup ---

# Define the expected incoming JSON payload
class ChatRequest(BaseModel):
    message: str

# Global variable to hold Cortex's active chat session
cortex_session = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- This block runs on startup ---
    global cortex_session
    print("Awakening Cortex server...")
    
    system_prompt = load_soul()
    
    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=0.7,
        tools=[
            agent_tools.create_file, 
            create_memory, 
            agent_tools.read_reddit_post_comments, 
            agent_tools.read_subreddit_top_posts,
            agent_tools.read_file,
            agent_tools.edit_file,
            agent_tools.execute_command # Ensure there are no typos here!
        ],
    )
    
    cortex_session = client.chats.create(model="gemini-2.5-flash", config=config)
    print("Cortex is online and listening at http://localhost:8000")
    
    yield  # The server runs here
    
    # --- This block runs on shutdown ---
    print("\nShutting down Cortex server...")

# Initialize the app with the lifespan manager
app = FastAPI(lifespan=lifespan)

# Enable CORS so your local index.html can talk to this server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def serve_chat_ui():
    """Serves the chat interface when you visit http://localhost:8000"""
    ui_path = Path("chat_app/index.html")
    if not ui_path.exists():
        return {"error": "Could not find chat_app/index.html. Make sure the file exists!"}
    return FileResponse(ui_path)

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    if not cortex_session:
        raise HTTPException(status_code=500, detail="Cortex brain not initialized.")
    
    try:
        print(f"\nUser: {request.message}")
        response = cortex_session.send_message(request.message)
        
        # If the response is empty or a function call, the .text property fails.
        # We handle that gracefully here.
        try:
            text_content = response.text
        except ValueError:
            # This happens when Gemini calls a tool (like 'ls')
            # We check the response parts to see if a function was called.
            if response.candidates[0].content.parts[0].function_call:
                # We send the response back once to get the text summary of the tool's result.
                response = cortex_session.send_message(response)
                text_content = response.text
            else:
                text_content = "[Action Executed Successfully but no text returned]"

        # Handle your custom memory extraction logic
        clean_text = extract_and_save_memory(text_content)
        print(f"Assistant: {clean_text}\n")
            
        return {"response": clean_text}
        
    except Exception as e:
        print(f"\nAn error occurred: {e}\n")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Start the server on port 8000
    uvicorn.run(app, host="127.0.0.1", port=8000)