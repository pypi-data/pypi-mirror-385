# T7-57: Agent Key in Workspace Configuration

**Priority**: Medium
**Status**: In Progress
**Created**: 2025-10-20

## Description

Enhance the `anyt init` command to save the agent key in `.anyt/anyt.json` workspace configuration file, so that future requests can use the agent key from the workspace config instead of relying solely on the `ANYT_AGENT_KEY` environment variable.

Currently, the `anyt init` function creates workspace configuration but does not include the agent key. This means all API requests must rely on the `ANYT_AGENT_KEY` environment variable. By storing the agent key in the workspace config, we can support workspace-specific agent authentication without requiring environment variables.

## Objectives

- Add `agent_key` field to `WorkspaceConfig` model
- Update `anyt init` command to save agent key from effective config to workspace config
- Ensure agent key from workspace config is used when available (falls back to env var if not present)
- Maintain backward compatibility with existing workspace configs that don't have agent key

## Acceptance Criteria

- [x] `WorkspaceConfig` model includes optional `agent_key: Optional[str]` field
- [x] `anyt init` command writes agent key to `.anyt/anyt.json` when available from effective config
- [x] API clients prioritize workspace config agent key over environment variable (workspace-specific key takes precedence)
- [x] Existing workspace configs without agent key continue to work (backward compatible)
- [ ] Tests written for new functionality
- [x] Type checking passes (`make typecheck`)
- [x] Linting passes (`make lint`)
- [ ] Code reviewed and merged

## Dependencies

None

## Estimated Effort

2-3 hours

## Technical Notes

### Files to Modify

1. **`src/cli/config.py`**:
   - Add `agent_key: Optional[str] = None` to `WorkspaceConfig` model (around line 189)
   - This change is backward compatible (optional field)

2. **`src/cli/commands/init.py`**:
   - Update workspace config creation to include agent key from effective config
   - Two places to modify:
     - Lines 128-136: When creating new workspace
     - Lines 173-181: When linking existing workspace
   - Add `agent_key=effective_config.get("agent_key")` to `WorkspaceConfig` initialization

3. **API Client Resolution** (if needed):
   - Review how agent keys are resolved in `GlobalConfig.get_effective_config()` or API client initialization
   - Ensure workspace config agent key is checked before falling back to environment variable
   - May need to update `BaseAPIClient` or similar if it doesn't already check workspace config

### Implementation Approach

1. **Update WorkspaceConfig Model**:
   ```python
   class WorkspaceConfig(BaseModel):
       workspace_id: str
       name: str
       api_url: str
       last_sync: Optional[str] = None
       current_project_id: Optional[int] = None
       workspace_identifier: Optional[str] = None
       agent_key: Optional[str] = None  # NEW FIELD
   ```

2. **Update init.py workspace creation**:
   ```python
   ws_config = WorkspaceConfig(
       workspace_id=str(workspace.id),
       name=workspace.name,
       api_url=effective_config["api_url"],
       workspace_identifier=workspace.identifier,
       current_project_id=current_project_id,
       agent_key=effective_config.get("agent_key"),  # NEW LINE
       last_sync=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
   )
   ```

3. **Verify API client uses workspace agent key**:
   - Check if `BaseAPIClient` or similar needs to load agent key from workspace config
   - Priority should be: workspace config > environment variable
   - May need to update client initialization to read from workspace config

### Testing Strategy

- **Unit tests**: Test that WorkspaceConfig properly stores and retrieves agent key
- **Integration tests**: Verify that `anyt init` writes agent key to workspace config
- **Backward compatibility**: Ensure existing configs without agent key still work
- **Priority testing**: Verify workspace config agent key takes precedence over env var

## Events

### 2025-10-20 19:30 - Created
- Task created based on user request
- User identified that current `anyt init` doesn't include agent key in workspace config
- User relies on `ANYT_AGENT_KEY=anyt_agent_6fwaBmF2oPUBW5zqJoJ3cElu5FNXcJSt` environment variable
- Goal: Store agent key in `.anyt/anyt.json` for workspace-specific authentication

### 2025-10-20 19:35 - Started work
- Task moved from backlog to active
- Status updated to "In Progress"
- Beginning implementation of agent key support in workspace config

### 2025-10-20 19:45 - Implementation completed
- Added `agent_key` field to `WorkspaceConfig` model in src/cli/config.py:190
- Updated `anyt init` command to save agent_key in both scenarios:
  - New workspace creation (src/cli/commands/init.py:134)
  - Existing workspace linking (src/cli/commands/init.py:180)
- Enhanced `GlobalConfig.get_effective_config()` to check workspace config for agent_key
- Priority order now: env vars > workspace config > global config
- Type checking passed (make typecheck)
- Linting passed (make lint)
- Code formatting passed (make format)
- Implementation is backward compatible (agent_key is optional field)
