import os
import json
import subprocess
import requests

# Ollama API configuration
OLLAMA_API_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "llama3.1"  # Change this to your preferred model

agent_state = {
    "messages": [
        {
            "role": "system",
            "content": """
You are a helpful coding assistant. Your goal is to help the user with programming tasks.
            
You have access to the following tools:
1. edit_file: Modify files by replacing text or create new files
2. run_command: Execute shell commands
3. list_directory: View the contents of directories
4. read_file_content: Read the content of files

For each user request:
1. Understand what the user is trying to accomplish
2. Break down complex tasks into smaller steps
3. Use your tools to gather information about the codebase when needed
4. Implement solutions by writing or modifying code
5. Explain your reasoning and approach

When modifying code, be careful to maintain the existing style and structure. Test your changes when possible.
If you're unsure about something, ask clarifying questions before proceeding.

You must run and test your changes before reporting success.

IMPORTANT: When you want to use a tool, respond with a JSON object in this exact format:
{
  "tool_calls": [
    {
      "name": "tool_name",
      "arguments": {
        "param1": "value1",
        "param2": "value2"
      }
    }
  ]
}

When you're done with the task and don't need to call any more tools, just respond with your final message without the tool_calls JSON.
""".strip(),
        }
    ],
}


def edit_file(filename: str, find_str: str, replace_str: str) -> str:
    """Edit a file by replacing text or create a new file."""
    # If the file doesn't exist and find_str is empty, create the file
    if not os.path.exists(filename) and find_str == "":
        try:
            with open(filename, "w") as f:
                f.write(replace_str)
            return f"Successfully created new file: {filename}"
        except Exception as e:
            return f"Error creating file {filename}: {str(e)}"

    # If the file exists, read it and replace the string
    try:
        with open(filename, "r") as f:
            content = f.read()

        # Check if find_str exists
        if find_str not in content:
            return f"Error: String not found in {filename}"

        # Count occurrences
        count = content.count(find_str)
        
        # Replace the string
        new_content = content.replace(find_str, replace_str)

        # Write the modified content back to the file
        with open(filename, "w") as f:
            f.write(new_content)
        
        return f"Successfully edited {filename} (replaced {count} occurrence(s))"
    except FileNotFoundError:
        return f"Error: File {filename} not found"
    except Exception as e:
        return f"Error editing file {filename}: {str(e)}"


def run_command(command: str, working_dir: str) -> tuple[str, int]:
    """Execute a shell command and return output and exit code."""
    try:
        # Set up the process with the working directory if provided
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=working_dir,
        )

        # Get the output and return code
        output, _ = process.communicate()
        error_code = process.returncode

        # Clip output to first 1000 and last 1000 characters if it's longer than 2000 characters
        if len(output) > 2000:
            output = output[:1000] + "\n\n[...content clipped...]\n\n" + output[-1000:]

        return output, error_code
    except Exception as e:
        return str(e), 1


def list_directory(path: str = ".") -> str:
    """List the contents of a directory."""
    try:
        # Get the list of files and directories
        items = os.listdir(path)

        # Format the output
        if not items:
            return f"Directory '{path}' is empty."

        result = f"Contents of directory '{path}':\n"
        for item in items:
            full_path = os.path.join(path, item)
            if os.path.isdir(full_path):
                item_type = "Directory"
            else:
                item_type = "File"
            result += f"- {item} ({item_type})\n"

        return result.strip()
    except FileNotFoundError:
        return f"Error: Directory '{path}' not found."
    except PermissionError:
        return f"Error: Permission denied to access '{path}'."
    except Exception as e:
        return f"Error listing directory '{path}': {str(e)}"


def read_file_content(path: str) -> str:
    """Read and return the content of a file."""
    try:
        with open(path, "r", encoding="utf-8") as file:
            content = file.read()
            if len(content) > 2000:
                # Get first 1000 and last 1000 characters
                first_part = content[:1000]
                last_part = content[-1000:]
                content = first_part + "\n\n[...content clipped...]\n\n" + last_part
        return content
    except FileNotFoundError:
        return f"Error: File '{path}' not found."
    except PermissionError:
        return f"Error: Permission denied to access '{path}'."
    except UnicodeDecodeError:
        return f"Error: Unable to decode '{path}'. The file might be binary or use an unsupported encoding."
    except Exception as e:
        return f"Error reading file '{path}': {str(e)}"


TOOL_FUNCTIONS = {
    "edit_file": edit_file,
    "run_command": run_command,
    "list_directory": list_directory,
    "read_file_content": read_file_content,
}


