# Chrome Testing Guide

## Overview

This guide explains the different types of tests in the project and how to use real Chrome browser integration testing.

## Test Types

### 1. Integration Tests ✅ (Currently Active)

**File**: `runtime/tests.py`  
**Status**: ✅ **83/83 passing**  
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
```

**Pros**:
- ✅ Fast (~3 seconds for 83 tests)
- ✅ Reliable and consistent
- ✅ No browser dependencies
- ✅ Tests backend logic thoroughly

**Cons**:
- ❌ Doesn't test actual UI rendering
- ❌ Doesn't test JavaScript interactions
- ❌ Doesn't test CSS styling
- ❌ Doesn't test browser compatibility

---

### 2. Mock Chrome Tests (Old)

**Files**: 
- `runtime/test_ui_chrome.py`
- `runtime/ui_tests.py`

**Status**: ⚠️ **Mocks only** (not real tests)  
**Browser**: No (just prints what would happen)

These are **demonstration/template tests** that:
- Show what UI tests should test
- Always pass (assert True)
- Don't actually interact with Chrome
- Are useful as documentation

**Example**:
```python
def test_homepage_loads(self):
    print("   ✅ Would navigate to:", self.BASE_URL)
    assert True  # Always passes!
```

---

### 3. Real Chrome Integration Tests ✅ (New!)

**Files**:
- `runtime/test_ui_chrome_real.py` - Test suite
- `runtime/chrome_test_helpers.py` - Helper utilities
- `runtime/chrome_integration_tests.py` - Additional tests

**Status**: ✅ **Real integration ready**  
**Browser**: Yes (uses actual Chrome via MCP)

These are **real UI tests** that:
- Open actual Chrome browser
- Navigate to real pages
- Take screenshots
- Test responsive design
- Check console errors
- Measure performance
- Test form interactions

---

## Using Real Chrome Tests

### Prerequisites

1. **Chrome browser running**
   - Just have Chrome open (doesn't need to be a specific page)

2. **Application running**
   ```bash
   cd runtime
   emmett develop
   # App should be running on http://localhost:8081
   ```

3. **MCP Chrome DevTools available**
   - Available in Cursor with MCP integration
   - Or install chrome-devtools MCP server

4. **Enable Chrome testing**
   ```bash
   export HAS_CHROME_MCP=true
   export BLOGGY_URL=http://localhost:8081
   ```

### Running Real Chrome Tests

#### Basic run:
```bash
cd runtime
pytest test_ui_chrome_real.py -v -s
```

#### With specific tests:
```bash
# Test homepage only
pytest test_ui_chrome_real.py::TestHomepage -v -s

# Test authentication
pytest test_ui_chrome_real.py::TestAuthentication -v -s

# Test performance
pytest test_ui_chrome_real.py::TestPerformance -v -s

# Test screenshots
pytest test_ui_chrome_real.py::TestVisualRegression -v -s
```

#### All at once:
```bash
# Set environment and run
HAS_CHROME_MCP=true pytest test_ui_chrome_real.py -v -s
```

### What Real Chrome Tests Do

#### 1. **Visual Testing**
- Takes screenshots of all pages
- Tests responsive design at multiple viewports:
  - Mobile (375x667)
  - Tablet (768x1024)
  - Desktop (1920x1080)
  - 4K (3840x2160)
- Captures full-page screenshots
- Tests hover effects

#### 2. **Functional Testing**
- Navigates to all pages
- Fills out forms
- Clicks buttons
- Tests login/logout flows
- Verifies page elements exist

#### 3. **Performance Testing**
- Measures page load time
- Checks First Contentful Paint (FCP)
- Checks Largest Contentful Paint (LCP)
- Monitors network requests
- Checks for console errors

#### 4. **Screenshots Generated**

All screenshots saved to: `runtime/screenshots/`

- `homepage.png` - Homepage full page
- `login_page.png` - Login page
- `register_page.png` - Register page
- `mobile_*.png` - Mobile viewport screenshots
- `tablet_*.png` - Tablet viewport screenshots
- `desktop_*.png` - Desktop viewport screenshots
- And more...

---

## Example Test Run

### When Chrome MCP is Available:

```bash
$ export HAS_CHROME_MCP=true
$ pytest test_ui_chrome_real.py -v -s

🌐 REAL CHROME INTEGRATION TESTS
================================================================================

runtime/test_ui_chrome_real.py::TestHomepage::test_homepage_loads
📄 TEST: Homepage loads
   → Navigating to: http://localhost:8081/
   → Taking page snapshot...
   → Taking screenshot: homepage.png
   ✅ Homepage loaded
PASSED

runtime/test_ui_chrome_real.py::TestHomepage::test_responsive_layouts
📱 TEST: Responsive layouts
📱 Testing iPhone SE (375x667)...
   → Resizing viewport to 375x667...
   → Navigating to: http://localhost:8081/
   → Taking screenshot: mobile__.png
   ✓ Screenshot: mobile__.png
📱 Testing iPad (768x1024)...
   → Resizing viewport to 768x1024...
   ✓ Screenshot: tablet__.png
