#!/usr/bin/env python3
"""Test CodeCourt with OpenAI API."""

import asyncio

from codecourt.tools import parse_diff
from codecourt.agents import CodeReviewAgent

sample_diff = """diff --git a/src/auth.py b/src/auth.py
--- a/src/auth.py
+++ b/src/auth.py
@@ -15,7 +15,9 @@ def login(username, password):
     user = find_user(username)
     if user and check_password(password, user.hash):
-        return create_token(user)
+        token = create_token(user + 234)
+        print(f"User logged in: {user}")  # Debug logging
+        return token;
     return None
"""


async def test_openai():
    print("Testing with gpt-4o-mini...")
    print()
    
    # Parse the diff
    parsed = parse_diff(sample_diff)
    
    # Create agent with OpenAI
    agent = CodeReviewAgent(
        provider_name="openai",
        model="gpt-4o-mini"
    )
    
    print(f"Files: {parsed.changed_files}")
    print(f"Lines added: {parsed.total_additions}")
    print()
    
    # Run review
    print("Calling OpenAI API...")
    result = await agent.review(parsed)
    
    print()
    print("=" * 60)
    print("REVIEW RESULT")
    print("=" * 60)
    print(f"Approval: {result.approval.value}")
    print(f"Confidence: {result.confidence}")
    print(f"Summary: {result.summary}")
    print()
    
    if result.findings:
        print(f"Findings ({len(result.findings)}):")
        for i, finding in enumerate(result.findings, 1):
            print(f"\n  {i}. [{finding.severity.value.upper()}] {finding.category.value}")
            print(f"     File: {finding.file}:{finding.line}")
            print(f"     Issue: {finding.message}")
            if finding.suggestion:
                print(f"     Fix: {finding.suggestion}")
    else:
        print("No findings.")
    
    print()
    print("=" * 60)
    print("Test complete!")


asyncio.run(test_openai())
