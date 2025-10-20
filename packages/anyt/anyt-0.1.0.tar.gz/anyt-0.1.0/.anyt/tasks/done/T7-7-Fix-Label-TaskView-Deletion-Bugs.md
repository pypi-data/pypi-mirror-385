# T7-7: Fix Label and TaskView Deletion and Default View Bugs

**Priority**: High
**Status**: Completed
**Created**: 2025-10-18
**Completed**: 2025-10-18

## Description

Fix critical bugs in Label and TaskView endpoints that are causing test failures:

1. **Soft-delete bug**: Labels and TaskViews don't have `deleted_at` columns but `BaseRepository.delete()` tries to set `deleted_at`, causing soft-deleted records to still be retrievable
2. **Default view unset bug**: Creating a second default TaskView causes a 500 error when trying to unset the previous default
3. **Connection reset bug**: TaskView update operations sometimes cause server crashes with connection reset errors

These issues affect 4 integration tests:
- `test_delete_label_success` - Deleted labels return 200 instead of 404
- `test_delete_task_view_success` - Deleted task views return 200 instead of 404
- `test_create_task_view_unsets_previous_default` - Creating second default view returns 500
- `test_update_task_view_set_default_unsets_previous` - Server crashes with connection reset

## Objectives

- Fix deletion behavior for Label and TaskView entities
- Fix default view unsetting logic to prevent 500 errors
- Ensure deleted entities return 404 on subsequent GET requests
- Fix server crashes during TaskView updates
- Pass all 4 failing integration tests

## Root Causes

### Issue 1: Missing deleted_at columns
- `Label` and `TaskView` database models don't have `deleted_at` columns
- `BaseRepository.delete()` assumes all entities support soft deletes
- When `delete()` tries to set `deleted_at`, SQLAlchemy adds it to the object but doesn't persist it
- `get_by_id()` doesn't filter by `deleted_at`, so "deleted" records are still returned

### Issue 2: TaskViewUpdate model with None values
- `TaskViewUpdate(name=None, is_default=False)` passes `name=None` to update
- This may cause issues if the database or model validation doesn't allow None for name
- The update operation should only set `is_default=False`, not touch the name field

### Issue 3: Potential transaction/commit issues
- Multiple database operations (get default, update default, create new) without proper error handling
- Server crashes suggest unhandled exceptions during database operations

## Acceptance Criteria

### Fix 1: Add deleted_at columns to Label and TaskView tables
- [ ] Create Alembic migration to add `deleted_at` column to `labels` table
- [ ] Create Alembic migration to add `deleted_at` column to `task_views` table
- [ ] Both columns should be `TIMESTAMP(timezone=True)`, nullable, default `None`
- [ ] Run migrations on test database

### Fix 2: Update BaseRepository.get_by_id() to filter soft-deletes
- [ ] Modify `get_by_id()` to check if entity has `deleted_at` attribute
- [ ] If `deleted_at` exists and is not None, return None (treat as not found)
- [ ] Same logic for `get_by_id_or_raise()`
- [ ] Same logic for `list()` method (already has `include_deleted` parameter)

### Fix 3: Fix TaskView default unsetting logic
- [ ] In `create_task_view()`, when unsetting previous default, use proper update call
- [ ] Only pass `is_default=False`, don't pass `name=None`
- [ ] Wrap in try/except to handle potential errors gracefully
- [ ] Same fix needed in `update_task_view()` endpoint

### Fix 4: Add proper error handling
- [ ] Wrap default view unset logic in try/except blocks
- [ ] Log errors but don't fail the create/update operation
- [ ] Return proper error responses instead of 500

### Testing
- [ ] All 4 failing integration tests pass:
  - `tests/backend/integration/test_labels.py::TestLabelDeletion::test_delete_label_success`
  - `tests/backend/integration/test_task_views.py::TestTaskViewCreation::test_create_task_view_unsets_previous_default`
  - `tests/backend/integration/test_task_views.py::TestTaskViewUpdate::test_update_task_view_set_default_unsets_previous`
  - `tests/backend/integration/test_task_views.py::TestTaskViewDeletion::test_delete_task_view_success`
