# Quibbler


`quibbler` is a background agent that monitors your claude code actions and interrupts  customizable  
Independent AI monitoring for Claude Code agents. Critic watches your agent's work through hook events and provides quality feedback to prevent common mistakes.

## Installation

```bash
pip install critic
```

## Usage

### 1. Start the monitoring server

```bash
critic-server [port]
```

Default port is 8081.

### 2. Configure Claude Code hooks

Add to your Claude Code project configuration:

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "critic-hook {session_id} {source_path}"
          }
        ]
      }
    ],
    "UserPromptSubmit": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "critic-display"
          }
        ]
      }
    ]
  }
}
```

### 3. Work normally

Critic monitors in the background and writes feedback to `.critic-messages.txt` when it has observations. The feedback is displayed at the next user prompt.

## How it works

1. **critic-hook** forwards Claude Code hook events to the monitoring server
2. The server runs a monitoring agent that watches for quality issues
3. When issues are detected, the monitor writes feedback to `.critic-messages.txt`
4. **critic-display** shows the feedback to the agent on the next interaction

## Environment Variables

- `ANTHROPIC_API_KEY`: Required for the monitoring agent (same as Claude Code)
- `CRITIC_MONITOR_BASE`: Override server URL (default: `http://127.0.0.1:8081`)
- `CLAUDE_MONITOR_SKIP_FORWARD`: Set to `1` to disable hook forwarding

## License

MIT
