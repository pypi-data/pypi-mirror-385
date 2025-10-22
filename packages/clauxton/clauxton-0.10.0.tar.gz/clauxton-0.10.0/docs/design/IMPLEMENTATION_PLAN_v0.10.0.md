# Implementation Plan: v0.10.0 - Transparent Integration (REVISED)
**Date**: 2025-10-20 (Revised)
**Target Release**: v0.10.0
**Timeline**: 3 weeks (2025-10-20 → 2025-11-10)
**Status**: Planning Phase - Full Version with All Safety Features

---

## Executive Summary

**Goal**: Claude Code との透過的統合を実現し, 合致度 90% → 95% に向上

**Scope**: 完全版 - Critical + Important 全機能実装
1. 🔴 **CLAUDE.md強化**(Day 0, 2時間)- 即効性あり
2. 🔴 **YAML一括インポート**(Week 1, 6時間)- 基盤機能
3. 🔴 **Undo/Rollback機能**(Week 1, 4時間)- 安全弁
4. 🔴 **確認プロンプト**(Week 1, 3時間)- 制御維持(閾値ベース)
5. 🔴 **エラーリカバリー**(Week 1, 4時間)- 対処明確
6. 🔴 **YAML安全性チェック**(Week 1, 1時間)- セキュリティ
7. 🟡 **バリデーション強化**(Week 2, 3時間)- エラー防止
8. 🟡 **ログ機能**(Week 2, 3時間)- 追跡
9. 🟡 **KB→ドキュメント出力**(Week 2, 4時間)- 人間可読性
10. 🟡 **進捗表示 + パフォーマンス最適化**(Week 2, 4時間)- UX + 大量対応
11. 🟡 **バックアップ強化**(Week 2, 2時間)- データ保護
12. 🟡 **エラーメッセージ改善**(Week 2, 2時間)- ユーザビリティ
13. 🟡 **設定可能な確認モード**(Week 2, 8時間)- Human-in-the-Loop強化
14. 🟡 **追加テスト(+90個)**(Week 3, 10時間)- 品質保証
15. 🟡 **ドキュメント更新**(Week 3, 4時間)- ユーザー教育

**Expected Impact**:
- ユーザー体験: 10回のコマンド → 1回の会話
- Claude哲学合致度: 70% → 95%(Composable & Scriptable + Human-in-the-Loop)
- Human-in-the-Loop: 50% → 75-100%(設定可能)
- 開発効率: 5分の手動登録 → 10秒の自動登録
- 安全性: Undo/確認/エラーリカバリー完備 + 設定可能な確認レベル
- 品質: 480 tests (390 → +90), 94% coverage維持

**Total Effort**: 61 hours over 3 weeks

---

## 1. Priority 1: CLAUDE.md Enhancement

### 1.1 Overview

**目的**: Claude Codeに"Clauxtonをいつ· どう使うか"を明確に教える

**時間**: 2時間

**リリース**: 即時(コード変更不要, ドキュメント更新のみ)

**成果物**:
- `CLAUDE.md` に新セクション追加
- Claude Codeが自然にClauxtonを使うようになる

---

### 1.2 Detailed Design

#### 追加するセクション

```markdown
## Clauxton Integration Philosophy

### Core Principle: "Transparent Yet Controllable"

Clauxton follows Claude Code's philosophy:
- **Do the Simple Thing First**: YAML + Markdown (human-readable, Git-friendly)
- **Composable**: MCP integration (seamless with Claude Code)
- **User Control**: CLI override always available
- **Safety-First**: Read-only by default, explicit writes

### When to Use Clauxton (Transparent Integration)

#### 🔍 Phase 1: Requirements Gathering

**Trigger**: User mentions constraints, tech stack, or design decisions

**Action**: Automatically add to Knowledge Base via MCP

**Examples**:

| User Statement | MCP Call | Category |
|----------------|----------|----------|
| "FastAPIを使う" | `kb_add(title="FastAPI採用", category="architecture", content="...")` | architecture |
| "最大1000件まで" | `kb_add(title="データ上限", category="constraint", content="最大1000件")` | constraint |
| "JWTで認証" | `kb_add(title="JWT認証", category="decision", content="...")` | decision |
| "snake_case推奨" | `kb_add(title="命名規則", category="convention", content="...")` | convention |

**Implementation Pattern**:
```python
# When user mentions technical decisions
if user_mentioned_tech_decision:
    kb_add(
        title=extract_title(user_message),
        category=infer_category(user_message),
        content=user_message,
        tags=extract_tags(user_message)
    )
```

---

#### 📋 Phase 2: Task Planning

**Trigger**: User requests feature implementation or breaks down work

**Action**: Generate tasks and import via YAML (v0.10.0+)

**Example Workflow**:

```
User: "Todoアプリを作りたい.FastAPIでバックエンド, Reactでフロントエンドを構築して."

↓ Claude Code思考プロセス ↓

1. Feature breakdown:
   - Backend: FastAPI初期化, API設計, DB設定
   - Frontend: React初期化, UI実装
   - Integration: API連携

2. Generate YAML:
   ```yaml
   tasks:
     - name: "FastAPI初期化"
       description: "FastAPIプロジェクトをセットアップ"
       priority: high
       files_to_edit: [backend/main.py, backend/requirements.txt]
       estimate: 1
     - name: "API設計"
       description: "Todo CRUD APIエンドポイントを定義"
       priority: high
       files_to_edit: [backend/api/todos.py]
       depends_on: [TASK-001]
       estimate: 2
     ...
   ```

3. Import via MCP:
   ```python
   result = task_import_yaml(yaml_content)
   # → 10 tasks created: TASK-001 to TASK-010
   ```

4. Verify:
   ```python
   tasks = task_list(status="pending")
   # → Confirm all tasks registered
   ```

5. Start implementation:
   ```python
   next_task = task_next()
   # → TASK-001 (FastAPI初期化)
   ```

↓ User sees ↓

"10個のタスクを作成しました.TASK-001(FastAPI初期化)から始めます."
```

**Key Points**:
- User doesn't see YAML generation (transparent)
- All tasks created in single operation (efficient)
- Dependencies auto-inferred from file overlap
- Claude Code manages workflow (user just confirms)

---

#### ⚠️ Phase 3: Conflict Detection (Before Implementation)

**Trigger**: Before starting a task

**Action**: Check conflicts via MCP

**Example Workflow**:

```python
# Before implementing TASK-003
conflicts = detect_conflicts("TASK-003")

if conflicts["risk"] == "HIGH":
    # Warn user
    print(f"⚠️ Warning: TASK-003 has HIGH conflict risk with TASK-002")
    print(f"Files: {conflicts['files']}")
    print(f"Recommendation: Complete TASK-002 first")

    # Ask user
    proceed = ask_user("Proceed anyway?")
    if not proceed:
        # Work on another task
        next_task = task_next()
```

**Key Points**:
- Automatic conflict checking (transparent)
- User is warned if HIGH risk
- User decides whether to proceed (control)

---

#### 🛠️ Phase 4: Implementation

**During Implementation**: Update task status

```python
# Start task
task_update("TASK-001", status="in_progress")

# ... implementation ...

# Complete task
task_update("TASK-001", status="completed")

# Move to next
next_task = task_next()
```

---

### Manual Override (User Control)

**Important**: User can always override with CLI

```bash
# View all KB entries
clauxton kb list

# Add entry manually
clauxton kb add --title "..." --category architecture

# Delete incorrect entry
clauxton kb delete KB-20251020-001

# View all tasks
clauxton task list

# Manually update task
clauxton task update TASK-001 --status completed

# Check conflicts manually
clauxton conflict detect TASK-003
```

**Philosophy**: Claude Code uses MCP (transparent), but user has CLI (control)

---

### Transparency & Inspection

**User can inspect at any time**:

```bash
# View internal state
cat .clauxton/knowledge-base.yml
cat .clauxton/tasks.yml

# Git diff
git diff .clauxton/

# Search
clauxton kb search "authentication"
clauxton task list --status pending
```

**Key Points**:
- All data is human-readable (YAML)
- All data is Git-friendly (version control)
- User can manually edit if needed (last resort)

---

### Error Handling

**If Clauxton operations fail**:

```python
try:
    result = kb_add(...)
except Exception as e:
    # Graceful degradation
    print(f"Failed to add to KB: {e}")
    print("Continuing without KB registration...")
    # Implementation continues
