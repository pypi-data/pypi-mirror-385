# Additional Considerations for v0.10.0
**Date**: 2025-10-20
**Purpose**: 見落としがちな重要事項, 追加検討事項, リスク対策
**Status**: Complete

---

## Executive Summary

v0.10.0実装計画は **方向性は正しい** が, 以下の重要事項が未検討: 

**🔴 Critical(実装前に必須)**:
1. Undo/Rollback機能(透過的操作の取り消し)
2. 確認プロンプト(重要な操作の前)
3. Dry-runモード(実際に実行せず確認)
4. エラーリカバリー(部分失敗時の対処)

**🟡 Important(v0.10.0に含めるべき)**:
5. ログ機能(何が起こったか追跡)
6. 進捗表示(長時間操作のフィードバック)
7. バリデーション強化(YAML品質チェック)
8. パフォーマンス最適化(大量タスク対応)

**🟢 Nice-to-have(v0.11.0以降)**:
9. インタラクティブモード(対話的なYAML生成)
10. テンプレート機能(よくあるプロジェクトパターン)

---

## 1. Critical Issues(実装前に必須)

### 1.1 Undo/Rollback機能

#### 問題

**透過的操作は便利だが, 取り消せないと危険**

```
User: "Todoアプリを作りたい"
↓
Claude Code: (内部で kb_add() × 3, task_import_yaml())
              "✅ 10個のタスクを作成しました"
↓
User: "あ, 待って!違うプロジェクトだった!"
↓
Claude Code: "..."(元に戻せない)
```

**影響**:
- ユーザーが誤操作を訂正できない
- 信頼性が低下
- 手動で `.clauxton/` を編集する必要

---

#### 解決策1: Operation History(操作履歴)

**設計**:

```yaml
# .clauxton/history.yml
operations:
  - id: OP-20251020-001
    timestamp: 2025-10-20T15:30:00
    type: kb_add_batch
    items:
      - KB-20251020-001
      - KB-20251020-002
      - KB-20251020-003
    reversible: true

  - id: OP-20251020-002
    timestamp: 2025-10-20T15:30:10
    type: task_import_yaml
    items:
      - TASK-001
      - TASK-002
      - TASK-003
      - TASK-004
      - TASK-005
      - TASK-006
      - TASK-007
      - TASK-008
      - TASK-009
      - TASK-010
    reversible: true
```

**実装**:

```python
# clauxton/core/history.py
class OperationHistory:
    """Track operations for undo/rollback."""

    def record(self, operation_type: str, items: List[str]) -> str:
        """Record an operation."""
        op_id = self._generate_op_id()
        operation = {
            "id": op_id,
            "timestamp": datetime.now().isoformat(),
            "type": operation_type,
            "items": items,
            "reversible": True
        }
        self._save(operation)
        return op_id

    def undo(self, operation_id: str) -> dict:
        """Undo a specific operation."""
        operation = self._load(operation_id)

        if operation["type"] == "kb_add_batch":
            # Delete KB entries
            for kb_id in operation["items"]:
                kb.delete(kb_id)

        elif operation["type"] == "task_import_yaml":
            # Delete tasks
            for task_id in operation["items"]:
                tm.delete(task_id)

        # Mark as undone
        operation["undone"] = True
        operation["undone_at"] = datetime.now().isoformat()
        self._save(operation)

        return {"status": "success", "undone": len(operation["items"])}

    def undo_last(self) -> dict:
        """Undo the last operation."""
        last_op = self._get_last_operation()
        return self.undo(last_op["id"])
```

**MCPツール**:

```python
@server.call_tool("undo_last_operation")
async def undo_last_operation() -> dict:
    """
    Undo the last Clauxton operation.

    This is a safety feature for transparent operations.
    Allows users to roll back if Claude Code made a mistake.

    Returns:
        {
            "status": "success" | "error",
            "operation_type": str,
            "items_removed": int,
            "items": List[str]
        }
    """
    history = OperationHistory()
    result = history.undo_last()
    return result
```

**使用例**:

```
User: "Todoアプリを作りたい"
↓
Claude Code: "✅ 10個のタスクを作成しました"
↓
User: "待って, 違うプロジェクトだった"
↓
Claude Code: (内部で undo_last_operation())
             "了解しました.先ほどの操作を取り消しました.
              - 削除したタスク: 10個(TASK-001~TASK-010)
              - 削除したKBエントリ: 3個

              改めて, どのプロジェクトですか?"
```

**優先度**: 🔴 **CRITICAL**(v0.10.0に必須)
**実装時間**: 4時間

---

### 1.2 確認プロンプト(Confirmation Prompt)

#### 問題

**大量の操作を透過的に実行すると, ユーザーが制御感を失う**

```
Claude Code: (内部で task_import_yaml())
             "✅ 50個のタスクを作成しました"
↓
User: "えっ, 50個も?多すぎる..."
```

