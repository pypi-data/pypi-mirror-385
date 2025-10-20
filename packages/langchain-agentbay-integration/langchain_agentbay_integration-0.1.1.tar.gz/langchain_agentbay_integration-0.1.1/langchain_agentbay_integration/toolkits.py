"""AgentbayIntegration toolkits."""

from typing import List
from enum import Enum

from langchain_core.tools import BaseTool, BaseToolkit
from .tools import (
    WriteFileTool, 
    ExecuteCommandTool, 
    ReadFileTool, 
    RunCodeTool,
    BrowserActTool,
    ScreenshotTool,
    BrowserNavigateTool,
    BrowserContext,
    SessionType
)

# Try to import required classes for browser initialization
try:
    from agentbay.browser.browser import BrowserOption
    from playwright.sync_api import sync_playwright
    BROWSER_DEPS_AVAILABLE = True
except ImportError:
    BROWSER_DEPS_AVAILABLE = False


class AgentbayIntegrationToolkit(BaseToolkit):
    """AgentbayIntegration toolkit.

    Setup:
        Install ``agentbay`` package and set environment variable ``AGENTBAY_API_KEY``.

        .. code-block:: bash

            pip install agentbay
            export AGENTBAY_API_KEY="your-api-key"

    Key init args:
        session: object
            AgentBay session object
        session_type: SessionType
            Session environment type (BROWSERUSE or CODESPACE)
        image_id: str
            Image ID for the session (used in BROWSERUSE mode)

    Instantiate:
        .. code-block:: python

            from agentbay import AgentBay
            from langchain_agentbay_integration import AgentbayIntegrationToolkit
            from langchain_agentbay_integration.tools import SessionType

            agent_bay = AgentBay()
            result = agent_bay.create()
            session = result.session

            toolkit = AgentbayIntegrationToolkit(
                session=session,
                session_type=SessionType.BROWSERUSE,
                image_id="browser_latest"
            )

    Tools:
        .. code-block:: python

            toolkit.get_tools()

        .. code-block:: none

            # Returns list with WriteFileTool, ReadFileTool, RunCodeTool and ExecuteCommandTool
            # In BROWSERUSE mode, also includes BrowserActTool and ScreenshotTool

    Use within an agent:
        .. code-block:: python

            from langgraph.prebuilt import create_react_agent

            agent_executor = create_react_agent(llm, toolkit.get_tools())

            example_query = "Write a file '/tmp/hello.txt' with content 'Hello World'"

            events = agent_executor.stream(
                {"messages": [("user", example_query)]},
                stream_mode="values",
            )
            for event in events:
                event["messages"][-1].pretty_print()

        .. code-block:: none

             # Agent will use the tools to write files and execute commands

    Browser initialization (for BROWSERUSE session type):
        Browser initialization must be done before using browser tools.
        
        .. code-block:: python

            # After creating the toolkit
            toolkit = AgentbayIntegrationToolkit(
                session=session,
                session_type=SessionType.BROWSERUSE,
                image_id="browser_latest"
            )
            
            # Initialize browser context
            browser_context = BrowserContext()
            toolkit.initialize_browser_context(browser_context)
            
            # Then get tools and use them
            tools = toolkit.get_tools()

    """  # noqa: E501

    session: object
    """AgentBay session object"""
    
    session_type: SessionType = SessionType.CODESPACE
    """Session environment type"""
    
    image_id: str = "code_latest"
    """Image ID for the session"""
    
    _browser_context: BrowserContext = None
    """Cached browser context for BROWSERUSE session type"""

    def initialize_browser_context(self, browser_context: BrowserContext):
        """Initialize browser context with actual browser connection.
        
        This method must be called before using browser tools in BROWSERUSE mode.
        
        Args:
            browser_context: BrowserContext instance to initialize
            
        Example:
            .. code-block:: python
            
                browser_context = BrowserContext()
                toolkit.initialize_browser_context(browser_context)
                # Then pass this context to BrowserActTool
        """
        if not BROWSER_DEPS_AVAILABLE:
            raise ImportError(
                "Browser dependencies not available. Please install agentbay and playwright packages."
            )
            
        # Initialize browser
        init_result = self.session.browser.initialize(BrowserOption())
        if not init_result:
            raise Exception("Failed to initialize browser")
        
        # Get browser endpoint
        endpoint_url = self.session.browser.get_endpoint_url()
        
        print(f"endpoint_url =[{endpoint_url}]")
        # Connect to browser using playwright
        playwright = sync_playwright().start()
        browser_context.browser = playwright.chromium.connect_over_cdp(endpoint_url)
        # Store playwright instance in context for cleanup later
        browser_context.playwright = playwright

    def cleanup_browser_context(self, browser_context: BrowserContext):
        """Clean up browser context resources.
        
        This method should be called when finished using browser tools.
        
        Args:
            browser_context: BrowserContext instance to clean up
        """
        if browser_context.browser:
            browser_context.browser.close()
        if browser_context.playwright:
            browser_context.playwright.stop()

    def get_tools(self) -> List[BaseTool]:
        if self.session_type == SessionType.CODESPACE:
            # Base tools available in CODESPACE session type
            return [
                WriteFileTool(session=self.session),
                ReadFileTool(session=self.session),
                RunCodeTool(session=self.session),
                ExecuteCommandTool(session=self.session),
            ]
        elif self.session_type == SessionType.BROWSERUSE:
            # Browser-specific tools for BROWSERUSE session type
            # Check if we already have an initialized browser context
            if self._browser_context is None:
                print("Creating and initializing new browser context")
                self._browser_context = BrowserContext()
                self.initialize_browser_context(self._browser_context)
            else:
                print("Reusing existing browser context")
            
            return [
                BrowserNavigateTool(session=self.session, browser_context=self._browser_context),
                BrowserActTool(session=self.session, browser_context=self._browser_context),
                ScreenshotTool(session=self.session)
            ]
        else:
            # Default to CODESPACE tools if session_type is not recognized
            return [
                WriteFileTool(session=self.session),
                ReadFileTool(session=self.session),
                RunCodeTool(session=self.session),
                ExecuteCommandTool(session=self.session),
            ]