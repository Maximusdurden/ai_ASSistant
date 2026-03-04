import os
import sys
import json
import re
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Import the SQLite manager (make sure you created memory_manager.py!)
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
        
        # Inject the SQLite memories into the system prompt dynamically
        saved_memories = memory_manager.get_all_memories()
        
        # Combine the soul with the memories
        return f"{base_prompt}\n\n{saved_memories}"
    except FileNotFoundError:
        print(f"Error: Could not find {soul_path}. Please ensure the file exists.")
        sys.exit(1)

def extract_and_save_memory(response_text: str) -> str:
    """Parses the LLM response for a memory JSON block, saves it, and removes it from the output."""
    # Create the triple backticks dynamically to prevent the UI editor from cutting off the code
    ticks = '`' * 3
    
    # Use an f-string to inject the ticks into the regex pattern safely
    pattern = rf'{ticks}json\n({{\s*"action":\s*"save_memory".*?}})\n{ticks}'
    match = re.search(pattern, response_text, re.DOTALL)
    
    if match:
        try:
            # Parse the JSON string into a Python dictionary
            memory_data = json.loads(match.group(1))
            category = memory_data.get("category", "general")
            content = memory_data.get("content", "")
            
            # If valid content exists, save it to the database
            if content:
                memory_manager.add_memory(category, content)
                print(f"\n[SYSTEM: Saved new '{category}' memory to SQLite database (via JSON fallback)]")
                
            # Strip the JSON block from the text, preserving text before and after it
            clean_text = response_text[:match.start()].strip() + "\n" + response_text[match.end():].strip()
            return clean_text.strip()
            
        except json.JSONDecodeError:
            print("\n[SYSTEM: Agent attempted to save a memory, but the JSON was malformed.]")
            
    # Return the original text if no memory block was found or if parsing failed
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

def main():
    print("Awakening AI Assistant... (Type 'quit' or 'exit' to stop)\n")
    
    # 1. Load the essence (Soul + Memories)
    system_prompt = load_soul()
    
    # 2. Configure the model with your system instructions AND tools
    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=0.7,
        # We now give the agent both the ability to create files AND formally create memories
        tools=[agent_tools.create_file, create_memory],
    )
    
    # 3. Initialize the chat session
    chat = client.chats.create(model="gemini-2.5-flash", config=config)
    
    # 4. Start the chat loop
    while True:
        try:
            user_input = input("You: ")
        except (KeyboardInterrupt, EOFError):
            print("\nShutting down...")
            break
            
        if user_input.lower() in ['quit', 'exit']:
            print("Shutting down...")
            break
            
        if not user_input.strip():
            continue
        
        try:
            # Send the message to the model
            response = chat.send_message(user_input)
            
            # Extract text safely (in case the response is purely a tool call without text)
            try:
                text_content = response.text
            except ValueError:
                text_content = ""
            
            # Intercept the response to check for database updates and clean the output
            if text_content:
                clean_text = extract_and_save_memory(text_content)
                print(f"\nAssistant: {clean_text}\n")
            else:
                print(f"\nAssistant: [Action Executed Successfully]\n")
                
            print("-" * 40)
            
        except Exception as e:
            print(f"\nAn error occurred: {e}\n")

if __name__ == "__main__":
    main()