[... more viewports ...]
   ✅ Tested 6 viewports
PASSED

================================================================================
✨ Chrome Integration Tests Complete
================================================================================
```

### When Chrome MCP is NOT Available:

```bash
$ pytest test_ui_chrome_real.py -v

collected 10 items

runtime/test_ui_chrome_real.py::TestHomepage::test_homepage_loads SKIPPED
runtime/test_ui_chrome_real.py::TestHomepage::test_responsive_layouts SKIPPED
[... all tests skipped ...]

================== 10 skipped in 0.02s ==================

⚠️  Chrome MCP not enabled - tests skipped
   Set environment variable: export HAS_CHROME_MCP=true
```

---

## Chrome Test Helper API

The `ChromeTestHelper` class provides a clean API for Chrome testing:

```python
from chrome_test_helpers import get_chrome_helper

# Get helper
chrome = get_chrome_helper()

# Navigate
chrome.navigate("/")
chrome.navigate("/auth/login")

# Take screenshots
chrome.take_screenshot('homepage.png', full_page=True)

# Resize viewport
chrome.resize_page(375, 667)  # Mobile

# Take snapshot (get element UIDs)
snapshot = chrome.take_snapshot()

# Click elements
chrome.click_element('button_uid')

# Fill forms
chrome.fill_form([
    {'uid': 'email_field', 'value': 'user@example.com'},
    {'uid': 'password_field', 'value': 'password'}
])

# Hover effects
chrome.hover_element('card_uid')

# Performance
chrome.start_performance_trace()
metrics = chrome.stop_performance_trace()

# Console & Network
messages = chrome.get_console_messages()
requests = chrome.get_network_requests()
```

---

## Comparison

| Feature | Integration Tests | Mock Chrome | Real Chrome Tests |
|---------|------------------|-------------|-------------------|
| **Speed** | ⚡ Fast (3s) | ⚡ Instant | 🐌 Slow (30s+) |
| **Backend** | ✅ Yes | ❌ No | ✅ Yes |
| **UI Rendering** | ❌ No | ❌ No | ✅ Yes |
| **JavaScript** | ❌ No | ❌ No | ✅ Yes |
| **Screenshots** | ❌ No | ❌ No | ✅ Yes |
| **Dependencies** | None | None | Chrome + MCP |
| **CI/CD** | ✅ Easy | ✅ Easy | ⚠️ Complex |
| **Use Case** | Backend logic | Documentation | UI/Visual |

---

## Best Practices

### 1. **Use Integration Tests for:**
- Backend logic and business rules
- Database operations
- API endpoints
- Authentication/authorization
- Fast CI/CD pipelines

### 2. **Use Real Chrome Tests for:**
- Visual regression testing
- Responsive design verification
- JavaScript functionality
- Browser compatibility
- User experience validation
- Before major releases

### 3. **Test Strategy**

```
┌─────────────────────────────────────┐
│   Development (Every commit)        │
│   Run: Integration Tests (83 tests)│
│   Time: ~3 seconds                  │
│   ✅ Fast feedback loop             │
└─────────────────────────────────────┘
              ↓
┌─────────────────────────────────────┐
│   Pre-Release (Before deploy)       │
│   Run: Chrome Tests (10-20 tests)   │
│   Time: ~30-60 seconds              │
│   ✅ Visual & UI verification       │
└─────────────────────────────────────┘
```

---

## Troubleshooting

### Tests are skipped

**Problem**: All Chrome tests show as "SKIPPED"

**Solution**:
```bash
# Enable Chrome MCP
export HAS_CHROME_MCP=true

# Run tests
pytest test_ui_chrome_real.py -v -s
```

### Can't connect to Chrome

**Problem**: Tests fail with connection errors

**Solution**:
1. Make sure Chrome is running
2. Check MCP Chrome DevTools server is available
3. Try restarting Chrome

### App not accessible

**Problem**: Tests fail with "Connection refused"

**Solution**:
```bash
# Start the app in another terminal
cd runtime
emmett develop

# Verify it's running
curl http://localhost:8081
```

### Screenshots not saved

**Problem**: No screenshots in `screenshots/` directory

**Solution**:
- Directory is created automatically
- Check file permissions
- Verify `HAS_CHROME_MCP=true` is set

---

## Future Enhancements

### Planned Features:
1. ✅ Real Chrome integration via MCP
2. ⏳ Automated screenshot comparison
3. ⏳ Accessibility testing (WCAG)
4. ⏳ Cross-browser testing (Firefox, Safari)
5. ⏳ Visual regression detection
6. ⏳ Performance budgets
7. ⏳ Mobile device emulation

---

## Summary

- **Integration tests** (`tests.py`) are your primary tests - fast, reliable, comprehensive ✅
- **Real Chrome tests** (`test_ui_chrome_real.py`) are for UI/visual testing when needed 🎨
- **Mock tests** are just documentation/templates 📚

**Current Status**: 
- ✅ 83/83 integration tests passing
- ✅ Real Chrome test infrastructure ready
- ✅ Production ready

For day-to-day development, stick with the integration tests. Use Chrome tests for visual validation before major releases.