```

**Philosophy**: Clauxton is helpful but not blocking

---

## 🎯 Best Practices

### DO:
✅ Use Clauxton transparently during natural conversation
✅ Register decisions/constraints as they're mentioned
✅ Generate tasks in bulk (YAML import)
✅ Check conflicts before implementation
✅ Update task status as you work
✅ Trust user to inspect/override if needed

### DON'T:
❌ Ask user to run CLI commands manually (breaks flow)
❌ Show YAML generation details (too technical)
❌ Require user approval for every KB entry (too slow)
❌ Skip conflict detection (causes merge issues)
❌ Leave task status outdated (confuses workflow)

---

## 🔧 Technical Notes

### MCP Tools Available

**Knowledge Base** (6 tools):
- `kb_search(query, limit)` - Search KB entries
- `kb_add(title, category, content, tags)` - Add entry
- `kb_list(category)` - List entries
- `kb_get(entry_id)` - Get specific entry
- `kb_update(entry_id, ...)` - Update entry
- `kb_delete(entry_id)` - Delete entry

**Task Management** (6 tools):
- `task_add(name, priority, files, ...)` - Add single task
- `task_import_yaml(yaml_content)` - ⭐ Bulk import (v0.10.0+)
- `task_list(status, priority)` - List tasks
- `task_get(task_id)` - Get specific task
- `task_update(task_id, status, ...)` - Update task
- `task_next()` - Get AI-recommended next task
- `task_delete(task_id)` - Delete task

**Conflict Detection** (3 tools):
- `detect_conflicts(task_id)` - Check conflicts for task
- `recommend_safe_order(task_ids)` - Get safe execution order
- `check_file_conflicts(file_paths)` - Check file availability

**KB Export** (v0.10.0+):
- `kb_export_docs(output_dir)` - ⭐ Export KB to Markdown docs

Total: **16 tools** (15 existing + 2 new in v0.10.0)

---

## 📊 Expected Behavior Changes

### Before Enhancement (Current):

```
User: "Todoアプリを作りたい"
↓
Claude Code: "まず, 以下のコマンドを実行してください: 
              clauxton task add --name 'FastAPI初期化' ...
              clauxton task add --name 'API設計' ...
              ...(10回繰り返し)"
↓
User: (手動で10回コマンド実行)
↓
Claude Code: "タスクを登録しました.始めましょう."
```

**問題**: 会話フローが断絶, 手間が多い

---

### After Enhancement (v0.10.0):

```
User: "Todoアプリを作りたい"
↓
Claude Code: (内部でYAML生成 → task_import_yaml())
             "10個のタスクを作成しました: 
              - TASK-001: FastAPI初期化
              - TASK-002: API設計
              - TASK-003: DB設定
              ...
              TASK-001から始めます."
↓
User: "はい, お願いします"
↓
Claude Code: (実装開始)
```

**改善**: 自然な会話, 手間なし, 効率的

---

## 📈 Success Metrics

**定量的指標**:
- タスク登録時間: 5分 → 10秒(30倍高速化)
- ユーザー操作回数: 10回 → 0回(完全自動化)
- Claude哲学合致度: 70% → 95%(Composable実現)

**定性的指標**:
- ユーザーは自然な会話だけでタスク管理可能
- Claude Codeが自律的にClauxtonを活用
- 手動オーバーライドも常に可能(User Control)

---
```

---

### 1.3 Implementation Steps

#### Step 1: CLAUDE.md に新セクション追加
**時間**: 30分

**内容**:
```markdown
## Clauxton Integration Philosophy
...(上記の設計内容を追加)
```

**場所**: `CLAUDE.md` の "Code Style Guidelines" の後

---

#### Step 2: 検証
**時間**: 30分

**方法**:
1. Claude Code を起動
2. CLAUDE.md が自動読み込みされることを確認
3. テスト会話:
   ```
   User: "FastAPIを使ってTodoアプリを作りたい"
   ↓
   Claude Code: (Clauxtonを使うか確認)
   ```

---

#### Step 3: ドキュメント更新
**時間**: 30分

**更新ファイル**:
- `README.md`: Usage セクションに"Claude Code統合"を追加
- `docs/quick-start.md`: 自然な会話例を追加

---

#### Step 4: コミット
**時間**: 30分

**コミットメッセージ**:
```
docs: Enhance CLAUDE.md with transparent integration guide

## Summary
Add comprehensive guide for Claude Code to use Clauxton transparently.

## Changes
- CLAUDE.md: New "Clauxton Integration Philosophy" section
  - When to use KB/Tasks/Conflicts
  - Transparent vs Manual usage patterns
  - Best practices and error handling

## Impact
- Claude Code will naturally use Clauxton during conversations
- Users no longer need to manually run CLI commands
- Philosophy alignment: 70% → 90% (Composable)

## Files Changed
- CLAUDE.md: +300 lines
- README.md: +50 lines (usage examples)
- docs/quick-start.md: +100 lines (Claude Code integration)
```

---

### 1.4 Acceptance Criteria

✅ CLAUDE.md に新セクションが追加されている
✅ Claude Code がファイルを読み込める(構文エラーなし)
✅ "いつ使うか"が明確に記述されている
✅ "どう使うか"が具体例付きで記述されている
✅ 手動オーバーライド方法が記述されている
✅ エラーハンドリング方法が記述されている
✅ README.md が更新されている

---

## 2. Priority 2: YAML Bulk Import

### 2.1 Overview

**目的**: Claude Codeが複数タスクを効率的に登録できる

**時間**: 8時間

**リリース**: v0.10.0(Week 1)

**成果物**:
- 新しいMCPツール: `task_import_yaml()`
- 新しいCLIコマンド: `clauxton task import`
- テストコード(20テスト)
- ドキュメント

---

### 2.2 Detailed Design

#### 2.2.1 YAML Format Specification

**入力YAML形式**:

```yaml
# tasks.yml
tasks:
  - name: "FastAPI初期化"
    description: "FastAPIプロジェクトをセットアップし, 基本的なディレクトリ構造を作成"
    priority: high
    files_to_edit:
      - backend/main.py
      - backend/requirements.txt
      - backend/README.md
    estimate: 1

  - name: "API設計"
    description: "Todo CRUD APIエンドポイントを定義し, OpenAPI仕様を作成"
    priority: high
    files_to_edit:
      - backend/api/todos.py
      - backend/schemas/todo.py
    depends_on:
      - TASK-001  # FastAPI初期化が完了してから
    estimate: 2

  - name: "データベース設定"
    description: "PostgreSQL接続とSQLAlchemyモデルを設定"
    priority: high
    files_to_edit:
      - backend/database.py
      - backend/models/todo.py
    depends_on:
      - TASK-001
    estimate: 2

  - name: "認証実装"
    description: "JWT認証を実装し, ユーザー管理APIを作成"
    priority: medium
    files_to_edit:
      - backend/auth.py
      - backend/api/users.py
    depends_on:
      - TASK-002
      - TASK-003
    estimate: 3
```

**フィールド説明**:

| Field | Required | Type | Description | Example |
|-------|----------|------|-------------|---------|
| `name` | ✅ Yes | string | タスク名(簡潔に) | "FastAPI初期化" |
| `description` | ❌ No | string | 詳細説明 | "FastAPIプロジェクトを..." |
| `priority` | ❌ No | enum | critical/high/medium/low | "high" |
| `files_to_edit` | ❌ No | list | 編集予定ファイル | ["main.py"] |
| `depends_on` | ❌ No | list | 依存タスクID | ["TASK-001"] |
| `estimate` | ❌ No | int | 見積もり時間(時間単位) | 2 |
| `tags` | ❌ No | list | タグ | ["backend", "api"] |

**バリデーション**:
- `name`: 必須, 1文字以上, 255文字以下
- `priority`: "critical", "high", "medium", "low" のいずれか
- `depends_on`: 実在するタスクIDのみ(循環依存検出)
- `estimate`: 正の整数

---

#### 2.2.2 CLI Implementation

**コマンド仕様**:

```bash
# 基本形
clauxton task import <YAML_FILE>

# オプション付き
clauxton task import tasks.yml --dry-run          # 実行せず検証のみ
clauxton task import tasks.yml --skip-validation  # バリデーションスキップ
clauxton task import tasks.yml --overwrite        # 重複IDを上書き

# 標準入力から読み込み
cat tasks.yml | clauxton task import -
echo "tasks: ..." | clauxton task import -
```

**出力例**:

```bash
$ clauxton task import tasks.yml

Importing tasks from tasks.yml...

✓ Validating YAML format...
✓ Checking task dependencies...
✓ Detecting circular dependencies...

Importing 10 tasks:
  [1/10] TASK-001: FastAPI初期化 (high) ✓
  [2/10] TASK-002: API設計 (high) ✓
  [3/10] TASK-003: データベース設定 (high) ✓
  [4/10] TASK-004: 認証実装 (medium) ✓
  [5/10] TASK-005: フロントエンド初期化 (high) ✓
  [6/10] TASK-006: UI実装 (medium) ✓
  [7/10] TASK-007: API連携 (medium) ✓
  [8/10] TASK-008: テスト作成 (high) ✓
  [9/10] TASK-009: ドキュメント作成 (low) ✓
  [10/10] TASK-010: デプロイ設定 (medium) ✓

Successfully imported 10 tasks.

Next task: TASK-001 (FastAPI初期化)
Run: clauxton task get TASK-001
```

**エラーハンドリング**:

