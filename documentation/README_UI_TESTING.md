# Real UI Testing with Chrome DevTools MCP

## 🚨 CRITICAL POLICY: NO MOCKING ALLOWED 🚨

**This guide covers REAL Chrome browser integration testing only.**

**Mock tests have been DELETED from this repository per strict no-mocking policy.**

---

## Overview

This document describes how to run REAL UI integration tests using actual Chrome browser via MCP Chrome DevTools integration.

## Test Files

### `test_ui_chrome_real.py` ✅

**REAL Chrome DevTools integration tests:**
- Actually opens Chrome browser
- Actually navigates to pages
- Actually interacts with real DOM elements
- Actually fills forms and clicks buttons
- Actually takes screenshots
- Actually monitors network requests
- Actually tests responsive design

**Test Scenarios:**
- Homepage loading and layout
- Navigation bar interactions
- Form submissions (login, posts, comments)
- Responsive design (mobile, tablet, desktop)
- Network request monitoring
- Console error detection
- Screenshot capture
- Authentication flows

### `chrome_integration_tests.py` ✅

Additional real Chrome integration tests for specific features.

### `chrome_test_helpers.py` ✅

Helper utilities for Chrome testing:
- ChromeTestHelper class
- Viewport management
- Element finding utilities
- Screenshot capture utilities

---

## Running Real Chrome Tests

### Prerequisites

1. **Chrome browser** must be running on host machine
2. **Application** must be running at http://localhost:8081
3. **MCP Chrome DevTools** server must be available
4. **Environment variable** `HAS_CHROME_MCP=true` must be set

### Setup

```bash
# Terminal 1: Start the application
cd runtime
emmett develop
# App runs at http://localhost:8081

# Terminal 2: Run Chrome tests
export HAS_CHROME_MCP=true
cd runtime
pytest test_ui_chrome_real.py -v -s
```

### Using Test Runner

```bash
# Run Chrome tests via test runner
HAS_CHROME_MCP=true ./run_tests.sh --chrome

# Run with verbose output
HAS_CHROME_MCP=true ./run_tests.sh --chrome -v

# Run specific test
HAS_CHROME_MCP=true ./run_tests.sh --chrome -k test_homepage
```

### Test Options

```bash
# Run all real Chrome tests
HAS_CHROME_MCP=true pytest test_ui_chrome_real.py -v -s

# Run specific test class
HAS_CHROME_MCP=true pytest test_ui_chrome_real.py::TestHomepage -v -s

# Run single test
HAS_CHROME_MCP=true pytest test_ui_chrome_real.py::TestHomepage::test_homepage_loads -v

# Run with more detailed output
HAS_CHROME_MCP=true pytest test_ui_chrome_real.py -vv -s

# Stop on first failure
HAS_CHROME_MCP=true pytest test_ui_chrome_real.py -x -v -s
```

---

## What These Tests Actually Do

### Example: Real Login Test

```python
async def test_login_real_browser(chrome):
    """Test login with REAL Chrome browser"""
    # 1. Actually navigate Chrome to login page
    chrome.navigate("/auth/login")
    
    # 2. Get REAL page snapshot with UIDs
    snapshot = await mcp_chrome-devtools_take_snapshot()
    
    # 3. Find REAL form elements in DOM
    email_field = find_element_by_label(snapshot, "Email")
    password_field = find_element_by_label(snapshot, "Password")
    submit_button = find_element_by_text(snapshot, "Login")
    
    # 4. Actually fill REAL form fields
    await mcp_chrome-devtools_fill(uid=email_field.uid, value="doc@emmettbrown.com")
    await mcp_chrome-devtools_fill(uid=password_field.uid, value="fluxcapacitor")
    
    # 5. Actually click REAL submit button
    await mcp_chrome-devtools_click(uid=submit_button.uid)
    
    # 6. Actually wait for REAL page navigation
    await mcp_chrome-devtools_wait_for(text="Welcome", timeout=5000)
    
    # 7. Actually take REAL screenshot
    await mcp_chrome-devtools_take_screenshot(
        filePath="screenshots/login_success.png",
        fullPage=True
    )
    
    # 8. Verify REAL database state changed
    with db.connection():
        session = Session.where(lambda s: s.user_email == "doc@emmettbrown.com").first()
        assert session is not None
        assert session.user_id == 1
```

