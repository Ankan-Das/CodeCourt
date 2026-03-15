#!/usr/bin/env python3
"""Test the Security Agent with a vulnerable code sample."""

import asyncio

from codecourt.config import settings
from codecourt.tools import parse_diff
from codecourt.agents import SecurityAgent

# Sample diff with INTENTIONAL security issues for testing
VULNERABLE_DIFF = """diff --git a/src/api.py b/src/api.py
--- a/src/api.py
+++ b/src/api.py
@@ -10,6 +10,25 @@ from flask import Flask, request
 
 app = Flask(__name__)
 
+# Database connection
+DB_PASSWORD = "super_secret_123"  # TODO: move to env
+
+@app.route("/user/<user_id>")
+def get_user(user_id):
+    # Get user from database
+    query = f"SELECT * FROM users WHERE id = {user_id}"
+    result = db.execute(query)
+    return jsonify(result)
+
+@app.route("/search")
+def search():
+    term = request.args.get("q")
+    return f"<h1>Results for: {term}</h1>"
+
+@app.route("/run")
+def run_command():
+    cmd = request.args.get("cmd")
+    output = os.system(cmd)
+    return str(output)
"""

print("=" * 60)
print("SECURITY AGENT TEST")
print("=" * 60)
print()
print("Testing with intentionally vulnerable code:")
print("  - Hardcoded password")
print("  - SQL injection")
print("  - XSS vulnerability")
print("  - Command injection")
print()


async def test_security_review():
    parsed = parse_diff(VULNERABLE_DIFF)
    
    print(f"Files: {parsed.changed_files}")
    print(f"Lines added: {parsed.total_additions}")
    print()

    # Determine which provider to use (checks .env file)
    if settings.openai_api_key:
        print("Using OpenAI (gpt-4o-mini) - key loaded from .env")
        agent = SecurityAgent(provider_name="openai", model="gpt-4o-mini")
    else:
        print("Using Ollama (local)...")
        print("(Add OPENAI_API_KEY to .env for better results)")
        agent = SecurityAgent(provider_name="ollama")

    print()
    print("🔍 Running security scan...")
    print()

    result = await agent.review(parsed)

    print("=" * 60)
    print("SECURITY SCAN RESULTS")
    print("=" * 60)
    print(f"Agent: {result.agent_name}")
    print(f"Approval: {result.approval.value}")
    print(f"Confidence: {result.confidence}")
    print()
    print(f"Summary: {result.summary}")
    print()

    if result.findings:
        print(f"🚨 Vulnerabilities Found: {len(result.findings)}")
        print("-" * 60)
        
        for i, finding in enumerate(result.findings, 1):
            severity_icon = {
                "critical": "🔴",
                "error": "🟠", 
                "warning": "🟡",
                "info": "🔵",
            }.get(finding.severity.value, "⚪")
            
            print(f"\n{severity_icon} Finding {i}: [{finding.severity.value.upper()}]")
            print(f"   File: {finding.file}:{finding.line}")
            print(f"   Issue: {finding.message}")
            if finding.suggestion:
                print(f"   Fix: {finding.suggestion}")
    else:
        print("✅ No security vulnerabilities found.")
        print("   (This is unexpected given the intentionally vulnerable code)")
        print("   Try using OpenAI for better detection.")

    print()
    print("=" * 60)


asyncio.run(test_security_review())
