# Personal AI Assistant (`ai_ASSistant`)

A locally hosted, personalized AI assistant built with **Python** and the **Google Gemini API**. This assistant features a persistent, self-editing memory system using **SQLite** and a customizable personality core ("Soul").

---

## 🚀 Features

### 🧠 Custom Persona ("Soul")

Behavior and rules are defined in a localized Markdown file.

### 💾 Persistent Memory

The agent uses SQLite to save facts, preferences, and project details across sessions.

### ✨ Self-Naming (The Awakening Directive)

On its first boot, the agent will invent a name for itself and commit it to memory permanently.

### 🔒 Isolated Environment

Built cleanly with Python virtual environments (`venv`) and environment variables.

---

## 📁 Project Structure

Before you begin, your project folder should look like this:

```bash
ai_ASSistant/
├── .env
├── main.py
├── memory_manager.py
└── your_essence/
    └── SOUL.md
```

> **Note:** The `agent_memory.db` file and `venv/` folder will be generated automatically during setup.

---

# 🛠 Setup Instructions

## 1️⃣ Create the Virtual Environment

Open your terminal in the `ai_ASSistant` project folder and create an isolated Python environment.

### Mac / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

### Windows

```bash
python -m venv venv
.\venv\Scripts\activate
```

---

## 2️⃣ Install Dependencies

With your virtual environment active, install the required libraries:

```bash
pip install google-genai python-dotenv
```

---

## 3️⃣ Configure the Environment Variables

Create a file named `.env` in the root of your project directory and add your Gemini API key:

```env
GEMINI_API_KEY=your_actual_api_key_here
```

---

## 4️⃣ Setup the Core Files

Ensure you have created the following files based on the project configuration:

### 📜 `your_essence/SOUL.md`

Contains:

* System instructions
* Core truths
* Memory management rules (JSON format schema)

### 🗄 `memory_manager.py`

Handles:

* SQLite database initialization (`init_db`)
* Adding memory (`add_memory`)
* Retrieving memory (`get_all_memories`)

### 🧩 `main.py`

The core application loop that:

* Initializes the Gemini client
* Injects stored memories into prompts
* Uses regex to parse and save JSON memory blocks
* Prevents memory JSON from being displayed to the user

---

## ▶️ 5️⃣ Run the Assistant

Make sure your virtual environment is active, then start the chat loop:

```bash
python main.py
```

On its very first run, the assistant will:

1. Read its **Awakening Directive**
2. Choose a name for itself
3. Greet you
4. Save its name to the persistent SQLite database

Type `quit` or `exit` at any time to shut the assistant down.
