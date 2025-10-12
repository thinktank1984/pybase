# Chrome Testing Guide

## 🚨 CRITICAL POLICY: NO MOCKING ALLOWED 🚨

**This repository ONLY supports REAL Chrome integration tests via MCP Chrome DevTools.**

**Mock tests have been DELETED. This is repository policy.**

---

## Overview

This guide explains how to run REAL Chrome browser integration tests using the MCP Chrome DevTools integration.

## Test Types

### 1. Integration Tests ✅ (Always Active)

**File**: `runtime/tests.py`  
**Status**: ✅ **Passing**  
**Browser**: No (uses Emmett TestClient)

These are **real backend integration tests** that test:
- Database operations
- Authentication/authorization
- Session management
- REST API endpoints
- Form processing
- Business logic

**Run with**:
```bash
cd runtime
pytest tests.py --no-cov -v

# Or via Docker
docker compose -f docker/docker-compose.yaml exec runtime pytest tests.py -v
```

**Pros**:
- ✅ Fast (~3 seconds)
- ✅ Reliable and consistent
- ✅ No browser dependencies
- ✅ Tests backend logic thoroughly

**Cons**:
- ❌ Doesn't test actual UI rendering
- ❌ Doesn't test JavaScript interactions
- ❌ Doesn't test CSS styling
- ❌ Doesn't test browser compatibility

---

### 2. Real Chrome Tests ✅ (Requires Setup)

**Files**: 
- `runtime/test_ui_chrome_real.py`
- `runtime/chrome_integration_tests.py`
- `runtime/chrome_test_helpers.py`

**Status**: ✅ **REAL tests using actual Chrome browser**  
**Browser**: Yes (Chrome via MCP Chrome DevTools)

These are **REAL UI integration tests** that:
- Actually open Chrome browser
- Actually navigate to pages
- Actually click buttons and fill forms
- Actually take screenshots
- Actually monitor network requests
- Actually test responsive design

**Prerequisites:**
1. ✅ Chrome browser running on host machine
2. ✅ Application running at http://localhost:8081
3. ✅ MCP Chrome DevTools server available
4. ✅ Environment variable: `HAS_CHROME_MCP=true`

**Run with**:
```bash
# Start application first
cd runtime
emmett develop

# In another terminal, run Chrome tests
export HAS_CHROME_MCP=true
cd runtime
pytest test_ui_chrome_real.py -v -s

# Or via test runner
HAS_CHROME_MCP=true ./run_tests.sh --chrome
```

**Pros**:
- ✅ Tests actual UI rendering
- ✅ Tests real JavaScript execution
- ✅ Tests real CSS styling
- ✅ Tests browser compatibility
- ✅ Captures real screenshots
- ✅ Monitors real network requests
- ✅ Tests responsive design at multiple viewports

**Cons**:
- 🐌 Slower (~30+ seconds for full suite)
- 🔧 Requires Chrome browser setup
- 🌐 Requires app to be running
- 💻 Requires MCP Chrome DevTools

---

## What Happened to Mock Tests?

**🚨 Mock tests have been DELETED from this repository.**

### Files That Were Removed:
- ❌ `runtime/test_ui_chrome.py` (DELETED - mock tests)
- ❌ `runtime/ui_tests.py` (DELETED - mock tests)
- ❌ `runtime/demo_chrome_tests.py` (DELETED - referenced mocks)

### Why They Were Deleted:

This repository has a **ZERO-TOLERANCE POLICY** for mocking:

- ❌ **ILLEGAL:** Mock database calls
- ❌ **ILLEGAL:** Mock HTTP requests  
- ❌ **ILLEGAL:** Mock browser interactions
- ❌ **ILLEGAL:** Fake tests that always pass
- ❌ **ILLEGAL:** unittest.mock, pytest-mock, or any mocking libraries

**Mocking creates false confidence** - tests pass but real code fails.

**Real integration tests provide real confidence** - if tests pass, code actually works.

---

## Real Chrome Test Features

### What These Tests Actually Do:

1. **Homepage Testing**
   - Navigate to real homepage
   - Take real screenshot
   - Verify real DOM elements
   - Check real Tailwind CSS classes
   - Test real responsive layouts

2. **Form Testing**
   - Actually fill form fields
   - Actually click submit buttons
   - Actually wait for real navigation
   - Verify real database changes

