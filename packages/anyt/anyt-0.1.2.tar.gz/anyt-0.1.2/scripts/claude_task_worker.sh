#!/bin/bash

# Claude Task Worker
# Automatically picks tasks from AnyTask, uses Claude to work on them, and marks them done

set -e

# Configuration
POLL_INTERVAL=5  # seconds
LOG_FILE="claude_task_worker.log"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} ✓ $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} ✗ $1" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} ⚠ $1" | tee -a "$LOG_FILE"
}

# Extract task identifier from suggest output
# Expected format: "1. DE-3 - Subtitle AnyT in landing page [Priority: 0]"
get_first_task() {
    local suggest_output="$1"
    # Extract task identifier (e.g., DE-3) from the first recommended task
    echo "$suggest_output" | grep -oE "^1\. [A-Z]+-[0-9]+" | grep -oE "[A-Z]+-[0-9]+" | head -1
}

# Get task details
get_task_details() {
    local task_id="$1"
    uv run anyt task show "$task_id" 2>&1
}

# Call Claude to work on the task
# This function sends the task to Claude and gets the work done
work_on_task_with_claude() {
    local task_id="$1"
    local task_details="$2"

    log "Requesting Claude to work on task $task_id..."

    # Create a prompt for Claude
    local prompt="You are an AI assistant helping with task completion. Here is the task:

Task ID: $task_id

$task_details

Please complete this task by:
1. Analyzing what needs to be done
2. Making the necessary code changes or actions
3. Testing your changes if applicable
4. Providing a summary of what was completed

Work on this task now and make all necessary changes."

    # Call Claude CLI in non-interactive mode
    if command -v claude &> /dev/null; then
        log "Executing task with Claude CLI (non-interactive mode)..."
        claude -p "$prompt" --dangerously-skip-permissions 2>&1
        return $?
    else
        log_error "Claude CLI not found"
        log_error "Please install claude CLI: npm install -g @anthropic-ai/claude-code"
        return 1
    fi
}

# Git commit changes after task completion
git_commit_changes() {
    local task_id="$1"
    local task_title="$2"

    # Check if we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log_warning "Not in a git repository, skipping commit"
        return 0
    fi

    # Check if there are any changes to commit
    if git diff --quiet && git diff --cached --quiet; then
        log "No changes to commit"
        return 0
    fi

    log "Committing changes for task $task_id..."

    # Add all changes
    if git add -A >> "$LOG_FILE" 2>&1; then
        log "Staged all changes"
    else
        log_error "Failed to stage changes"
        return 1
    fi

    # Create commit message
    local commit_message="feat: ${task_id} - ${task_title}

Completed by Claude Task Worker
Task ID: ${task_id}

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"

    # Commit changes
    if git commit -m "$commit_message" >> "$LOG_FILE" 2>&1; then
        log_success "Committed changes"
        local commit_hash=$(git rev-parse --short HEAD)
        log "Commit hash: $commit_hash"

        # Add note to task with commit hash
        uv run anyt task note "$task_id" --message "📝 Committed changes: $commit_hash" >> "$LOG_FILE" 2>&1 || true
        return 0
    else
        log_error "Failed to commit changes"
        return 1
    fi
}

# Main task processing function
process_task() {
    local task_id="$1"

    log "Processing task: $task_id"

    # Get task details
    log "Fetching task details..."
    local task_details=$(get_task_details "$task_id")

    if [ $? -ne 0 ]; then
        log_error "Failed to fetch task details for $task_id"
        return 1
    fi

    # Extract task title for commit message
    local task_title=$(echo "$task_details" | grep "^Title:" | sed 's/^Title: //' | head -1 || echo "Task $task_id")

    # Update task status to in progress
    log "Updating task status to 'inprogress'..."
    if uv run anyt task edit --status inprogress "$task_id" >> "$LOG_FILE" 2>&1; then
        log_success "Task $task_id marked as in progress"
    else
        log_error "Failed to update task status to inprogress"
        return 1
    fi

    # Add note that Claude is starting to work on this
    log "Adding start note to task..."
    if uv run anyt task note "$task_id" --message "🤖 Claude started working on this task (automated worker)" >> "$LOG_FILE" 2>&1; then
        log "Start note added"
    else
        log_warning "Failed to add start note (non-critical)"
    fi

    # Work on the task with Claude
    log "Working on task with Claude..."
    local claude_response=$(work_on_task_with_claude "$task_id" "$task_details")
    local claude_exit_code=$?

    # Display Claude's response
    echo ""
    echo "=== Claude's Response ==="
    echo "$claude_response"
    echo "========================="
    echo ""

    # Add completion note
    if [ $claude_exit_code -eq 0 ]; then
        log "Adding completion note to task..."
        # Extract a summary from Claude's output (first 500 chars)
        local summary=$(echo "$claude_response" | head -c 500)
        if uv run anyt task note "$task_id" --message "✅ Claude completed work: $summary" >> "$LOG_FILE" 2>&1; then
            log "Completion note added"
        else
            log_warning "Failed to add completion note (non-critical)"
        fi
    else
        log_error "Claude failed to work on task $task_id"
        # Add error note
        if uv run anyt task note "$task_id" --message "❌ Claude encountered an error during execution" >> "$LOG_FILE" 2>&1; then
            log "Error note added to task"
        fi
        return 1
    fi

    # Git commit changes
    log "Checking for code changes to commit..."
    if git_commit_changes "$task_id" "$task_title"; then
        log_success "Code changes committed (if any)"
    else
        log_warning "Git commit failed or skipped"
    fi

    # Mark task as done
    log "Marking task as done..."
    if uv run anyt task done "$task_id" --note "Completed by Claude Task Worker" >> "$LOG_FILE" 2>&1; then
        log_success "Task $task_id completed and marked as done!"
    else
        log_error "Failed to mark task as done"
        return 1
    fi

    return 0
}

# Main loop
main() {
    log "Claude Task Worker started"
    log "Polling interval: ${POLL_INTERVAL}s"
    log "Log file: $LOG_FILE"
    echo ""

    # Check if claude CLI is available
    if ! command -v claude &> /dev/null; then
        log_error "Claude CLI not found"
        log_error "Please install claude CLI: npm install -g @anthropic-ai/claude-code"
        exit 1
    fi

    # Check if anyt CLI is available
    if ! command -v uv &> /dev/null; then
        log_error "uv command not found. Please install uv first."
        exit 1
    fi

    while true; do
        log "Checking for available tasks..."

        # Get task suggestions
        local suggest_output=$(uv run anyt task suggest --status todo 2>&1)

        # Check if there are any tasks
        if echo "$suggest_output" | grep -q "No tasks found" || echo "$suggest_output" | grep -q "Top 0 Recommended"; then
            log_warning "No tasks available. Waiting ${POLL_INTERVAL}s..."
        else
            # Extract first task
            local task_id=$(get_first_task "$suggest_output")

            if [ -n "$task_id" ]; then
                log_success "Found task: $task_id"

                # Process the task
                if process_task "$task_id"; then
                    log_success "Successfully completed task $task_id"
                    # Continue immediately to next task instead of waiting
                    continue
                else
                    log_error "Failed to process task $task_id"
                fi
            else
                log_warning "Could not extract task identifier from suggestions"
            fi
        fi

        # Wait before next poll
        sleep "$POLL_INTERVAL"
    done
}

# Handle Ctrl+C gracefully
trap 'echo ""; log "Shutting down Claude Task Worker..."; exit 0' INT TERM

# Run main loop
main
