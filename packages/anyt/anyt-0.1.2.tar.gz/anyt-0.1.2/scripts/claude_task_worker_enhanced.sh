#!/bin/bash

# Claude Task Worker (Enhanced)
# Automatically picks tasks, uses Claude to work on them, commits changes,
# marks tasks done, and creates follow-up/blocking tasks with dependencies

set -e

# Configuration
POLL_INTERVAL=${POLL_INTERVAL:-5}  # seconds
LOG_FILE=${LOG_FILE:-"claude_task_worker.log"}
AUTO_COMMIT=${AUTO_COMMIT:-true}   # Automatically commit changes
COMMIT_PREFIX=${COMMIT_PREFIX:-"feat"}  # Git commit prefix (feat/fix/docs/etc)
CREATE_FOLLOWUP_TASKS=${CREATE_FOLLOWUP_TASKS:-true}  # Auto-create follow-up tasks

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging functions
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

log_info() {
    echo -e "${CYAN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} ℹ $1" | tee -a "$LOG_FILE"
}

# Extract task identifier from suggest output
# Expected format: "1. DE-3 - Subtitle AnyT in landing page [Priority: 0]"
get_first_task() {
    local suggest_output="$1"
    echo "$suggest_output" | grep -oE "^1\. [A-Z]+-[0-9]+" | grep -oE "[A-Z]+-[0-9]+" | head -1
}

# Get task details
get_task_details() {
    local task_id="$1"
    uv run anyt task show "$task_id" 2>&1
}

# Git commit changes
git_commit_changes() {
    local task_id="$1"
    local commit_message="$2"

    if [ "$AUTO_COMMIT" != "true" ]; then
        log_info "Auto-commit disabled, skipping git commit"
        return 0
    fi

    # Check if we're in a git repository
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log_warning "Not in a git repository, skipping commit"
        return 0
    fi

    # Check if there are any changes to commit
    if git diff --quiet && git diff --cached --quiet; then
        log_info "No changes to commit"
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
    local full_commit_message="${COMMIT_PREFIX}: ${task_id} - ${commit_message}

Completed by Claude Task Worker
Task ID: ${task_id}

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>"

    # Commit changes
    if git commit -m "$full_commit_message" >> "$LOG_FILE" 2>&1; then
        log_success "Committed changes: ${COMMIT_PREFIX}: ${task_id} - ${commit_message}"

        # Get commit hash
        local commit_hash=$(git rev-parse --short HEAD)
        log_info "Commit hash: $commit_hash"

        # Add note to task with commit hash
        uv run anyt task note "$task_id" --message "📝 Committed changes: $commit_hash" >> "$LOG_FILE" 2>&1 || true

        return 0
    else
        log_error "Failed to commit changes"
        return 1
    fi
}

# Parse Claude output for follow-up tasks
# Expected format in Claude's response:
# FOLLOW_UP_TASK: Title of follow-up task
# BLOCKING_TASK: Title of blocking task
parse_follow_up_tasks() {
    local claude_output="$1"
    local current_task_id="$2"

    if [ "$CREATE_FOLLOWUP_TASKS" != "true" ]; then
        return 0
    fi

    log_info "Checking for follow-up or blocking tasks..."

    # Extract follow-up tasks
    local followup_tasks=$(echo "$claude_output" | grep -i "^FOLLOW_UP_TASK:" | sed 's/^FOLLOW_UP_TASK: //' || true)

    # Extract blocking tasks
    local blocking_tasks=$(echo "$claude_output" | grep -i "^BLOCKING_TASK:" | sed 's/^BLOCKING_TASK: //' || true)

    # Create follow-up tasks (current task is dependency for these)
    if [ -n "$followup_tasks" ]; then
        while IFS= read -r task_title; do
            if [ -n "$task_title" ]; then
                log_info "Creating follow-up task: $task_title"

                # Create task with status=todo
                local new_task_output=$(uv run anyt task add "$task_title" --status todo --json 2>&1)
                local new_task_id=$(echo "$new_task_output" | grep -oE '"identifier":"[A-Z]+-[0-9]+"' | grep -oE '[A-Z]+-[0-9]+' | head -1)

                if [ -n "$new_task_id" ]; then
                    log_success "Created follow-up task: $new_task_id - $task_title"

                    # Add dependency: new task depends on current task
                    if uv run anyt task dep add "$new_task_id" --on "$current_task_id" >> "$LOG_FILE" 2>&1; then
                        log_success "Added dependency: $new_task_id depends on $current_task_id"

                        # Add note to original task
                        uv run anyt task note "$current_task_id" --message "📌 Created follow-up task: $new_task_id" >> "$LOG_FILE" 2>&1 || true
                    else
                        log_warning "Failed to add dependency for $new_task_id"
                    fi
                else
                    log_error "Failed to create follow-up task: $task_title"
                fi
            fi
        done <<< "$followup_tasks"
    fi

    # Create blocking tasks (current task depends on these)
    if [ -n "$blocking_tasks" ]; then
        while IFS= read -r task_title; do
            if [ -n "$task_title" ]; then
                log_info "Creating blocking task: $task_title"

                # Create task with high priority and status=todo
                local new_task_output=$(uv run anyt task add "$task_title" --status todo --priority 1 --json 2>&1)
                local new_task_id=$(echo "$new_task_output" | grep -oE '"identifier":"[A-Z]+-[0-9]+"' | grep -oE '[A-Z]+-[0-9]+' | head -1)

                if [ -n "$new_task_id" ]; then
                    log_success "Created blocking task: $new_task_id - $task_title"

                    # Add dependency: current task depends on new blocking task
                    # First, need to reopen current task if it was marked done
                    # For now, just add note
                    uv run anyt task note "$current_task_id" --message "🚧 Created blocking task: $new_task_id (needs to be completed first)" >> "$LOG_FILE" 2>&1 || true

                    log_warning "Note: Task $current_task_id may need to depend on $new_task_id (manual review required)"
                else
                    log_error "Failed to create blocking task: $task_title"
                fi
            fi
        done <<< "$blocking_tasks"
    fi
}

