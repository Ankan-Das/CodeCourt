#!/usr/bin/env python3
"""Interactive test script for CodeCourt."""

import asyncio

# Test 1: Parse a diff
print("=" * 60)
print("TEST 1: Parsing a Git Diff")
print("=" * 60)

from codecourt.tools import parse_diff, format_diff_for_review

sample_diff = """diff --git a/src/auth.py b/src/auth.py
--- a/src/auth.py
+++ b/src/auth.py
@@ -15,7 +15,9 @@ def login(username, password):
     user = find_user(username)
     if user and check_password(password, user.hash):
-        return create_token(user)
+        token = create_token(user)
+        priiiiint(f"User logged in: {user}");  # Debug logging
+        return token
     return None
"""

parsed = parse_diff(sample_diff)

print(f"✓ Files changed: {parsed.changed_files}")
print(f"✓ Lines added: {parsed.total_additions}")
print(f"✓ Lines removed: {parsed.total_deletions}")
print(f"✓ Language detected: {parsed.files[0].language}")
print()

# Test 2: Format for LLM
print("=" * 60)
print("TEST 2: Formatted Diff (what the LLM sees)")
print("=" * 60)
formatted = format_diff_for_review(parsed)
print(formatted)
print()

# Test 3: Create an agent (without calling LLM)
print("=" * 60)
print("TEST 3: Creating Code Review Agent")
print("=" * 60)

from codecourt.agents import CodeReviewAgent
from codecourt.providers import list_providers

print(f"✓ Available providers: {list_providers()}")

# Create agent with Ollama (local, free)
agent = CodeReviewAgent(provider_name="ollama")
print(f"✓ Agent created: {agent.name}")
print(f"✓ Using provider: {agent.provider.name}")
print()

# Test 4: Test with Ollama (if running)
print("=" * 60)
print("TEST 4: Live Review (requires Ollama running)")
print("=" * 60)


async def test_live_review():
    """Test actual review with Ollama."""
    from codecourt.providers.ollama import OllamaProvider

    provider = OllamaProvider()

    # Check if Ollama is running
    if not await provider.is_available():
        print("⚠ Ollama is not running. To test live review:")
        print("  1. Install Ollama: brew install ollama")
        print("  2. Start Ollama: ollama serve")
        print("  3. Pull a model: ollama pull llama3")
        print("  4. Run this script again")
        return

    print("✓ Ollama is running!")

    # List available models
    models = await provider.list_models()
    print(f"✓ Available models: {models}")

    if not models:
        print("⚠ No models found. Pull one with: ollama pull llama3")
        return

    # Run actual review
    print("\n🔍 Running review (this may take 10-30 seconds)...")
    agent = CodeReviewAgent(provider_name="ollama", model=models[0].split(":")[0])
    result = await agent.review(parsed)

    print(f"\n✓ Review complete!")
    print(f"  Approval: {result.approval.value}")
    print(f"  Summary: {result.summary}")
    print(f"  Findings: {len(result.findings)}")

    for i, finding in enumerate(result.findings, 1):
        print(f"\n  Finding {i}:")
        print(f"    Severity: {finding.severity.value}")
        print(f"    Category: {finding.category.value}")
        print(f"    Message: {finding.message}")
        if finding.suggestion:
            print(f"    Suggestion: {finding.suggestion}")


# Run the async test
asyncio.run(test_live_review())

print()
print("=" * 60)
print("All basic tests completed!")
print("=" * 60)
