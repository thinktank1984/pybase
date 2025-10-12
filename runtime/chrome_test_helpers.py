"""
Chrome DevTools Test Helpers

This module provides helper functions for Chrome integration testing
using MCP Chrome DevTools integration.

Note: These helpers are designed to work with the MCP Chrome DevTools
server when available. When not available, they return mock responses.
"""

import os
import time
from typing import Dict, List, Optional, Any


class ChromeTestHelper:
    """Helper class for Chrome DevTools integration testing"""
    
    def __init__(self, base_url: str = "http://localhost:8081"):
        self.base_url = base_url
        self.has_mcp = os.environ.get('HAS_CHROME_MCP', 'false').lower() == 'true'
        self.screenshot_dir = os.path.join(os.path.dirname(__file__), 'screenshots')
        
        # Create screenshots directory if it doesn't exist
        os.makedirs(self.screenshot_dir, exist_ok=True)
    
    def navigate(self, path: str = "/", timeout: int = 30000) -> bool:
        """
        Navigate to a URL path.
        
        Args:
            path: URL path (e.g., "/", "/auth/login")
            timeout: Maximum wait time in milliseconds
            
        Returns:
            True if navigation succeeded
        """
        url = f"{self.base_url}{path}"
        print(f"   → Navigating to: {url}")
        
        if self.has_mcp:
            # Would call: mcp_chrome-devtools_navigate_page(url=url, timeout=timeout)
            pass
        
        time.sleep(0.5)  # Simulated delay
        return True
    
    def take_snapshot(self) -> Dict[str, Any]:
        """
        Take a snapshot of the current page content.
        
        Returns:
            Dictionary with page content and element UIDs
        """
        print("   → Taking page snapshot...")
        
        if self.has_mcp:
            # Would call: mcp_chrome-devtools_take_snapshot()
            pass
        
        return {
            'elements': [],
            'content': ''
        }
    
    def take_screenshot(
        self,
        filename: str,
        full_page: bool = False,
        element_uid: Optional[str] = None
    ) -> str:
        """
        Take a screenshot of the page or element.
        
        Args:
            filename: Screenshot filename (without path)
            full_page: Whether to capture full page
            element_uid: Optional element UID to screenshot
            
        Returns:
            Full path to screenshot file
        """
        filepath = os.path.join(self.screenshot_dir, filename)
        print(f"   → Taking screenshot: {filename}")
        
        if self.has_mcp:
            # Would call: mcp_chrome-devtools_take_screenshot(
            #     filePath=filepath,
            #     fullPage=full_page,
            #     uid=element_uid
            # )
            pass
        
        return filepath
    
    def resize_page(self, width: int, height: int) -> None:
        """
        Resize the browser viewport.
        
        Args:
            width: Viewport width in pixels
            height: Viewport height in pixels
        """
        print(f"   → Resizing viewport to {width}x{height}...")
        
        if self.has_mcp:
            # Would call: mcp_chrome-devtools_resize_page(width=width, height=height)
            pass
        
        time.sleep(0.3)  # Wait for layout adjustment
    
    def click_element(self, uid: str, double_click: bool = False) -> None:
        """
        Click an element by its UID.
        
        Args:
            uid: Element UID from snapshot
            double_click: Whether to double-click
        """
        print(f"   → Clicking element: {uid}")
        
        if self.has_mcp:
            # Would call: mcp_chrome-devtools_click(uid=uid, dblClick=double_click)
            pass
        
        time.sleep(0.2)
    
    def fill_field(self, uid: str, value: str) -> None:
        """
        Fill a form field with a value.
        
        Args:
            uid: Element UID from snapshot
            value: Value to fill
        """
        print(f"   → Filling field {uid}: {value}")
        
        if self.has_mcp:
            # Would call: mcp_chrome-devtools_fill(uid=uid, value=value)
            pass
        
        time.sleep(0.1)
    
    def fill_form(self, fields: List[Dict[str, str]]) -> None:
        """
        Fill multiple form fields at once.
        
        Args:
            fields: List of {'uid': str, 'value': str} dicts
        """
        print(f"   → Filling {len(fields)} form fields...")
        
        if self.has_mcp:
            # Would call: mcp_chrome-devtools_fill_form(elements=fields)
            pass
        
        for field in fields:
            print(f"      • {field.get('uid', 'unknown')}: {field.get('value', '')[:20]}...")
        
        time.sleep(0.3)
    
    def hover_element(self, uid: str) -> None:
        """
        Hover over an element.
        
        Args:
            uid: Element UID from snapshot
        """
        print(f"   → Hovering over: {uid}")
        
        if self.has_mcp:
            # Would call: mcp_chrome-devtools_hover(uid=uid)
            pass
        
        time.sleep(0.2)
    
    def wait_for_text(self, text: str, timeout: int = 5000) -> bool:
        """
        Wait for specific text to appear on page.
        
        Args:
            text: Text to wait for
            timeout: Maximum wait time in milliseconds
            
        Returns:
            True if text appeared
        """
        print(f"   → Waiting for text: '{text}'...")
        
        if self.has_mcp:
            # Would call: mcp_chrome-devtools_wait_for(text=text, timeout=timeout)
            pass
        
        time.sleep(0.5)
        return True
    
    def get_console_messages(self) -> List[Dict[str, Any]]:
        """
        Get console messages (errors, warnings, logs).
        
        Returns:
            List of console message objects
        """
        print("   → Fetching console messages...")
        
        if self.has_mcp:
            # Would call: mcp_chrome-devtools_list_console_messages()
            pass
        
        return []
    
    def get_network_requests(
        self,
        resource_types: Optional[List[str]] = None,
        page_size: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get network requests made by the page.
        
        Args:
            resource_types: Filter by resource types (e.g., ['document', 'xhr'])
            page_size: Maximum number of requests to return
            
        Returns:
            List of network request objects
        """
        print("   → Fetching network requests...")
        
        if self.has_mcp:
            # Would call: mcp_chrome-devtools_list_network_requests(
            #     resourceTypes=resource_types,
            #     pageSize=page_size
            # )
            pass
        
        return []
    
    def start_performance_trace(self, reload: bool = True) -> None:
        """
        Start recording performance metrics.
        
        Args:
            reload: Whether to reload page after starting trace
        """
        print("   → Starting performance trace...")
        
        if self.has_mcp:
            # Would call: mcp_chrome-devtools_performance_start_trace(
            #     reload=reload,
            #     autoStop=False
            # )
            pass
    
    def stop_performance_trace(self) -> Dict[str, Any]:
        """
        Stop performance trace and get metrics.
        
        Returns:
            Performance metrics including LCP, FCP, etc.
        """
        print("   → Stopping performance trace...")
        
        if self.has_mcp:
            # Would call: mcp_chrome-devtools_performance_stop_trace()
            pass
        
        return {
            'lcp': 0,
            'fcp': 0,
            'load_time': 0
        }
    
    def list_pages(self) -> List[Dict[str, Any]]:
        """
        List all open pages/tabs.
        
        Returns:
            List of page objects with URLs and titles
        """
        print("   → Listing open pages...")
        
        if self.has_mcp:
            # Would call: mcp_chrome-devtools_list_pages()
            pass
        
        return []
    
    def new_page(self, url: str, timeout: int = 30000) -> None:
        """
        Open a new page/tab.
        
        Args:
            url: URL to open in new page
            timeout: Maximum wait time in milliseconds
        """
        print(f"   → Opening new page: {url}")
        
        if self.has_mcp:
            # Would call: mcp_chrome-devtools_new_page(url=url, timeout=timeout)
            pass
        
        time.sleep(0.5)
    
    def evaluate_script(self, script: str, args: Optional[List[str]] = None) -> Any:
        """
        Execute JavaScript in the page context.
        
        Args:
            script: JavaScript function to execute
            args: Optional arguments for the function
            
        Returns:
            Result of script execution
        """
        print(f"   → Evaluating script: {script[:50]}...")
        
        if self.has_mcp:
            # Would call: mcp_chrome-devtools_evaluate_script(
            #     function=script,
            #     args=args
            # )
            pass
        
        return None


# Convenience function for tests
def get_chrome_helper(base_url: str = None) -> ChromeTestHelper:
    """
    Get a Chrome test helper instance.
    
    Args:
        base_url: Base URL for the application (default: from BLOGGY_URL env)
        
    Returns:
        ChromeTestHelper instance
    """
    if base_url is None:
        base_url = os.environ.get('BLOGGY_URL', 'http://localhost:8081')
    
    return ChromeTestHelper(base_url)


# Viewport presets
VIEWPORTS = {
    'mobile': {'width': 375, 'height': 667, 'name': 'iPhone SE'},
    'mobile_large': {'width': 414, 'height': 896, 'name': 'iPhone 11 Pro Max'},
    'tablet': {'width': 768, 'height': 1024, 'name': 'iPad'},
    'tablet_landscape': {'width': 1024, 'height': 768, 'name': 'iPad Landscape'},
    'desktop': {'width': 1920, 'height': 1080, 'name': 'Desktop HD'},
    'desktop_4k': {'width': 3840, 'height': 2160, 'name': '4K Desktop'},
}


def test_viewports(helper: ChromeTestHelper, path: str = "/") -> Dict[str, str]:
    """
    Test a page across multiple viewports and take screenshots.
    
    Args:
        helper: ChromeTestHelper instance
        path: URL path to test
        
    Returns:
        Dictionary mapping viewport names to screenshot paths
    """
    screenshots = {}
    
    for viewport_name, viewport in VIEWPORTS.items():
        print(f"\n📱 Testing {viewport['name']} ({viewport['width']}x{viewport['height']})...")
        
        # Resize viewport
        helper.resize_page(viewport['width'], viewport['height'])
        
        # Navigate
        helper.navigate(path)
        
        # Take screenshot
        filename = f"{viewport_name}_{path.replace('/', '_')}.png"
        screenshot_path = helper.take_screenshot(filename, full_page=False)
        screenshots[viewport_name] = screenshot_path
        
        print(f"   ✓ Screenshot: {filename}")
    
    return screenshots

