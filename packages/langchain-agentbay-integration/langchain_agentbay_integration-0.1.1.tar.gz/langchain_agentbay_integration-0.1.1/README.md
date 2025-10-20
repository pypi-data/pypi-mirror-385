# AgentBay <> LangChain Integration

## Installation

It's recommended to create a virtual environment before installing the package:

```bash
python -m venv agentbay_langchain_env
source ./agentbay_langchain_env/bin/activate
```

To ensure you have the latest version of pip, first run:

```bash
pip install --upgrade pip
```

To install the package, run:

```bash
pip install -U langchain-agentbay-integration wuying-agentbay-sdk==0.9.0
```

You'll also need to install LangChain and an LLM provider package. For example, to use with OpenAI:

```bash
pip install langchain==0.3.27 langchain-openai
```

## Setup

You need to configure credentials by setting the following environment variables:

### API Keys Setup

**AgentBay API Key**:
1. Visit [Agent-Bay Console](https://agentbay.console.aliyun.com/service-management)
2. Sign up or log in to your Alibaba Cloud account
3. Navigate to the Service Management section
4. Create a new API KEY or select an existing one
5. Copy the API Key and set it as the value of `AGENTBAY_API_KEY` environment variable

**DashScope API Key**:
1. Visit [DashScope Platform](https://bailian.console.aliyun.com/#/home)
2. Sign up or log in to your account
3. Navigate to the API Key management section
4. Copy the API Key and set it as the value of `DASHSCOPE_API_KEY` environment variable

```bash
export AGENTBAY_API_KEY="your-agentbay-api-key"
export DASHSCOPE_API_KEY="your-dashscope-api-key"
```

## AgentBay Integration Toolkit

The AgentbayIntegrationToolkit provides a comprehensive set of tools for interacting with the AgentBay cloud computing platform.

### Instantiation

The AgentbayIntegrationToolkit supports two session types: CODESPACE (default) and BROWSERUSE. The session type determines which tools are available.

#### Code Operations Mode (CODESPACE - default)

Create an AgentBay session for code operations:

```python
import os
from agentbay import AgentBay
from agentbay.session_params import CreateSessionParams
from langchain_agentbay_integration import AgentbayIntegrationToolkit

# Create AgentBay session for code operations
agent_bay = AgentBay()
params = CreateSessionParams(image_id="code_latest")
result = agent_bay.create(params)
session = result.session

# Initialize the toolkit for code operations (default)
toolkit = AgentbayIntegrationToolkit(session=session)
```

#### Browser Automation Mode (BROWSERUSE)

Create an AgentBay session for browser automation:

```python
import os
from agentbay import AgentBay
from agentbay.session_params import CreateSessionParams
from langchain_agentbay_integration import AgentbayIntegrationToolkit
from langchain_agentbay_integration.tools import SessionType

# Create AgentBay session for browser operations
browser_agent_bay = AgentBay()
browser_params = CreateSessionParams(image_id="browser_latest")
browser_result = browser_agent_bay.create(browser_params)
browser_session = browser_result.session

# Initialize the toolkit for browser operations
browser_toolkit = AgentbayIntegrationToolkit(
    session=browser_session,
    session_type=SessionType.BROWSERUSE,
    image_id="browser_latest"
)
```

### Tools

The toolkit includes the following tools:

#### Code Operations Mode (CODESPACE - default)

1. **WriteFileTool**: Write content to files in the AgentBay session with support for both overwrite and append modes.

   **Input Format**:
   ```json
   {
     "path": "/path/to/file.txt",
     "content": "File content to write",
     "mode": "overwrite" // Optional, can be "overwrite" or "append"
   }
   ```

   **Output Format**:
   ```json
   "File written successfully to /path/to/file.txt with mode 'overwrite'"
   ```
   or
   ```json
   "Failed to write file: <error_message>"
   ```

2. **ReadFileTool**: Read content from files in the AgentBay session.

   **Input Format**:
   ```json
   {
     "path": "/path/to/file.txt"
   }
   ```

   **Output Format**:
   ```json
   "File content:\n<file_content>"
   ```
   or
   ```json
   "Failed to read file: <error_message>"
   ```

3. **RunCodeTool**: Execute Python or JavaScript code in a secure cloud environment.

   **Input Format**:
   ```json
   {
     "code": "print('Hello World')",
     "language": "python", // Can be "python" or "javascript"
     "timeout_s": 60 // Optional, default is 60 seconds
   }
   ```

   **Output Format**:
   ```json
   "Code execution result:\n<code_output>\nRequest ID: <request_id>"
   ```
   or
   ```json
   "Code execution failed with error: <error_message>"
   ```

4. **ExecuteCommandTool**: Run shell commands with configurable timeout settings.

   **Input Format**:
   ```json
   {
     "command": "ls -la",
     "timeout_ms": 1000 // Optional, default is 1000 milliseconds
   }
   ```

   **Output Format**:
   ```json
   "Command output:\n<command_output>"
   ```
   or
   ```json
   "Command failed with error: <error_message>"
   ```

#### Browser Automation Mode (BROWSERUSE)

When initialized with `session_type=SessionType.BROWSERUSE` and `image_id="browser_latest"`:

1. **BrowserNavigateTool**: Navigate to URLs in the AgentBay browser session. Optional: set `extract_content=True` to enable page content extraction (disabled by default for performance).

   **Input Format**:
   ```json
   {
     "url": "https://www.example.com",
     "extract_content": false // Optional, default is false
   }
   ```

   **Output Format** (when extract_content=false):
   ```json
   {
     "success": true,
     "message": "Successfully navigated to https://www.example.com",
     "url": "https://www.example.com"
   }
   ```
   or (when extract_content=true):
   ```json
   {
     "success": true,
     "message": "Successfully navigated to https://www.example.com",
     "url": "https://www.example.com",
     "extract_results": {
       "title": "Page Title",
       "description": "Page Description",
       "urls": ["url1", "url2"],
       "content": "Page Content"
     }
   }
   ```
   or (on error):
   ```json
   {
     "success": false,
     "error": "Error occurred while navigating to URL: <error_message>"
   }
   ```

2. **BrowserActTool**: Perform actions on browser pages in the AgentBay session. You can open URLs, click buttons, fill forms, etc. Optional: set `extract_content=True` to enable page content extraction (disabled by default for performance).

   **Input Format**:
   ```json
   {
     "action": "Click the login button",
     "extract_content": false // Optional, default is false
   }
   ```

   **Output Format** (when extract_content=false):
   ```json
   {
     "success": true,
     "message": "Action completed successfully",
     "action": "Click the login button"
   }
   ```
   or (when extract_content=true):
   ```json
   {
     "success": true,
     "message": "Action completed successfully",
     "action": "Click the login button",
     "extract_results": {
       "title": "Page Title",
       "description": "Page Description",
       "urls": ["url1", "url2"],
       "content": "Page Content"
     }
   }
   ```
   or (on error):
   ```json
   "Error occurred while performing browser action: <error_message>"
   ```

3. **ScreenshotTool**: Take screenshots of the current browser page in the AgentBay session.

   **Input Format**:
   ```json
   {
     "file_path": "/path/to/screenshot.png"
   }
   ```

   **Output Format** (on success):
   ```json
   {
     "success": true,
     "message": "Screenshot captured successfully",
     "file_path": "/path/to/screenshot.png"
   }
   ```
   or (on failure):
   ```json
   {
     "success": false,
     "error": "Failed to capture screenshot"
   }
   ```
   or (on error):
   ```json
   {
     "success": false,
     "error": "Error occurred while capturing screenshot: <error_message>"
   }
   ```

### List available tools

```python
# For code operations tools
codespace_tools = toolkit.get_tools()
for tool in codespace_tools:
    print(f"Tool: {tool.name}")
    print(f"Description: {tool.description}")

# For browser operations tools
browser_tools = browser_toolkit.get_tools()
for tool in browser_tools:
    print(f"Tool: {tool.name}")
    print(f"Description: {tool.description}")
```

### Use within an agent

You can use the toolkit with a LangChain agent. Here are examples for both CODESPACE and BROWSERUSE modes:

#### Code Operations Mode (CODESPACE)

```python
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import os

# Initialize LLM
llm = ChatOpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    model=os.getenv("DASHSCOPE_MODEL", "qwen3-max")
)

# Create prompt for code operations
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful assistant with access to AgentBay tools that can write files, read files, execute code, and execute commands.
    
Available tools:
1. write_file - Write content to a file in the AgentBay session. Supports 'overwrite' and 'append' modes.
2. read_file - Read content from a file in the AgentBay session.
3. run_code - Execute code in the AgentBay session. Supported languages are: python, javascript.
4. execute_command - Execute a shell command in the AgentBay session

Use these tools to help the user accomplish their tasks. When using write_file, you can specify the mode parameter to either overwrite (default) or append to a file. When appending content, make sure to include newline characters if needed to separate lines."""),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

# Create agent
agent = create_tool_calling_agent(llm, toolkit.get_tools(), prompt)
agent_executor = AgentExecutor(agent=agent, tools=toolkit.get_tools(), verbose=True)

# Example usage for code operations
example_query = """Write a Python file '/tmp/script.py' with content 'print("Hello from Python!")
print("AgentBay integration successful!")
' using default mode.
Then run the Python code in that file using the run_code tool.
Next, write a file '/tmp/demo.txt' with content 'First line
' using default mode.
Then append a second line 'Second line
' to the same file using append mode.
After that, read the file '/tmp/demo.txt' to verify its content.
Finally, execute command 'cat /tmp/demo.txt' to show the file content."""

result = agent_executor.invoke({"input": example_query})
print(f"Final result: {result['output']}")
```

#### Browser Automation Mode (BROWSERUSE)

```python
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import os

# Initialize LLM
llm = ChatOpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    model=os.getenv("DASHSCOPE_MODEL", "qwen3-max")
)

# Create prompt for browser operations
browser_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful assistant with access to AgentBay browser tools that can automate web browsing tasks.
    
Available tools:
1. browser_navigate - Navigate to a URL in the AgentBay session. Optional: set extract_content=True to enable content extraction (disabled by default for performance).
2. browser_act - Perform actions on browser pages in the AgentBay session. You can open URLs, click buttons, fill forms, etc. Optional: set extract_content=True to enable content extraction (disabled by default for performance).
3. screenshot - Take a screenshot of the current browser page in the AgentBay session.

Use these tools to help the user accomplish their web browsing tasks. When using browser_act, provide clear actions like:
- "Navigate to https://www.example.com"
- "Click the login button"
- "Enter 'search term' in the search box"
- "Click the search button"

Always be specific about what element you want to interact with."""), 
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

# Create browser agent
browser_agent = create_tool_calling_agent(llm, browser_toolkit.get_tools(), browser_prompt)
browser_agent_executor = AgentExecutor(agent=browser_agent, tools=browser_toolkit.get_tools(), verbose=True)

# Example usage for browser operations
browser_example_query = """
Navigate to https://www.baidu.com/.
Then take a screenshot of the page.
Then enter 'AgentBay官网' in the search box and click the search button.
Then take a screenshot of the search results page.
Then, click the first search result link.
Finally take a screenshot.
"""

browser_result = browser_agent_executor.invoke({"input": browser_example_query})
print(f"Final result: {browser_result['output']}")
```