**This is a REAL test!** It actually:
- Opens Chrome
- Navigates to the page
- Fills the form
- Submits it
- Waits for response
- Takes a screenshot
- Verifies database changes

---

## Test Coverage

### Homepage Tests
- ✅ Homepage loads successfully
- ✅ Navigation bar displays correctly
- ✅ Post list or empty state renders
- ✅ Tailwind CSS classes are applied
- ✅ Responsive design works at all viewports

### Authentication Tests
- ✅ Login page loads and displays form
- ✅ Login form submission works
- ✅ Session is created in database
- ✅ Redirect after login
- ✅ Logout works correctly

### Post Tests
- ✅ Post creation form displays
- ✅ Post creation submits successfully
- ✅ Post detail page displays content
- ✅ Post list shows all posts
- ✅ Post content renders with Tailwind styles

### Responsive Design Tests
- ✅ Mobile layout (375px width)
- ✅ Tablet layout (768px width)
- ✅ Desktop layout (1920px width)
- ✅ Navigation adapts to viewport
- ✅ Content flows correctly at all sizes

### Network Tests
- ✅ All requests return 200/302
- ✅ Static files load correctly
- ✅ API endpoints respond properly
- ✅ No failed requests

### Console Tests
- ✅ No JavaScript errors
- ✅ No console warnings
- ✅ Clean console output

---

## Screenshots

Real screenshots are automatically saved to:
```
runtime/screenshots/
├── homepage_desktop.png
├── homepage_tablet.png
├── homepage_mobile.png
├── login_page.png
├── login_success.png
├── post_detail.png
├── post_creation.png
├── navigation_bar.png
└── ... more screenshots
```

### Viewing Screenshots

```bash
# Open screenshots directory
open runtime/screenshots/

# View specific screenshot
open runtime/screenshots/homepage_desktop.png
```

---

## MCP Chrome DevTools API

### Navigation
- `navigate_page(url)` - Navigate to URL
- `navigate_page_history(navigate)` - Go back/forward

### Page Inspection
- `take_snapshot()` - Get DOM snapshot with UIDs for all elements
- `take_screenshot(filePath, fullPage, format, quality)` - Capture screenshot

### Element Interaction
- `click(uid)` - Click element by UID
- `fill(uid, value)` - Fill form field by UID
- `fill_form(elements)` - Fill multiple fields at once
- `hover(uid)` - Hover over element
- `drag(from_uid, to_uid)` - Drag and drop

### Monitoring
- `list_network_requests()` - Get all network requests
- `get_network_request(url)` - Get specific request details
- `list_console_messages()` - Get console logs

### Browser Control
- `resize_page(width, height)` - Resize browser viewport
- `list_pages()` - List all open tabs
- `select_page(pageIdx)` - Switch to tab
- `new_page(url)` - Open new tab
- `close_page(pageIdx)` - Close tab

### Waiting
- `wait_for(text, timeout)` - Wait for text to appear

---

## Helper Utilities

### ChromeTestHelper Class

```python
from chrome_test_helpers import get_chrome_helper

chrome = get_chrome_helper()

# Navigate to page
chrome.navigate("/")
chrome.navigate("/auth/login")

# Take screenshots
chrome.take_screenshot("page.png")
chrome.take_screenshot("page.png", full_page=True)

# Get snapshot
snapshot = chrome.take_snapshot()

# Test responsive design
chrome.test_responsive_design("/", "homepage")
# Creates: homepage_mobile.png, homepage_tablet.png, homepage_desktop.png
```

### Finding Elements

```python
# Find element by label text
email_field = find_element_by_label(snapshot, "Email")

# Find element by text content
button = find_element_by_text(snapshot, "Login")

# Find element by ID
element = find_element_by_id(snapshot, "post-123")

# Use element UID
await mcp_chrome-devtools_fill(uid=email_field.uid, value="test@example.com")
```

---

## What If Chrome Isn't Available?

**If prerequisites aren't met, tests are SKIPPED (not mocked):**

```python
# In test_ui_chrome_real.py
HAS_CHROME_MCP = os.environ.get('HAS_CHROME_MCP', 'false').lower() == 'true'

pytestmark = pytest.mark.skipif(
    not HAS_CHROME_MCP,
    reason="Chrome MCP not available. Set HAS_CHROME_MCP=true to enable."
)
```