**影響**:
- ユーザーの意図と異なる結果
- 信頼性の低下
- 後で大量のタスクを手動削除

---

#### 解決策: Pre-execution Confirmation

**設計**:

```python
# 一定数以上の操作は確認を求める
CONFIRMATION_THRESHOLDS = {
    "kb_add": 5,           # 5個以上のKBエントリ
    "task_import": 10,     # 10個以上のタスク
    "kb_delete": 3,        # 3個以上の削除
    "task_delete": 5       # 5個以上の削除
}
```

**実装**:

```python
@server.call_tool("task_import_yaml")
async def task_import_yaml(
    yaml_content: str,
    skip_confirmation: bool = False
) -> dict:
    """
    Import multiple tasks from YAML.

    Args:
        yaml_content: YAML string
        skip_confirmation: Skip confirmation if True

    Returns:
        If confirmation needed:
            {
                "status": "confirmation_required",
                "preview": {...},
                "task_count": int,
                "confirmation_token": str
            }

        If confirmed:
            {
                "status": "success",
                "imported": int,
                "task_ids": List[str]
            }
    """
    # Parse YAML
    data = yaml.safe_load(yaml_content)
    task_count = len(data["tasks"])

    # Check threshold
    if task_count >= CONFIRMATION_THRESHOLDS["task_import"] and not skip_confirmation:
        # Return preview for confirmation
        return {
            "status": "confirmation_required",
            "preview": {
                "task_count": task_count,
                "categories": _categorize_tasks(data["tasks"]),
                "total_estimate": _sum_estimates(data["tasks"]),
                "high_priority": _count_high_priority(data["tasks"])
            },
            "confirmation_token": _generate_token(yaml_content)
        }

    # Proceed with import
    result = tm.import_yaml(yaml_content)

    # Record in history
    if result["status"] == "success":
        history.record("task_import_yaml", result["task_ids"])

    return result
```

**使用例**:

```
User: "大規模なEコマースサイトを作りたい"
↓
Claude Code: (内部でタスク生成)
             "タスクを作成する準備ができました.

             📊 Preview:
                Task count: 45 tasks
                Categories:
                  - Backend: 20 tasks (35h)
                  - Frontend: 15 tasks (28h)
                  - Infrastructure: 10 tasks (15h)
                Total estimate: 78 hours

             この45個のタスクを作成してよろしいですか?"
↓
User: "45個は多すぎる.重要なものだけにして"
↓
Claude Code: "承知しました.優先度HIGHのタスクのみ(15個)に絞ります."
```

**優先度**: 🔴 **CRITICAL**(v0.10.0に必須)
**実装時間**: 3時間

---

### 1.3 Dry-run Mode(実行せず確認)

#### 問題

**実際に実行する前に, 何が起こるか確認したい**

```
User: "このYAMLファイルをインポートしたい"
↓
Claude Code: (いきなりインポート)
             "✅ 20個のタスクを作成しました"
↓
User: "その前に内容を確認したかった..."
```

---

#### 解決策: Dry-run Flag

**実装済み(計画に含まれている)**:

```python
@server.call_tool("task_import_yaml")
async def task_import_yaml(
    yaml_content: str,
    dry_run: bool = False  # ✅ Already planned
) -> dict:
    """Import tasks (dry_run=True for preview only)."""
    if dry_run:
        # Validate only, don't create
        result = tm.import_yaml(yaml_content, dry_run=True)
        return {
            "status": "dry_run",
            "would_create": result["imported"],
            "validation": "passed",
            "errors": result["errors"]
        }

    # Actual import
    return tm.import_yaml(yaml_content)
```

**使用例**:

```
User: "tasks.ymlをインポートしたい(まず確認)"
↓
Claude Code: (内部で dry_run=True)
             "📋 Dry-run結果: 

             ✅ Validation passed
             Would create: 20 tasks

             Task breakdown:
               - Backend: 8 tasks
               - Frontend: 7 tasks
               - Testing: 5 tasks

             Dependencies: All valid
             Circular dependencies: None

             実際にインポートしますか?"
↓
User: "はい"
↓
Claude Code: (実際にインポート)
```

**優先度**: 🔴 **CRITICAL**(v0.10.0に必須, 既に計画済み)
**実装時間**: 0時間(既に設計に含まれている)

---

### 1.4 エラーリカバリー(部分失敗時の対処)

#### 問題

**10個のタスクをインポート中, 5個目でエラーが発生したらどうする?**

```
Claude Code: (task_import_yaml() 実行中)
             Task 1: ✓
             Task 2: ✓
             Task 3: ✓
             Task 4: ✓
             Task 5: ✗ Error: Circular dependency
             → どうする?
               A) 全てロールバック(4個も削除)
               B) 5個目だけスキップ(不完全な状態)
               C) エラーで停止, ユーザーに判断を求める
```

---

#### 解決策: Transactional Import with Rollback