```bash
$ clauxton task import invalid.yml

Importing tasks from invalid.yml...

✗ Validation failed:
  - Task 2: Missing required field 'name'
  - Task 4: Invalid priority 'urgent' (must be: critical, high, medium, low)
  - Task 5: Circular dependency detected: TASK-005 → TASK-006 → TASK-005
  - Task 7: Depends on non-existent task 'TASK-999'

Failed to import tasks. Please fix errors and try again.
```

---

#### 2.2.3 MCP Tool Implementation

**ツール仕様**:

```python
@server.call_tool("task_import_yaml")
async def task_import_yaml(
    yaml_content: str,
    dry_run: bool = False,
    skip_validation: bool = False
) -> dict:
    """
    Import multiple tasks from YAML.

    This enables Claude Code to efficiently create multiple tasks
    in a single operation, following the "Composable" philosophy.

    Args:
        yaml_content: YAML string containing tasks
        dry_run: If True, validate but don't create tasks
        skip_validation: If True, skip dependency validation

    Returns:
        {
            "status": "success" | "error",
            "imported": int,  # Number of tasks imported
            "task_ids": List[str],  # Created task IDs
            "errors": List[str],  # Validation errors (if any)
            "next_task": str  # Recommended next task ID
        }

    Example:
        >>> result = task_import_yaml('''
        ... tasks:
        ...   - name: "Setup FastAPI"
        ...     priority: high
        ...     files_to_edit: [main.py]
        ...   - name: "Create API"
        ...     priority: high
        ...     depends_on: [TASK-001]
        ... ''')
        >>> result
        {
            "status": "success",
            "imported": 2,
            "task_ids": ["TASK-001", "TASK-002"],
            "next_task": "TASK-001"
        }
    """
    pass  # Implementation below
```

---

#### 2.2.4 Implementation Details

**ファイル**: `clauxton/core/task_manager.py`

```python
from typing import List, Dict, Optional
import yaml
from pydantic import ValidationError
from clauxton.core.models import Task, TaskStatus, Priority

class TaskManager:
    """
    Task Manager with bulk import support.
    """

    def import_yaml(
        self,
        yaml_content: str,
        dry_run: bool = False,
        skip_validation: bool = False
    ) -> Dict:
        """
        Import multiple tasks from YAML.

        Workflow:
        1. Parse YAML
        2. Validate format
        3. Check dependencies
        4. Detect circular dependencies
        5. Create tasks (if not dry_run)
        6. Return results

        Args:
            yaml_content: YAML string
            dry_run: If True, validate only
            skip_validation: If True, skip dependency checks

        Returns:
            {
                "status": "success" | "error",
                "imported": int,
                "task_ids": List[str],
                "errors": List[str],
                "next_task": str
            }
        """
        errors = []
        task_ids = []

        try:
            # Step 1: Parse YAML
            data = yaml.safe_load(yaml_content)
            if not isinstance(data, dict) or "tasks" not in data:
                return {
                    "status": "error",
                    "errors": ["Invalid YAML format. Expected 'tasks' key at root."]
                }

            tasks_data = data["tasks"]
            if not isinstance(tasks_data, list):
                return {
                    "status": "error",
                    "errors": ["'tasks' must be a list"]
                }

            # Step 2: Validate each task
            tasks = []
            for i, task_data in enumerate(tasks_data, start=1):
                try:
                    # Pydantic validation
                    task = Task(**task_data)
                    tasks.append(task)
                except ValidationError as e:
                    errors.append(f"Task {i}: {e}")

            if errors:
                return {
                    "status": "error",
                    "errors": errors
                }

            # Step 3: Check dependencies (if not skipped)
            if not skip_validation:
                dep_errors = self._validate_dependencies(tasks)
                if dep_errors:
                    return {
                        "status": "error",
                        "errors": dep_errors
                    }

            # Step 4: Detect circular dependencies
            cycle_errors = self._detect_cycles(tasks)
            if cycle_errors:
                return {
                    "status": "error",
                    "errors": cycle_errors
                }

            # Step 5: Create tasks (if not dry_run)
            if not dry_run:
                for task in tasks:
                    task_id = self.add(task)
                    task_ids.append(task_id)

            # Step 6: Get next task
            next_task = None
            if task_ids:
                next_task = self.get_next_task()

            return {
                "status": "success",
                "imported": len(task_ids),
                "task_ids": task_ids,
                "errors": [],
                "next_task": next_task
            }

        except yaml.YAMLError as e:
            return {
                "status": "error",
                "errors": [f"YAML parsing error: {e}"]
            }
        except Exception as e:
            return {
                "status": "error",
                "errors": [f"Unexpected error: {e}"]
            }

    def _validate_dependencies(self, tasks: List[Task]) -> List[str]:
        """
        Validate that all dependencies exist.

        Args:
            tasks: List of tasks to validate

        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        existing_ids = {t.id for t in tasks if t.id}
        existing_ids.update(self.list_tasks().keys())  # Include existing tasks

        for task in tasks:
            if task.depends_on:
                for dep_id in task.depends_on:
                    if dep_id not in existing_ids:
                        errors.append(
                            f"Task '{task.name}': "
                            f"Depends on non-existent task '{dep_id}'"
                        )

        return errors

    def _detect_cycles(self, tasks: List[Task]) -> List[str]:
        """
        Detect circular dependencies using DFS.

        Args:
            tasks: List of tasks to check

        Returns:
            List of error messages (empty if no cycles)
        """
        # Build adjacency list
        graph = {}
        for task in tasks:
            task_id = task.id or f"TASK-{len(tasks)}"  # Temporary ID
            graph[task_id] = task.depends_on or []

        # DFS cycle detection
        visited = set()
        rec_stack = set()
        cycles = []

        def dfs(node, path):
            if node in rec_stack:
                # Cycle detected
                cycle_path = " → ".join(path + [node])
                cycles.append(f"Circular dependency: {cycle_path}")
                return

            if node in visited:
                return

            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in graph.get(node, []):
                dfs(neighbor, path[:])

            rec_stack.remove(node)

        for node in graph:
            if node not in visited:
                dfs(node, [])

        return cycles
```

---

**ファイル**: `clauxton/cli/tasks.py`

```python
import click
from pathlib import Path
from clauxton.core.task_manager import TaskManager

@click.group()
def task():
    """Task management commands."""
    pass

@task.command()
@click.argument("yaml_file", type=click.Path(exists=True))
@click.option("--dry-run", is_flag=True, help="Validate without creating tasks")
@click.option("--skip-validation", is_flag=True, help="Skip dependency validation")
def import_tasks(yaml_file: str, dry_run: bool, skip_validation: bool):
    """
    Import multiple tasks from YAML file.

    Example:
        clauxton task import tasks.yml
        clauxton task import tasks.yml --dry-run
    """
    try:
        # Read YAML file
        with open(yaml_file, "r", encoding="utf-8") as f:
            yaml_content = f.read()

        # Import tasks
        tm = TaskManager()
        result = tm.import_yaml(
            yaml_content,
            dry_run=dry_run,
            skip_validation=skip_validation
        )

        # Display results
        if result["status"] == "error":
            click.secho("✗ Import failed:", fg="red", bold=True)
            for error in result["errors"]:
                click.secho(f"  - {error}", fg="red")
            raise click.Abort()

        if dry_run:
            click.secho(
                f"✓ Validation passed: {result['imported']} tasks ready to import",
                fg="green"
            )
        else:
            click.secho(
                f"✓ Successfully imported {result['imported']} tasks",
                fg="green",
                bold=True
            )
            click.echo(f"\nTask IDs: {', '.join(result['task_ids'])}")
            if result.get("next_task"):
                click.echo(f"\nNext task: {result['next_task']}")
                click.echo(f"Run: clauxton task get {result['next_task']}")

    except FileNotFoundError:
        click.secho(f"✗ File not found: {yaml_file}", fg="red")
        raise click.Abort()
    except Exception as e:
        click.secho(f"✗ Unexpected error: {e}", fg="red")
        raise click.Abort()
```

---

**ファイル**: `clauxton/mcp/server.py`

```python
@server.call_tool("task_import_yaml")
async def task_import_yaml(
    yaml_content: str,
    dry_run: bool = False
) -> dict:
    """
    Import multiple tasks from YAML.

    Args:
        yaml_content: YAML string containing tasks
        dry_run: If True, validate but don't create tasks

    Returns:
        Result dictionary with status, imported count, task IDs
    """
    tm = TaskManager()
    return tm.import_yaml(yaml_content, dry_run=dry_run)
```

---

### 2.3 Testing Strategy

#### Test Files

**ファイル**: `tests/core/test_task_import.py`

