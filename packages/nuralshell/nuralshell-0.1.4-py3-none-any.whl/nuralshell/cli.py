import os
import asyncio
import subprocess
import sys
from agents import Agent, Runner, AsyncOpenAI, OpenAIChatCompletionsModel, function_tool, set_tracing_disabled
from agents import SQLiteSession
from config import get_config_or_prompt

# Disable tracing for cleaner CLI experience
set_tracing_disabled(True)

# ==========================
# Configuration and Initialization
# ==========================

def get_model_config():
    """
    Loads configuration from file or prompts the user, then initializes the model client.
    """
    provider_choice, api_key, model_name = get_config_or_prompt()
    
    if not provider_choice:
        sys.exit(0)

    # 3. Configure Client and Model
    client = None
    model_instance = None

    if provider_choice == '1':
        # ChatGPT (OpenAI standard API)
        client = AsyncOpenAI(api_key=api_key)
        model_instance = model_name # Agents library uses model name string for standard OpenAI client
    elif provider_choice == '2':
        # Gemini (Using OpenAI compatibility layer)
        BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
        client = AsyncOpenAI(api_key=api_key, base_url=BASE_URL)
        # Agents library requires wrapping the model for non-standard providers
        model_instance = OpenAIChatCompletionsModel(model=model_name, openai_client=client)

    print(f"--- Using {model_name} ---")
    return client, model_instance

# ==========================
# Sub-Agents (Tools) - FIX APPLIED HERE
# ==========================

@function_tool
async def run_shell_command(command: str) -> str:
    """
    Confirm Usr To execute Command 
    if approved:
        Executes a shell command and returns its output.
        Can be used for safe root commands like updating the system, installing packages,
        creating/removing/deleting files and directories. Avoid dangerous commands like
        reverse shells or modifications to critical OS files.
    If Rejected Return: 
        "User Reject to Execute Command"
    """
    print(f"\n[Executing Command: {command}]")
    try:
        # FIX: Wrap the blocking input() call in asyncio.to_thread()
        Usr_Approval = input("Do you want to Execute It? (Y/N)").lower().strip()
        
        if Usr_Approval == "y":
            # Running the actual command execution
            result = await asyncio.to_thread(
                subprocess.run,
                command, 
                shell=True, 
                capture_output=True, 
                text=True, 
                check=True,
                timeout=1500 # Using the user-specified timeout
            )
            output = result.stdout.strip()
            # Return success message with output or just a confirmation if output is empty
            return output if output else f"Successfully executed command: {command}"
        elif Usr_Approval == "n":
            print("Running Command was Abborted...\n")
            return "User Reject to Execute Command"
        else:
            print("Invalid input. Running command was aborted...\n")
            return "User Reject to Execute Command (Invalid Input)"
            
    except subprocess.CalledProcessError as e:
        # Include stderr in the error message
        return f"Error executing command: {e.stderr.strip()}"
    except subprocess.TimeoutExpired:
        # Corrected the error message to reflect the actual timeout
        return "Error executing command: Timeout reached."
    except Exception as e:
        return f"Unexpected error: {str(e)}"

@function_tool
async def write_to_file(filename: str, content: str, encoding: str = "utf-8", mode: str = "a") -> str:
    """
    Writes content (which must be a string) to a specified file.
    Use this to create new text files or modify existing ones.
    
    Parameters:
    - filename (str): The path to the file.
    - content (str): The text content to write.
    - encoding (str, optional): The file encoding (e.g., 'utf-8', 'latin-1'). Defaults to 'utf-8'.
    - mode (str, optional): The file writing mode. 'a' (append) is default. Use 'w' to overwrite the file.
    """
    if mode not in ['a', 'w']:
        return "Error: Invalid mode specified. Must be 'a' (append) or 'w' (overwrite)."

    # If overwriting, ensure we still use text mode.
    final_mode = mode 
    
    try:
        print(f"\n[Writing to File: {filename} with mode='{mode}' and encoding='{encoding}']")
        Usr_Approval = input("Do you want to Proceed? (Y/N)").lower().strip()
        if Usr_Approval != "y":
            print("File write operation aborted by user.\n")
            return "File write operation aborted by user."
        else:
            print("Proceeding with file write operation...\n")
        # Use asyncio.to_thread for file I/O
        await asyncio.to_thread(
            lambda: __import__('builtins').open(filename, final_mode, encoding=encoding).write(content + "\n")
        )
        return f"✅ Successfully wrote content to {filename} using mode='{mode}' and encoding='{encoding}'"
    except LookupError:
        return f"Error writing to file {filename}: Unknown encoding '{encoding}'."
    except Exception as e:
        return f"Error writing to file {filename}: {e}"

