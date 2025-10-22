# Welcome to Orchestra

Orchestra is a multi agent coding interface and workflow. Its goal is to allow you to focus on designing your software, delegating tasks to sub agents, and moving faster than you could otherwise.

There is one main designer thread, that you can interact with either via the window on the right or by modifying the designer.md file (which you can open via typing s). Discuss features, specs, or new functionality with it, and then it will spawn sub sessions that implement your spec.

You can easily jump into the sub agent execution by selecting them in the top left session pane, and then giving instructions, looking at diffs, and even using the p command to pair and stage their changes on your system to collaborate in real time. By default they are isolated in containers.


## The Three-Pane Layout

Cerb uses a three-pane interface in tmux:

- **Top Left Pane (Session List)**: Shows your designer session and all spawned executor agents. Use arrow keys or `j`/`k` to navigate, and press Enter to select a session and view its Claude conversation.

- **Bottom Left Pane (Spec Editor)**: Your collaboration workspace with the designer agent. This is where `designer.md` opens by default - use it to plan tasks, track progress, and communicate requirements before spawning executors. You can also use `t` to open a terminal of that session or `m` to open these docs.

- **Right Pane (Claude Session)**: Displays the active Claude conversation for the selected session. This is where you interact with the designer or watch executor agents work.

## Key Commands

These commands are all available when the top left pane is focused.

- **`s`**: Open the spec editor (`designer.md`) to plan and discuss tasks with the designer
- **`m`**: Open this documentation file
- **`p`**: Toggle pairing mode to share your screen with the active session
- **`t`**: Open a terminal in the selected session's work directory
- **`Ctrl+r`**: Refresh the session list
- **`Ctrl+d`**: Delete a selected executor session
- **`Ctrl+q`**: Quit Cerb

## Getting Started

You're all set! The designer agent is ready in the right pane. Start by describing what you'd like to build or improve, and the designer will help you plan and delegate the work.