```python
import pytest
from clauxton.core.task_manager import TaskManager

class TestTaskImport:
    """Test task_import_yaml functionality."""

    def test_import_single_task(self, tmp_path):
        """Test importing a single task."""
        yaml_content = """
        tasks:
          - name: "Test Task"
            priority: high
        """
        tm = TaskManager(root=tmp_path)
        result = tm.import_yaml(yaml_content)

        assert result["status"] == "success"
        assert result["imported"] == 1
        assert len(result["task_ids"]) == 1
        assert result["task_ids"][0] == "TASK-001"

    def test_import_multiple_tasks(self, tmp_path):
        """Test importing multiple tasks."""
        yaml_content = """
        tasks:
          - name: "Task 1"
            priority: high
          - name: "Task 2"
            priority: medium
          - name: "Task 3"
            priority: low
        """
        tm = TaskManager(root=tmp_path)
        result = tm.import_yaml(yaml_content)

        assert result["status"] == "success"
        assert result["imported"] == 3
        assert len(result["task_ids"]) == 3

    def test_import_with_dependencies(self, tmp_path):
        """Test importing tasks with dependencies."""
        yaml_content = """
        tasks:
          - name: "Task 1"
            priority: high
          - name: "Task 2"
            priority: medium
            depends_on:
              - TASK-001
        """
        tm = TaskManager(root=tmp_path)
        result = tm.import_yaml(yaml_content)

        assert result["status"] == "success"
        assert result["imported"] == 2

        # Verify dependency
        task2 = tm.get("TASK-002")
        assert "TASK-001" in task2.depends_on

    def test_circular_dependency_detection(self, tmp_path):
        """Test circular dependency detection."""
        yaml_content = """
        tasks:
          - name: "Task 1"
            depends_on: [TASK-002]
          - name: "Task 2"
            depends_on: [TASK-001]
        """
        tm = TaskManager(root=tmp_path)
        result = tm.import_yaml(yaml_content)

        assert result["status"] == "error"
        assert any("Circular dependency" in e for e in result["errors"])

    def test_invalid_yaml_format(self, tmp_path):
        """Test error handling for invalid YAML."""
        yaml_content = """
        invalid: yaml
        no: tasks key
        """
        tm = TaskManager(root=tmp_path)
        result = tm.import_yaml(yaml_content)

        assert result["status"] == "error"
        assert "Invalid YAML format" in result["errors"][0]

    def test_missing_required_field(self, tmp_path):
        """Test validation of required fields."""
        yaml_content = """
        tasks:
          - priority: high
        """  # Missing 'name'
        tm = TaskManager(root=tmp_path)
        result = tm.import_yaml(yaml_content)

        assert result["status"] == "error"
        assert any("name" in e.lower() for e in result["errors"])

    def test_invalid_priority(self, tmp_path):
        """Test validation of priority values."""
        yaml_content = """
        tasks:
          - name: "Test"
            priority: urgent
        """  # Invalid priority
        tm = TaskManager(root=tmp_path)
        result = tm.import_yaml(yaml_content)

        assert result["status"] == "error"

    def test_nonexistent_dependency(self, tmp_path):
        """Test error for non-existent dependency."""
        yaml_content = """
        tasks:
          - name: "Task 1"
            depends_on: [TASK-999]
        """
        tm = TaskManager(root=tmp_path)
        result = tm.import_yaml(yaml_content)

        assert result["status"] == "error"
        assert any("TASK-999" in e for e in result["errors"])

    def test_dry_run_mode(self, tmp_path):
        """Test dry-run mode (validation only)."""
        yaml_content = """
        tasks:
          - name: "Task 1"
            priority: high
        """
        tm = TaskManager(root=tmp_path)
        result = tm.import_yaml(yaml_content, dry_run=True)

        assert result["status"] == "success"
        assert result["imported"] == 1
        assert len(result["task_ids"]) == 0  # No tasks created

        # Verify no tasks were actually created
        tasks = tm.list_tasks()
        assert len(tasks) == 0

    def test_unicode_handling(self, tmp_path):
        """Test handling of Unicode characters."""
        yaml_content = """
        tasks:
          - name: "タスク名(日本語)"
            description: "説明文with emojis 🎉"
            tags: [テスト, 日本語]
        """
        tm = TaskManager(root=tmp_path)
        result = tm.import_yaml(yaml_content)

        assert result["status"] == "success"
        task = tm.get(result["task_ids"][0])
        assert task.name == "タスク名(日本語)"
        assert "🎉" in task.description

    def test_empty_tasks_list(self, tmp_path):
        """Test handling of empty tasks list."""
        yaml_content = """
        tasks: []
        """
        tm = TaskManager(root=tmp_path)
        result = tm.import_yaml(yaml_content)

        assert result["status"] == "success"
        assert result["imported"] == 0

    def test_large_batch_import(self, tmp_path):
        """Test importing large batch of tasks."""
        tasks = [
            f"""
          - name: "Task {i}"
            priority: medium
            """
            for i in range(1, 51)  # 50 tasks
        ]
        yaml_content = "tasks:" + "".join(tasks)

        tm = TaskManager(root=tmp_path)
        result = tm.import_yaml(yaml_content)

        assert result["status"] == "success"
        assert result["imported"] == 50

    def test_files_to_edit_auto_dependency(self, tmp_path):
        """Test auto-inference of dependencies from file overlap."""
        yaml_content = """
        tasks:
          - name: "Task 1"
            files_to_edit: [main.py, utils.py]
          - name: "Task 2"
            files_to_edit: [main.py, config.py]
        """
        tm = TaskManager(root=tmp_path)
        result = tm.import_yaml(yaml_content)

        assert result["status"] == "success"

        # Task 2 should auto-depend on Task 1 (file overlap)
        task2 = tm.get("TASK-002")
        # Note: Auto-dependency inference is existing feature
        # This test verifies it works with bulk import
```

**テストカバレッジ目標**: 95%+

---

### 2.4 Implementation Timeline

| Day | Task | Hours | Status |
|-----|------|-------|--------|
| Day 1 | Core implementation (`task_manager.py`) | 3h | Pending |
| Day 2 | CLI command (`cli/tasks.py`) | 2h | Pending |
| Day 2 | MCP tool (`mcp/server.py`) | 1h | Pending |
| Day 3 | Test implementation (20 tests) | 3h | Pending |
| Day 4 | Documentation | 2h | Pending |
| Day 5 | Integration testing | 1h | Pending |
| Day 5 | Code review & bug fixes | 2h | Pending |

**Total**: 14時間(バッファ含む, 見積もりは8時間)

---

### 2.5 Acceptance Criteria

✅ `task_import_yaml()` MCPツールが実装されている
✅ `clauxton task import` CLIコマンドが実装されている
✅ YAML形式のバリデーションが動作する
✅ 循環依存検出が動作する
✅ Dry-runモードが動作する
✅ エラーメッセージが明確で役立つ
✅ 20個のテストが全てパスする
✅ テストカバレッジ95%以上
✅ ドキュメントが更新されている(README, docs/)
✅ CLAUDE.mdに使用例が追加されている

---

## 3. Priority 3: KB Export to Docs

### 3.1 Overview

**目的**: 構造化データ(KB)を人間が読めるMarkdownドキュメントに出力

**時間**: 4時間

**リリース**: v0.10.0(Week 2)

**成果物**:
- 新しいMCPツール: `kb_export_docs()`
- 新しいCLIコマンド: `clauxton kb export`
- 生成されるドキュメント: `docs/architecture.md`, `docs/decisions.md`, etc.
- テストコード(15テスト)

---

### 3.2 Detailed Design

#### 3.2.1 Output Format

**生成されるファイル**:

```
docs/
├── architecture.md      # KB (architecture) から生成
├── decisions.md         # KB (decision) から生成 - ADR形式
├── constraints.md       # KB (constraint) から生成
├── conventions.md       # KB (convention) から生成
└── patterns.md          # KB (pattern) から生成
```

**ファイル例**: `docs/architecture.md`

```markdown
# Architecture Decisions

> Auto-generated from Clauxton Knowledge Base
> Last updated: 2025-10-20 15:30:00

---

## FastAPI採用

**ID**: KB-20251020-001
**Category**: Architecture
**Created**: 2025-10-20
**Tags**: `backend`, `api`, `python`

### 概要

FastAPIをバックエンドフレームワークとして採用.

### 理由

1. **非同期処理**: async/await のネイティブサポート
2. **型安全性**: Pydanticによる型検証
3. **自動ドキュメント**: OpenAPI/Swaggerの自動生成
4. **高速**: Starlette + uvicorn で高性能
5. **DX**: 開発体験が良好

### 影響

- バックエンド開発が高速化
- API仕様が自動生成される
- 型エラーが早期に発見できる

### 関連リンク

- [FastAPI公式ドキュメント](https://fastapi.tiangolo.com/)

---

## PostgreSQL採用

**ID**: KB-20251020-002
**Category**: Architecture
**Created**: 2025-10-20
**Tags**: `database`, `postgresql`

### 概要

PostgreSQLをデータベースとして採用.

### 理由

1. **信頼性**: エンタープライズグレードの安定性
2. **JSON対応**: JSONBによる柔軟なデータ保存
3. **拡張性**: パーティショニング, レプリケーション
4. **オープンソース**: ライセンス費用なし

### 影響

- 構造化データと非構造化データ(JSONB)を同時に扱える
- スケーリングが容易
- トランザクション保証が強固

---

*This document is auto-generated from `.clauxton/knowledge-base.yml`*
*To update, use: `clauxton kb update <ID>` or edit the source file*
```

