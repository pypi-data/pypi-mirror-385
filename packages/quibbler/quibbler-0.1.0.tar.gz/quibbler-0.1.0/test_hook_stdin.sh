#!/bin/bash
# Test if the hook command receives and forwards data correctly

echo "Testing hook forward with sample PostToolUse event..."

# Create a sample hook event JSON
cat <<'EOF' | uv run critic hook
{
  "hook_event_name": "PostToolUse",
  "session_id": "debug-test-session",
  "timestamp": "2025-10-20T20:10:00Z",
  "tool_name": "Bash",
  "tool_input": {"command": "echo 'test'"},
  "tool_output": "test"
}
EOF

echo ""
echo "Check ~/.critic/log.txt for forwarding logs"
echo "Check server logs for received event"
