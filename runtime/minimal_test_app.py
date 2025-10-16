#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minimal test app to isolate the server hanging issue.
"""

from emmett import App

# Create minimal app
app = App(__name__)

@app.route("/")
async def index():
    return "Hello World! Minimal test app is working."

@app.route("/test")
async def test():
    return "Test route works!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)