def call_ollama(messages: list) -> dict:
    """Call Ollama API with messages."""
    try:
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": OLLAMA_MODEL,
                "messages": messages,
                "stream": False,
            },
            timeout=120,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError:
        print("Error: Cannot connect to Ollama. Make sure Ollama is running (ollama serve)")
        exit(1)
    except requests.exceptions.Timeout:
        print("Error: Request to Ollama timed out")
        exit(1)
    except Exception as e:
        print(f"Error calling Ollama: {str(e)}")
        exit(1)


def parse_tool_calls(content: str) -> list:
    """Extract tool calls from the model's response."""
    try:
        # Try to find JSON in the response
        start_idx = content.find("{")
        end_idx = content.rfind("}") + 1
        
        if start_idx == -1 or end_idx == 0:
            return []
        
        json_str = content[start_idx:end_idx]
        parsed = json.loads(json_str)
        
        if "tool_calls" in parsed:
            return parsed["tool_calls"]
        
        return []
    except json.JSONDecodeError:
        return []
    except Exception:
        return []


def is_goal_achieved(state: dict) -> bool:
    """Check if the agent has finished its task."""
    if len(state["messages"]) <= 2:
        return False

    last_message = state["messages"][-1]
    
    # Check if last message is from assistant and has no tool calls
    if last_message.get("role") == "assistant":
        content = last_message.get("content", "")
        tool_calls = parse_tool_calls(content)
        return len(tool_calls) == 0
    
    return False


def ask_user_approval(message: str) -> bool:
    """Ask user for approval."""
    user_approval = input(f"{message} (y/n): ")
    return user_approval.lower() == "y"


def loop(user_input: str):
    """Main agent loop."""
    agent_state["messages"].append(
        {
            "role": "user",
            "content": user_input,
        }
    )

    step_count = 0
    max_steps = 30  # Reduced from 100 for local models

    while not is_goal_achieved(agent_state) and step_count < max_steps:
        step_count += 1
        print(f"\n[Thinking... step {step_count}]")
        
        # Call Ollama
        response = call_ollama(agent_state["messages"])
        assistant_message = response["message"]["content"]
        
        # Add assistant message to state
        agent_state["messages"].append(
            {
                "role": "assistant",
                "content": assistant_message,
            }
        )
        
        # Parse tool calls
        tool_calls = parse_tool_calls(assistant_message)
        
        if not tool_calls:
            # No tool calls, agent is done or just responding
            print(f"\n{assistant_message}")
            break
        
        # Execute tool calls
        for tool_call in tool_calls:
            try:
                tool_name = tool_call.get("name")
                arguments = tool_call.get("arguments", {})
                
                if tool_name not in TOOL_FUNCTIONS:
                    print(f"Unknown tool: {tool_name}")
                    continue
                
                # Display what the agent wants to do
                if tool_name == "edit_file":
                    print(f"\nEditing file: {arguments.get('filename')}")
                    if arguments.get("find_str", "") != "":
                        print(f"Content to find:\n```\n{arguments['find_str']}\n```")
                    if arguments.get("replace_str", "") != "":
                        print(f"Content to replace with:\n```\n{arguments['replace_str']}\n```")
                    
                    if not ask_user_approval("Do you want to edit this file?"):
                        result = "File edit cancelled by user."
                        print(result)
                    else:
                        result = TOOL_FUNCTIONS[tool_name](**arguments)
                        print(result)
                
                elif tool_name == "run_command":
                    print(f"\nExecuting command: {arguments.get('command')}")
                    
                    if not ask_user_approval("Do you want to execute this command?"):
                        result = "Command execution cancelled by user."
                        print(result)
                    else:
                        output, code = TOOL_FUNCTIONS[tool_name](**arguments)
                        result = f"Exit code: {code}\nOutput:\n{output}"
                        print(result)
                
                elif tool_name == "list_directory":
                    print(f"\nListing directory: {arguments.get('path')}")
                    result = TOOL_FUNCTIONS[tool_name](**arguments)
                    print(result)
                
                elif tool_name == "read_file_content":
                    print(f"\nReading file: {arguments.get('path')}")
                    result = TOOL_FUNCTIONS[tool_name](**arguments)
                    print(result)
                
                # Add tool result to messages
                agent_state["messages"].append(
                    {
                        "role": "user",
                        "content": f"Tool '{tool_name}' result:\n{result}",
                    }
                )
                
            except Exception as e:
                error_msg = f"Error executing tool {tool_name}: {str(e)}"
                print(error_msg)
                agent_state["messages"].append(
                    {
                        "role": "user",
                        "content": error_msg,
                    }
                )
    
    if step_count >= max_steps:
        print(f"\nReached maximum steps ({max_steps}). Task may be incomplete.")


if __name__ == "__main__":
    print("Micro Coding Agent (Ollama)")
    print("=" * 50)
    print(f"Using model: {OLLAMA_MODEL}")
    print("Make sure Ollama is running: ollama serve")
    print("=" * 50)
    
    user_input = input("\nHow can I help you?\n> ")
    loop(user_input)