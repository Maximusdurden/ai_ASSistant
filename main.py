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
    # We use \x60 instead of literal backticks here to prevent UI truncation, 
    # but it evaluates to the exact same regex search!
    match = re.search(r'\x60\x60\x60json\n({\s*"action":\s*"save_memory".*?})\n\x60\x60\x60', response_text, re.DOTALL)
    
    if match:
        try:
            # Parse the JSON string into a Python dictionary
            memory_data = json.loads(match.group(1))
            category = memory_data.get("category", "general")
            content = memory_data.get("content", "")
            
            # If valid content exists, save it to the database
            if content:
                memory_manager.add_memory(category, content)
                print(f"\n[SYSTEM: Saved new '{category}' memory to SQLite database]")
                
            # Strip the JSON block from the text, preserving text before and after it
            clean_text = response_text[:match.start()].strip() + "\n" + response_text[match.end():].strip()
            return clean_text.strip()
            
        except json.JSONDecodeError:
            print("\n[SYSTEM: Agent attempted to save a memory, but the JSON was malformed.]")
            
    # Return the original text if no memory block was found or if parsing failed
    return response_text

def main():
    print("Awakening AI Assistant... (Type 'quit' or 'exit' to stop)\n")
    
    # 1. Load the essence (Soul + Memories)
    system_prompt = load_soul()
    
    # 2. Configure the model with your system instructions
    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        temperature=0.7,
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
            
            # Intercept the response to check for database updates and clean the output
            clean_text = extract_and_save_memory(response.text)
            
            # Print the final cleaned response
            print(f"\nAssistant: {clean_text}\n")
            print("-" * 40)
            
        except Exception as e:
            print(f"\nAn error occurred: {e}\n")

if __name__ == "__main__":
    main()