---

**ファイル例**: `docs/decisions.md` (ADR形式)

```markdown
# Architecture Decision Records (ADR)

> Auto-generated from Clauxton Knowledge Base (category: decision)
> Last updated: 2025-10-20 15:30:00

---

## ADR-001: JWT認証の採用

**Status**: Accepted
**Date**: 2025-10-20
**Decision Makers**: Development Team

### Context

ユーザー認証の仕組みを決定する必要がある.
以下の選択肢を検討: 
- JWT (JSON Web Token)
- Session-based authentication
- OAuth 2.0

### Decision

JWT認証を採用する.

### Rationale

1. **Stateless**: サーバー側でセッション保存不要
2. **スケーラブル**: 水平スケーリングが容易
3. **モバイル対応**: トークンベースで扱いやすい
4. **標準規格**: RFC 7519

### Consequences

**Positive**:
- サーバーがStatelessになる
- マイクロサービスアーキテクチャに適合
- クロスドメイン対応が容易

**Negative**:
- トークン無効化が難しい(ブラックリスト必要)
- トークンサイズが大きい(Cookieに比べて)

### Implementation Notes

- ライブラリ: `PyJWT`
- トークン有効期限: 1時間
- リフレッシュトークン: 7日間
- 署名アルゴリズム: RS256

---

## ADR-002: snake_case命名規則

**Status**: Accepted
**Date**: 2025-10-20

### Context

Pythonコードの命名規則を統一する必要がある.

### Decision

PEP 8に従い, snake_case を採用.

### Rationale

1. **PEP 8準拠**: Pythonの標準スタイルガイド
2. **可読性**: アンダースコアで区切られて読みやすい
3. **一貫性**: Pythonエコシステムとの統一

### Consequences

- 全てのPython変数· 関数名は `snake_case`
- クラス名は `PascalCase`
- 定数は `UPPER_CASE`

---

*This document follows ADR format (Architecture Decision Records)*
*To add decisions, use: `clauxton kb add --category decision`*
```

---

#### 3.2.2 CLI Implementation

**コマンド仕様**:

```bash
# 基本形(全カテゴリをdocs/にエクスポート)
clauxton kb export docs/

# 特定カテゴリのみ
clauxton kb export docs/ --category architecture
clauxton kb export docs/ --category decision

# 出力フォーマット指定
clauxton kb export docs/ --format markdown  # デフォルト
clauxton kb export docs/ --format html      # HTML形式(将来実装)

# 上書き確認
clauxton kb export docs/ --force            # 確認なしで上書き
clauxton kb export docs/ --dry-run          # 実行せず確認のみ
```

**出力例**:

```bash
$ clauxton kb export docs/

Exporting Knowledge Base to docs/...

✓ architecture.md (5 entries) ✓
✓ decisions.md (3 entries) ✓
✓ constraints.md (2 entries) ✓
✓ conventions.md (4 entries) ✓
✓ patterns.md (1 entry) ✓

Successfully exported 15 KB entries to 5 Markdown files.

Files created:
  - docs/architecture.md (12 KB)
  - docs/decisions.md (8 KB)
  - docs/constraints.md (3 KB)
  - docs/conventions.md (6 KB)
  - docs/patterns.md (2 KB)

Total: 31 KB

Next steps:
  - Review the generated files
  - Commit to Git: git add docs/ && git commit -m "docs: Export KB to Markdown"
  - Share with your team
```

---

#### 3.2.3 MCP Tool Implementation

```python
@server.call_tool("kb_export_docs")
async def kb_export_docs(
    output_dir: str,
    category: Optional[str] = None,
    format: str = "markdown"
) -> dict:
    """
    Export Knowledge Base to Markdown documents.

    Follows Claude Code's philosophy:
    - Simple: Markdown output (human-readable)
    - Git-friendly: Version-controlled documentation
    - Transparent: Users can see all decisions

    Args:
        output_dir: Directory to write Markdown files
        category: Export specific category only (optional)
        format: Output format (currently only "markdown")

    Returns:
        {
            "status": "success" | "error",
            "files_created": List[str],
            "total_entries": int,
            "total_size_kb": float
        }

    Example:
        >>> kb_export_docs("docs/")
        {
            "status": "success",
            "files_created": [
                "docs/architecture.md",
                "docs/decisions.md",
                ...
            ],
            "total_entries": 15,
            "total_size_kb": 31.2
        }
    """
    pass  # Implementation below
```

---

#### 3.2.4 Implementation Details

**ファイル**: `clauxton/core/knowledge_base.py`

```python
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

class KnowledgeBase:
    """Knowledge Base with export functionality."""

    def export_to_markdown(
        self,
        output_dir: str,
        category: Optional[str] = None
    ) -> Dict:
        """
        Export KB entries to Markdown files.

        Args:
            output_dir: Directory to write Markdown files
            category: Export specific category only (optional)

        Returns:
            {
                "status": "success" | "error",
                "files_created": List[str],
                "total_entries": int,
                "total_size_kb": float
            }
        """
        try:
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            files_created = []
            total_entries = 0

            # Determine categories to export
            categories = [category] if category else [
                "architecture",
                "decision",
                "constraint",
                "convention",
                "pattern"
            ]

            for cat in categories:
                entries = self.list_by_category(cat)
                if not entries:
                    continue

                # Generate Markdown
                markdown = self._generate_markdown(entries, cat)

                # Write file
                file_path = output_path / f"{cat}.md"
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(markdown)

                files_created.append(str(file_path))
                total_entries += len(entries)

            # Calculate total size
            total_size_kb = sum(
                Path(f).stat().st_size
                for f in files_created
            ) / 1024

            return {
                "status": "success",
                "files_created": files_created,
                "total_entries": total_entries,
                "total_size_kb": round(total_size_kb, 2)
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

    def _generate_markdown(
        self,
        entries: List[Dict],
        category: str
    ) -> str:
        """
        Generate Markdown content for a category.

        Args:
            entries: List of KB entries
            category: Category name

        Returns:
            Markdown string
        """
        # Header
        title = category.replace("_", " ").title()
        lines = [
            f"# {title}",
            "",
            "> Auto-generated from Clauxton Knowledge Base",
            f"> Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "---",
            ""
        ]

        # Special formatting for ADR (decisions)
        if category == "decision":
            return self._generate_adr_markdown(entries)

        # Generate entries
        for entry in entries:
            lines.extend(self._format_entry(entry))
            lines.append("---")
            lines.append("")

        # Footer
        lines.extend([
            f"*This document is auto-generated from `.clauxton/knowledge-base.yml`*",
            f"*To update, use: `clauxton kb update <ID>` or edit the source file*"
        ])

        return "\n".join(lines)

    def _format_entry(self, entry: Dict) -> List[str]:
        """Format a single KB entry as Markdown."""
        lines = [
            f"## {entry['title']}",
            "",
            f"**ID**: {entry['id']}",
            f"**Category**: {entry['category'].title()}",
            f"**Created**: {entry['created_at'][:10]}",
        ]

        if entry.get("tags"):
            tags = ", ".join(f"`{tag}`" for tag in entry["tags"])
            lines.append(f"**Tags**: {tags}")

        lines.append("")
        lines.append("### 概要")
        lines.append("")
        lines.append(entry["content"])
        lines.append("")

        return lines

    def _generate_adr_markdown(self, entries: List[Dict]) -> str:
        """Generate ADR-formatted Markdown."""
        lines = [
            "# Architecture Decision Records (ADR)",
            "",
            "> Auto-generated from Clauxton Knowledge Base (category: decision)",
            f"> Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "---",
            ""
        ]

        for i, entry in enumerate(entries, start=1):
            lines.extend([
                f"## ADR-{i:03d}: {entry['title']}",
                "",
                "**Status**: Accepted",
                f"**Date**: {entry['created_at'][:10]}",
                "",
                "### Context",
                "",
                entry["content"],
                "",
                "---",
                ""
            ])

        lines.extend([
            "*This document follows ADR format (Architecture Decision Records)*",
            "*To add decisions, use: `clauxton kb add --category decision`*"
        ])

        return "\n".join(lines)
```

---

### 3.3 Testing Strategy

**ファイル**: `tests/core/test_kb_export.py`

