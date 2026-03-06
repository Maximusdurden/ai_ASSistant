# Personal AI Assistant (ai_ASSistant)

A locally hosted, personalized AI assistant built with Python, FastAPI, and the Google Gemini API. This assistant features a custom web-based chat interface, a persistent self-editing memory system using SQLite, custom tool execution, and is fully containerized using Docker.

## Features

* **Custom Persona ("Soul"):** Behavior and rules are defined in a localized Markdown file.
* **Persistent Memory:** The agent uses SQLite to save facts, preferences, and project details across sessions.
* **Web Interface:** A clean, responsive HTML/JS frontend served directly from the FastAPI backend.
* **Custom Tooling:** Equipped with Python-based tools allowing the AI to interact with the local file system (read/create files) and scrape external sources like Reddit.
* **Dockerized:** Fully containerized for seamless setup, ensuring the core Python environment and dependencies remain isolated.

## Project Structure

Before you begin, your project folder should look like this:

    ai_ASSistant/
    ├── .env
    ├── .gitignore
    ├── .dockerignore
    ├── Dockerfile
    ├── requirements.txt
    ├── main.py
    ├── memory_manager.py
    ├── agent_tools.py
    ├── chat_app/
    │   └── index.html
    └── your_essence/
        └── SOUL.md

## Setup Instructions

### 1. Configure Environment Variables

Create a file named `.env` in the root of your project directory and add your Gemini API key exactly as shown below, ensuring there are no spaces or quotes:

    GEMINI_API_KEY=your_actual_api_key_here

*Note: The `.env` and `.db` files are included in the `.gitignore` to prevent leaking API keys and personal memory databases to public repositories.*

### 2. Build the Docker Image

Open your terminal in the `ai_ASSistant` project folder and run the following command to build the container image:

    docker build -t cortex-assistant .

### 3. Run the Assistant

Run the container with volume mounts to ensure that the memory database and local file edits persist on your host machine.

**For Windows (PowerShell):**
    docker run -d `
      --name cortex-brain `
      -p 8000:8000 `
      --env-file .env `
      -v ${PWD}:/app `
      cortex-assistant

**For Linux/macOS:**
    docker run -d \
      --name cortex-brain \
      -p 8000:8000 \
      --env-file .env \
      -v ${PWD}:/app \
      cortex-assistant

## Usage

**Access the Chat Interface**
Once the container is running, open a web browser and navigate to:
`http://localhost:8000`

**Monitor Internal Logs**
To view the backend server logs, tool execution status, and the AI's internal reasoning, run the following command:

    docker logs -f cortex-brain

**Stopping and Starting**
* To stop the assistant: `docker stop cortex-brain`
* To wake it back up: `docker start cortex-brain`