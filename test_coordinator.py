#!/usr/bin/env python3
"""Test the Coordinator with multiple agents."""

import asyncio

from codecourt.config import settings
from codecourt.tools import parse_diff
from codecourt.agents import Coordinator

# Sample diff with both style and security issues
SAMPLE_DIFF = """diff --git a/src/api.py b/src/api.py
--- a/src/api.py
+++ b/src/api.py
@@ -10,6 +10,20 @@ from flask import Flask, request
 
 app = Flask(__name__)
 
+API_KEY = "sk-secret-key-12345"  # Security: hardcoded secret
+
+@app.route("/user/<user_id>")
+def get_user(user_id):
+    # Style: no type hints
+    # Security: SQL injection
+    query = f"SELECT * FROM users WHERE id = {user_id}"
+    result = db.execute(query)
+    # Style: inconsistent return
+    if result:
+        return result
+    else:
+        return None
"""

print("=" * 60)
print("COORDINATOR TEST - Multi-Agent Review")
print("=" * 60)
print()
print("This runs BOTH CodeReviewer AND SecurityAgent in parallel,")
print("then combines their findings.")
print()


async def test_coordinator():
    parsed = parse_diff(SAMPLE_DIFF)
    
    print(f"Files: {parsed.changed_files}")
    print(f"Lines added: {parsed.total_additions}")
    print()

    # Determine provider (checks .env file)
    if settings.openai_api_key:
        print("Using OpenAI (gpt-4o-mini) - key loaded from .env")
        coordinator = Coordinator.with_default_agents(
            provider_name="openai",
            model="gpt-4o-mini"
        )
    else:
        print("Using Ollama (local)...")
        print("(Add OPENAI_API_KEY to .env for better results)")
        coordinator = Coordinator.with_default_agents(provider_name="ollama")

    print(f"Agents: {coordinator.agent_names}")
    print(f"Parallel mode: {coordinator.parallel}")
    print()
    print("🔍 Running coordinated review...")
    print()

    result = await coordinator.review(parsed)

    print("=" * 60)
    print("COORDINATED REVIEW RESULTS")
    print("=" * 60)
    print()
    print(f"Total agents: {result.total_agents}")
    print(f"Agents approving: {result.agents_approving}")
    print(f"Agents requesting changes: {result.agents_requesting_changes}")
    print()
    print(f"Overall approval: {result.approval.value}")
    print(f"Average confidence: {result.confidence:.2f}")
    print()
    print(f"Summary: {result.summary}")
    print()

    # Show per-agent results
    print("-" * 60)
    print("Per-Agent Results:")
    print("-" * 60)
    for agent_name, agent_result in result.agent_results.items():
        print(f"\n📋 {agent_name}:")
        print(f"   Approval: {agent_result.approval.value}")
        print(f"   Findings: {len(agent_result.findings)}")
        print(f"   Summary: {agent_result.summary[:100]}...")

    # Show combined findings
    print()
    print("-" * 60)
    print(f"Combined Findings ({len(result.findings)} total, deduplicated):")
    print("-" * 60)

    if result.findings:
        for i, finding in enumerate(result.findings, 1):
            severity_icon = {
                "critical": "🔴",
                "error": "🟠",
                "warning": "🟡",
                "info": "🔵",
                "praise": "🟢",
            }.get(finding.severity.value, "⚪")

            print(f"\n{severity_icon} {i}. [{finding.severity.value.upper()}] {finding.category.value}")
            print(f"   File: {finding.file}:{finding.line}")
            print(f"   Issue: {finding.message}")
            if finding.suggestion:
                print(f"   Fix: {finding.suggestion}")
    else:
        print("\nNo findings (agents may not have returned valid JSON)")

    print()
    print("=" * 60)
    print("✓ Coordinated review complete!")
    print("=" * 60)


asyncio.run(test_coordinator())
