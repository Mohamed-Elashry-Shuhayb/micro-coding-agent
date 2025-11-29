# Micro Coding Agent

A lightweight Python coding agent that uses Ollama for local LLM execution. The agent can autonomously edit files, execute shell commands, and navigate your codebase through natural language interaction—all with human-in-the-loop approval for safety.

## ✨ Features

- 🤖 **Natural Language Coding Assistance** - Describe what you want in plain English
- 📝 **Intelligent File Editing** - Create and modify files with find-and-replace operations
- 💻 **Shell Command Execution** - Run commands with approval prompts
- 📂 **Directory Navigation** - List and explore your project structure
- 📖 **File Reading** - Read and analyze code files
- ✅ **Human-in-the-Loop Safety** - Explicit approval required for destructive operations
- 🏠 **100% Local** - No API keys, no cloud costs, complete privacy

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- [Ollama](https://ollama.ai) installed and running

### Installation

1. **Install Ollama** (if not already installed):
   ```bash
   # macOS/Linux
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Or download from https://ollama.ai
   ```

2. **Pull a model** (choose one):
   ```bash
   ollama pull qwen2.5-coder  # Recommended for coding (best)
   ollama pull codellama      # Good for code generation
   ollama pull llama3.1       # General purpose
   ollama pull mistral        # Balanced performance
   ```

3. **Start Ollama server**:
   ```bash
   ollama serve
   ```

4. **Install the agent**:
   ```bash
   # Clone the repository
   git clone https://github.com/yourusername/micro-coding-agent.git
   cd micro-coding-agent
   
   # Install dependencies with uv (recommended)
   curl -LsSf https://astral.sh/uv/install.sh | sh
   uv pip install -e .
   
   # Or with pip
   pip install -e .
   ```

## 🎯 Usage

### Starting the Agent

```bash
python coder_agent.py
```

Or with uv:
```bash
uv run coder_agent.py
```

### Example Interactions

**Create a new Python script:**
```
> Create a Python script that calculates fibonacci numbers
```

**Debug existing code:**
```
> There's a bug in main.py where the loop never terminates. Can you fix it?
```

**Add features:**
```
> Add error handling to the database connection in app.py
```

**Refactor code:**
```
> Refactor the User class to use dataclasses instead of __init__
```

## ⚙️ Configuration

Edit the configuration variables at the top of `coder_agent.py`:

```python
OLLAMA_API_URL = "http://localhost:11434/api/chat"  # Ollama server URL
OLLAMA_MODEL = "qwen2.5-coder"                      # Model to use
```

### Recommended Models

| Model | Size | Best For | Speed |
|-------|------|----------|-------|
| **qwen2.5-coder** | 7B | Code generation & editing | ⚡⚡⚡ |
| **codellama** | 7B-34B | Code understanding | ⚡⚡ |
| **deepseek-coder** | 6.7B | Advanced coding | ⚡⚡⚡ |
| **llama3.1** | 8B | General tasks | ⚡⚡⚡ |
| **mistral** | 7B | Balanced performance | ⚡⚡⚡ |

## 🛠️ Available Tools

The agent has access to these tools:

1. **edit_file** - Modify existing files or create new ones
2. **run_command** - Execute shell commands (with approval)
3. **list_directory** - View directory contents
4. **read_file_content** - Read file contents

## 🔒 Safety Features

- **Approval Prompts**: All file edits and commands require explicit user confirmation
- **Preview Changes**: See exactly what will be modified before approval
- **Local Execution**: Everything runs on your machine—no data sent to external APIs
- **Step Limits**: Prevents infinite loops (max 30 steps by default)

## 📋 Examples

### Example 1: Create a Flask App
```
> Create a simple Flask app with a hello world endpoint in app.py
```

### Example 2: Add Tests
```
> Add unit tests for the calculate_total function in utils.py
```

### Example 3: Fix Import Errors
```
> I'm getting an import error when running main.py. Can you investigate and fix it?
```

## 🐛 Troubleshooting

**"Cannot connect to Ollama"**
- Make sure Ollama is running: `ollama serve`
- Check if the port is correct (default: 11434)

**Model not found**
- Pull the model first: `ollama pull qwen2.5-coder`
- Verify available models: `ollama list`

**Agent makes too many steps**
- Adjust `max_steps` in the code (default: 30)
- Be more specific in your requests

**Slow performance**
- Use smaller models (7B instead of 13B+)
- Ensure you have adequate RAM
- Consider using GPU acceleration

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

MIT License - feel free to use this project however you'd like!

## 🙏 Acknowledgments

- Built with [Ollama](https://ollama.ai) for local LLM inference
- Inspired by autonomous coding agents and human-in-the-loop AI systems

## 📚 Learn More

- [Ollama Documentation](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [Function Calling with LLMs](https://docs.anthropic.com/claude/docs/tool-use)
- [Prompt Engineering Guide](https://www.promptingguide.ai/)

---

**Note**: This agent is designed for development assistance. Always review changes before accepting them, especially for production code.