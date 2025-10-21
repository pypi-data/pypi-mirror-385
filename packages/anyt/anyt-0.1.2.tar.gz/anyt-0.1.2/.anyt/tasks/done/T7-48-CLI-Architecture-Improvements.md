# T7-48: CLI Architecture Improvements - Type Layer and Folder Structure (PARENT TASK)

**Priority**: High
**Status**: Completed
**Created**: 2025-10-20
**Completed**: 2025-10-21

## Description

**This is a PARENT task that has been broken down into smaller, PR-sized subtasks.**

Refactor the AnyTask CLI architecture to introduce proper type safety, shared schemas, and improved folder structure. This epic transforms the CLI from using `dict[str, Any]` everywhere to a fully typed, well-structured codebase with clear separation of concerns.

## Subtasks

This task has been broken down into 8 independent, PR-sized tasks:

1. **T7-49: Models and Schemas Foundation** (3-4h)
   - Create Pydantic models for all domain entities
   - Create API response schemas
   - Foundation for all subsequent work
   - Status: ✅ Completed (PR #29)

2. **T7-50: Refactor BaseClient and Tasks API** (4-5h)
   - Create BaseAPIClient pattern
   - Implement TasksAPIClient with typed operations
   - Establish client architecture
   - Status: ✅ Completed (PR #30)
   - Depends on: T7-49

3. **T7-51: Refactor Workspace and Project APIs** (3-4h)
   - Implement WorkspacesAPIClient
   - Implement ProjectsAPIClient
   - Implement PreferencesAPIClient
   - Status: ✅ Completed (PR #31)
   - Depends on: T7-49, T7-50

4. **T7-52: Refactor Label, View, and AI APIs** (3-4h)
   - Implement LabelsAPIClient
   - Implement ViewsAPIClient
   - Implement AIAPIClient
   - Status: ✅ Completed (PR #32)
   - Depends on: T7-49, T7-50

5. **T7-53: Service Layer Foundation** (4-5h)
   - Create BaseService pattern
   - Implement TaskService with business logic
   - Implement WorkspaceService
   - Status: ✅ Completed (PR #33)
   - Depends on: T7-49, T7-50, T7-51

6. **T7-54: Migrate Task Commands to Services** (4-5h)
   - Refactor all task commands to use TaskService
   - Remove dict[str, Any] from task commands
   - Status: ✅ Completed (PR #34)
   - Depends on: T7-49, T7-50, T7-53

7. **T7-55: Migrate Core Commands to Services** (4-5h)
   - Refactor workspace, project, label, view commands
   - Create remaining services as needed
   - Status: ✅ Completed (PR #35, #36)
   - Depends on: T7-49, T7-51, T7-52, T7-53, T7-54

8. **T7-56: Cleanup - Remove Old Client** (2-3h)
   - Delete old monolithic client.py
   - Reorganize config into module
   - Update documentation
   - Final validation
   - Status: ✅ Completed (PR #37)
   - Depends on: T7-54, T7-55

## Total Estimated Effort

27-34 hours (broken into 8 PRs of 2-5 hours each)

## Current Architecture Issues

1. **No Type Safety**: All API methods return `dict[str, Any]`, no type hints for response structure
2. **Duplicated Logic**: Response unwrapping (`data["data"]`) repeated in every API method
3. **No Domain Models**: Commands work directly with dictionaries, no Task/Workspace/Project models
4. **Mixed Concerns**: Commands contain business logic, API calls, and presentation logic
5. **Large Client File**: 1600+ lines of similar boilerplate code
6. **No Schema Validation**: API responses not validated against expected structure

## Proposed Architecture

### New Folder Structure
```
src/cli/
├── models/          # Domain models (Pydantic)
├── schemas/         # API request/response schemas
├── client/          # HTTP clients (split by domain)
├── services/        # Business logic layer
├── config/          # Configuration models
├── utils/           # Utilities and formatters
└── commands/        # Thin CLI command layer
```

### Architecture Layers

1. **Models Layer**: Pydantic domain models (Task, Workspace, etc.)
2. **Schemas Layer**: API request/response wrappers
3. **Client Layer**: Typed HTTP clients for API communication
4. **Service Layer**: Business logic and validation
5. **Command Layer**: Thin CLI interface (Typer)

## Benefits

- **Type Safety**: Catch errors at compile-time with mypy --strict
- **Better IDE Support**: Autocomplete for all API responses
- **Self-Documenting**: Models serve as API documentation
- **Maintainability**: Clear separation of concerns
- **Testability**: Services tested independently
- **Reusability**: Services used by CLI, MCP server, future integrations

## Migration Strategy

Each subtask:
1. Creates new code alongside existing code (no breaking changes)
2. Can be merged independently
3. Has its own tests and validation
4. Maintains backward compatibility

Old code removed only in final cleanup task (T7-56).

## Dependencies

None - this is a refactoring epic

## Events

### 2025-10-20 15:30 - Created
- Task created based on architecture review
- User requested analysis of folder structure and type layer

### 2025-10-20 16:25 - Broken down into subtasks
- Created 8 smaller, PR-sized tasks (T7-49 through T7-56)
- Each task is independently mergeable
- Each task is 2-5 hours of work
- This task now serves as parent/epic for tracking

### 2025-10-21 01:45 - Epic completed
- All 8 subtasks successfully completed and merged:
  - T7-49: Models and Schemas Foundation (PR #29) ✅
  - T7-50: Refactor BaseClient and Tasks API (PR #30) ✅
  - T7-51: Refactor Workspace and Project APIs (PR #31) ✅
  - T7-52: Refactor Label, View, and AI APIs (PR #32) ✅
  - T7-53: Service Layer Foundation (PR #33) ✅
  - T7-54: Migrate Task Commands to Services (PR #34) ✅
  - T7-55: Migrate Core Commands to Services (PR #35, #36) ✅
  - T7-56: Cleanup - Remove Old Client (PR #37) ✅
- Successfully removed 3,619 lines of legacy code (old_client.py)
- Achieved full type safety with mypy --strict
- Established 4-layer architecture: Models → Clients → Services → Commands
- All tests passing, code formatted and linted
- CLI architecture migration complete
