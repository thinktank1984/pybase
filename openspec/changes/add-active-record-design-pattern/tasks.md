# Implementation Tasks: Active Record Design Pattern

## Task Overview

**Goal**: Implement Active Record design pattern for clean model architecture  
**Estimated Total Time**: 12 hours (3-4 days part-time)  
**Impact**: Cleaner separation of concerns, better maintainability, improved auto-UI generation

---

## Phase 1: Foundation & Base Class (3 hours)

### Task 1.1: Create ActiveRecord Base Class
**File**: `runtime/app.py`  
**Estimated Time**: 1.5 hours  
**Priority**: High (blocking other tasks)

**Subtasks**:
- [ ] Design `ActiveRecord` mixin/base class
- [ ] Add model introspection utilities
- [ ] Add attribute collection methods
- [ ] Add method collection methods
- [ ] Add decorator detection utilities
- [ ] Add validation for anti-patterns
- [ ] Write comprehensive docstrings

**Acceptance Criteria**:
```python
# Should provide model metadata
class Post(Model, ActiveRecord):
    title = Field.string()
    
# Introspection should work
assert 'title' in Post.get_attributes()
assert len(Post.get_methods()) > 0
assert Post.get_ui_overrides() == {}
```

**Test Command**:
```bash
python -c "from app import Post; print(Post.get_attributes())"
```

---

### Task 1.2: Add Decorator Infrastructure
**File**: `runtime/app.py`  
**Estimated Time**: 1.5 hours  
**Priority**: High

**Subtasks**:
- [ ] Create `@ui_override` decorator for field widgets
- [ ] Create `@computed_field` decorator for derived attributes
- [ ] Create `@validates` decorator for attribute validation
- [ ] Create `@requires_permission` decorator for method authorization
- [ ] Add decorator registry system
- [ ] Add decorator metadata storage
- [ ] Test decorator composition

**Acceptance Criteria**:
```python
class Post(Model, ActiveRecord):
    @ui_override(field='content', widget='rich_text')
    def content_widget(self):
        return {'toolbar': ['bold', 'italic']}
    
    @validates('title')
    def validate_title(self, value):
        return len(value) >= 3

# Should register decorators
assert 'content' in Post.get_ui_overrides()
assert 'title' in Post.get_validators()
```

**Test Command**:
```bash
pytest test_active_record.py::test_decorators -v
```

---

## Phase 2: Pattern Validation (2 hours)

### Task 2.1: Add Anti-Pattern Detection
**File**: `runtime/app.py`  
**Estimated Time**: 1 hour  
**Priority**: Medium

**Subtasks**:
- [ ] Detect HTTP request handling in models
- [ ] Detect template rendering in models
- [ ] Detect external API calls in models
- [ ] Detect direct UI logic in models
- [ ] Add warnings/errors for violations
- [ ] Create allow-list for infrastructure methods

**Acceptance Criteria**:
```python
class BadModel(Model, ActiveRecord):
    def render_html(self):  # Should warn
        return "<div>Bad</div>"
    
# Should detect anti-patterns
violations = BadModel.validate_pattern()
assert len(violations) > 0
assert 'presentation logic' in str(violations[0])
```

**Test Command**:
```bash
pytest test_active_record.py::test_anti_patterns -v
```

---

### Task 2.2: Create Validation CLI
**File**: `runtime/validate_models.py` (new)  
**Estimated Time**: 1 hour  
**Priority**: Low

**Subtasks**:
- [ ] Create CLI script to validate all models
- [ ] Add JSON output for CI/CD
- [ ] Add verbose mode for debugging
- [ ] Add auto-fix suggestions
- [ ] Integrate with test suite

**Acceptance Criteria**:
```bash
# Should validate all models
python validate_models.py --all

# Should output violations
python validate_models.py --json | jq '.violations'
```

**Test Command**:
```bash
python validate_models.py --all --verbose
```

---

## Phase 3: Model Refactoring (4 hours)