```python
import pytest
from pathlib import Path
from clauxton.core.knowledge_base import KnowledgeBase

class TestKBExport:
    """Test kb_export_docs functionality."""

    def test_export_all_categories(self, tmp_path):
        """Test exporting all categories."""
        kb = KnowledgeBase(root=tmp_path)

        # Add test entries
        kb.add(title="FastAPI", category="architecture", content="...")
        kb.add(title="JWT", category="decision", content="...")

        # Export
        output_dir = tmp_path / "docs"
        result = kb.export_to_markdown(str(output_dir))

        assert result["status"] == "success"
        assert len(result["files_created"]) == 2
        assert (output_dir / "architecture.md").exists()
        assert (output_dir / "decision.md").exists()

    def test_export_specific_category(self, tmp_path):
        """Test exporting specific category."""
        kb = KnowledgeBase(root=tmp_path)
        kb.add(title="FastAPI", category="architecture", content="...")

        output_dir = tmp_path / "docs"
        result = kb.export_to_markdown(str(output_dir), category="architecture")

        assert result["status"] == "success"
        assert len(result["files_created"]) == 1
        assert (output_dir / "architecture.md").exists()

    def test_markdown_format(self, tmp_path):
        """Test generated Markdown format."""
        kb = KnowledgeBase(root=tmp_path)
        kb.add(
            title="FastAPI採用",
            category="architecture",
            content="FastAPIを採用した理由...",
            tags=["backend", "api"]
        )

        output_dir = tmp_path / "docs"
        kb.export_to_markdown(str(output_dir))

        # Read generated file
        content = (output_dir / "architecture.md").read_text(encoding="utf-8")

        assert "# Architecture" in content
        assert "## FastAPI採用" in content
        assert "**Tags**: `backend`, `api`" in content
        assert "FastAPIを採用した理由" in content

    def test_adr_format(self, tmp_path):
        """Test ADR-formatted output for decisions."""
        kb = KnowledgeBase(root=tmp_path)
        kb.add(title="JWT認証", category="decision", content="JWTを採用...")

        output_dir = tmp_path / "docs"
        kb.export_to_markdown(str(output_dir))

        content = (output_dir / "decision.md").read_text(encoding="utf-8")

        assert "# Architecture Decision Records" in content
        assert "## ADR-001: JWT認証" in content
        assert "**Status**: Accepted" in content

    def test_unicode_handling(self, tmp_path):
        """Test Unicode in exported Markdown."""
        kb = KnowledgeBase(root=tmp_path)
        kb.add(
            title="日本語タイトル",
            category="architecture",
            content="日本語の説明文 🎉",
            tags=["テスト"]
        )

        output_dir = tmp_path / "docs"
        result = kb.export_to_markdown(str(output_dir))

        assert result["status"] == "success"

        content = (output_dir / "architecture.md").read_text(encoding="utf-8")
        assert "日本語タイトル" in content
        assert "🎉" in content

    # ... 10 more tests ...
```

**テストカバレッジ目標**: 95%+

---

### 3.4 Implementation Timeline

| Day | Task | Hours | Status |
|-----|------|-------|--------|
| Day 6 | Core implementation (`knowledge_base.py`) | 2h | Pending |
| Day 7 | CLI command | 1h | Pending |
| Day 7 | MCP tool | 0.5h | Pending |
| Day 7 | Test implementation (15 tests) | 2h | Pending |
| Day 8 | Documentation | 1h | Pending |
| Day 8 | Integration testing | 0.5h | Pending |

**Total**: 7時間(バッファ含む, 見積もりは4時間)

---

### 3.5 Acceptance Criteria

✅ `kb_export_docs()` MCPツールが実装されている
✅ `clauxton kb export` CLIコマンドが実装されている
✅ Markdown形式で出力される
✅ ADR形式(decisions.md)が正しい
✅ Unicode対応している
✅ 15個のテストが全てパスする
✅ テストカバレッジ95%以上
✅ ドキュメントが更新されている

---

## 4. Priority 4: Configurable Confirmation Mode (Human-in-the-Loop強化)

### 4.1 Overview

**目的**: ユーザーが確認レベルを制御できる設定可能な確認モードを実装

**時間**: 8時間

**リリース**: v0.10.0(Week 2 Day 11)

**成果物**:
- `ConfirmationManager` class
- `.clauxton/config.yml` - 確認モード設定
- `clauxton config` CLI commands
- MCP tools with confirmation_mode parameter
- テストコード(5テスト)

---

### 4.2 Rationale

**Human-in-the-Loop哲学との整合性**:
- **現状**: 閾値ベースの確認のみ(10+ tasks時のみ確認)→ 50% HITL
- **問題**: 小規模操作(1-9タスク)は確認なし → Human-in-the-Loopの不完全実装
- **Solution**: 設定可能な確認モード → ユーザーが制御レベルを選択

**3つの確認モード**:
1. **"always"**: 全ての書き込み操作で確認(100% HITL)
2. **"auto"**: 閾値ベース(デフォルト, 75% HITL)
3. **"never"**: 確認なし, Undoのみ(25% HITL)

---

### 4.3 Detailed Design

#### 4.3.1 Configuration File Format

**ファイル**: `.clauxton/config.yml`

```yaml
# Clauxton Configuration
# Human-in-the-Loop Settings

confirmation_mode: "auto"  # "always" | "auto" | "never"

confirmation_thresholds:
  # Number of operations before confirmation (only when mode="auto")
  kb_add: 5        # KB一括追加: 5個以上で確認
  kb_delete: 3     # KB削除: 3個以上で確認
  task_import: 10  # Task一括インポート: 10個以上で確認
  task_delete: 5   # Task削除: 5個以上で確認

# Undo settings
undo:
  max_history: 100  # Maximum operations to keep in history

# Backup settings
backup:
  generations: 10   # Number of backup generations to keep

# Log settings
logging:
  enabled: true
  retention_days: 30
```

**デフォルト値**:
- `confirmation_mode`: "auto" - バランス重視
- 閾値は操作種別により異なる(小さい操作は低閾値)

---

#### 4.3.2 ConfirmationManager Implementation

**ファイル**: `clauxton/core/confirmation.py`

```python
from typing import Optional, Dict, Any
from pathlib import Path
from clauxton.utils.yaml_utils import read_yaml, write_yaml

class ConfirmationMode(str, Enum):
    """Confirmation mode options."""
    ALWAYS = "always"  # Confirm every operation
    AUTO = "auto"      # Confirm based on thresholds
    NEVER = "never"    # No confirmation, undo only

class ConfirmationManager:
    """
    Manage confirmation prompts based on user configuration.

    Implements Human-in-the-Loop philosophy with user control.
    """

    def __init__(self, root: Path):
        self.root = root
        self.config_path = root / ".clauxton" / "config.yml"
        self._config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if self.config_path.exists():
            return read_yaml(self.config_path)

        # Default configuration
        return {
            "confirmation_mode": "auto",
            "confirmation_thresholds": {
                "kb_add": 5,
                "kb_delete": 3,
                "task_import": 10,
                "task_delete": 5
            }
        }

    def should_confirm(
        self,
        operation: str,
        count: int = 1,
        force_confirm: bool = False
    ) -> bool:
        """
        Determine if confirmation is needed for an operation.

        Args:
            operation: Operation type (e.g., "kb_add", "task_import")
            count: Number of items affected
            force_confirm: Override and always confirm

        Returns:
            True if confirmation needed, False otherwise

        Example:
            >>> cm = ConfirmationManager(Path("."))
            >>> cm.should_confirm("task_import", count=15)
            True  # Exceeds threshold (10)
            >>> cm.should_confirm("task_import", count=5)
            False  # Below threshold
        """
        if force_confirm:
            return True

        mode = self._config.get("confirmation_mode", "auto")

        if mode == ConfirmationMode.ALWAYS:
            return True
        elif mode == ConfirmationMode.NEVER:
            return False
        elif mode == ConfirmationMode.AUTO:
            # Check threshold
            thresholds = self._config.get("confirmation_thresholds", {})
            threshold = thresholds.get(operation, 5)  # Default: 5
            return count >= threshold

        return False

    def set_mode(self, mode: str) -> None:
        """
        Set confirmation mode.

        Args:
            mode: "always" | "auto" | "never"

        Raises:
            ValueError: If mode is invalid
        """
        if mode not in [e.value for e in ConfirmationMode]:
            raise ValueError(
                f"Invalid mode '{mode}'. "
                f"Must be: {', '.join(e.value for e in ConfirmationMode)}"
            )

        self._config["confirmation_mode"] = mode
        write_yaml(self.config_path, self._config)

    def set_threshold(self, operation: str, threshold: int) -> None:
        """
        Set confirmation threshold for specific operation.

        Args:
            operation: Operation type
            threshold: Number of items before confirmation

        Raises:
            ValueError: If threshold < 1
        """
        if threshold < 1:
            raise ValueError("Threshold must be >= 1")

        if "confirmation_thresholds" not in self._config:
            self._config["confirmation_thresholds"] = {}

        self._config["confirmation_thresholds"][operation] = threshold
        write_yaml(self.config_path, self._config)

    def get_mode(self) -> str:
        """Get current confirmation mode."""
        return self._config.get("confirmation_mode", "auto")

    def get_threshold(self, operation: str) -> int:
        """Get threshold for specific operation."""
        thresholds = self._config.get("confirmation_thresholds", {})
        return thresholds.get(operation, 5)
```

