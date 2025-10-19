# ChatShell: Your AI-Powered Terminal Assistant

ChatShell is an intelligent AI assistant designed to streamline your terminal interactions, especially for server deployment and automation tasks. It operates with root permissions, allowing it to execute shell commands (with your explicit confirmation for safety), read and write files, and maintain a persistent chat history across sessions. ChatShell is flexible, supporting both OpenAI/ChatGPT and Google Gemini as its underlying AI model.

## Features

*   **Intelligent Command Execution:** Safely execute shell commands with user confirmation.
*   **File System Interaction:** Read and write files to manage code, configurations, and data.
*   **Persistent Chat History:** Maintains conversation context across sessions for a seamless experience.
*   **Configurable AI Model:** Easily switch between OpenAI/ChatGPT and Google Gemini, with simple API key and model name setup.
*   **Modular Architecture:** Built with a clean, modular design using sub-agents for specific tasks like command execution and file I/O.

## Installation

You can install ChatShell as a Python package using `pip`.

```bash
pip install chatshell
```

## Configuration

Upon its first run, ChatShell will guide you through a one-time setup process to configure your AI model (ChatGPT or Gemini), API key, and desired model name. This configuration is saved in `~/.chatshell/config.json`.

You can also set your API keys as environment variables:
*   For OpenAI/ChatGPT: `OPENAI_API_KEY`
*   For Gemini: `GEMINI_API_KEY`

## Usage

Once installed, you can launch ChatShell directly from your terminal:

```bash
chatshell
```

### Basic Interaction

ChatShell acts like a conversational terminal. You can ask it to perform tasks, run commands, or read/write files.

```
You: List all files in the current directory.
ChatShell: Do you want to Execute `dir`? (Y/N)
You: Y
ChatShell: (output of `dir` command)
```

### Example Commands

*   **Read a file:**
    ```
    You: Read the content of `my_script.py`
    ```
*   **Write to a file:**
    ```
    You: Write "Hello, World!" to `output.txt`
    ```
*   **Execute a shell command:**
    ```
    You: Update the system packages.
    ChatShell: Do you want to Execute `sudo apt update && sudo apt upgrade -y`? (Y/N)
    You: Y
    ```

### Exiting ChatShell

To exit the ChatShell session, simply type `exit` or `quit`:

```
You: exit
```