**設計**:

```python
class TaskManager:
    """Task Manager with transactional import."""

    def import_yaml(
        self,
        yaml_content: str,
        on_error: str = "rollback"  # "rollback" | "skip" | "abort"
    ) -> dict:
        """
        Import tasks with error handling.

        Args:
            yaml_content: YAML string
            on_error: Error handling strategy
                - "rollback": Undo all changes on error
                - "skip": Skip failed tasks, continue
                - "abort": Stop immediately, keep successful

        Returns:
            {
                "status": "success" | "partial" | "error",
                "imported": int,
                "failed": int,
                "task_ids": List[str],
                "errors": List[dict]
            }
        """
        backup = self._create_backup()  # Backup current state

        tasks_data = yaml.safe_load(yaml_content)["tasks"]
        imported = []
        failed = []

        try:
            for i, task_data in enumerate(tasks_data, start=1):
                try:
                    task = Task(**task_data)
                    task_id = self.add(task)
                    imported.append(task_id)

                except Exception as e:
                    error_info = {
                        "task_index": i,
                        "task_name": task_data.get("name", "Unknown"),
                        "error": str(e)
                    }
                    failed.append(error_info)

                    # Handle error based on strategy
                    if on_error == "rollback":
                        # Rollback all changes
                        self._restore_backup(backup)
                        return {
                            "status": "error",
                            "imported": 0,
                            "failed": len(failed),
                            "errors": failed,
                            "message": f"Rolled back due to error at task {i}"
                        }

                    elif on_error == "abort":
                        # Stop, but keep successful imports
                        return {
                            "status": "partial",
                            "imported": len(imported),
                            "failed": len(failed),
                            "task_ids": imported,
                            "errors": failed,
                            "message": f"Aborted at task {i}"
                        }

                    elif on_error == "skip":
                        # Continue with next task
                        continue

            # Success (or partial success with skip)
            status = "success" if not failed else "partial"
            return {
                "status": status,
                "imported": len(imported),
                "failed": len(failed),
                "task_ids": imported,
                "errors": failed
            }

        finally:
            self._cleanup_backup(backup)
```

**MCPツール**:

```python
@server.call_tool("task_import_yaml")
async def task_import_yaml(
    yaml_content: str,
    on_error: str = "rollback"  # Add error handling strategy
) -> dict:
    """
    Import tasks with error handling.

    Args:
        yaml_content: YAML string
        on_error: "rollback" | "skip" | "abort"
    """
    tm = TaskManager()
    return tm.import_yaml(yaml_content, on_error=on_error)
```

**使用例**:

```
Claude Code: (task_import_yaml() with on_error="skip")

             Importing tasks...
             [1/10] TASK-001: FastAPI初期化 ✓
             [2/10] TASK-002: API設計 ✓
             [3/10] TASK-003: DB設定 ✗ Error: Invalid file path
             [4/10] TASK-004: 認証実装 ✓
             ...
             [10/10] TASK-010: デプロイ設定 ✓

             ⚠️ Import completed with warnings:
                Imported: 9 tasks
                Failed: 1 task
                  - Task 3 (DB設定): Invalid file path "backend/db.py"

             9個のタスクは正常に作成されました.
             TASK-003のエラーを修正しますか?"
```

**優先度**: 🔴 **CRITICAL**(v0.10.0に必須)
**実装時間**: 4時間

---

## 2. Important Issues(v0.10.0に含めるべき)

### 2.1 ログ機能(操作の追跡)

#### 問題

**透過的操作が多いと, 何が起こったか分からなくなる**

```
User: "何か問題が起きた.何が実行されたの?"
Claude Code: "..."(ログがないと説明できない)
```

---

#### 解決策: Operation Log

**設計**:

```yaml
# .clauxton/logs/2025-10-20.log
2025-10-20T15:30:00 [INFO] kb_add: KB-20251020-001 (FastAPI採用)
2025-10-20T15:30:01 [INFO] kb_add: KB-20251020-002 (React採用)
2025-10-20T15:30:02 [INFO] kb_add: KB-20251020-003 (PostgreSQL採用)
2025-10-20T15:30:10 [INFO] task_import_yaml: Starting import (10 tasks)
2025-10-20T15:30:11 [INFO] task_import_yaml: Created TASK-001
2025-10-20T15:30:11 [INFO] task_import_yaml: Created TASK-002
...
2025-10-20T15:30:15 [INFO] task_import_yaml: Completed (10 tasks created)
2025-10-20T15:35:00 [INFO] detect_conflicts: TASK-001 (no conflicts)
2025-10-20T15:35:01 [INFO] task_update: TASK-001 status=in_progress
2025-10-20T15:40:00 [INFO] task_update: TASK-001 status=completed
```

**実装**:

