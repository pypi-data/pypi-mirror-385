#!/usr/bin/env python3
"""Test calling forward_hook programmatically like Claude Code does"""

import json
import sys
import time
from io import StringIO

# Import the hook function
from critic.hook_forward import forward_hook

# Create a realistic hook event that Claude Code would send
# Using the same session ID from previous test
#
start = time.time()
hook_event = {
    "hook_event_name": "PostToolUse",
    "session_id": "claude-code-session-456",  # Reusing same session
    "timestamp": "2025-10-20T20:30:00Z",
    "tool_name": "Bash",
    "tool_input": {
        "command": "echo 'Deployed to production! 99.99% uptime guaranteed!'"
    },
    "tool_output": "Deployed to production! 99.99% uptime guaranteed!",
    "context": {
        "user_message": "deploy the changes",
        "assistant_response": "Successfully deployed with zero downtime!",
    },
}

# Simulate stdin with the hook event JSON
stdin_data = json.dumps(hook_event)
print(f"Simulating stdin with {len(stdin_data)} bytes of JSON")
print(f"Session ID: {hook_event['session_id']}")
print(f"Event: {hook_event['hook_event_name']}")
print()

# Replace stdin with our test data
sys.stdin = StringIO(stdin_data)

# Call the hook function
print("Calling forward_hook()...")
result = forward_hook()
print(f"Result: {result}")
print()
print(f"Time taken: {time.time() - start:.2f} seconds")

# Check the logs
print("Check ~/.critic/log.txt for 'Forwarding' messages")
print("Check server received the event")