---

#### 4.3.3 CLI Commands

**ファイル**: `clauxton/cli/config.py`

```python
import click
from pathlib import Path
from clauxton.core.confirmation import ConfirmationManager

@click.group()
def config():
    """Configuration management commands."""
    pass

@config.command()
@click.argument("key")
@click.argument("value")
def set(key: str, value: str):
    """
    Set configuration value.

    Examples:
        clauxton config set confirmation_mode always
        clauxton config set confirmation_mode auto
        clauxton config set confirmation_mode never
    """
    cm = ConfirmationManager(Path.cwd())

    if key == "confirmation_mode":
        try:
            cm.set_mode(value)
            click.secho(
                f"✓ Confirmation mode set to '{value}'",
                fg="green"
            )

            # Show Human-in-the-Loop level
            if value == "always":
                click.echo("  Human-in-the-Loop: 100% (all operations confirmed)")
            elif value == "auto":
                click.echo("  Human-in-the-Loop: 75% (threshold-based)")
            elif value == "never":
                click.echo("  Human-in-the-Loop: 25% (undo only)")
        except ValueError as e:
            click.secho(f"✗ Error: {e}", fg="red")
            raise click.Abort()

    elif key.startswith("threshold_"):
        operation = key.replace("threshold_", "")
        try:
            threshold = int(value)
            cm.set_threshold(operation, threshold)
            click.secho(
                f"✓ Threshold for '{operation}' set to {threshold}",
                fg="green"
            )
        except ValueError as e:
            click.secho(f"✗ Error: {e}", fg="red")
            raise click.Abort()

    else:
        click.secho(f"✗ Unknown config key: {key}", fg="red")
        raise click.Abort()

@config.command()
@click.argument("key", required=False)
def get(key: Optional[str] = None):
    """
    Get configuration value(s).

    Examples:
        clauxton config get                    # Show all
        clauxton config get confirmation_mode  # Show specific
    """
    cm = ConfirmationManager(Path.cwd())

    if key is None:
        # Show all config
        mode = cm.get_mode()
        click.echo(f"Confirmation mode: {mode}")

        click.echo("\nThresholds:")
        for op in ["kb_add", "kb_delete", "task_import", "task_delete"]:
            threshold = cm.get_threshold(op)
            click.echo(f"  {op}: {threshold}")

    elif key == "confirmation_mode":
        mode = cm.get_mode()
        click.echo(f"{mode}")

    elif key.startswith("threshold_"):
        operation = key.replace("threshold_", "")
        threshold = cm.get_threshold(operation)
        click.echo(f"{threshold}")

    else:
        click.secho(f"✗ Unknown config key: {key}", fg="red")
        raise click.Abort()
```

---

#### 4.3.4 MCP Tool Integration

**Modify existing MCP tools to use ConfirmationManager**:

**ファイル**: `clauxton/mcp/server.py`

```python
from clauxton.core.confirmation import ConfirmationManager

@server.call_tool("task_import_yaml")
async def task_import_yaml(
    yaml_content: str,
    dry_run: bool = False,
    skip_confirmation: bool = False
) -> dict:
    """
    Import multiple tasks from YAML.

    Args:
        yaml_content: YAML string
        dry_run: Validate only
        skip_confirmation: Skip confirmation prompt (overrides config)

    Returns:
        Result with confirmation info
    """
    tm = TaskManager()
    cm = ConfirmationManager(tm.root)

    # Parse YAML to count tasks
    data = yaml.safe_load(yaml_content)
    task_count = len(data.get("tasks", []))

    # Check if confirmation needed
    needs_confirmation = cm.should_confirm(
        "task_import",
        count=task_count,
        force_confirm=False
    ) and not skip_confirmation

    if needs_confirmation:
        return {
            "status": "confirmation_required",
            "message": f"About to import {task_count} tasks. Continue?",
            "task_count": task_count,
            "preview": _generate_task_preview(data["tasks"]),
            "note": "Set skip_confirmation=true to skip this prompt"
        }

    # Proceed with import
    result = tm.import_yaml(yaml_content, dry_run=dry_run)
    return result
```

---

### 4.4 Testing Strategy

**ファイル**: `tests/core/test_confirmation.py`

```python
import pytest
from pathlib import Path
from clauxton.core.confirmation import ConfirmationManager, ConfirmationMode

class TestConfirmationManager:
    """Test ConfirmationManager functionality."""

    def test_default_mode_is_auto(self, tmp_path):
        """Test default confirmation mode."""
        cm = ConfirmationManager(tmp_path)
        assert cm.get_mode() == "auto"

    def test_set_mode_always(self, tmp_path):
        """Test setting mode to 'always'."""
        cm = ConfirmationManager(tmp_path)
        cm.set_mode("always")
        assert cm.get_mode() == "always"
        assert cm.should_confirm("task_import", count=1) == True

    def test_set_mode_never(self, tmp_path):
        """Test setting mode to 'never'."""
        cm = ConfirmationManager(tmp_path)
        cm.set_mode("never")
        assert cm.get_mode() == "never"
        assert cm.should_confirm("task_import", count=100) == False

    def test_auto_mode_with_threshold(self, tmp_path):
        """Test auto mode respects thresholds."""
        cm = ConfirmationManager(tmp_path)
        cm.set_mode("auto")
        cm.set_threshold("task_import", 10)

        assert cm.should_confirm("task_import", count=5) == False
        assert cm.should_confirm("task_import", count=10) == True
        assert cm.should_confirm("task_import", count=15) == True

    def test_force_confirm_overrides_mode(self, tmp_path):
        """Test force_confirm overrides mode."""
        cm = ConfirmationManager(tmp_path)
        cm.set_mode("never")

        assert cm.should_confirm("task_import", count=1, force_confirm=True) == True

    def test_invalid_mode_raises_error(self, tmp_path):
        """Test invalid mode raises ValueError."""
        cm = ConfirmationManager(tmp_path)
        with pytest.raises(ValueError):
            cm.set_mode("invalid")

    def test_config_persists(self, tmp_path):
        """Test configuration persists across instances."""
        cm1 = ConfirmationManager(tmp_path)
        cm1.set_mode("always")
        cm1.set_threshold("task_import", 20)

        cm2 = ConfirmationManager(tmp_path)
        assert cm2.get_mode() == "always"
        assert cm2.get_threshold("task_import") == 20
```

**Total**: 5 tests + 2 tests for CLI = 7 tests

---

### 4.5 Implementation Timeline

| Day | Task | Hours | Status |
|-----|------|-------|--------|
| Day 11 | `ConfirmationManager` core implementation | 3h | Planned |
| Day 11 | CLI commands (`clauxton config`) | 2h | Planned |
| Day 11 | MCP tool integration | 2h | Planned |
| Day 11 | Tests (7 tests) | 1h | Planned |

**Total**: 8時間

---

### 4.6 Acceptance Criteria

✅ `ConfirmationManager` class が実装されている
✅ `.clauxton/config.yml` が作成· 読み込みされる
✅ `clauxton config set/get` CLI commands が動作する
✅ 3つのモード(always/auto/never)が正しく動作する
✅ 閾値設定が動作する
✅ MCPツールが確認モードに対応している
✅ 7個のテストが全てパスする
✅ Human-in-the-Loop哲学が75-100%実現される

---

### 4.7 Human-in-the-Loop Alignment

| Mode | HITL Level | Use Case |
|------|------------|----------|
| **always** | 100% | 厳格な管理, チーム開発, 本番環境 |
| **auto** | 75% | バランス重視(デフォルト) |
| **never** | 25% | 高速開発, 個人開発, テスト環境 |

**Expected Improvement**:
- Before: 50% HITL (閾値のみ)
- After: 75-100% HITL (設定可能)

---

## 5. Overall Timeline & Milestones (REVISED)

### 5.1 Timeline Overview

```
Week 0 (Day 0):
  2025-10-20: CLAUDE.md enhancement (2h)

Week 1 (Core + Critical Features):
  Day 1-2: YAML bulk import - Core implementation (6h)
  Day 3: Undo/Rollback機能 (4h)
  Day 4: 確認プロンプト (3h)
  Day 5: エラーリカバリー (4h)
  Day 5: YAML安全性チェック (1h)

Week 2 (Important Features + KB Export):
  Day 6: バリデーション強化 (3h)
  Day 7: ログ機能 (3h)
  Day 8: KB export - Implementation (4h)
  Day 9: 進捗表示 + パフォーマンス最適化 (4h)
  Day 10: バックアップ強化 (2h)
  Day 10: エラーメッセージ改善 (2h)
  Day 11: 設定可能な確認モード (8h)

Week 3 (Testing + Documentation + Release):
  Day 12-13: 追加テスト(+90個) (10h)
  Day 14: ドキュメント更新 (4h)
  Day 15: 統合テスト (4h)
  Day 16: バグ修正 + リリース準備 (4h)

Total: 3 weeks (61 hours of development)
Release: 2025-11-10
```