3. **Authentication Testing**
   - Actually log in with real credentials
   - Actually create real sessions
   - Actually verify real session cookies
   - Actually test real logout

4. **Responsive Design Testing**
   - Actually resize browser window
   - Actually test at mobile (375px), tablet (768px), desktop (1920px)
   - Actually capture screenshots at each viewport
   - Verify real layout changes

5. **Network Monitoring**
   - Actually monitor real HTTP requests
   - Verify real API calls
   - Check real response status codes
   - Validate real response data

6. **Console Monitoring**
   - Actually check browser console
   - Catch real JavaScript errors
   - Monitor real console warnings
   - Verify clean console output

### Example Real Test:

```python
def test_login_real(chrome):
    """Test login with REAL Chrome browser"""
    # Actually navigate Chrome browser
    chrome.navigate("/auth/login")
    
    # Get REAL page snapshot
    snapshot = chrome.take_snapshot()
    
    # Find REAL form elements
    email_field = find_element_by_label(snapshot, "Email")
    password_field = find_element_by_label(snapshot, "Password")
    
    # Actually fill REAL form
    await mcp_chrome_devtools_fill(uid=email_field.uid, value="doc@emmettbrown.com")
    await mcp_chrome_devtools_fill(uid=password_field.uid, value="fluxcapacitor")
    
    # Actually click REAL submit button
    submit_button = find_element_by_text(snapshot, "Login")
    await mcp_chrome_devtools_click(uid=submit_button.uid)
    
    # Wait for REAL navigation
    await mcp_chrome_devtools_wait_for(text="Welcome")
    
    # Take REAL screenshot
    chrome.take_screenshot("login_success.png", full_page=True)
    
    # Verify REAL database session
    with db.connection():
        session = Session.where(lambda s: s.user_email == "doc@emmettbrown.com").first()
        assert session is not None  # REAL session was created!
```

**This is a REAL test** - it actually opens Chrome, fills forms, clicks buttons, and verifies database changes!

---

## Setup Instructions

### 1. Start the Application

```bash
# Terminal 1: Start app
cd runtime
emmett develop

# App should be running at http://localhost:8081
```

### 2. Ensure Chrome is Running

Make sure Chrome browser is running on your host machine.

### 3. Enable Chrome MCP

```bash
# Terminal 2: Set environment variable
export HAS_CHROME_MCP=true
```

### 4. Run Real Chrome Tests

```bash
# Run all Chrome tests
cd runtime
pytest test_ui_chrome_real.py -v -s

# Or use test runner
HAS_CHROME_MCP=true ./run_tests.sh --chrome

# Run specific test
pytest test_ui_chrome_real.py::TestHomepage::test_homepage_loads -v -s
```

### 5. View Screenshots

Real screenshots are saved to:
```
runtime/screenshots/
├── homepage_desktop.png
├── homepage_tablet.png
├── homepage_mobile.png
├── login_page.png
├── post_detail.png
└── ... more screenshots
```

---

## Chrome Test Options

### Run All Tests:
```bash
HAS_CHROME_MCP=true pytest test_ui_chrome_real.py -v -s
```

### Run Specific Test Class:
```bash
HAS_CHROME_MCP=true pytest test_ui_chrome_real.py::TestHomepage -v -s
```

### Run Single Test:
```bash
HAS_CHROME_MCP=true pytest test_ui_chrome_real.py::TestHomepage::test_homepage_loads -v -s
```

### Run with More Output:
```bash
HAS_CHROME_MCP=true pytest test_ui_chrome_real.py -vv -s
```

---

## What If Chrome Isn't Available?

**If prerequisites aren't met, Chrome tests are SKIPPED (not mocked):**

```bash
$ ./run_tests.sh --chrome

🌐 Running Chrome DevTools Tests...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ℹ️  Chrome MCP integration not enabled
⚠️  Skipping Chrome tests (NO MOCKING ALLOWED per repository policy)

   To enable REAL Chrome testing:
   1. Export environment variable: export HAS_CHROME_MCP=true
   2. Ensure Chrome browser is running on host
   3. Ensure app is running at http://localhost:8081
   4. Ensure MCP Chrome DevTools is available

   Then run: HAS_CHROME_MCP=true ./run_tests.sh --chrome

✅ Chrome tests skipped (prerequisites not met)
```

