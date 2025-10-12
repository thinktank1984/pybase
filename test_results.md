[0;34m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[0m
[0;34m🧪 Bloggy Test Runner[0m
[0;34m🐳 App tests in Docker | 💻 Chrome --headed on HOST[0m
[0;34m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[0m

[0;36m📋 Test Mode: Chrome DevTools Tests Only[0m
[0;36m📢 Verbosity: Verbose (-v)[0m
[0;36m👁️  Chrome Mode: Visible/Foreground (--headed)[0m


[1;33m🌐 Running Chrome DevTools Tests...[0m
[0;34m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[0m
[0;36m💻 Running on HOST (--headed mode for visible browser)[0m

[1;33m🧹 Cleaning screenshots directory...[0m
[0;32m✅ Removed 9 screenshot(s)[0m

[0;36m🌐 Running REAL Chrome integration tests via MCP...[0m
[0;36m   👁️  VISIBLE MODE: Running on HOST (not Docker)[0m
[0;36m   Chrome window will be visible during tests[0m
[0;36m   You can watch the tests interact with the browser in real-time![0m

[0;36m📡 Checking if app is accessible...[0m
[0;32m✅ App is running[0m

[0;36m💻 Running on HOST (not Docker) for visible browser[0m

[0;36m📝 Host Command: CHROME_HEADED=true /Users/ed.sharood2/code/pybase/venv/bin/pytest integration_tests/test_ui_chrome_real.py -v -s[0m

Warning: emmett-sentry not installed. Error tracking disabled.
✗ Error tracking unavailable: emmett-sentry not installed
✓ Prometheus metrics enabled at /metrics (pipeline-based)
✓ Prometheus metrics enabled at /metrics (pipeline integration)
✓ Metrics tracked automatically for all requests via pipeline
============================= test session starts ==============================
platform darwin -- Python 3.12.11, pytest-8.4.2, pluggy-1.6.0 -- /Users/ed.sharood2/code/pybase/venv/bin/python
cachedir: .pytest_cache
rootdir: /Users/ed.sharood2/code/pybase
plugins: base-url-2.1.0, playwright-0.7.1, cov-7.0.0
collecting ... collected 13 items

integration_tests/test_ui_chrome_real.py::TestHomepage::test_homepage_loads ✅ Patched Role.get_permissions() method
✅ Patched Post.can_edit() and Post.can_delete() methods
   🚀 Starting REAL Chrome browser (headless=False)...
   👁️  Running in HEADED mode (visible browser)
   ✅ REAL Chrome browser started

🌐 REAL Chrome browser started for http://localhost:8081
   → Navigating to: http://localhost:8081/

📄 TEST: Homepage loads
   → Taking page snapshot...
   → Taking screenshot: homepage.png
   ✓ Screenshot saved: /Users/ed.sharood2/code/pybase/integration_tests/../runtime/screenshots/homepage.png
   ✅ Homepage loaded
PASSED
integration_tests/test_ui_chrome_real.py::TestHomepage::test_navigation_present    → Navigating to: http://localhost:8081/

🧭 TEST: Navigation present
   → Taking page snapshot...
   → Taking screenshot: navigation.png
   ✓ Screenshot saved: /Users/ed.sharood2/code/pybase/integration_tests/../runtime/screenshots/navigation.png
   ✅ Navigation verified
PASSED
integration_tests/test_ui_chrome_real.py::TestHomepage::test_responsive_layouts    → Navigating to: http://localhost:8081/

📱 TEST: Responsive layouts

📱 Testing iPhone SE (375x667)...
   → Resizing viewport to 375x667...
   → Navigating to: http://localhost:8081/
   → Taking screenshot: mobile__.png
   ✓ Screenshot saved: /Users/ed.sharood2/code/pybase/integration_tests/../runtime/screenshots/mobile__.png
   ✓ Screenshot: mobile__.png

📱 Testing iPhone 11 Pro Max (414x896)...
   → Resizing viewport to 414x896...
   → Navigating to: http://localhost:8081/
   → Taking screenshot: mobile_large__.png
   ✓ Screenshot saved: /Users/ed.sharood2/code/pybase/integration_tests/../runtime/screenshots/mobile_large__.png
   ✓ Screenshot: mobile_large__.png

📱 Testing iPad (768x1024)...
   → Resizing viewport to 768x1024...
   → Navigating to: http://localhost:8081/
   → Taking screenshot: tablet__.png
   ✓ Screenshot saved: /Users/ed.sharood2/code/pybase/integration_tests/../runtime/screenshots/tablet__.png
   ✓ Screenshot: tablet__.png

📱 Testing iPad Landscape (1024x768)...
   → Resizing viewport to 1024x768...
   → Navigating to: http://localhost:8081/
   → Taking screenshot: tablet_landscape__.png
   ✓ Screenshot saved: /Users/ed.sharood2/code/pybase/integration_tests/../runtime/screenshots/tablet_landscape__.png
   ✓ Screenshot: tablet_landscape__.png

📱 Testing Desktop HD (1920x1080)...
   → Resizing viewport to 1920x1080...
   → Navigating to: http://localhost:8081/
   → Taking screenshot: desktop__.png
   ✓ Screenshot saved: /Users/ed.sharood2/code/pybase/integration_tests/../runtime/screenshots/desktop__.png
   ✓ Screenshot: desktop__.png

📱 Testing 4K Desktop (3840x2160)...
   → Resizing viewport to 3840x2160...
   → Navigating to: http://localhost:8081/
   → Taking screenshot: desktop_4k__.png
   ✓ Screenshot saved: /Users/ed.sharood2/code/pybase/integration_tests/../runtime/screenshots/desktop_4k__.png
   ✓ Screenshot: desktop_4k__.png
   ✅ Tested 6 viewports
PASSED
integration_tests/test_ui_chrome_real.py::TestAuthentication::test_login_page_loads 
🔐 TEST: Login page
   → Navigating to: http://localhost:8081/auth/login
   → Taking screenshot: login_page.png
   ✓ Screenshot saved: /Users/ed.sharood2/code/pybase/integration_tests/../runtime/screenshots/login_page.png
   ✅ Login page loaded
PASSED
integration_tests/test_ui_chrome_real.py::TestAuthentication::test_register_page_loads 
📝 TEST: Register page
   → Navigating to: http://localhost:8081/auth/register
   → Taking screenshot: register_page.png
   ✓ Screenshot saved: /Users/ed.sharood2/code/pybase/integration_tests/../runtime/screenshots/register_page.png
   ✅ Register page loaded
PASSED
integration_tests/test_ui_chrome_real.py::TestAuthentication::test_login_page_has_form 
🔑 TEST: Login form elements
   → Navigating to: http://localhost:8081/auth/login
   → Taking page snapshot...
   → Taking screenshot: login_form.png
   ✓ Screenshot saved: /Users/ed.sharood2/code/pybase/integration_tests/../runtime/screenshots/login_form.png
   ✅ Login form present
PASSED
integration_tests/test_ui_chrome_real.py::TestPerformance::test_console_errors    → Navigating to: http://localhost:8081/

🐛 TEST: Console errors
   → Fetching console messages...
   → Found 0 console messages
   ✅ Console checked
PASSED
integration_tests/test_ui_chrome_real.py::TestPerformance::test_network_requests    → Navigating to: http://localhost:8081/

🌐 TEST: Network requests
   → Fetching network requests...
   → Found 0 network requests
   ✅ Network checked
PASSED
integration_tests/test_ui_chrome_real.py::TestPerformance::test_page_performance 
⚡ TEST: Page performance
   → Starting performance trace...
   → Stopping performance trace...
   → Metrics collected
   ✅ Performance measured
PASSED
integration_tests/test_ui_chrome_real.py::TestVisualRegression::test_page_screenshots[homepage-/] 
📸 TEST: Screenshot homepage
   → Navigating to: http://localhost:8081/
   → Taking screenshot: homepage_full.png
   ✓ Screenshot saved: /Users/ed.sharood2/code/pybase/integration_tests/../runtime/screenshots/homepage_full.png
   ✅ Screenshot: homepage
PASSED
integration_tests/test_ui_chrome_real.py::TestVisualRegression::test_page_screenshots[login-/auth/login] 
📸 TEST: Screenshot login
   → Navigating to: http://localhost:8081/auth/login
   → Taking screenshot: login_full.png
   ✓ Screenshot saved: /Users/ed.sharood2/code/pybase/integration_tests/../runtime/screenshots/login_full.png
   ✅ Screenshot: login
PASSED
integration_tests/test_ui_chrome_real.py::TestVisualRegression::test_page_screenshots[register-/auth/register] 
📸 TEST: Screenshot register
   → Navigating to: http://localhost:8081/auth/register
   → Taking screenshot: register_full.png
   ✓ Screenshot saved: /Users/ed.sharood2/code/pybase/integration_tests/../runtime/screenshots/register_full.png
   ✅ Screenshot: register
PASSED
integration_tests/test_ui_chrome_real.py::TestVisualRegression::test_viewport_screenshots 
📱 TEST: Viewport screenshots

📱 Testing iPhone SE (375x667)...
   → Resizing viewport to 375x667...
   → Navigating to: http://localhost:8081/
   → Taking screenshot: mobile__.png
   ✓ Screenshot saved: /Users/ed.sharood2/code/pybase/integration_tests/../runtime/screenshots/mobile__.png
   ✓ Screenshot: mobile__.png

📱 Testing iPhone 11 Pro Max (414x896)...
   → Resizing viewport to 414x896...
   → Navigating to: http://localhost:8081/
   → Taking screenshot: mobile_large__.png
   ✓ Screenshot saved: /Users/ed.sharood2/code/pybase/integration_tests/../runtime/screenshots/mobile_large__.png
   ✓ Screenshot: mobile_large__.png

📱 Testing iPad (768x1024)...
   → Resizing viewport to 768x1024...
   → Navigating to: http://localhost:8081/
   → Taking screenshot: tablet__.png
   ✓ Screenshot saved: /Users/ed.sharood2/code/pybase/integration_tests/../runtime/screenshots/tablet__.png
   ✓ Screenshot: tablet__.png

📱 Testing iPad Landscape (1024x768)...
   → Resizing viewport to 1024x768...
   → Navigating to: http://localhost:8081/
   → Taking screenshot: tablet_landscape__.png
   ✓ Screenshot saved: /Users/ed.sharood2/code/pybase/integration_tests/../runtime/screenshots/tablet_landscape__.png
   ✓ Screenshot: tablet_landscape__.png

📱 Testing Desktop HD (1920x1080)...
   → Resizing viewport to 1920x1080...
   → Navigating to: http://localhost:8081/
   → Taking screenshot: desktop__.png
   ✓ Screenshot saved: /Users/ed.sharood2/code/pybase/integration_tests/../runtime/screenshots/desktop__.png
   ✓ Screenshot: desktop__.png

📱 Testing 4K Desktop (3840x2160)...
   → Resizing viewport to 3840x2160...
   → Navigating to: http://localhost:8081/
   → Taking screenshot: desktop_4k__.png
   ✓ Screenshot saved: /Users/ed.sharood2/code/pybase/integration_tests/../runtime/screenshots/desktop_4k__.png
   ✓ Screenshot: desktop_4k__.png
   → /: 6 screenshots

📱 Testing iPhone SE (375x667)...
   → Resizing viewport to 375x667...
   → Navigating to: http://localhost:8081/auth/login
   → Taking screenshot: mobile__auth_login.png
   ✓ Screenshot saved: /Users/ed.sharood2/code/pybase/integration_tests/../runtime/screenshots/mobile__auth_login.png
   ✓ Screenshot: mobile__auth_login.png

📱 Testing iPhone 11 Pro Max (414x896)...
   → Resizing viewport to 414x896...
   → Navigating to: http://localhost:8081/auth/login
   → Taking screenshot: mobile_large__auth_login.png
   ✓ Screenshot saved: /Users/ed.sharood2/code/pybase/integration_tests/../runtime/screenshots/mobile_large__auth_login.png
   ✓ Screenshot: mobile_large__auth_login.png

📱 Testing iPad (768x1024)...
   → Resizing viewport to 768x1024...
   → Navigating to: http://localhost:8081/auth/login
   → Taking screenshot: tablet__auth_login.png
   ✓ Screenshot saved: /Users/ed.sharood2/code/pybase/integration_tests/../runtime/screenshots/tablet__auth_login.png
   ✓ Screenshot: tablet__auth_login.png

📱 Testing iPad Landscape (1024x768)...
   → Resizing viewport to 1024x768...
   → Navigating to: http://localhost:8081/auth/login
   → Taking screenshot: tablet_landscape__auth_login.png
   ✓ Screenshot saved: /Users/ed.sharood2/code/pybase/integration_tests/../runtime/screenshots/tablet_landscape__auth_login.png
   ✓ Screenshot: tablet_landscape__auth_login.png

📱 Testing Desktop HD (1920x1080)...
   → Resizing viewport to 1920x1080...
   → Navigating to: http://localhost:8081/auth/login
   → Taking screenshot: desktop__auth_login.png
   ✓ Screenshot saved: /Users/ed.sharood2/code/pybase/integration_tests/../runtime/screenshots/desktop__auth_login.png
   ✓ Screenshot: desktop__auth_login.png

📱 Testing 4K Desktop (3840x2160)...
   → Resizing viewport to 3840x2160...
   → Navigating to: http://localhost:8081/auth/login
   → Taking screenshot: desktop_4k__auth_login.png
   ✓ Screenshot saved: /Users/ed.sharood2/code/pybase/integration_tests/../runtime/screenshots/desktop_4k__auth_login.png
   ✓ Screenshot: desktop_4k__auth_login.png
   → /auth/login: 6 screenshots
   ✅ Total screenshots: 12
PASSED   🛑 REAL Chrome browser closed

✨ REAL Chrome tests complete


============================= 13 passed in 25.03s ==============================

[0;32m✅ Chrome tests passed! (ran on HOST)[0m
[0;32m📸 Screenshots saved to: runtime/screenshots/[0m

[0;34m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[0m
[0;32m✅ All tests passed![0m
[0;34m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[0m