```python
# clauxton/utils/logger.py
import logging
from pathlib import Path
from datetime import datetime

class ClauxtonLogger:
    """Centralized logging for Clauxton operations."""

    def __init__(self, root: Path):
        self.log_dir = root / ".clauxton" / "logs"
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Daily log file
        log_file = self.log_dir / f"{datetime.now().date()}.log"

        # Configure logger
        self.logger = logging.getLogger("clauxton")
        self.logger.setLevel(logging.INFO)

        handler = logging.FileHandler(log_file, encoding="utf-8")
        handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        )
        self.logger.addHandler(handler)

    def log_operation(self, operation: str, details: str):
        """Log an operation."""
        self.logger.info(f"{operation}: {details}")

    def log_error(self, operation: str, error: str):
        """Log an error."""
        self.logger.error(f"{operation}: {error}")
```

**使用**:

```python
# 各操作でログを記録
logger = ClauxtonLogger(root)

# KB追加
logger.log_operation("kb_add", f"{entry.id} ({entry.title})")

# タスクインポート
logger.log_operation("task_import_yaml", f"Starting import ({len(tasks)} tasks)")
for task_id in task_ids:
    logger.log_operation("task_import_yaml", f"Created {task_id}")
logger.log_operation("task_import_yaml", f"Completed ({len(task_ids)} tasks)")
```

**MCPツール**:

```python
@server.call_tool("get_recent_logs")
async def get_recent_logs(limit: int = 50) -> dict:
    """
    Get recent Clauxton operation logs.

    Args:
        limit: Number of log entries to return

    Returns:
        {
            "logs": List[str],
            "count": int
        }
    """
    logger = ClauxtonLogger(root)
    logs = logger.get_recent(limit)
    return {"logs": logs, "count": len(logs)}
```

**使用例**:

```
User: "さっき何が実行されたの?"
↓
Claude Code: (get_recent_logs(limit=20))
             "直近の操作履歴: 

             15:30:00 - KB追加: FastAPI採用
             15:30:01 - KB追加: React採用
             15:30:02 - KB追加: PostgreSQL採用
             15:30:10 - タスクインポート開始(10個)
             15:30:15 - タスクインポート完了(10個作成)
             15:35:00 - 競合チェック: TASK-001(競合なし)
             15:35:01 - タスク更新: TASK-001 → 進行中
             15:40:00 - タスク更新: TASK-001 → 完了

             過去10分間で18個の操作を実行しました."
```

**優先度**: 🟡 **IMPORTANT**(v0.10.0に含めるべき)
**実装時間**: 3時間

---

### 2.2 進捗表示(長時間操作のフィードバック)

#### 問題

**大量のタスク(50個)をインポート中, ユーザーは何が起こっているか分からない**

```
Claude Code: (task_import_yaml() 実行中, 30秒かかる)
             "..."(無音)
↓
User: "固まった?"
```

---

#### 解決策: Progress Feedback

**実装**:

```python
@server.call_tool("task_import_yaml")
async def task_import_yaml(
    yaml_content: str,
    progress_callback: Optional[Callable] = None
) -> dict:
    """
    Import tasks with progress updates.

    Args:
        yaml_content: YAML string
        progress_callback: Function to call for progress updates
    """
    data = yaml.safe_load(yaml_content)
    tasks = data["tasks"]
    total = len(tasks)

    imported = []

    for i, task_data in enumerate(tasks, start=1):
        # Report progress (every 5 tasks or last)
        if i % 5 == 0 or i == total:
            if progress_callback:
                progress_callback({
                    "current": i,
                    "total": total,
                    "percent": int((i / total) * 100)
                })

        # Create task
        task = Task(**task_data)
        task_id = tm.add(task)
        imported.append(task_id)

    return {
        "status": "success",
        "imported": len(imported),
        "task_ids": imported
    }
```

**使用例(Claude Codeの内部処理)**:

```
Claude Code: "タスクをインポートしています...

             [████░░░░░░] 5/50 (10%)
             "

(5秒後)

Claude Code: "[████████░░] 25/50 (50%)
             "

(5秒後)

Claude Code: "[██████████] 50/50 (100%) ✓

             ✅ 50個のタスクを作成しました"
```

**優先度**: 🟡 **IMPORTANT**(v0.10.0に含めるべき)
**実装時間**: 2時間

---

### 2.3 バリデーション強化

#### 問題

**Claude Codeが生成するYAMLにエラーがあるかもしれない**

```yaml
# Claude Codeが生成したYAML(エラーあり)
tasks:
  - name: "Task 1"
    files_to_edit: ["main.py", "utils.py", "main.py"]  # 重複
  - name: "Task 2"
    depends_on: ["TASK-001", "TASK-001"]  # 重複
    estimate: -5  # 負の数
  - name: ""  # 空の名前
```

---

#### 解決策: Enhanced Validation

**実装**:

