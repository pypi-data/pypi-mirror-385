# Feature: Quibbler Learning & Rules System

## Goal
Allow the quibbler to learn from user feedback and establish project-specific rules that get enforced in future sessions.

## Architecture

### Prompt Hierarchy
- Global system prompt: `~/.quibbler/prompt.md` (existing)
- Project rules: `.quibbler/rules.md` (new, per-project)
- When loading prompt for a session, concatenate: `global + "\n\n# Project Rules\n\n" + rules`

### Rule Learning Flow
1. Quibbler detects user interaction with agent being monitored.
2. Quibbler adds a message to `.quibbler-{session_id}.txt` asking if the rejection should become a rule
3. User responds with yes/no in the file
4. If yes, quibbler writes the rule to `.quibbler/rules.md` and notifies the user
5. Next session automatically includes the rule

## Implementation Details

### 1. Prompt Loading (update `quibbler/prompts.py`)
- `load_prompt()` now also loads `.quibbler/rules.md` if it exists
- Concatenate: `prompt + "\n\n## Project-Specific Rules\n\n" + rules_content`
- remove old logic with loading .quibbler/prompt.md project specific to replace
- Return combined prompt

### 2. Rule Detection (`quibbler/agent.py` in `_run()`)
- pay attention in the session to user suggestions or rejections of agent changes that are representative of general rules
- Compare hash of sent message vs current file content to detect edits/deletions
- If changed, add a rule proposal to the file

### 3. Rule Proposal Format (append to feedback file)

you need to tell the model being monitored to ask the user
```
---

## Quibbler Proposal

I noticed you removed/modified my feedback. Would you like to establish this as a project rule?

**Proposed rule:**
[Extract the principle from the rejected feedback]
```

### 4. Rule Acceptance (monitor output file)

the monitor is prompted to do this
- Check for `@quibbler accept` command in feedback file 
- Parse the rule text and append to `.quibbler/rules.md`
- Remove the proposal from feedback file
- Log confirmation to user

## Files to Modify
1. `quibbler/prompts.py` - Update `load_prompt()` to include rules
2. `quibbler/agent.py` - Add rule detection and proposal logic in `_run()`
3. `quibbler/server.py` - Optional: add endpoint to manually manage rules

## Success Criteria
- Rules persist across sessions for a project
- User can reject feedback and have it become a rule
- Rules are included in system prompt automatically
- User has clear way to accept/reject proposals
- Rules can be manually edited