### Task 3.1: Refactor Post Model
**File**: `runtime/app.py`  
**Estimated Time**: 1.5 hours  
**Priority**: High (pilot model)

**Subtasks**:
- [ ] Inherit from ActiveRecord
- [ ] Move attributes to top of class
- [ ] Add attribute decorators where needed
- [ ] Extract business methods
- [ ] Add UI overrides for rich content
- [ ] Remove any anti-patterns
- [ ] Add comprehensive tests

**Acceptance Criteria**:
- ✅ Post follows Active Record pattern
- ✅ All existing tests still pass
- ✅ Pattern validation passes
- ✅ UI overrides defined for auto-generation

**Test Command**:
```bash
pytest tests.py -k "post" -v
python validate_models.py Post
```

---

### Task 3.2: Refactor User Model
**File**: `runtime/app.py`  
**Estimated Time**: 1.5 hours  
**Priority**: High

**Subtasks**:
- [ ] Inherit from ActiveRecord
- [ ] Organize attributes
- [ ] Add password validation decorators
- [ ] Add email validation
- [ ] Extract authentication methods
- [ ] Add role/permission methods
- [ ] Test all auth flows

**Acceptance Criteria**:
- ✅ User follows Active Record pattern
- ✅ Authentication still works
- ✅ Password validation enforced
- ✅ All user tests pass

**Test Command**:
```bash
pytest tests.py -k "user or auth" -v
python validate_models.py User
```

---

### Task 3.3: Refactor Comment Model
**File**: `runtime/app.py`  
**Estimated Time**: 1 hour  
**Priority**: Medium

**Subtasks**:
- [ ] Inherit from ActiveRecord
- [ ] Organize attributes
- [ ] Add content validation
- [ ] Add moderation methods
- [ ] Test comment creation
- [ ] Test relationships

**Acceptance Criteria**:
- ✅ Comment follows Active Record pattern
- ✅ Post relationships work
- ✅ Comment tests pass
- ✅ Validation works correctly

**Test Command**:
```bash
pytest tests.py -k "comment" -v
python validate_models.py Comment
```

---

## Phase 4: Auto-UI Integration (2 hours)

### Task 4.1: Update Auto-UI Generator
**File**: `runtime/auto_ui_generator.py`  
**Estimated Time**: 1.5 hours  
**Priority**: High

**Subtasks**:
- [ ] Use ActiveRecord introspection API
- [ ] Read UI overrides from decorators
- [ ] Use validators for client-side validation
- [ ] Generate forms from Active Record metadata
- [ ] Test generated forms
- [ ] Update documentation

**Acceptance Criteria**:
```python
# Should generate form from Active Record
form = generate_form(Post)
assert 'content' in form.fields
assert form.fields['content'].widget == 'rich_text'
assert form.fields['title'].validators
```

**Test Command**:
```bash
pytest test_auto_ui.py -v
```

---

### Task 4.2: Add UI Override Examples
**File**: `runtime/app.py`  
**Estimated Time**: 30 minutes  
**Priority**: Low

**Subtasks**:
- [ ] Add rich text editor for Post.content
- [ ] Add date picker for date fields
- [ ] Add color picker for color fields (if any)
- [ ] Add custom select widgets
- [ ] Test generated UI in browser

**Acceptance Criteria**:
- ✅ UI overrides work in generated forms
- ✅ Widgets render correctly
- ✅ Validation messages display
- ✅ Forms are functional

**Test Command**:
```bash
# Manual browser testing
python -m app
# Visit /auto-ui/posts/new
```

---

## Phase 5: Documentation & Testing (1 hour)

### Task 5.1: Write Pattern Documentation
**File**: `documentation/active_record_pattern.md` (new)  
**Estimated Time**: 30 minutes  
**Priority**: High

**Subtasks**:
- [ ] Document pattern principles
- [ ] Add examples of good patterns
- [ ] Add examples of anti-patterns
- [ ] Document decorator usage
- [ ] Add migration guide
- [ ] Add troubleshooting section