```python
class TaskValidator:
    """Enhanced validation for tasks."""

    @staticmethod
    def validate_task(task_data: dict) -> List[str]:
        """
        Validate a single task.

        Returns:
            List of error messages (empty if valid)
        """
        errors = []

        # Name validation
        if not task_data.get("name", "").strip():
            errors.append("Task name cannot be empty")

        if len(task_data.get("name", "")) > 255:
            errors.append("Task name too long (max 255 chars)")

        # Files validation
        files = task_data.get("files_to_edit", [])
        if files:
            # Check for duplicates
            if len(files) != len(set(files)):
                duplicates = [f for f in files if files.count(f) > 1]
                errors.append(f"Duplicate files: {duplicates}")

            # Check for invalid paths
            for file_path in files:
                if ".." in file_path or file_path.startswith("/"):
                    errors.append(f"Invalid file path: {file_path}")

        # Dependencies validation
        deps = task_data.get("depends_on", [])
        if deps:
            # Check for duplicates
            if len(deps) != len(set(deps)):
                errors.append("Duplicate dependencies")

            # Check for self-dependency (if task_id known)
            task_id = task_data.get("id")
            if task_id and task_id in deps:
                errors.append("Task cannot depend on itself")

        # Estimate validation
        estimate = task_data.get("estimate")
        if estimate is not None:
            if not isinstance(estimate, (int, float)):
                errors.append("Estimate must be a number")
            elif estimate <= 0:
                errors.append("Estimate must be positive")
            elif estimate > 1000:
                errors.append("Estimate too large (max 1000 hours)")

        # Priority validation
        priority = task_data.get("priority")
        if priority and priority not in ["critical", "high", "medium", "low"]:
            errors.append(f"Invalid priority: {priority}")

        return errors

    @staticmethod
    def validate_task_list(tasks: List[dict]) -> dict:
        """
        Validate a list of tasks.

        Returns:
            {
                "valid": bool,
                "errors": List[dict],
                "warnings": List[dict]
            }
        """
        errors = []
        warnings = []

        for i, task_data in enumerate(tasks, start=1):
            task_errors = TaskValidator.validate_task(task_data)
            if task_errors:
                errors.append({
                    "task_index": i,
                    "task_name": task_data.get("name", "Unknown"),
                    "errors": task_errors
                })

        # Check for common issues
        if len(tasks) > 100:
            warnings.append({
                "type": "large_batch",
                "message": f"Creating {len(tasks)} tasks. Consider breaking into smaller batches."
            })

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
```

**優先度**: 🟡 **IMPORTANT**(v0.10.0に含めるべき)
**実装時間**: 3時間

---

### 2.4 パフォーマンス最適化

#### 問題

**100個のタスクをインポートすると遅い可能性**

```python
# 現在の実装(1個ずつ保存)
for task in tasks:
    tm.add(task)  # ファイルを100回書き込み → 遅い
```

---

#### 解決策: Batch Write

**実装**:

```python
class TaskManager:
    """Task Manager with batch operations."""

    def import_yaml(self, yaml_content: str) -> dict:
        """Import tasks with batch write."""
        tasks_data = yaml.safe_load(yaml_content)["tasks"]

        # Validate all tasks first
        validation = TaskValidator.validate_task_list(tasks_data)
        if not validation["valid"]:
            return {"status": "error", "errors": validation["errors"]}

        # Create all tasks in memory
        tasks = []
        for task_data in tasks_data:
            task = Task(**task_data)
            tasks.append(task)

        # Write all at once (atomic)
        task_ids = self._batch_add(tasks)

        return {
            "status": "success",
            "imported": len(task_ids),
            "task_ids": task_ids
        }

    def _batch_add(self, tasks: List[Task]) -> List[str]:
        """Add multiple tasks in a single write operation."""
        # Load existing tasks
        existing = self._load_all()

        # Add new tasks
        task_ids = []
        for task in tasks:
            task_id = self._generate_task_id()
            task.id = task_id
            existing[task_id] = task
            task_ids.append(task_id)

        # Write all at once (single file operation)
        self._save_all(existing)

        return task_ids
```

**パフォーマンス**:
- Before: 100個 × 50ms = 5秒
- After: 1回 × 200ms = 0.2秒(25倍高速)

**優先度**: 🟡 **IMPORTANT**(v0.10.0に含めるべき)
**実装時間**: 2時間

---

## 3. Nice-to-have Features(v0.11.0以降)

### 3.1 インタラクティブモード

**概要**: Claude CodeがユーザーにYAML内容を確認しながら生成

```
Claude Code: "Todoアプリのタスクを作成します.

             Backend tasks:
               1. FastAPI初期化 (high, 1h)
               2. API設計 (high, 2h)
               3. DB設定 (high, 2h)

             これでよろしいですか?変更したい項目は?"
↓
User: "DB設定は後回しにして"
↓
Claude Code: "承知しました.DB設定を low priority に変更します.

             他に変更は?"
```

