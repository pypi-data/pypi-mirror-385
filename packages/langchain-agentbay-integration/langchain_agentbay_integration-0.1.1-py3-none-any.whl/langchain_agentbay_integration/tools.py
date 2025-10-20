"""AgentbayIntegration tools."""

import traceback
import asyncio
import json
from enum import Enum
from typing import Optional, Type, List, Dict, Any

from langchain_core.callbacks import (
    CallbackManagerForToolRun,
)
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

# Import ActOptions from agentbay
try:
    from agentbay.browser.browser_agent import ActOptions
    ACT_OPTIONS_AVAILABLE = True
except ImportError:
    ACT_OPTIONS_AVAILABLE = False
    # Create a mock ActOptions if the import fails
    class ActOptions:
        def __init__(self, action: str, context: Optional[Dict] = None):
            self.action = action
            self.context = context or {}
def get_page_infos(broswer: Any):
    contexts = broswer.contexts
    print(f"Contexts size:{len(contexts)}")
    context_index = -1
    all_infos = []
    for context in contexts:
        context_index += 1
        print(f"Context index: {context_index}") 
        pages = context.pages
        page_infos_list = []
        page_infos = {"context_index":context_index, "page_infos":page_infos_list}
        all_infos.append(page_infos) 
        i = -1
        for page in pages:
            i += 1
            now_item = {"page_index":i, "page_title":page.title(), "page_url":page.url}
            page_infos_list.append(now_item)
    return all_infos


def extract_page_content(session: Any) -> dict:
    """
    Extract page content using the browser agent.
    
    Args:
        session: AgentBay session object
        
    Returns:
        Dictionary containing extracted content or error information
    """
    try:
        from agentbay.browser.browser_agent import ExtractOptions
        from pydantic import BaseModel
        
        class ExtractSchema(BaseModel):
            title: str
            description: str
            urls: list[str]
            content: str
        
        extract_options = ExtractOptions(
            instruction="Extract the main content, title, description, and urls from the current page",
            schema=ExtractSchema
        )
        extract_success, extract_result = session.browser.agent.extract(extract_options)
        
        if extract_success:
            # Convert the Pydantic model to a dictionary
            return extract_result.model_dump()
        else:
            return {"error": "Extraction failed"}
    except Exception as extract_error:
        return {"error": f"Error occurred while extracting: {str(extract_error)}"}


class SessionType(Enum):
    """Session environment types."""
    CODESPACE = "codespace"
    BROWSERUSE = "browseruse"


class BrowserContext:
    """Context for sharing browser instances between tools."""
    
    def __init__(self):
        self.browser: Any = None
        self.playwright: Any = None


class WriteFileInput(BaseModel):
    """Input schema for writing file to AgentBay session."""

    path: str = Field(..., description="Path where to write the file")
    content: str = Field(..., description="Content to write to the file")
    mode: str = Field(default="overwrite", description="Write mode ('overwrite' or 'append')")