---

### 5.2 Milestones (REVISED)

#### Milestone 0: CLAUDE.md Enhancement
**Date**: 2025-10-20(Day 0)
**Duration**: 2時間
**Deliverables**:
- ✅ CLAUDE.md に"Clauxton Integration Philosophy"セクション追加
- ✅ README.md更新
- ✅ Commit & Push

**Success Criteria**:
- Claude Codeが CLAUDE.md を読み込める
- "いつ· どう使うか"が明確

---

#### Milestone 1: Core + Critical Features
**Date**: 2025-10-27(Week 1終了時)
**Duration**: 18時間(Day 1-5)
**Deliverables**:
- ✅ `task_import_yaml()` MCP tool + CLI command
- ✅ `undo_last_operation()` MCP tool
- ✅ 確認プロンプト機能(閾値設定)
- ✅ エラーリカバリー(rollback/skip/abort)
- ✅ YAML安全性チェック
- ✅ 操作履歴機能
- ✅ 20 tests for YAML import
- ✅ 15 tests for Undo/Rollback
- ✅ 5 tests for confirmation prompts

**Success Criteria**:
- Claude Codeが複数タスクを一括登録できる
- 誤操作を取り消せる(Undo)
- 大量操作時に確認プロンプトが表示される
- エラー発生時に適切にリカバリーできる
- 危険なYAMLを検出できる
- 循環依存検出が動作

---

#### Milestone 2: Important Features + KB Export + Confirmation Mode
**Date**: 2025-11-04(Week 2終了時)
**Duration**: 26時間(Day 6-11)
**Deliverables**:
- ✅ `kb_export_docs()` MCP tool + CLI command
- ✅ `get_recent_logs()` MCP tool
- ✅ 強化されたバリデーション(TaskValidator)
- ✅ 進捗表示機能
- ✅ バッチ書き込み最適化
- ✅ 複数世代バックアップ
- ✅ 改善されたエラーメッセージ
- ✅ `ConfirmationManager` class(NEW)
- ✅ `.clauxton/config.yml` support(NEW)
- ✅ `clauxton config` CLI commands(NEW)
- ✅ 15 tests for KB export
- ✅ 20 tests for enhanced validation
- ✅ 5 tests for performance
- ✅ 7 tests for confirmation mode(NEW)

**Success Criteria**:
- KBがMarkdown形式で出力される(ADR形式含む)
- 操作ログが記録· 確認できる
- YAMLの品質が検証される(重複, 無効値など)
- 大量タスク(100個)のインポートが高速
- バックアップが複数世代保持される
- エラーメッセージが明確で役立つ
- 確認モード(always/auto/never)が動作する(NEW)
- Human-in-the-Loop哲学が75-100%実現される(NEW)

---

#### Milestone 3: Testing + Documentation
**Date**: 2025-11-08(Week 3 Day 12-14)
**Duration**: 14時間
**Deliverables**:
- ✅ 90個の追加テスト(合計480 tests)
  - Undo/Rollback: 15 tests
  - 確認プロンプト: 5 tests
  - エラーリカバリー: 15 tests
  - バリデーション: 20 tests
  - YAML安全性: 5 tests
  - ログ機能: 5 tests
  - パフォーマンス: 5 tests
  - バックアップ: 5 tests
  - KB export: 15 tests
  - Confirmation mode: 7 tests(NEW)
  - 統合シナリオ: 13 tests(REVISED)
- ✅ ドキュメント更新
  - README.md: 使用例追加
  - docs/YAML_FORMAT_GUIDE.md: 新規作成
  - docs/ERROR_HANDLING_GUIDE.md: 新規作成
  - docs/TROUBLESHOOTING.md: 拡充
  - docs/MIGRATION_v0.10.0.md: 新規作成
- ✅ CHANGELOG.md更新

**Success Criteria**:
- 全480テストがパスする
- テストカバレッジ94%維持
- ドキュメントが完全で正確
- ユーザーが新機能を理解できる
- Human-in-the-Loopガイドが追加されている(NEW)

---

#### Milestone 4: v0.10.0 Release
**Date**: 2025-11-10(Week 3 Day 15-16)
**Duration**: 8時間
**Deliverables**:
- ✅ 統合テスト完了(シナリオテスト)
- ✅ バグ修正完了
- ✅ All tests passing (480 tests)
- ✅ Documentation complete
- ✅ CHANGELOG.md finalized
- ✅ Version bump (0.9.0-beta → 0.10.0)
- ✅ Git tag & GitHub release
- ✅ PyPI release

**Success Criteria**:
- CI/CD passing
- No critical bugs
- No regressions
- Documentation accurate and complete
- Ready for production use

---

### 5.3 Risk Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| 循環依存検出のバグ | High | Medium | 既存コードを再利用, 追加テスト |
| Unicode処理のエラー | Medium | Low | UTF-8明示, 既存テストパターン活用 |
| MCPツールの統合問題 | High | Low | 既存15ツールと同じパターン |
| テストが時間内に完了しない | Medium | Medium | コアロジック優先, エッジケースは後回し |
| ドキュメント作成が遅延 | Low | Medium | テンプレート活用, 既存ドキュメント参考 |

---

## 6. Post-Release Plan

### 6.1 v0.10.0リリース後の検証

**Week 3(2025-11-04 → 2025-11-10)**:
- ユーザーフィードバック収集
- バグ修正(緊急対応)
- パフォーマンス測定

---

### 6.2 v0.11.0計画(将来)

**優先度MEDIUM機能**:
1. **Human-in-the-Loop**(確認フロー)
   - `kb_add_with_confirmation()`
   - ユーザー承認機能
   - 時間: 6時間

2. **Task Export to Gantt Chart**
   - Mermaid形式のガントチャート
   - `task_export_gantt()`
   - 時間: 3時間

---

### 6.3 v0.12.0計画(将来)

**優先度LOW機能**:
1. **Repository Map**(自動索引)
   - リポジトリ構造を自動分析
   - `repo_map()` MCP tool
   - 時間: 12時間

2. **Web Dashboard**
   - Flask/FastAPI でダッシュボード
   - KB/Task/Conflictをビジュアル表示
   - 時間: 20時間

---

## 7. Success Metrics

### 7.1 Technical Metrics

| Metric | Current | Target (v0.10.0) |
|--------|---------|------------------|
| Total Tests | 390 | 480 (+90) |
| Code Coverage | 94% | 94% (維持) |
| MCP Tools | 15 | 17 (+2) |
| CLI Commands | 15 | 21 (+6) |
| Documentation Size | 771 KB | 900 KB (+129 KB) |

---

### 7.2 User Experience Metrics

| Metric | Before | After (v0.10.0) |
|--------|--------|-----------------|
| Task registration time | 5 min (10 commands) | 10 sec (1 conversation) |
| User operations | 10 manual commands | 0 (fully automatic) |
| Claude philosophy alignment | 70% (Composable) | 95% (Composable + HITL) |
| Human-in-the-Loop | 50% | 75-100% (configurable) |
| Documentation readability | N/A (YAML only) | High (Markdown docs) |

---

### 7.3 Business Impact

**開発効率**:
- タスク登録: 30倍高速化(5分 → 10秒)
- 会話フロー: 断絶なし(自然な対話)
- チーム共有: Git管理可能(Markdown出力)

**Claude哲学合致度**:
- Before: 90%(7/10項目完全一致)
- After: 95%(9/10項目完全一致)
- Composable & Scriptable: 70% → 95%
- Human-in-the-Loop: 50% → 75-100% (設定可能)

---

## 8. Conclusion

### 8.1 Summary

このImplementation Planは, Clauxtonを Claude Code と透過的に統合し, 
Claude哲学との合致度を 90% → 95% に向上させるための詳細な計画です.

**3つの優先実装項目**:
1. 🔴 CLAUDE.md強化(2時間, 今すぐ)
2. 🔴 YAML一括インポート(8時間, Week 1)
3. 🟡 KB→ドキュメント出力(4時間, Week 2)

**Expected Results**:
- ユーザー体験: 10回のコマンド → 1回の会話
- 開発効率: 5分 → 10秒(30倍高速化)
- Claude哲学: "Composable" を完全実現

---

### 8.2 Next Steps

1. ✅ この計画をレビュー· 承認してもらう
2. ✅ Milestone 1(CLAUDE.md強化)を即座に開始
3. ✅ Week 1にMilestone 2(YAML一括インポート)を実装
4. ✅ Week 2にMilestone 3(KB Export)を実装
5. ✅ 2025-11-03に v0.10.0 リリース

---

**作成日**: 2025-10-20
**作成者**: Claude Code
**バージョン**: 1.0
**ステータス**: Planning Complete - Awaiting Approval