**優先度**: 🟢 **NICE-TO-HAVE**(v0.11.0)
**実装時間**: 6時間

---

### 3.2 テンプレート機能

**概要**: よくあるプロジェクトパターンのテンプレート

```yaml
# templates/fastapi-backend.yml
name: "FastAPI Backend Project"
description: "Standard FastAPI backend with PostgreSQL"
tasks:
  - name: "FastAPI初期化"
    priority: high
    files_to_edit: [backend/main.py]
    estimate: 1
  - name: "DB設定"
    priority: high
    files_to_edit: [backend/database.py]
    estimate: 2
  ...
```

```
User: "FastAPIバックエンドを作りたい"
↓
Claude Code: "FastAPIバックエンドのテンプレートがあります.
             使いますか?"
↓
User: "はい"
↓
Claude Code: (テンプレートをインポート)
             "✅ 10個のタスクを作成しました"
```

**優先度**: 🟢 **NICE-TO-HAVE**(v0.11.0)
**実装時間**: 4時間

---

## 4. Security & Data Integrity

### 4.1 YAML Injection攻撃の防止

#### 問題

**Claude CodeがユーザーメッセージからYAMLを生成する際, 悪意あるコードが埋め込まれる可能性**

```yaml
# 悪意あるYAML
tasks:
  - name: "Innocent task"
    description: !!python/object/apply:os.system ["rm -rf /"]
```

---

#### 解決策: Safe YAML Loading(既に実装済み)

```python
# ✅ Already using yaml.safe_load()
data = yaml.safe_load(yaml_content)  # No code execution
```

**追加チェック**:

```python
def validate_yaml_safety(yaml_content: str) -> bool:
    """Check for dangerous YAML constructs."""
    dangerous_patterns = [
        r"!!python",  # Python object deserialization
        r"!!exec",    # Execution tags
        r"__import__",  # Python imports
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, yaml_content):
            raise SecurityError(f"Dangerous YAML pattern detected: {pattern}")

    return True
```

**優先度**: 🔴 **CRITICAL**(v0.10.0に必須)
**実装時間**: 1時間

---

### 4.2 File Path Validation(既に実装済み)

```python
# ✅ Already implemented
def validate_path(path: Path, root: Path) -> None:
    """Validate path stays within project root."""
    if not path.resolve().is_relative_to(root.resolve()):
        raise SecurityError("Path traversal detected")
```

**優先度**: 🔴 **CRITICAL**(既に実装済み)

---

### 4.3 Backup Strategy

#### 問題

**大量の操作を実行する前にバックアップがあると安心**

---

#### 解決策: Automatic Backups(既に一部実装済み)

```python
# Existing backup in yaml_utils.py
def write_yaml(path: Path, data: dict):
    """Write YAML with automatic backup."""
    if path.exists():
        backup_path = path.with_suffix(".yml.bak")
        shutil.copy(path, backup_path)

    # Atomic write
    # ...
```

**強化**: 複数世代のバックアップ

```python
class BackupManager:
    """Manage multiple backup generations."""

    def create_backup(self, file_path: Path) -> Path:
        """Create timestamped backup."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = file_path.parent / "backups"
        backup_dir.mkdir(exist_ok=True)

        backup_path = backup_dir / f"{file_path.stem}_{timestamp}.yml"
        shutil.copy(file_path, backup_path)

        # Keep only last 10 backups
        self._cleanup_old_backups(backup_dir, keep=10)

        return backup_path
```

**優先度**: 🟡 **IMPORTANT**(v0.10.0に強化)
**実装時間**: 2時間

---

## 5. Documentation & User Education

### 5.1 Examples & Tutorials

**必要なドキュメント**:

1. **Quick Start Guide**(既にあるが更新が必要)
   - v0.10.0の透過的統合を反映
   - 自然な会話例を追加

2. **YAML Format Guide**(新規)
   - タスクYAMLの書き方
   - バリデーションルール
   - ベストプラクティス

3. **Error Handling Guide**(新規)
   - よくあるエラーと対処法
   - Undo/Rollback の使い方
   - トラブルシューティング

4. **Migration Guide**(新規)
   - v0.9.0-beta → v0.10.0
   - 破壊的変更なし(100% backward compatible)

**優先度**: 🟡 **IMPORTANT**(v0.10.0リリース時)
**実装時間**: 4時間

---

### 5.2 Error Messages Improvement

**現在のエラーメッセージ**:
```
Error: Validation failed
```

**改善後のエラーメッセージ**:
```
✗ Task import failed: Validation error

Task 3 (DB設定):
  - Invalid file path: "../../../etc/passwd"
    → File paths must be within project directory
    → Use relative paths like "backend/database.py"

Task 5 (認証実装):
  - Circular dependency detected: TASK-005 → TASK-006 → TASK-005
    → Remove dependency: TASK-005 → TASK-006

Need help? Run: clauxton task import --help
Or visit: https://github.com/nakishiyaman/clauxton/docs/troubleshooting
```

