# clickup-cli

CLI tool for managing ClickUp tasks.

## Installation

```bash
uv sync
```

## Setup

```bash
clickup config init
```

You will be prompted for your ClickUp API token and workspace.

## Commands

### Config

```bash
# Initialize configuration (API token + workspace)
clickup config init

# Show current configuration
clickup config show
```

### Aliases

Aliases let you save named shortcuts for space, folder, and list IDs so you don't have to remember raw IDs.

```bash
# Set an alias for a space
clickup alias set dev --space-id 12345

# Set an alias for a folder
clickup alias set backend --folder-id 67890

# Set an alias for a list
clickup alias set sprint42 --list-id 11111

# List all aliases
clickup alias list

# Remove an alias
clickup alias remove dev
```

### Spaces

```bash
# List all spaces in the workspace
clickup space list
```

### Folders

```bash
# List folders in a space (interactive space selection)
clickup folder list

# List folders in a specific space
clickup folder list --space-id 12345

# List folders using an alias
clickup folder list --space-id @dev
```

### Lists

```bash
# List lists (interactive space/folder selection)
clickup list list

# List lists in a folder
clickup list list --folder-id 67890

# List folderless lists in a space
clickup list list --space-id 12345

# Using aliases
clickup list list --folder-id @backend
clickup list list --space-id @dev
```

### Tasks

```bash
# List tasks in a list
clickup task list --list-id 11111

# List tasks using an alias
clickup task list --list-id @sprint42

# Filter tasks by status
clickup task list --list-id @sprint42 --status "in progress"

# Filter tasks by assignee
clickup task list --list-id @sprint42 --assignee 12345678

# View a single task
clickup task view TASK_ID

# Create a task
clickup task create --list-id @sprint42 --name "Fix login bug"

# Create a task with all options
clickup task create --list-id @sprint42 \
  --name "Fix login bug" \
  --description "Users can't log in with SSO" \
  --status "in progress" \
  --priority 2 \
  --assignee 12345678 \
  --due-date 2025-06-01 \
  --tag urgent \
  --tag backend

# Update a task
clickup task update TASK_ID --status "complete"

# Update a task with multiple fields
clickup task update TASK_ID \
  --name "Updated title" \
  --priority 1 \
  --assignee 12345678

# Delete a task (with confirmation prompt)
clickup task delete TASK_ID
```
