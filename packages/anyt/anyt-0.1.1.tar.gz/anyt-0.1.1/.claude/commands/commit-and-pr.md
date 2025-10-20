# Commit and Create PR Command

Run quality checks, commit changes, and create a pull request with task context.

## Workflow

1. **Run Commit Workflow**:
   - Execute all steps from the `/commit` command
   - Run `make lint`, `make typecheck`, `make test`
   - Fix issues if possible, or stop and inform user
   - Commit changes if all checks pass

2. **Check for Active Task**:
   - Look in `.anyt/tasks/active/` for current task
   - If task exists, extract:
     - Task ID (e.g., "T2-1" from filename "T2-1-Task-CRUD-API.md")
     - Task title from filename
     - Task description and objectives from file content

3. **Create Pull Request**:
   - Push current branch to remote (with -u flag if needed)
   - Use `gh pr create` with task context:
     - If active task exists:
       - Title: `[T2-1] Task CRUD API` (using task ID and title)
       - Body: Include task description, objectives, and acceptance criteria
     - If no active task:
       - Title: Descriptive title based on git commits
       - Body: Summary of changes from git log and diff
   - Include test plan and checklist in PR description
   - Add standard footer: "🤖 Generated with Claude Code"
   - Return PR URL to user

## PR Body Format (with task)

```markdown
## Summary
Implements [T2-1] Task CRUD API

**Task Objectives**:
- [Objective 1 from task file]
- [Objective 2 from task file]

**Changes**:
- [Bullet points from git log since divergence]

## Acceptance Criteria
- [ ] [Criterion 1 from task file]
- [ ] [Criterion 2 from task file]

## Test Plan
- [ ] All unit tests pass (`make test`)
- [ ] Type checking passes (`make typecheck`)
- [ ] Linting passes (`make lint`)
- [ ] Manual testing of new endpoints/features

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

## PR Body Format (without task)

```markdown
## Summary
- [Bullet 1: Main change]
- [Bullet 2: Secondary change]

## Changes
[Summary from git log and git diff main...HEAD]

## Test Plan
- [ ] All unit tests pass (`make test`)
- [ ] Type checking passes (`make typecheck`)
- [ ] Linting passes (`make lint`)

🤖 Generated with [Claude Code](https://claude.com/claude-code)
```

## Important Notes

- Follow all rules from `/commit` command
- Use HEREDOC format for PR body in `gh pr create --body "$(cat <<'EOF' ...)"`
- Check active task BEFORE creating PR
- If task exists, update task file with event entry noting PR creation
- Do NOT push to main/master
- Return PR URL when complete

## Example Execution

```bash
# 1. Run quality checks and commit (from /commit)
make lint && make typecheck && make test
git add . && git commit -m "..."

# 2. Check for active task
ls .anyt/tasks/active/

# 3. Create PR with task context
gh pr create --title "[T2-1] Task CRUD API" --body "$(cat <<'EOF'
...
EOF
)"
```