**This is correct behavior** - we skip tests we can't run, we don't mock them!

---

## MCP Chrome DevTools Tools

The following MCP tools are available for real browser testing:

### Navigation:
- `mcp_chrome-devtools_navigate_page(url)` - Navigate to URL
- `mcp_chrome-devtools_navigate_page_history(navigate)` - Back/forward

### Page Inspection:
- `mcp_chrome-devtools_take_snapshot()` - Get DOM snapshot with UIDs
- `mcp_chrome-devtools_take_screenshot(filePath, fullPage)` - Capture screenshot

### Interaction:
- `mcp_chrome-devtools_click(uid)` - Click element
- `mcp_chrome-devtools_fill(uid, value)` - Fill form field
- `mcp_chrome-devtools_fill_form(elements)` - Fill multiple fields
- `mcp_chrome-devtools_hover(uid)` - Hover over element

### Monitoring:
- `mcp_chrome-devtools_list_network_requests()` - Get network activity
- `mcp_chrome-devtools_list_console_messages()` - Get console logs
- `mcp_chrome-devtools_wait_for(text, timeout)` - Wait for content

### Browser Control:
- `mcp_chrome-devtools_resize_page(width, height)` - Resize viewport
- `mcp_chrome-devtools_list_pages()` - List open tabs
- `mcp_chrome-devtools_select_page(pageIdx)` - Switch tabs

See `runtime/chrome_test_helpers.py` for helper utilities that wrap these tools.

---

## Comparison: Integration vs Chrome Tests

| Feature | Integration Tests | Real Chrome Tests |
|---------|------------------|------------------|
| **Speed** | ⚡ Fast (3s) | 🐌 Slow (30s+) |
| **Setup** | ✅ None | 🔧 Chrome + App + MCP |
| **Backend** | ✅ Yes | ✅ Yes |
| **UI Rendering** | ❌ No | ✅ Yes |
| **JavaScript** | ❌ No | ✅ Yes |
| **CSS Styling** | ❌ No | ✅ Yes |
| **Screenshots** | ❌ No | ✅ Yes |
| **Network Monitoring** | ❌ No | ✅ Yes |
| **Responsive Design** | ❌ No | ✅ Yes |
| **Use Case** | Daily development | Pre-release UI validation |

---

## Best Practices

### When to Run Integration Tests:
- ✅ Every code change
- ✅ Before committing
- ✅ In CI/CD pipeline
- ✅ Daily development

### When to Run Chrome Tests:
- ✅ Before releases
- ✅ After UI changes
- ✅ After CSS changes
- ✅ For visual regression testing
- ✅ To capture screenshots
- ⚠️ Not in regular CI/CD (too slow)

### What NOT to Do:
- ❌ **NEVER** create mock tests
- ❌ **NEVER** fake browser interactions
- ❌ **NEVER** use unittest.mock for UI testing
- ❌ **NEVER** create tests that always pass without testing

---

## Troubleshooting

### Issue: "Chrome tests skipped"
**Solution:** Set `HAS_CHROME_MCP=true` and ensure Chrome is running

### Issue: "Connection refused to localhost:8081"
**Solution:** Start the application first: `cd runtime && emmett develop`

### Issue: "Element not found"
**Solution:** Take snapshot first, find element by UID, then interact

### Issue: "Tests are slow"
**Solution:** This is expected - real browser tests are slower. Use integration tests for daily development.

### Issue: "Where are the mock tests?"
**Solution:** They were DELETED. This repository doesn't allow mocking. Use real Chrome tests instead.

---

## Summary

✅ **Integration tests** (`tests.py`) - Fast, reliable, test backend  
✅ **Real Chrome tests** (`test_ui_chrome_real.py`) - Slow, comprehensive, test UI  
❌ **Mock tests** - DELETED per repository policy  

**Use integration tests for daily development.**  
**Use real Chrome tests before releases.**  
**Never create mock tests - they're illegal in this repository.**

---

**Status:** 📋 Real Tests Only  
**Last Updated:** 2025-10-12  
**Mock Tests:** DELETED (policy violation)  
**Real Chrome Tests:** Available with `HAS_CHROME_MCP=true`