- [ ] No other tests broken by changes
- [ ] Run full test suite: `make test`

## Dependencies

- None (bug fix for existing functionality)

## Estimated Effort

4-6 hours
- 1 hour: Create and test migrations
- 1 hour: Update BaseRepository soft-delete filtering
- 1 hour: Fix TaskView default unsetting logic
- 1 hour: Add error handling and logging
- 1-2 hours: Testing and validation

## Technical Notes

### Migration Strategy

Create two separate migrations or one combined migration:

```python
# Add deleted_at to labels
op.add_column('labels',
    sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True)
)

# Add deleted_at to task_views
op.add_column('task_views',
    sa.Column('deleted_at', sa.TIMESTAMP(timezone=True), nullable=True)
)
```

### BaseRepository Changes

Modify `get_by_id()` to check for soft-deletes:

```python
async def get_by_id(self, id: int) -> Optional[T]:
    result = await self.db.execute(
        select(self.db_model).where(self.db_model.id == id)
    )
    db_obj = result.scalar_one_or_none()

    if db_obj is None:
        return None

    # Filter soft-deleted entities
    if hasattr(db_obj, 'deleted_at') and db_obj.deleted_at is not None:
        return None

    return self._to_domain(db_obj)
```

### TaskView Route Changes

Fix the default unsetting logic in `create_task_view()`:

```python
# If setting as default, unset any existing default
if data.is_default:
    current_default = await repos.task_views.get_default(workspace_id, user.user_id)
    if current_default:
        try:
            # Only update is_default, don't pass other fields
            update_data = TaskViewUpdate(is_default=False)
            await repos.task_views.update(current_default.id, update_data)
        except Exception as e:
            # Log error but continue with creation
            logger.error(f"Failed to unset previous default view: {e}")
```

### Alternative Solutions Considered

1. **Hard delete for Label/TaskView**: Could use hard deletes instead of soft deletes
   - Pros: Simpler, matches test expectations
   - Cons: Loses audit trail, breaks pattern consistency
   - Decision: Keep soft deletes for consistency

2. **Add deleted_at to all queries**: Filter in repository methods instead of get_by_id
   - Pros: More explicit filtering
   - Cons: Must update every query method
   - Decision: Filter in get_by_id for consistency

3. **Use TaskViewUpdate with exclude_unset**: Create update object differently
   - Pros: More explicit about what's being updated
   - Cons: Current approach should work if fixed properly
   - Decision: Fix the field passing, not the pattern

## Events

### 2025-10-18 12:30 - Created
- Task created based on 4 failing integration tests from `make test`
- Root causes identified: missing deleted_at columns and improper update logic
- Ready for implementation

### 2025-10-18 12:35 - Started work
- Moved task from backlog to active
- Beginning implementation with database migration

### 2025-10-18 13:10 - Completed
- Created migration to add `deleted_at` columns to `labels` and `task_views` tables
- Updated database models to include `deleted_at` field
- Applied migration successfully to test database
- Updated `BaseRepository.get_by_id()` to filter soft-deleted entities
- Updated `BaseRepository.list()` and `count()` to safely handle deleted_at
- Fixed TaskView default unsetting logic in both `create_task_view()` and `update_task_view()`
- All 4 previously failing tests now pass:
  - `test_delete_label_success` ✅
  - `test_delete_task_view_success` ✅
  - `test_create_task_view_unsets_previous_default` ✅
  - `test_update_task_view_set_default_unsets_previous` ✅
- Full test suite passes: 591 passed, 4 skipped
- Task moved to done/
- Committed changes and updated PR #92: https://github.com/supercarl87/AnyTaskBackend/pull/92