class WriteFileTool(BaseTool):  # type: ignore[override]
    """Tool for writing files in AgentBay session.

    Setup:
        Install ``agentbay`` package and set environment variable ``AGENTBAY_API_KEY``.

        .. code-block:: bash

            pip install wuying-agentbay-sdk
            export AGENTBAY_API_KEY="your-api-key"

    Instantiation:
        .. code-block:: python

            from agentbay import AgentBay
            from langchain_agentbay_integration.tools import WriteFileTool
            
            agent_bay = AgentBay()
            result = agent_bay.create()
            session = result.session

            tool = WriteFileTool(
                session=session
            )

    Invocation with args:
        .. code-block:: python

            tool.invoke({"path": "/tmp/test.txt", "content": "Hello World"})

        .. code-block:: python

            # Output: "File written successfully to /tmp/test.txt"

    """  # noqa: E501

    name: str = "write_file"
    """The name that is passed to the model when performing tool calling."""
    description: str = "Write content to a file in the AgentBay session"
    """The description that is passed to the model when performing tool calling."""
    args_schema: Type[BaseModel] = WriteFileInput
    """The schema that is passed to the model when performing tool calling."""

    session: object
    """AgentBay session object"""

    def _run(
        self, 
        path: str, 
        content: str, 
        mode: str = "overwrite",
        *, 
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Write content to a file in the AgentBay session."""
        try:     
            result = self.session.file_system.write_file(path, content, mode)
            if result.success:
                return f"File written successfully to {path} with mode '{mode}'"
            else:
                return f"Failed to write file: {result.error_message}"
        except Exception as e:
            return f"Error occurred while writing file: {str(e)}"

class ReadFileInput(BaseModel):
    """Input schema for reading file from AgentBay session."""

    path: str = Field(..., description="Path of the file to read")


class ReadFileTool(BaseTool):  # type: ignore[override]
    """Tool for reading files in AgentBay session.

    Setup:
        Install ``agentbay`` package and set environment variable ``AGENTBAY_API_KEY``.

        .. code-block:: bash

            pip install wuying-agentbay-sdk
            export AGENTBAY_API_KEY="your-api-key"

    Instantiation:
        .. code-block:: python

            from agentbay import AgentBay
            from langchain_agentbay_integration.tools import ReadFileTool
            
            agent_bay = AgentBay()
            result = agent_bay.create()
            session = result.session

            tool = ReadFileTool(
                session=session
            )

    Invocation with args:
        .. code-block:: python

            tool.invoke({"path": "/tmp/test.txt"})

        .. code-block:: python

            # Output: "File content:\\n<file_content>"

    """  # noqa: E501

    name: str = "read_file"
    """The name that is passed to the model when performing tool calling."""
    description: str = "Read content from a file in the AgentBay session"
    """The description that is passed to the model when performing tool calling."""
    args_schema: Type[BaseModel] = ReadFileInput
    """The schema that is passed to the model when performing tool calling."""

    session: object
    """AgentBay session object"""

    def _run(
        self, 
        path: str, 
        *, 
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Read content from a file in the AgentBay session."""
        try:
            result = self.session.file_system.read_file(path)
            if result.success:
                return f"File content:\n{result.content}"
            else:
                return f"Failed to read file: {result.error_message}"
        except Exception as e:
            return f"Error occurred while reading file: {str(e)}"


class RunCodeInput(BaseModel):
    """Input schema for running code in AgentBay session."""

    code: str = Field(..., description="The code to execute")
    language: str = Field(..., description="The programming language of the code. Supported languages are: 'python', 'javascript'")
    timeout_s: int = Field(default=60, description="The timeout for the code execution in seconds")


class RunCodeTool(BaseTool):  # type: ignore[override]
    """Tool for running code in AgentBay session.

    Setup:
        Install ``agentbay`` package and set environment variable ``AGENTBAY_API_KEY``.

        .. code-block:: bash

            pip install wuying-agentbay-sdk
            export AGENTBAY_API_KEY="your-api-key"

    Instantiation:
        .. code-block:: python

            from agentbay import AgentBay
            from langchain_agentbay_integration.tools import RunCodeTool
            
            agent_bay = AgentBay()
            result = agent_bay.create()
            session = result.session

            tool = RunCodeTool(
                session=session
            )

    Invocation with args:
        .. code-block:: python

            tool.invoke({"code": "print('Hello World')", "language": "python"})

        .. code-block:: python

            # Output: "Code execution result:\\n<code_output>"

    """  # noqa: E501

    name: str = "run_code"
    """The name that is passed to the model when performing tool calling."""
    description: str = "Execute code in the AgentBay session. Supported languages are: python, javascript. Note: Requires session created with code_latest image."
    """The description that is passed to the model when performing tool calling."""
    args_schema: Type[BaseModel] = RunCodeInput
    """The schema that is passed to the model when performing tool calling."""

    session: object
    """AgentBay session object"""

    def _run(
        self, 
        code: str, 
        language: str,
        timeout_s: int = 60,
        *, 
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Execute code in the AgentBay session."""
        try:
            # Use the direct run_code method from AgentBay SDK
            result = self.session.code.run_code(code, language, timeout_s)
            if result.success:
                return f"Code execution result:\n{result.result}\nRequest ID: {result.request_id}"
            else:
                return f"Code execution failed with error: {result.error_message}"
        except Exception as e:
            return f"Error occurred while executing code: {str(e)}"


class ExecuteCommandInput(BaseModel):
    """Input schema for executing command in AgentBay session."""

    command: str = Field(..., description="Shell command to execute")
    timeout_ms: int = Field(default=1000, description="Timeout for command execution in milliseconds")


class ExecuteCommandTool(BaseTool):  # type: ignore[override]
    """Tool for executing shell commands in AgentBay session.

    Setup:
        Install ``agentbay`` package and set environment variable ``AGENTBAY_API_KEY``.

        .. code-block:: bash

            pip install wuying-agentbay-sdk
            export AGENTBAY_API_KEY="your-api-key"

    Instantiation:
        .. code-block:: python

            from agentbay import AgentBay
            from langchain_agentbay_integration.tools import ExecuteCommandTool
            
            agent_bay = AgentBay()
            result = agent_bay.create()
            session = result.session

            tool = ExecuteCommandTool(
                session=session
            )

    Invocation with args:
        .. code-block:: python

            tool.invoke({"command": "ls -la", "timeout_ms": 1000})

        .. code-block:: python

            # Output: "Command output:\n<command_output>"

    """  # noqa: E501

    name: str = "execute_command"
    """The name that is passed to the model when performing tool calling."""
    description: str = "Execute a shell command in the AgentBay session"
    """The description that is passed to the model when performing tool calling."""
    args_schema: Type[BaseModel] = ExecuteCommandInput
    """The schema that is passed to the model when performing tool calling."""

    session: object
    """AgentBay session object"""

    def _run(
        self, 
        command: str, 
        timeout_ms: int = 1000,
        *, 
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Execute a shell command in the AgentBay session."""
        try:
            result = self.session.command.execute_command(command, timeout_ms)
            if result.success:
                return f"Command output:\n{result.output}"
            else:
                return f"Command failed with error: {result.error_message}"
        except Exception as e:
            return f"Error occurred while executing command: {str(e)}"


class BrowserActInput(BaseModel):
    """Input schema for browser action tool."""
    
    action: str = Field(..., description="Action to perform on the page")
    extract_content: bool = Field(default=False, description="Whether to extract page content after performing the action")


class BrowserActTool(BaseTool):
    """Tool for performing actions on browser pages in AgentBay session.

    Setup:
        Install ``agentbay`` package and set environment variable ``AGENTBAY_API_KEY``.

        .. code-block:: bash

            pip install wuying-agentbay-sdk
            export AGENTBAY_API_KEY="your-api-key"

    Instantiation:
        .. code-block:: python

            from agentbay import AgentBay
            from langchain_agentbay_integration.tools import BrowserActTool
            
            agent_bay = AgentBay()
            result = agent_bay.create()
            session = result.session

            # Initialize browser context
            browser_context = BrowserContext()
            
            tool = BrowserActTool(
                session=session,
                browser_context=browser_context
            )

    Invocation with args:
        .. code-block:: python

            tool.invoke({
                "action": "Click the login button",
                "extract_content": True
            })

        .. code-block:: python

            # Output: JSON string with action result

    """

    name: str = "browser_act"
    """The name that is passed to the model when performing tool calling."""
    description: str = "Perform an action on browser page in the AgentBay session"
    """The description that is passed to the model when performing tool calling."""
    args_schema: Type[BaseModel] = BrowserActInput
    """The schema that is passed to the model when performing tool calling."""

    session: object
    """AgentBay session object"""
    
    browser_context: BrowserContext
    """Browser context for sharing browser instances between tools"""

    def _run(
        self,
        action: str,
        extract_content: bool = False,
        *,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Perform an action on browser page in the AgentBay session."""
        try:
            # Check if browser is initialized
            if not self.browser_context.browser:
                return "Browser not initialized. Please initialize the browser context first."

            # Create ActOptions for the action
            act_options = ActOptions(action=action)
            
            # Use run_until_complete if there's an event loop, otherwise use asyncio.run
            try:
                loop = asyncio.get_running_loop()
                result = loop.run_until_complete(self.session.browser.agent.act_async(act_options))
            except RuntimeError:
                # No event loop running, use asyncio.run
                result = asyncio.run(self.session.browser.agent.act_async(act_options))
            
            # Call extract method to get page information only if extract_content is True
            extract_data = {}
            if extract_content:
                extract_data = extract_page_content(self.session)
          
            # Return result as JSON string
            result_dict = {
                "success": result.success,
                "message": result.message,
                "action": action
            }
            
            # Only add extract_results if extract_content is True
            if extract_content:
                result_dict["extract_results"] = extract_data
            
            result_json_str = json.dumps(result_dict, ensure_ascii=False)
            return result_json_str
        except Exception as e:
            return f"Error occurred while performing browser action: {str(e)}"

class BrowserNavigateInput(BaseModel):
    """Input schema for browser navigation tool."""
    
    url: str = Field(..., description="URL to navigate to")
    extract_content: bool = Field(default=False, description="Whether to extract page content after navigation")


class BrowserNavigateTool(BaseTool):
    """Tool for navigating to URLs in AgentBay session.

    Setup:
        Install ``agentbay`` package and set environment variable ``AGENTBAY_API_KEY``.

        .. code-block:: bash

            pip install wuying-agentbay-sdk
            export AGENTBAY_API_KEY="your-api-key"

    Instantiation:
        .. code-block:: python

            from agentbay import AgentBay
            from langchain_agentbay_integration.tools import BrowserNavigateTool
            
            agent_bay = AgentBay()
            result = agent_bay.create()
            session = result.session

            # Initialize browser context
            browser_context = BrowserContext()
            
            tool = BrowserNavigateTool(
                session=session,
                browser_context=browser_context
            )

    Invocation with args:
        .. code-block:: python

            tool.invoke({
                "url": "https://www.example.com",
                "extract_content": True
            })

        .. code-block:: python

            # Output: "Successfully navigated to https://www.example.com"

    """

    name: str = "browser_navigate"
    """The name that is passed to the model when performing tool calling."""
    description: str = "Navigate to a URL in the AgentBay session"
    """The description that is passed to the model when performing tool calling."""
    args_schema: Type[BaseModel] = BrowserNavigateInput
    """The schema that is passed to the model when performing tool calling."""

    session: object
    """AgentBay session object"""
    
    browser_context: BrowserContext
    """Browser context for sharing browser instances between tools"""

    def _run(
        self,
        url: str,
        extract_content: bool = False,
        *,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Navigate to a URL in the AgentBay session."""
        try:
            # Check if browser is initialized
            if not self.browser_context.browser:
                return "Browser not initialized. Please initialize the browser context first."

            # Handle nested event loop issue
            try:
                # Try to import and apply nest_asyncio to handle nested event loops
                import nest_asyncio
                nest_asyncio.apply()
            except ImportError:
                pass
            
            # Navigate to the URL using the AgentBay session browser agent
            now_agent = self.session.browser.agent
            # Use run_until_complete if there's an event loop, otherwise use asyncio.run
            try:
                loop = asyncio.get_running_loop()
                result = loop.run_until_complete(now_agent.navigate_async(url))
            except RuntimeError:
                # No event loop running, use asyncio.run
                result = asyncio.run(now_agent.navigate_async(url))

            # Call extract method to get page information only if extract_content is True
            extract_data = {}
            if extract_content:
                extract_data = extract_page_content(self.session)
            
            # Return result as JSON string
            result_dict = {
                "success": True,
                "message": f"Successfully navigated to {url}",
                "url": url
            }
            
            # Only add extract_results if extract_content is True
            if extract_content:
                result_dict["extract_results"] = extract_data
            
            result_json_str = json.dumps(result_dict, ensure_ascii=False)
            return result_json_str
        except Exception as e:
            traceback.print_exc()
            result_dict = {
                "success": False,
                "error": f"Error occurred while navigating to URL: {str(e)}"
            }
            return json.dumps(result_dict, ensure_ascii=False)

class ScreenshotInput(BaseModel):
    """Input schema for screenshot tool."""
    
    file_path: str = Field(..., description="File path to save the screenshot")
    
class ScreenshotTool(BaseTool):
    """Tool for taking screenshots of browser pages in AgentBay session.

    Setup:
        Install ``agentbay`` package and set environment variable ``AGENTBAY_API_KEY``.

        .. code-block:: bash

            pip install wuying-agentbay-sdk
            export AGENTBAY_API_KEY="your-api-key"

    Instantiation:
        .. code-block:: python

            from agentbay import AgentBay
            from langchain_agentbay_integration.tools import ScreenshotTool
            
            agent_bay = AgentBay()
            result = agent_bay.create()
            session = result.session

            tool = ScreenshotTool(
                session=session
            )

    Invocation with args:
        .. code-block:: python

            tool.invoke({})

        .. code-block:: python

            # Output: "Screenshot URL: <screenshot_url>"

    """

    name: str = "screenshot"
    """The name that is passed to the model when performing tool calling."""
    description: str = "Take a screenshot of the current browser page in the AgentBay session"
    """The description that is passed to the model when performing tool calling."""
    args_schema: Type[BaseModel] = ScreenshotInput
    """The schema that is passed to the model when performing tool calling."""

    session: object
    """AgentBay session object"""

    def _run(
        self,
        file_path: str,
        *,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Take a screenshot of the current browser page in the AgentBay session."""
        try:
            # Capture screenshot using browser agent
            screenshot_result = self.session.browser.agent.screenshot()
            if screenshot_result:
                import base64
                # Decode base64 string to bytes
                screenshot_data = base64.b64decode(screenshot_result.split(',')[1] if ',' in screenshot_result else screenshot_result)
                
                # Save to file
                with open(file_path, "wb") as f:
                    f.write(screenshot_data)
                
                # Return result as JSON string
                result_dict = {
                    "success": True,
                    "message": "Screenshot captured successfully",
                    "file_path": file_path
                }
                
                return json.dumps(result_dict, ensure_ascii=False)
            else:
                result_dict = {
                    "success": False,
                    "error": "Failed to capture screenshot"
                }
                return json.dumps(result_dict, ensure_ascii=False)
        except Exception as e:
            result_dict = {
                "success": False,
                "error": f"Error occurred while capturing screenshot: {str(e)}"
            }
            return json.dumps(result_dict, ensure_ascii=False)