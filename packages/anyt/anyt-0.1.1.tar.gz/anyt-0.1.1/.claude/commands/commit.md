# Commit Command

Run quality checks and commit changes if all checks pass.

## Workflow

1. **Run Quality Checks**:
   - Execute `make lint` (ruff check)
   - Execute `make typecheck` (mypy on src/)
   - Execute `make test` (all unit tests)

2. **If All Checks Pass**:
   - Stage and commit all changes
   - Follow the standard git commit workflow from CLAUDE.md:
     - Run git status to see untracked files
     - Run git diff to see changes
     - Run git log to understand commit message style
     - Draft concise commit message (1-2 sentences, focus on "why" not "what")
     - Add relevant files and create commit with proper footer
     - Verify with git status after commit

3. **If Any Checks Fail**:
   - Analyze the failures
   - Attempt to fix issues automatically:
     - For linting issues: Run `make format` to auto-fix formatting
     - For type checking issues: Analyze and fix type annotations
     - For test failures: Analyze failure output and attempt fixes
   - Re-run the failed checks after fixes
   - If fixes work, proceed to commit
   - If issues are complex or ambiguous, stop and inform the user with:
     - Clear description of what failed
     - Why it's difficult to fix automatically
     - Suggested next steps

## Important Notes

- NEVER skip checks with --no-verify
- Follow all git safety protocols from CLAUDE.md
- Only commit when user explicitly requests it (via this command)
- Use proper commit message format with co-author footer
- Do NOT update git config
- Do NOT push unless explicitly requested

## Example Execution

```bash
# Run checks in parallel
make lint && make typecheck && make test

# If all pass:
git add <relevant-files>
git commit -m "..."

# If checks fail:
# Attempt fixes, re-run checks, then commit or report issues
```
