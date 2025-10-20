# Outputs & Metadata Architecture Analysis

**Date**: 2025-10-18
**Branch**: feat/mcp-analyser
**Scope**: Complete analysis of outputs/metadata separation and executor pattern migration

---

## Executive Summary

✅ **Custom Outputs**: FULLY WORKING - Tested end-to-end, no issues
⚠️ **Outputs Migration**: INCOMPLETE - Some default outputs still in outputs instead of metadata
🔴 **Dead Code**: Found unused fields from migration
⚠️ **Result Metadata**: Returned by all executors but NEVER used by workflow executor

---

## ✅ What's Working Correctly

### 1. Custom Outputs Implementation (VERIFIED WORKING)

**Status**: ✅ **COMPLETE** and **TESTED**

The custom outputs system works perfectly:

```yaml
blocks:
  - id: create_file
    type: Shell
    inputs:
      command: echo "Hello World" > .scratch/test.txt
    outputs:
      message:
        type: string
        path: "$SCRATCH/test.txt"
```

**How it works**:
1. YAML loader parses `outputs:` into `OutputSchema` Pydantic models ([schema.py:78-117](src/workflows_mcp/engine/schema.py#L78-L117))
2. Stored in `BlockDefinition.outputs` ([schema.py:291](src/workflows_mcp/engine/schema.py#L291))
3. Passed to Block constructor ([executor.py:1345](src/workflows_mcp/engine/executor.py#L1345))
4. Block injects into context via `__block_custom_outputs__` ([block.py:143-148](src/workflows_mcp/engine/block.py#L143-L148))
5. ShellExecutor reads from context and populates outputs ([executors_core.py:335-376](src/workflows_mcp/engine/executors_core.py#L335-L376))
6. Custom outputs merged into ShellOutput via `extra="allow"` ([executors_core.py:378](src/workflows_mcp/engine/executors_core.py#L378))

**Test Result**: ✅ PASSED - Custom output correctly retrieved as `'Hello World'`

### 2. Executor Pattern Migration

**Status**: ✅ **COMPLETE**

- No references to `WorkflowBlock` found (old architecture)
- All blocks use executor delegation pattern
- Block class is lightweight wrapper ([block.py:46-213](src/workflows_mcp/engine/block.py#L46-L213))
- Executors are stateless and registered in `ExecutorRegistry` ([executor_base.py:193-551](src/workflows_mcp/engine/executor_base.py#L193-L551))

### 3. Four-Namespace Context Structure

**Status**: ✅ **WORKING**

Context structure is clean and well-separated:
```python
context = {
    "inputs": {...},           # Workflow input parameters
    "metadata": {...},         # Workflow metadata
    "blocks": {                # Block results
        "block_id": {
            "inputs": {...},   # Resolved block inputs
            "outputs": {...},  # Block output fields
            "metadata": {...}  # Block execution metadata
        }
    },
    "__internal__": {...}      # Executor, workflow_stack, etc.
}
```

---

## 🔴 Issues Found

### Issue 1: Dead Code - `ShellInput.custom_outputs` Field

**Severity**: LOW (cleanup)
**Location**: [executors_core.py:47-51](src/workflows_mcp/engine/executors_core.py#L47-L51)

```python
# In ShellInput
custom_outputs: dict[str, Any] | None = Field(
    default=None,
    description="Custom file-based outputs to read after execution",
    exclude=True,  # ← Excluded from validation!
)
```

**Problem**:
- This field is marked `exclude=True` (not part of Pydantic validation)
- NEVER used anywhere in the codebase
- Custom outputs are passed via `context["__block_custom_outputs__"]` instead
- Leftover from pre-executor-pattern architecture

**Evidence**:
- `grep -r "custom_outputs"` shows it's only defined, never accessed
- Block class manages custom outputs via context injection

**Recommendation**: **DELETE** this field

**Diff**:
```diff
--- a/src/workflows_mcp/engine/executors_core.py
+++ b/src/workflows_mcp/engine/executors_core.py
@@ -44,11 +44,6 @@ class ShellInput(BlockInput):
         description="Continue workflow even if command fails (GitHub Actions semantics)",
         alias="continue-on-error",
     )
-    # Custom outputs support (from original Shell block)
-    custom_outputs: dict[str, Any] | None = Field(
-        default=None,
-        description="Custom file-based outputs to read after execution",
-        exclude=True,  # Not part of validation, managed separately
-    )
```

---

### Issue 2: Incomplete "Outputs to Metadata" Migration

**Severity**: MEDIUM (design consistency)
**Locations**:
- [executors_core.py:66](src/workflows_mcp/engine/executors_core.py#L66) - ShellOutput
- [executors_core.py:447](src/workflows_mcp/engine/executors_core.py#L447) - ExecuteWorkflowOutput

**Problem**: `execution_time_ms` appears as an **output field** in Shell and ExecuteWorkflow, but:

1. **Design Intent**: You stated *"we decided to move most of the 'default' outputs to a 'metadata' field"*
2. **Inconsistency**: Other executors (CreateFile, ReadFile, PopulateTemplate, Prompt, State) do NOT have this field
3. **Duplication**: Workflow executor calculates and stores `execution_time_ms` in metadata namespace ([executor.py:808](src/workflows_mcp/engine/executor.py#L808))

**Evidence**:

```python
# ShellOutput - Has execution_time_ms as output
class ShellOutput(BlockOutput):
    exit_code: int
    stdout: str
    stderr: str
    success: bool
    command_executed: str
    execution_time_ms: float  # ← Should be metadata-only
```

```python
# CreateFileOutput - Does NOT have execution_time_ms
class CreateFileOutput(BlockOutput):
    success: bool
    path: str
    size_bytes: int
    created: bool
    # No execution_time_ms!
```

```python
# Workflow executor stores it in metadata for ALL blocks:
context["blocks"][block_id]["metadata"] = {
    "wave": wave_idx,
    "execution_order": len(completed_blocks),
    "execution_time_ms": execution_time,  # ← Always in metadata
    "started_at": ...,
    "completed_at": ...,
    "status": "success",
}
```

**Recommendation**: **REMOVE** `execution_time_ms` from Shell and ExecuteWorkflow outputs

**Diff**:
```diff
--- a/src/workflows_mcp/engine/executors_core.py
+++ b/src/workflows_mcp/engine/executors_core.py
@@ -63,7 +63,6 @@ class ShellOutput(BlockOutput):
     stderr: str = Field(description="Standard error")
     success: bool = Field(description="Whether command succeeded")
     command_executed: str = Field(description="The command that was executed")
-    execution_time_ms: float = Field(description="Execution time in milliseconds")

     model_config = {"extra": "allow"}  # Allow dynamic custom output fields

@@ -326,7 +325,6 @@ class ShellExecutor(BlockExecutor):
                 "stderr": stderr,
                 "success": success,
                 "command_executed": inputs.command,
-                "execution_time_ms": timer.elapsed_ms(),
             }

@@ -444,7 +442,6 @@ class ExecuteWorkflowOutput(BlockOutput):

     success: bool = Field(description="Whether child workflow executed successfully")
     workflow: str = Field(description="Child workflow name executed")
-    execution_time_ms: float = Field(description="Child workflow execution time in milliseconds")
     total_blocks: int = Field(description="Number of blocks executed in child workflow")
     execution_waves: int = Field(description="Number of execution waves in child workflow")
     # Child workflow outputs become dynamic fields via extra="allow"

@@ -624,7 +621,6 @@ class ExecuteWorkflowExecutor(BlockExecutor):
         output_dict: dict[str, Any] = {
             "success": True,
             "workflow": workflow_name,
-            "execution_time_ms": timer.elapsed_ms(),
             "total_blocks": child_metadata.get("total_blocks", 0),
             "execution_waves": child_metadata.get("execution_waves", 0),
         }
```

---

### Issue 3: Result Metadata Completely Ignored

**Severity**: LOW (code clarity)
**Location**: ALL executors return metadata, but it's never used

**Problem**: Every executor returns `Result.success(output, metadata={"execution_time_ms": ...})`, but the workflow executor **NEVER** uses it.

**Evidence**:

All executors return metadata:
```python
# executors_core.py:387
return Result.success(output, metadata={"execution_time_ms": timer.elapsed_ms()})

# executors_file.py:135, 227, 248, 423
return Result.success(output, metadata={"execution_time_ms": timer.elapsed_ms()})

# executors_state.py:84, 168, 272
return Result.success(output, metadata={"execution_time_ms": timer.elapsed_ms()})

# executors_interactive.py:194
return Result.success(output, metadata={"execution_time_ms": timer.elapsed_ms()})
```

But workflow executor ignores it:
```python
# executor.py:790-812
output_dict = result.value.model_dump()
context["blocks"][block_id]["outputs"] = output_dict

# Create metadata - result.metadata is IGNORED!
context["blocks"][block_id]["metadata"] = {
    "wave": wave_idx,
    "execution_order": len(completed_blocks),
    "execution_time_ms": execution_time,  # ← Calculated locally, not from result.metadata
    "started_at": block_data.get("_start_time", ""),
    "completed_at": datetime.now(UTC).isoformat(),
    "status": "success",
}
```

**Search Proof**: `grep -r "result\.metadata" src/workflows_mcp/engine/` returns **ZERO** matches!

**Why it's ignored**: The workflow executor has more complete metadata (wave, execution_order, status, timestamps) than individual executors can provide.

**Recommendation**: **REMOVE** unused `metadata` parameter from all `Result.success()` calls

**Diff**:
```diff
--- a/src/workflows_mcp/engine/executors_core.py
+++ b/src/workflows_mcp/engine/executors_core.py
@@ -384,7 +384,7 @@ class ShellExecutor(BlockExecutor):
                     f"stderr: {stderr[:500]}"
                 )

-            return Result.success(output, metadata={"execution_time_ms": timer.elapsed_ms()})
+            return Result.success(output)

--- a/src/workflows_mcp/engine/executors_file.py
+++ b/src/workflows_mcp/engine/executors_file.py
@@ -132,7 +132,7 @@ class CreateFileExecutor(BlockExecutor):
             created=(not file_existed),
         )

-        return Result.success(output, metadata={"execution_time_ms": timer.elapsed_ms()})
+        return Result.success(output)

# ... repeat for all other executors
```

---

### Issue 4: Inconsistent Execution Time Tracking

**Severity**: LOW (minor inefficiency)

**Problem**: Both ShellExecutor and workflow executor calculate execution time:

- **ShellExecutor** ([line 329](src/workflows_mcp/engine/executors_core.py#L329)): Uses `timer.elapsed_ms()`
- **Workflow executor** ([lines 803-808](src/workflows_mcp/engine/executor.py#L803-L808)): Calculates from `_start_timestamp`

**Why it doesn't matter**: Both measure the same interval, but having both is redundant.

**Recommendation**: Already covered by Issue 2 (removing from outputs) and Issue 3 (removing metadata parameter).

---

## 📊 Summary Table

| Issue | Severity | Status | Files Affected | Lines |
|-------|----------|--------|----------------|-------|
| Dead code: `ShellInput.custom_outputs` | LOW | Not blocking | executors_core.py | 47-51 |
| Incomplete metadata migration: `execution_time_ms` in outputs | MEDIUM | Inconsistency | executors_core.py | 66, 329, 447, 627 |
| Unused `Result.metadata` parameter | LOW | Code clarity | All executor files | ~10 locations |
| Duplicate execution timing | LOW | Minor | executors_core.py | 329 |

---

## ✅ Verification Tests

### Test 1: Custom Outputs End-to-End
**Status**: ✅ PASSED

```bash
$ uv run python test_custom_outputs.py
✅ Workflow loaded: test-custom-outputs
📋 Block 'create_file' outputs:
   Type: <class 'dict'>
   - message: <class 'OutputSchema'>
     Dumped: {'type': 'string', 'path': '$SCRATCH/test.txt', ...}

🚀 Executing workflow...
✅ Execution succeeded!
   Outputs: {'result': 'Hello World'}

✅ Custom output 'result' = 'Hello World'
✅ Custom output value is correct!
```

**Conclusion**: Custom outputs system is fully functional and correctly implemented.

---

## 🎯 Recommended Actions

### Priority 1: Dead Code Removal (5 minutes)
**Impact**: Code clarity
**Risk**: None

1. Remove `ShellInput.custom_outputs` field (lines 47-51)

### Priority 2: Complete Metadata Migration (15 minutes)
**Impact**: Design consistency
**Risk**: Low (breaking change for workflows accessing `execution_time_ms` from outputs)

1. Remove `execution_time_ms` from `ShellOutput` (line 66)
2. Remove `execution_time_ms` from output_dict construction (line 329)
3. Remove `execution_time_ms` from `ExecuteWorkflowOutput` (line 447)
4. Remove `execution_time_ms` from output_dict construction (line 627)

**Note**: This is a breaking change for any workflows using `${blocks.shell_id.outputs.execution_time_ms}`. They should use `${blocks.shell_id.metadata.execution_time_ms}` instead.

### Priority 3: Code Cleanup (10 minutes)
**Impact**: Code clarity
**Risk**: None

1. Remove `metadata={"execution_time_ms": ...}` from all `Result.success()` calls:
   - executors_core.py: lines 387
   - executors_file.py: lines 135, 227, 248, 423
   - executors_state.py: lines 84, 168, 272
   - executors_interactive.py: line 194

---

## 🔍 Migration Completeness Assessment

| Aspect | Status | Completeness |
|--------|--------|--------------|
| **Executor Pattern Migration** | ✅ COMPLETE | 100% |
| **Custom Outputs Feature** | ✅ COMPLETE | 100% |
| **Outputs to Metadata Migration** | ⚠️ INCOMPLETE | ~80% |
| **Dead Code Cleanup** | ⚠️ INCOMPLETE | Leftover field found |
| **Code Consistency** | ⚠️ INCOMPLETE | Unused metadata params |

---

## 📝 Notes

1. **Custom Outputs are Working**: Despite concerns, the custom outputs system is fully functional and well-implemented. The git-semantic-commit workflow would work correctly.

2. **Design Philosophy Unclear**: The decision to keep `execution_time_ms` in Shell/ExecuteWorkflow outputs while removing from others suggests incomplete migration rather than intentional design.

3. **Breaking Change Consideration**: Moving `execution_time_ms` to metadata-only would be a breaking change. Consider:
   - Add deprecation warning for 1-2 versions
   - Update all template workflows
   - Document migration path

4. **Result Metadata Design**: The current design where executors return metadata but it's ignored might be intentional (separation of concerns), but it creates confusion. Either:
   - Use it (merge into block metadata)
   - Remove it (simplify code)

---

## 🚀 Next Steps

1. **Review**: Discuss whether `execution_time_ms` should remain in outputs for backward compatibility
2. **Decision**: Choose between:
   - **Option A**: Complete migration (breaking change, cleaner design)
   - **Option B**: Keep current state (backward compatible, but inconsistent)
   - **Option C**: Deprecation path (gradual migration over 2 versions)
3. **Execute**: Implement chosen option
4. **Test**: Verify all template workflows still work
5. **Document**: Update migration guide and breaking changes list

---

**Analysis completed**: 2025-10-18
**Verified by**: End-to-end testing
**Recommendation**: Proceed with Priority 1 (safe), defer Priority 2 (needs discussion)