**Acceptance Criteria**:
- ✅ Clear pattern explanation
- ✅ Code examples work
- ✅ Anti-patterns documented
- ✅ Migration path clear

---

### Task 5.2: Add Comprehensive Tests
**File**: `runtime/test_active_record.py` (new)  
**Estimated Time**: 30 minutes  
**Priority**: High

**Subtasks**:
- [ ] Test ActiveRecord base class
- [ ] Test all decorators
- [ ] Test introspection API
- [ ] Test anti-pattern detection
- [ ] Test model validation
- [ ] Achieve 100% coverage

**Acceptance Criteria**:
- ✅ All tests pass
- ✅ 100% code coverage for ActiveRecord
- ✅ Edge cases covered
- ✅ Error conditions tested

**Test Command**:
```bash
pytest test_active_record.py -v --cov=app --cov-report=term-missing
```

---

## Testing Checkpoints

### After Each Phase
```bash
# Quick check
pytest tests.py test_active_record.py --no-cov -q

# Full validation
python validate_models.py --all

# Coverage check
pytest --cov=app --cov-report=html
```

### Before Committing
```bash
# All tests pass
pytest tests.py test_active_record.py -v

# Models validate
python validate_models.py --all --json

# No linter errors
ruff check runtime/

# Documentation complete
ls documentation/active_record_pattern.md
```

---

## Success Metrics

| Phase | Time | Deliverable | Success Criteria |
|-------|------|-------------|------------------|
| Phase 1 | 3h | Base class & decorators | Introspection API works |
| Phase 2 | 2h | Pattern validation | Anti-patterns detected |
| Phase 3 | 4h | Refactored models | All tests pass |
| Phase 4 | 2h | Auto-UI integration | UI generation works |
| Phase 5 | 1h | Documentation & tests | 100% coverage |
| **Total** | **12h** | **Active Record Pattern** | **Clean architecture** |

---

## Rollback Plan

### If Pattern Doesn't Work
```bash
# Remove ActiveRecord mixin
git checkout HEAD -- runtime/app.py

# Restore original models
git checkout HEAD -- runtime/app.py
```

### Feature Flag (Gradual Rollout)
```python
USE_ACTIVE_RECORD = os.environ.get('USE_ACTIVE_RECORD', 'false') == 'true'

if USE_ACTIVE_RECORD:
    class Post(Model, ActiveRecord):
        pass
else:
    class Post(Model):
        pass
```

---

## Commit Strategy

### After Each Phase
```bash
git add runtime/app.py runtime/test_active_record.py
git commit -m "Phase X: [description]

- Task X.1: [subtask]
- Task X.2: [subtask]

Tests passing: X/Y"
```

---

## Dependencies

### Required Before Starting
- [x] Emmett ORM stable and working
- [x] Auto-UI generation functional
- [x] Test suite passing
- [ ] Team agreement on pattern

### Blocking Dependencies
- None (can implement incrementally)

### Nice to Have
- Code review after Phase 1 (foundation)
- Team feedback after Phase 3 (pilot model)

---

## Risk Mitigation

### High Risk Areas
1. **Breaking Changes**: Existing code may depend on current model structure
   - Mitigation: Use feature flag for gradual rollout
   
2. **Performance Impact**: Introspection may add overhead
   - Mitigation: Cache introspection results
   
3. **Team Adoption**: Pattern may be unfamiliar
   - Mitigation: Provide training and examples

---

## Post-Implementation

### Code Review Checklist
- [ ] All models follow Active Record pattern
- [ ] No anti-patterns in codebase
- [ ] Documentation is clear
- [ ] Tests are comprehensive
- [ ] Auto-UI generation works

### Deployment Checklist
- [ ] All tests passing locally
- [ ] All tests passing in CI
- [ ] Pattern validation passes
- [ ] Documentation updated
- [ ] Team trained on pattern

---

**Task List Status**: Ready for review  
**Total Estimated Time**: 12 hours  
**Next Step**: Get team approval, then begin Phase 1

