# NuralShell: Your AI-Powered Terminal Assistant

NuralShell is an intelligent AI assistant designed to streamline your terminal interactions, especially for server deployment and automation tasks. It operates with root permissions, allowing it to execute shell commands (with your explicit confirmation for safety), read and write files, and maintain a persistent chat history across sessions. NuralShell is flexible, supporting both OpenAI/ChatGPT and Google Gemini as its underlying AI model.

## Features

*   **Intelligent Command Execution:** Safely execute shell commands with user confirmation.
*   **File System Interaction:** Read and write files to manage code, configurations, and data.
*   **Persistent Chat History:** Maintains conversation context across sessions for a seamless experience.
*   **Configurable AI Model:** Easily switch between OpenAI/ChatGPT and Google Gemini, with simple API key and model name setup.
*   **Modular Architecture:** Built with a clean, modular design using sub-agents for specific tasks like command execution and file I/O.

## Installation

You can install NuralShell as a Python package using `pip`.

```bash
pip install NuralShell
```

## Configuration

Upon its first run, NuralShell will guide you through a one-time setup process to configure your AI model (ChatGPT or Gemini), API key, and desired model name. This configuration is saved in `~/.NuralShell/config.json`.

You can also set your API keys as environment variables:
*   For OpenAI/ChatGPT: `OPENAI_API_KEY`
*   For Gemini: `GEMINI_API_KEY`

## Usage

Once installed, you can launch NuralShell directly from your terminal:

```bash
nuralshell
```

### Basic Interaction

NuralShell acts like a conversational terminal. You can ask it to perform tasks, run commands, or read/write files.

```
You: List all files in the current directory.
NuralShell: Do you want to Execute `dir`? (Y/N)
You: Y
NuralShell: (output of `dir` command)
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
    NuralShell: Do you want to Execute `sudo apt update && sudo apt upgrade -y`? (Y/N)
    You: Y
    ```

### Exiting NuralShell

To exit the NuralShell session, simply type `exit` or `quit`:

```
You: exit
```