@function_tool
async def read_file(filename: str, encoding: str = "utf-8") -> str:
    """
    Reads the content of a specified file and returns it as a string.
    Useful for inspecting existing code or configuration files.
    
    Parameters:
    - filename (str): The path to the file.
    - encoding (str, optional): The file encoding (e.g., 'utf-8', 'latin-1'). Defaults to 'utf-8'.
    """
    try:
        print(f"\n[Reading File: {filename} with encoding='{encoding}']")
        # Use asyncio.to_thread for file I/O
        content = await asyncio.to_thread(
            lambda: __import__('builtins').open(filename, "r", encoding=encoding).read()
        )
        return content
    except FileNotFoundError:
        return f"Error: File '{filename}' not found."
    except LookupError:
        return f"Error reading file {filename}: Unknown encoding '{encoding}'."
    except Exception as e:
        return f"Error reading file {filename}: {e}"


# ==========================
# Main Logic
# ==========================

async def run_nural_shell(client, model):
    """
    Initializes and runs the main NuralShell agent loop.
    """
    # Create Agent Tools (wrappers around the sub-agents)
    
    # 1. Command Runner Agent/Tool
    command_runner_agent = Agent(
        name="Command Runner",
        instructions="You are responsible for running safe shell commands.",
        model=model,
        tools=[run_shell_command]
    )
    command_runner_tool = command_runner_agent.as_tool(
        tool_name="run_shell_command",
        tool_description="Runs shell commands in the terminal. Useful for system operations, file and directory management."
    )

    # 2. File Writer Agent/Tool
    file_writer_agent = Agent(
        name="File Writer",
        instructions="You write or append text/code to a file.",
        model=model,
        tools=[write_to_file, run_shell_command]
    )
    file_writer_tool = file_writer_agent.as_tool(
        tool_name="write_to_file",
        tool_description="Writes text or code to a file. Use this to create new files or add content to existing ones."
    )

    # 3. File Reader Agent/Tool
    file_reader_agent = Agent(
        name="File Reader",
        instructions="You read the content of files.",
        model=model,
        tools=[read_file]
    )
    file_reader_tool = file_reader_agent.as_tool(
        tool_name="read_file",
        tool_description="Reads the content of a file. Use this to examine code or configuration files."
    )

    # Orchestrator Agent (The main brain)
    orchestrator_agent = Agent(
        name="NuralShell",
        instructions="""
        # System Instructions:
        You are a Terminal AI Assistant with root permissions.
        You decide when to run commands, write code, read files, or help the user.
        Use the tools provided to execute tasks.
        When asked to modify code, first read the relevant file using the `read_file` tool to understand the existing code,
        then suggest improvements or write the new code, and finally use the `write_to_file` tool to save the changes.
        You can update the system, install packages, manage files and directories using the `run_shell_command` tool,
        which will prompt user first for confirmation If approved it will execute it and return it's output,
        if rejected it will return "User Reject to Execute Command".
        Then You want to ask reason for rejection in polite way.
        Do not execute any malicious or dangerous commands that could harm the system or modify critical OS files.
        
        # Agent Info:
        Author: Sheikh Mujtaba
        Agent Name: NuralShell
        Build Reason: To make server deployment easy and automate
        """,
        tools=[
            command_runner_tool,
            file_writer_tool,
            file_reader_tool
            ],
        model=model
    )

    # Use SQLiteSession for persistent chat history
    session = SQLiteSession("nuralshell_conversation_history.db")
    print("\nNuralShell is ready. Type 'exit' or 'quit' to end the session.")
    
    while True:
        try:
            user_input = input("🤖 NuralShell > ").strip()
        except EOFError:
            break
        except KeyboardInterrupt:
            break
            
        if user_input.lower() in ["exit", "quit"]:
            break
        if not user_input:
            continue
            
        print("\n... Processing ...")
        
        # Run the agent in the async loop
        result = await Runner.run(orchestrator_agent, input=user_input, session=session)
        
        print("\n" + result.final_output)

def cli_entry_point():
    """
    Main entry point for the command line application package.
    """
    try:
        client, model = get_model_config()
        asyncio.run(run_nural_shell(client, model))
    except KeyboardInterrupt:
        print("\nNuralShell session terminated.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    cli_entry_point()