**優先度**: 🟡 **IMPORTANT**(v0.10.0に含めるべき)
**実装時間**: 2時間

---

## 6. Testing Strategy

### 6.1 Additional Test Cases

**新機能のテストが必要**:

1. **Undo/Rollback機能** (10 tests)
   - 最後の操作をUndoできる
   - 複数回Undoできる
   - Undo後にRedoできる(将来)
   - Undo不可能な操作のハンドリング

2. **確認プロンプト** (5 tests)
   - 閾値を超えると確認が求められる
   - skip_confirmation=Trueで確認スキップ
   - 確認を拒否すると実行されない

3. **エラーリカバリー** (15 tests)
   - rollback: 全てロールバック
   - skip: 失敗をスキップして続行
   - abort: 停止, 成功分は維持
   - 部分失敗時のレポート

4. **バリデーション** (20 tests)
   - 空の名前を検出
   - 重複ファイルを検出
   - 重複依存関係を検出
   - 負の見積もりを検出
   - パストラバーサルを検出

5. **パフォーマンス** (5 tests)
   - 100個のタスクを3秒以内にインポート
   - 1000個のタスクを30秒以内にインポート

**Total**: +55 tests(390 → 445 tests)

**優先度**: 🔴 **CRITICAL**(v0.10.0に必須)
**実装時間**: 10時間

---

### 6.2 Integration Tests

**シナリオテスト**:

1. **Happy Path**: 全てが正常に動作
2. **Error Recovery**: エラーが発生してもリカバリー
3. **Undo Flow**: 操作を取り消す
4. **Large Batch**: 大量のタスクをインポート

**優先度**: 🟡 **IMPORTANT**(v0.10.0に含めるべき)
**実装時間**: 4時間

---

## 7. Updated Timeline

### Original Plan
```
Week 1: YAML bulk import (8h)
Week 2: KB export (4h)
Total: 12h
```

### Updated Plan(追加事項を含む)
```
Week 1:
  Day 1-2: YAML bulk import - Core (6h)
  Day 3: Undo/Rollback機能 (4h)
  Day 4: 確認プロンプト (3h)
  Day 5: エラーリカバリー (4h)

Week 2:
  Day 6: バリデーション強化 (3h)
  Day 7: ログ機能 (3h)
  Day 8: KB export (4h)
  Day 9: 進捗表示 + パフォーマンス最適化 (4h)
  Day 10: テスト追加 (10h)

Week 3:
  Day 11-12: ドキュメント更新 (4h)
  Day 13: 統合テスト (4h)
  Day 14: バグ修正 + リリース準備 (4h)

Total: 53 hours (3 weeks)
```

**変更**:
- 期間: 2週間 → **3週間**
- 作業時間: 12時間 → **53時間**
- テスト: +35個 → +55個

---

## 8. Priority Matrix

| 機能 | 優先度 | 実装時間 | v0.10.0 | 理由 |
|------|--------|---------|---------|------|
| **Undo/Rollback** | 🔴 CRITICAL | 4h | ✅ Yes | 透過的操作の安全弁 |
| **確認プロンプト** | 🔴 CRITICAL | 3h | ✅ Yes | ユーザーコントロール維持 |
| **エラーリカバリー** | 🔴 CRITICAL | 4h | ✅ Yes | 部分失敗時の対処 |
| **YAML安全性チェック** | 🔴 CRITICAL | 1h | ✅ Yes | セキュリティ |
| **追加テスト(+55)** | 🔴 CRITICAL | 10h | ✅ Yes | 品質保証 |
| **ログ機能** | 🟡 IMPORTANT | 3h | ✅ Yes | デバッグ· 追跡 |
| **進捗表示** | 🟡 IMPORTANT | 2h | ✅ Yes | UX改善 |
| **バリデーション強化** | 🟡 IMPORTANT | 3h | ✅ Yes | エラー防止 |
| **パフォーマンス最適化** | 🟡 IMPORTANT | 2h | ✅ Yes | 大量タスク対応 |
| **バックアップ強化** | 🟡 IMPORTANT | 2h | ✅ Yes | データ保護 |
| **エラーメッセージ改善** | 🟡 IMPORTANT | 2h | ✅ Yes | ユーザビリティ |
| **ドキュメント更新** | 🟡 IMPORTANT | 4h | ✅ Yes | ユーザー教育 |
| **インタラクティブモード** | 🟢 NICE-TO-HAVE | 6h | ❌ v0.11.0 | 優先度低 |
| **テンプレート機能** | 🟢 NICE-TO-HAVE | 4h | ❌ v0.11.0 | 優先度低 |

---

## 9. Risk Assessment