# Call Claude to work on the task
work_on_task_with_claude() {
    local task_id="$1"
    local task_details="$2"

    log "Requesting Claude to work on task $task_id..."

    # Create a comprehensive prompt for Claude
    local prompt="You are an AI assistant helping with task completion. Here is the task:

Task ID: $task_id

$task_details

Please complete this task by:
1. Analyzing what needs to be done
2. Making the necessary code changes or actions
3. Testing your changes if applicable
4. Committing your changes to git (if code changes were made)
5. Providing a summary of what was completed

If you identify follow-up tasks that should be created, include them in your response with this format:
FOLLOW_UP_TASK: Title of the follow-up task

If you identify blocking tasks (tasks that should have been completed first), include them with:
BLOCKING_TASK: Title of the blocking task

Work on this task now and make all necessary changes."

    # Call Claude CLI in non-interactive mode
    if command -v claude &> /dev/null; then
        log "Executing task with Claude CLI..."

        # Use --dangerously-skip-permissions for non-interactive execution
        claude -p "$prompt" --dangerously-skip-permissions 2>&1
        return $?
    else
        log_error "Claude CLI not found"
        log_error "Please install: npm install -g @anthropic-ai/claude-code"
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

    # Update task status to inprogress
    log "Updating task status to 'inprogress'..."
    if uv run anyt task edit "$task_id" --status inprogress >> "$LOG_FILE" 2>&1; then
        log_success "Task $task_id marked as in progress"
    else
        log_error "Failed to update task status to inprogress"
        return 1
    fi

    # Add note that Claude is starting work
    log "Adding start note to task..."
    if uv run anyt task note "$task_id" --message "🤖 Claude Task Worker started working on this task" >> "$LOG_FILE" 2>&1; then
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

    # Check if Claude succeeded
    if [ $claude_exit_code -ne 0 ]; then
        log_error "Claude failed to work on task $task_id"

        # Add error note
        uv run anyt task note "$task_id" --message "❌ Claude encountered an error during execution" >> "$LOG_FILE" 2>&1 || true

        # Revert status back to todo
        uv run anyt task edit "$task_id" --status todo >> "$LOG_FILE" 2>&1 || true

        return 1
    fi

    # Add completion note with summary
    log "Adding completion note to task..."
    local summary=$(echo "$claude_response" | head -c 500)
    if uv run anyt task note "$task_id" --message "✅ Claude completed work: $summary" >> "$LOG_FILE" 2>&1; then
        log "Completion note added"
    else
        log_warning "Failed to add completion note (non-critical)"
    fi

    # Git commit changes
    log "Checking for code changes to commit..."
    if git_commit_changes "$task_id" "$task_title"; then
        log_success "Code changes committed"
    else
        log_warning "Git commit failed or skipped"
    fi

    # Parse and create follow-up/blocking tasks
    parse_follow_up_tasks "$claude_response" "$task_id"

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

# Check prerequisites
check_prerequisites() {
    local missing_deps=false

    # Check uv
    if ! command -v uv &> /dev/null; then
        log_error "uv command not found. Please install uv first."
        missing_deps=true
    fi

    # Check Claude CLI
    if ! command -v claude &> /dev/null; then
        log_error "Claude CLI not found"
        log_error "Please install: npm install -g @anthropic-ai/claude-code"
        missing_deps=true
    fi

    # Check anyt CLI
    if ! uv run anyt --version &> /dev/null; then
        log_error "AnyTask CLI not properly configured"
        missing_deps=true
    fi

    if [ "$missing_deps" = true ]; then
        exit 1
    fi
}

# Main loop
main() {
    log "Claude Task Worker (Enhanced) started"
    log "Configuration:"
    log "  - Poll interval: ${POLL_INTERVAL}s"
    log "  - Log file: $LOG_FILE"
    log "  - Auto-commit: $AUTO_COMMIT"
    log "  - Commit prefix: $COMMIT_PREFIX"
    log "  - Create follow-up tasks: $CREATE_FOLLOWUP_TASKS"
    echo ""

    # Check prerequisites
    check_prerequisites

    while true; do
        log "Checking for available tasks..."

        # Get task suggestions (prefer high priority, unblocked tasks)
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