This means:
- ✅ Tests are **SKIPPED** if Chrome not available
- ❌ Tests are **NEVER MOCKED**
- ✅ No false confidence from fake tests
- ✅ Clear indication that UI wasn't tested

**Running without Chrome:**
```bash
$ ./run_tests.sh --chrome

🌐 Running Chrome DevTools Tests...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ℹ️  Chrome MCP integration not enabled
⚠️  Skipping Chrome tests (NO MOCKING ALLOWED per repository policy)

✅ Chrome tests skipped (prerequisites not met)
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: UI Tests

on: [push, pull_request]

jobs:
  ui-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Start Application
        run: docker compose -f docker/docker-compose.yaml up -d runtime
      
      - name: Run Integration Tests (Always)
        run: docker compose -f docker/docker-compose.yaml exec -T runtime pytest tests.py -v
      
      - name: Run Chrome Tests (Optional)
        if: env.HAS_CHROME_MCP == 'true'
        run: pytest test_ui_chrome_real.py -v -s
        env:
          HAS_CHROME_MCP: true
      
      - name: Upload Screenshots
        if: always()
        uses: actions/upload-artifact@v2
        with:
          name: screenshots
          path: runtime/screenshots/
      
      - name: Stop Application
        run: docker compose -f docker/docker-compose.yaml down
```

**Note:** Chrome tests are typically NOT run in CI because:
- They require Chrome browser setup
- They're slower than integration tests
- Integration tests provide sufficient coverage for CI

**Use Chrome tests locally before releases**, not in automated CI.

---

## Best Practices

### When to Use Real Chrome Tests:
- ✅ Before releases to verify UI works
- ✅ After CSS/styling changes
- ✅ After JavaScript changes
- ✅ To capture screenshots for documentation
- ✅ To test responsive design
- ✅ To test browser compatibility

### When to Use Integration Tests:
- ✅ Daily development
- ✅ Every code change
- ✅ In CI/CD pipeline
- ✅ Testing backend logic
- ✅ Testing API endpoints
- ✅ Testing database operations

### What NOT to Do:
- ❌ **ILLEGAL:** Create mock UI tests
- ❌ **ILLEGAL:** Fake browser interactions
- ❌ **ILLEGAL:** Use unittest.mock for UI testing
- ❌ **FORBIDDEN:** Tests that always pass without testing anything
- ❌ **FORBIDDEN:** Simulated DOM interactions

---

## Troubleshooting

### "Chrome MCP not available"
**Solution:** Set `export HAS_CHROME_MCP=true` and ensure Chrome is running

### "Connection refused to localhost:8081"
**Solution:** Start app first: `cd runtime && emmett develop`

### "Element not found with UID"
**Solution:** Take fresh snapshot before finding elements

### "Tests are slow"
**Solution:** This is expected. Real browser tests are slower. Use integration tests for speed.

### "Where are the mock tests?"
**Solution:** They were DELETED per repository policy. Use real Chrome tests or integration tests.

### "Screenshots not saved"
**Solution:** Ensure `screenshots/` directory exists in runtime/

---

## Deleted Files

### ❌ `ui_tests.py` (DELETED)
**Reason:** Mock tests that violated no-mocking policy  
**Replacement:** Use `test_ui_chrome_real.py` for real UI testing

### ❌ `test_ui_chrome.py` (DELETED)
**Reason:** Mock tests that always passed without testing  
**Replacement:** Use `test_ui_chrome_real.py` for real UI testing

### ❌ `demo_chrome_tests.py` (DELETED)
**Reason:** Referenced deleted mock tests  
**Replacement:** This guide and `chrome_test_helpers.py`

---

## Summary

✅ **Real Chrome Tests** (`test_ui_chrome_real.py`)
- Actually open Chrome
- Actually test UI
- Actually take screenshots
- Actually verify behavior

❌ **Mock Tests** (DELETED)
- Illegal per repository policy
- Created false confidence
- Always passed without testing
- Removed from codebase

**Use real Chrome tests for UI validation.**  
**Use integration tests for daily development.**  
**Never create mock tests - they're forbidden.**

---

**Status:** 📋 Real Tests Only  
**Last Updated:** 2025-10-12  
**Mock Tests:** DELETED (policy violation)  
**Real Chrome Tests:** Available with `HAS_CHROME_MCP=true`