| リスク | 影響 | 確率 | 対策 | ステータス |
|--------|------|------|------|-----------|
| Undo機能のバグ | High | Medium | 十分なテスト(15 tests) | 🟡 Mitigated |
| 確認プロンプトがうるさい | Medium | High | 閾値を調整可能に | ✅ Planned |
| パフォーマンス問題 | High | Low | バッチ書き込み実装 | ✅ Planned |
| エラーリカバリーの複雑性 | Medium | Medium | 3つの戦略を提供 | ✅ Planned |
| テスト時間不足 | High | Medium | 55個の追加テスト | ✅ Planned |
| ドキュメント不足 | Medium | High | 4時間確保 | ✅ Planned |
| リリース遅延 | Medium | Medium | 3週間に延長 | ✅ Adjusted |

---

## 10. Summary & Recommendations

### 10.1 Critical Additions(v0.10.0に必須)

**必ず実装すべき機能**:
1. ✅ **Undo/Rollback機能**(4時間)
2. ✅ **確認プロンプト**(3時間)
3. ✅ **エラーリカバリー**(4時間)
4. ✅ **YAML安全性チェック**(1時間)
5. ✅ **追加テスト**(10時間)

**理由**:
- 透過的操作の安全性を確保
- ユーザーコントロールを維持
- エラー時の対処が明確
- 品質保証

---

### 10.2 Important Additions(v0.10.0に推奨)

**できるだけ実装すべき機能**:
1. ✅ **ログ機能**(3時間)
2. ✅ **進捗表示**(2時間)
3. ✅ **バリデーション強化**(3時間)
4. ✅ **パフォーマンス最適化**(2時間)
5. ✅ **バックアップ強化**(2時間)
6. ✅ **エラーメッセージ改善**(2時間)
7. ✅ **ドキュメント更新**(4時間)

**理由**:
- UX向上
- デバッグ容易性
- 大量タスク対応
- ユーザー教育

---

### 10.3 Updated Release Plan

**リリース日**: 2025-11-03 → **2025-11-10**(1週間延期)

**理由**:
- Critical機能追加(Undo/確認/エラーリカバリー)
- テスト追加(+55個)
- ドキュメント更新

**作業時間**:
- Original: 12時間(2週間)
- Updated: **53時間(3週間)**

**内訳**:
- YAML bulk import: 6h
- Critical additions: 12h(Undo 4h + 確認 3h + エラーリカバリー 4h + YAML安全性 1h)
- Important additions: 18h(ログ 3h + 進捗 2h + バリデーション 3h + パフォーマンス 2h + バックアップ 2h + エラーメッセージ 2h + ドキュメント 4h)
- KB export: 4h
- Testing: 10h
- Integration testing: 4h
- Bug fixes: 4h

---

### 10.4 Recommendation

**提案**: 以下の順序で実装

#### Phase 1: Core + Critical(Week 1)
1. YAML bulk import(6時間)
2. Undo/Rollback(4時間)
3. 確認プロンプト(3時間)
4. エラーリカバリー(4時間)

**Total**: 17時間

---

#### Phase 2: Important + KB Export(Week 2)
5. バリデーション強化(3時間)
6. ログ機能(3時間)
7. KB export(4時間)
8. 進捗表示 + パフォーマンス(4時間)

**Total**: 14時間

---

#### Phase 3: Testing + Documentation(Week 3)
9. 追加テスト(10時間)
10. ドキュメント更新(4時間)
11. 統合テスト(4時間)
12. バグ修正 + リリース準備(4時間)

**Total**: 22時間

---

**Grand Total**: 53時間(3週間)

---

## 11. Conclusion

### 主要な発見

**当初の計画(12時間, 2週間)は不十分でした.**

**理由**:
1. 透過的操作には **安全機能** が必須(Undo/確認/エラーリカバリー)
2. ユーザーコントロールを維持する必要がある
3. 十分なテスト(+55個)が必要
4. ドキュメント更新が必要

---

### 推奨される対応

**Option A: 完全版を3週間でリリース**
- すべての機能を実装(Critical + Important)
- 品質保証を徹底(55個の追加テスト)
- リリース日: 2025-11-10

**Option B: 段階的リリース**
- v0.10.0-alpha: Core + Critical のみ(2週間, 2025-11-03)
- v0.10.0-beta: Important追加(+1週間, 2025-11-10)
- v0.10.0: 最終版(+1週間, 2025-11-17)

**推奨**: **Option A**(完全版を3週間で)

**理由**:
- Undo/確認なしの透過的操作は危険
- ユーザーに段階的リリースの負担をかけたくない
- 品質を最優先

---

### Next Steps

1. ✅ この追加検討事項をレビュー· 承認
2. ✅ 実装計画を更新(2週間 → 3週間)
3. ✅ Phase 1(Core + Critical)から開始
4. ✅ 2025-11-10に v0.10.0 リリース

---

**作成日**: 2025-10-20
**作成者**: Claude Code
**バージョン**: 1.0
**ステータス**: Complete - Awaiting Approval
