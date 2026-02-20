# clickup-cli

CLI tool for managing ClickUp tasks.

## Installation

```bash
uv sync
```

## Setup

```bash
cl config init
```

You will be prompted for your ClickUp API token and workspace.

## Commands

### Config

```bash
# Initialize configuration (API token + workspace)
cl config init

# Show current configuration
cl config show
```

### Aliases

Aliases let you save named shortcuts for space, folder, and list IDs so you don't have to remember raw IDs.

```bash
# Set an alias for a space
cl alias set dev -s 12345

# Set an alias for a folder
cl alias set backend -f 67890

# Set an alias for a list
cl alias set sprint42 -l 11111

# List all aliases
cl alias list

# Remove an alias
cl alias remove dev
```

### Spaces

```bash
# List all spaces in the workspace
cl space list
```

### Folders

```bash
# List folders in a space (interactive space selection)
cl folder list

# List folders in a specific space
cl folder list -s 12345

# List folders using an alias
cl folder list -s @dev
```

### Lists

```bash
# List lists (interactive space/folder selection)
cl list list

# List lists in a folder
cl list list -f 67890

# List folderless lists in a space
cl list list -s 12345

# Using aliases
cl list list -f @backend
cl list list -s @dev
```

### Tasks

```bash
# List tasks in a list
cl task list -l 11111

# List tasks using an alias
cl task list -l @sprint42

# Filter tasks by status
cl task list -l @sprint42 -s "in progress"

# Filter tasks by assignee
cl task list -l @sprint42 -a 12345678

# View a single task
cl task view TASK_ID

# Create a task
cl task create -l @sprint42 -n "Fix login bug"

# Create a task with all options
cl task create -l @sprint42 \
  -n "Fix login bug" \
  -d "Users can't log in with SSO" \
  -s "in progress" \
  -p 2 \
  -a 12345678 \
  -D 2025-06-01 \
  -t urgent \
  -t backend \
  -T 2h30m

cl task create -l @everything -n "Investigate Clickup API results" -d "Look for more data Clickup API can provide" -a "Lester Tay"

# Update a task
cl task update TASK_ID -s "complete"

# Update a task with multiple fields
cl task update TASK_ID \
  -n "Updated title" \
  -p 1 \
  -a 12345678 \
  -T 1h

# Delete a task (with confirmation prompt)
cl task delete TASK_ID
```
