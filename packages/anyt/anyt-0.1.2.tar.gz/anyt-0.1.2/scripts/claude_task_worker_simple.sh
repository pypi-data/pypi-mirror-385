#!/bin/bash

# Simple Claude Task Worker - Interactive mode with manual approval
# Picks tasks, shows details, waits for user to complete, then marks done

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=== Claude Task Worker (Simple Mode) ===${NC}"
echo ""

# Check for tasks
echo "Checking for available tasks..."
SUGGEST_OUTPUT=$(uv run anyt task suggest --status todo 2>&1)

# Extract first task ID
TASK_ID=$(echo "$SUGGEST_OUTPUT" | grep -oE "^1\. [A-Z]+-[0-9]+" | grep -oE "[A-Z]+-[0-9]+" | head -1)

if [ -z "$TASK_ID" ]; then
    echo -e "${YELLOW}No tasks available.${NC}"
    exit 0
fi

echo -e "${GREEN}Found task: $TASK_ID${NC}"
echo ""

# Show task details
echo "=== Task Details ==="
uv run anyt task show "$TASK_ID"
echo ""

# Ask if user wants to work on this task
read -p "Do you want to work on this task? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Skipped task $TASK_ID"
    exit 0
fi

# Update status to inprogress
echo "Updating task status to 'inprogress'..."
uv run anyt task edit --status inprogress "$TASK_ID"
echo -e "${GREEN}✓ Task marked as in progress${NC}"

# Add note that Claude is starting to work on this
echo "Adding start note to task..."
uv run anyt task note "$TASK_ID" --message "🤖 Claude started working on this task"
echo ""

# Prepare Claude prompt
TASK_DETAILS=$(uv run anyt task show "$TASK_ID" 2>&1)

PROMPT="You are an AI assistant helping with task completion. Here is the task:

Task ID: $TASK_ID

$TASK_DETAILS

Please provide:
1. A summary of what needs to be done
2. Step-by-step approach to complete the task
3. Any code changes or specific actions required

Analyze this task and provide your recommendations."

# Call Claude to actually work on the task
echo "=== Calling Claude AI to work on task ==="
echo ""

CLAUDE_OUTPUT=""
if command -v claude &> /dev/null; then
    # Use Claude CLI in non-interactive mode
    echo "Executing task with Claude..."
    CLAUDE_OUTPUT=$(claude -p "$PROMPT" --dangerously-skip-permissions 2>&1)
    CLAUDE_EXIT_CODE=$?

    # Display Claude's output
    echo "$CLAUDE_OUTPUT"

    # Add note with Claude's work summary
    if [ $CLAUDE_EXIT_CODE -eq 0 ]; then
        echo ""
        echo "Adding completion note to task..."
        # Extract a summary from Claude's output (first 500 chars)
        SUMMARY=$(echo "$CLAUDE_OUTPUT" | head -c 500)
        uv run anyt task note "$TASK_ID" --message "✅ Claude completed work: $SUMMARY"
    else
        echo ""
        echo "Adding error note to task..."
        uv run anyt task note "$TASK_ID" --message "❌ Claude encountered an error during execution"
    fi
else
    echo -e "${YELLOW}Warning: claude CLI not found${NC}"
    echo ""
    echo "To use Claude AI, install claude CLI:"
    echo "  npm install -g @anthropic-ai/claude-code"
    echo ""
    echo "For now, please review the task and complete it manually."
fi

echo ""
echo "==========================="
echo ""

# Check for code changes and commit
if git rev-parse --git-dir > /dev/null 2>&1; then
    if ! git diff --quiet || ! git diff --cached --quiet; then
        echo "Code changes detected."
        read -p "Commit changes? (y/n): " -n 1 -r
        echo ""

        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "Committing changes..."
            git add -A

            TASK_TITLE=$(echo "$TASK_DETAILS" | grep "^Title:" | sed 's/^Title: //' | head -1 || echo "Task $TASK_ID")

            COMMIT_MSG="feat: ${TASK_ID} - ${TASK_TITLE}

Completed by Claude Task Worker
Task ID: ${TASK_ID}

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"

            git commit -m "$COMMIT_MSG"

            COMMIT_HASH=$(git rev-parse --short HEAD)
            echo -e "${GREEN}✓ Changes committed: $COMMIT_HASH${NC}"

            # Add note to task with commit hash
            uv run anyt task note "$TASK_ID" --message "📝 Committed changes: $COMMIT_HASH"
        fi
    else
        echo "No code changes to commit."
    fi
else
    echo "Not in a git repository, skipping commit."
fi

echo ""

# Ask if task is complete
read -p "Mark task as done? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    uv run anyt task done "$TASK_ID" --note "Completed by Claude Task Worker"
    echo -e "${GREEN}✓ Task $TASK_ID marked as done!${NC}"
else
    echo "Task $TASK_ID remains in progress."
    echo "You can mark it done later with: uv run anyt task done $TASK_ID"
fi
