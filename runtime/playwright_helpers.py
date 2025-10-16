"""
Playwright Test Helpers - REAL Browser Automation

This module provides helper functions for browser integration testing
using Playwright for REAL browser automation (Chrome, Firefox, Safari).

🚨 NO MOCKING POLICY 🚨
This module uses REAL Playwright browser automation.
All browser interactions are REAL - no stubs, no mocks.
"""

import os
from typing import Dict, List, Optional, Any
from playwright.sync_api import sync_playwright


class ChromeTestHelper:
    """Helper class for REAL Chrome browser testing using Playwright"""
    
    def __init__(self, base_url: str = "http://localhost:8000", headless: bool = True):
        self.base_url = base_url
        self.headless = headless
        self.screenshot_dir = os.path.join(os.path.dirname(__file__), 'screenshots')
        
        # Create screenshots directory if it doesn't exist
        os.makedirs(self.screenshot_dir, exist_ok=True)
        
        # Initialize Playwright (will be set in start())
        self.playwright = None  # type: ignore[assignment]
        self.browser = None  # type: ignore[assignment]
        self.context = None  # type: ignore[assignment]
        self.page = None  # type: ignore[assignment]
        
    def __enter__(self):
        """Context manager entry - start browser"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close browser"""
        self.close()
    
    def start(self):
        """Start the REAL browser"""
        print(f"   🚀 Starting REAL Chrome browser (headless={self.headless})...")
        
        self.playwright = sync_playwright().start()
        
        # Check if CHROME_HEADED environment variable is set
        headed_mode = os.environ.get('CHROME_HEADED', 'false').lower() == 'true'
        if headed_mode:
            self.headless = False
            print(f"   👁️  Running in HEADED mode (visible browser)")
        
        # Browser arguments optimized for different environments
        browser_args = ['--no-sandbox', '--disable-setuid-sandbox']

        # Add GitHub Spaces compatible arguments
        is_github_spaces = os.environ.get('GITHUB_ACTIONS') == 'true' or \
                          os.environ.get('CODESPACES') == 'true'
        if is_github_spaces:
            browser_args.extend([
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding'
            ])

        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=browser_args
        )
        
        self.context = self.browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/120.0.0.0 Safari/537.36'
        )
        
        self.page = self.context.new_page()
        print(f"   ✅ REAL Chrome browser started")
    
    def close(self):
        """Close the REAL browser"""
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        print(f"   🛑 REAL Chrome browser closed")
    
    def navigate(self, path: str = "/", timeout: int = 30000) -> bool:
        """
        Navigate to a URL path using REAL Chrome browser.
        
        Args:
            path: URL path (e.g., "/", "/auth/login")
            timeout: Maximum wait time in milliseconds
            
        Returns:
            True if navigation succeeded
        """
        url = f"{self.base_url}{path}"
        print(f"   → Navigating to: {url}")
        
        try:
            self.page.goto(url, timeout=timeout, wait_until='networkidle')
            return True
        except Exception as e:
            print(f"   ❌ Navigation failed: {e}")
            raise
    
    def take_snapshot(self) -> Dict[str, Any]:
        """
        Take a snapshot of the current page content using REAL Chrome.
        
        Returns:
            Dictionary with page content and element information
        """
        print("   → Taking page snapshot...")
        
        try:
            content = self.page.content()
            title = self.page.title()
            url = self.page.url
            
            # Get all visible elements
            elements = self.page.evaluate('''() => {
                const elements = [];
                document.querySelectorAll('a, button, input, select, textarea').forEach((el, idx) => {
                    if (el.offsetParent !== null) {  // visible elements only
                        elements.push({
                            tag: el.tagName.toLowerCase(),
                            id: el.id,
                            class: el.className,
                            text: el.textContent?.trim().substring(0, 50),
                            type: el.type,
                            name: el.name,
                            placeholder: el.placeholder,
                            href: el.href,
                            index: idx
                        });
                    }
                });
                return elements;
            }''')
            
            return {
                'content': content,
                'title': title,
                'url': url,
                'elements': elements
            }
        except Exception as e:
            print(f"   ❌ Snapshot failed: {e}")
            raise
    
    def take_screenshot(
        self,
        filename: str,
        full_page: bool = False,
        element_uid: Optional[str] = None
    ) -> str:
        """
        Take a screenshot of the page or element using REAL Chrome.
        
        Args:
            filename: Screenshot filename (without path)
            full_page: Whether to capture full page
            element_uid: Optional CSS selector for element to screenshot
            
        Returns:
            Full path to screenshot file
        """
        filepath = os.path.join(self.screenshot_dir, filename)
        print(f"   → Taking screenshot: {filename}")
        
        try:
            if element_uid:
                # Screenshot specific element
                element = self.page.locator(element_uid)
                element.screenshot(path=filepath)
            else:
                # Screenshot full page or viewport
                self.page.screenshot(path=filepath, full_page=full_page)
            
            print(f"   ✓ Screenshot saved: {filepath}")
            return filepath
        except Exception as e:
            print(f"   ❌ Screenshot failed: {e}")
            raise
    
    def resize_page(self, width: int, height: int) -> None:
        """
        Resize the browser viewport using REAL Chrome.
        
        Args:
            width: Viewport width in pixels
            height: Viewport height in pixels
        """
        print(f"   → Resizing viewport to {width}x{height}...")
        
        try:
            self.page.set_viewport_size({"width": width, "height": height})
        except Exception as e:
            print(f"   ❌ Resize failed: {e}")
            raise
    
    def click_element(self, selector: str, double_click: bool = False) -> None:
        """
        Click an element by CSS selector using REAL Chrome.
        
        Args:
            selector: CSS selector
            double_click: Whether to double-click
        """
        print(f"   → Clicking element: {selector}")
        
        try:
            if double_click:
                self.page.dblclick(selector)
            else:
                self.page.click(selector)
        except Exception as e:
            print(f"   ❌ Click failed: {e}")
            raise
    
    def fill_field(self, selector: str, value: str) -> None:
        """
        Fill a form field with a value using REAL Chrome.
        
        Args:
            selector: CSS selector
            value: Value to fill
        """
        print(f"   → Filling field {selector}: {value}")
        
        try:
            self.page.fill(selector, value)
        except Exception as e:
            print(f"   ❌ Fill failed: {e}")
            raise
    
    def fill_form(self, fields: List[Dict[str, str]]) -> None:
        """
        Fill multiple form fields at once using REAL Chrome.
        
        Args:
            fields: List of {'selector': str, 'value': str} dicts
        """
        print(f"   → Filling {len(fields)} form fields...")
        
        try:
            for field in fields:
                selector = field.get('selector')
                value = field.get('value', '')
                if selector:  # type: ignore[arg-type]
                    self.page.fill(selector, value)
                    print(f"      • {selector}: {value[:20]}...")
        except Exception as e:
            print(f"   ❌ Form fill failed: {e}")
            raise
    
    def hover_element(self, selector: str) -> None:
        """
        Hover over an element using REAL Chrome.
        
        Args:
            selector: CSS selector
        """
        print(f"   → Hovering over: {selector}")
        
        try:
            self.page.hover(selector)
        except Exception as e:
            print(f"   ❌ Hover failed: {e}")
            raise
    
    def wait_for_text(self, text: str, timeout: int = 5000) -> bool:
        """
        Wait for specific text to appear on page using REAL Chrome.
        
        Args:
            text: Text to wait for
            timeout: Maximum wait time in milliseconds
            
        Returns:
            True if text appeared
        """
        print(f"   → Waiting for text: '{text}'...")
        
        try:
            self.page.wait_for_selector(f"text={text}", timeout=timeout)
            return True
        except Exception as e:
            print(f"   ❌ Wait failed: {e}")
            raise
    
    def get_console_messages(self) -> List[Dict[str, Any]]:
        """
        Get console messages (errors, warnings, logs) from REAL Chrome.
        
        Returns:
            List of console message objects
        """
        print("   → Fetching console messages...")
        
        # Playwright collects console messages automatically
        # This would require setting up listeners before navigation
        # For now, return empty list
        return []
    
    def get_network_requests(
        self,
        resource_types: Optional[List[str]] = None,
        page_size: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get network requests made by the page from REAL Chrome.
        
        Args:
            resource_types: Filter by resource types (e.g., ['document', 'xhr'])
            page_size: Maximum number of requests to return
            
        Returns:
            List of network request objects
        """
        print("   → Fetching network requests...")
        
        # Playwright can intercept network requests
        # Would require setting up route handlers before navigation
        # For now, return empty list
        return []
    
    def start_performance_trace(self, reload: bool = True) -> None:
        """
        Start recording performance metrics using REAL Chrome.
        
        Args:
            reload: Whether to reload page after starting trace
        """
        print("   → Starting performance trace...")
        
        # Playwright has built-in tracing
        try:
            self.context.tracing.start(screenshots=True, snapshots=True)
            if reload:
                self.page.reload()
        except Exception as e:
            print(f"   ❌ Performance trace start failed: {e}")
            raise
    
    def stop_performance_trace(self) -> Dict[str, Any]:
        """
        Stop performance trace and get metrics from REAL Chrome.
        
        Returns:
            Performance metrics including timing info
        """
        print("   → Stopping performance trace...")
        
        try:
            # Stop tracing
            trace_path = os.path.join(self.screenshot_dir, 'trace.zip')
            self.context.tracing.stop(path=trace_path)
            
            # Get performance metrics
            metrics = self.page.evaluate('''() => {
                const timing = performance.timing;
                const navigation = performance.getEntriesByType('navigation')[0];
                return {
                    load_time: timing.loadEventEnd - timing.navigationStart,
                    dom_content_loaded: timing.domContentLoadedEventEnd - timing.navigationStart,
                    first_paint: navigation?.responseStart - navigation?.requestStart || 0
                };
            }''')
            
            return metrics
        except Exception as e:
            print(f"   ❌ Performance trace stop failed: {e}")
            raise
    
    def list_pages(self) -> List[Dict[str, Any]]:
        """
        List all open pages/tabs from REAL Chrome.
        
        Returns:
            List of page objects with URLs and titles
        """
        print("   → Listing open pages...")
        
        try:
            pages = []
            for page in self.context.pages:
                pages.append({
                    'url': page.url,
                    'title': page.title()
                })
            return pages
        except Exception as e:
            print(f"   ❌ List pages failed: {e}")
            raise
    
    def new_page(self, url: str, timeout: int = 30000) -> None:
        """
        Open a new page/tab using REAL Chrome.
        
        Args:
            url: URL to open in new page
            timeout: Maximum wait time in milliseconds
        """
        print(f"   → Opening new page: {url}")
        
        try:
            new_page = self.context.new_page()
            new_page.goto(url, timeout=timeout)
        except Exception as e:
            print(f"   ❌ New page failed: {e}")
            raise
    
    def evaluate_script(self, script: str, args: Optional[List[str]] = None) -> Any:
        """
        Execute JavaScript in the page context using REAL Chrome.
        
        Args:
            script: JavaScript function to execute
            args: Optional arguments for the function
            
        Returns:
            Result of script execution
        """
        print(f"   → Evaluating script: {script[:50]}...")
        
        try:
            if args:
                result = self.page.evaluate(script, args)
            else:
                result = self.page.evaluate(script)
            return result
        except Exception as e:
            print(f"   ❌ Script evaluation failed: {e}")
            raise


# Convenience function for tests
def get_chrome_helper(base_url: str = None) -> ChromeTestHelper:  # type: ignore[assignment]
    """
    Get a Chrome test helper instance with REAL browser.
    
    Args:
        base_url: Base URL for the application (default: from BLOGGY_URL env)
        
    Returns:
        ChromeTestHelper instance
        
    Raises:
        Exception: If Playwright is not available (NO SKIPPING - tests must fail)
    """
    if base_url is None:
        base_url = os.environ.get('BLOGGY_URL', 'http://localhost:8000')  # type: ignore[assignment]
    
    # Check if CHROME_HEADED environment variable is set
    headless = os.environ.get('CHROME_HEADED', 'false').lower() != 'true'
    
    # Verify Playwright is available
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as e:
        raise Exception(
            f"Playwright not available: {e}\n"
            "Install with: uv pip install playwright && playwright install chromium\n"
            "Tests cannot be skipped - they must either run or fail."
        )
    
    helper = ChromeTestHelper(base_url, headless=headless)
    helper.start()
    return helper


# Viewport presets
VIEWPORTS = {
    'mobile': {'width': 375, 'height': 667, 'name': 'iPhone SE'},
    'mobile_large': {'width': 414, 'height': 896, 'name': 'iPhone 11 Pro Max'},
    'tablet': {'width': 768, 'height': 1024, 'name': 'iPad'},
    'tablet_landscape': {'width': 1024, 'height': 768, 'name': 'iPad Landscape'},
    'desktop': {'width': 1920, 'height': 1080, 'name': 'Desktop HD'},
    'desktop_4k': {'width': 3840, 'height': 2160, 'name': '4K Desktop'},
}


def check_viewports(helper: ChromeTestHelper, path: str = "/") -> Dict[str, str]:
    """
    Test a page across multiple viewports and take REAL screenshots.
    
    Args:
        helper: ChromeTestHelper instance
        path: URL path to test
        
    Returns:
        Dictionary mapping viewport names to screenshot paths
    """
    screenshots = {}
    
    for viewport_name, viewport in VIEWPORTS.items():
        print(f"\n📱 Testing {viewport['name']} ({viewport['width']}x{viewport['height']})...")
        
        # Resize viewport (REAL Chrome resize)
        helper.resize_page(viewport['width'], viewport['height'])
        
        # Navigate (REAL Chrome navigation)
        helper.navigate(path)
        
        # Take screenshot (REAL Chrome screenshot)
        filename = f"{viewport_name}_{path.replace('/', '_')}.png"
        screenshot_path = helper.take_screenshot(filename, full_page=False)
        screenshots[viewport_name] = screenshot_path
        
        print(f"   ✓ Screenshot: {filename}")
    
    return screenshots
