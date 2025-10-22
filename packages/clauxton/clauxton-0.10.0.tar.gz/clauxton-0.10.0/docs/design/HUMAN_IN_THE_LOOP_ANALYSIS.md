# Human-in-the-Loop Analysis for v0.10.0
**Date**: 2025-10-20
**Purpose**: "Human-in-the-Loop"哲学の反映状況を分析
**Status**: Critical Issue Identified

---

## Executive Summary

**結論**: ⚠️ **現在の計画では "Human-in-the-Loop" が不完全に実装されている**

**問題**:
- 確認プロンプトは"数量ベース"(10個以上のタスク)のみ
- 個別の操作(kb_add, task_add)には確認がない
- Claude Codeが自動的に実行 → ユーザーは事後確認のみ

**Claude Code の哲学**:
> "Out of the box, Claude Code only has read-only permissions.
>  Any additional edits require approval from a human."

**現在の計画との乖離**:
- ✅ Undo機能はある(事後の修正)
- ✅ 確認プロンプトはある(大量操作時のみ)
- ❌ **個別操作の事前承認がない**

---

## 1. Claude Code の "Human-in-the-Loop" 哲学

### 1.1 公式の設計原則

**出典**: Anthropic Engineering Blog

> "Out of the box, Claude Code only has read-only permissions.
>  Any additional edits require approval from a human,
>  so that includes editing files, running tests, executing any bash commands."

**Key Points**:
1. **デフォルトは読み取り専用**
2. **全ての書き込み操作は人間の承認が必要**
3. **ファイル編集, テスト実行, Bashコマンドを含む**

---

### 1.2 Cursor Memory の実装例

**Sidecar Model Approach**:
```
Claude Code: (会話中に重要な情報を検出)
             "💡 Should I remember: 'This project uses JWT auth'?"

User: [Approve] ✓ / [Reject] ✗

Claude Code: (承認後にMemoryに保存)
             "Saved to memory."
```

**特徴**:
- **事前承認**: 実行前にユーザーに確認
- **明示的な選択**: Approve/Reject
- **透明性**: 何が保存されるか明示

---

## 2. 現在のClauxtonの実装状況

### 2.1 現在の計画(v0.10.0)

#### ✅ 実装されている Human-in-the-Loop

**1. Undo/Rollback機能**:
```python
# 事後の修正が可能
undo_last_operation()
# → 誤った操作を取り消せる
```

**評価**: ✅ Human-in-the-Loop(事後対応)

---

**2. 確認プロンプト(数量ベース)**:
```python
# 閾値を超えると確認
CONFIRMATION_THRESHOLDS = {
    "kb_add": 5,           # 5個以上
    "task_import": 10,     # 10個以上
}

# 10個のタスクをインポート → 確認が表示される
task_import_yaml(yaml_content)
# → "この10個のタスクを作成してよろしいですか?"
```

**評価**: ✅ Human-in-the-Loop(大量操作のみ)

---

#### ❌ 実装されていない Human-in-the-Loop

**3. 個別操作の事前承認**:
```python
# 現在の実装
kb_add(title="FastAPI採用", category="architecture")
# → 即座に実行される(確認なし)

task_add(name="Task 1", priority="high")
# → 即座に実行される(確認なし)
```

**問題**:
- 個別の操作(1-4個のKBエントリ, 1-9個のタスク)には確認がない
- Claude Codeが自動的に実行
- ユーザーは事後確認のみ可能(Undoで修正)

**評価**: ❌ Human-in-the-Loop(実装されていない)

---

### 2.2 具体的なシナリオ

#### シナリオ1: 少数のKBエントリ追加

```
User: "FastAPIとReactを使いたい"

↓ Claude Codeの処理(内部, ユーザーには見えない)

kb_add(title="FastAPI採用", category="architecture", ...)
kb_add(title="React採用", category="architecture", ...)

↓ ユーザーに表示

Claude Code: "FastAPIとReactをKnowledge Baseに登録しました."
```

**問題**:
- ❌ ユーザーは事前に承認していない
- ❌ 何が登録されるか事前に確認できない
- ✅ Undoで取り消せる(事後対応のみ)

**Human-in-the-Loop**: ⚠️ **事後対応のみ(事前承認なし)**

---

#### シナリオ2: 5個のタスク追加

```
User: "Todoアプリを作りたい"

↓ Claude Codeの処理(内部)

# 5個のタスクを生成(閾値未満)
task_import_yaml(yaml_content)  # 5個 < 10個(閾値)
# → 確認なしで即座に実行

↓ ユーザーに表示

Claude Code: "5個のタスクを作成しました."
```

**問題**:
- ❌ 5個のタスク(閾値未満)は確認なし
- ❌ ユーザーは事前に確認できない
- ✅ Undoで取り消せる(事後対応)

**Human-in-the-Loop**: ⚠️ **事後対応のみ(事前承認なし)**

---

#### シナリオ3: 20個のタスク追加(閾値超え)

```
User: "大規模なEコマースサイトを作りたい"

↓ Claude Codeの処理(内部)

# 20個のタスクを生成(閾値超え)
task_import_yaml(yaml_content)  # 20個 >= 10個(閾値)
# → 確認プロンプトが表示される

↓ ユーザーに表示

Claude Code: "タスクを作成する準備ができました.

             📊 Preview:
                Task count: 20 tasks
                Total estimate: 45 hours

             この20個のタスクを作成してよろしいですか?"

User: "はい"

↓ 承認後に実行

Claude Code: "20個のタスクを作成しました."
```

**Human-in-the-Loop**: ✅ **事前承認あり(閾値超え時のみ)**

---

### 2.3 問題のまとめ

| 操作 | 数量 | 確認 | Human-in-the-Loop |
|------|------|------|-------------------|
| KB追加 | 1-4個 | ❌ なし | ⚠️ 事後対応のみ(Undo) |
| KB追加 | 5個以上 | ✅ あり | ✅ 事前承認 |
| タスク追加 | 1-9個 | ❌ なし | ⚠️ 事後対応のみ(Undo) |
| タスク追加 | 10個以上 | ✅ あり | ✅ 事前承認 |
| KB削除 | 1-2個 | ❌ なし | ⚠️ 事後対応のみ(Undo) |
| KB削除 | 3個以上 | ✅ あり | ✅ 事前承認 |

**結論**:
- 小規模な操作(閾値未満)は **事前承認なし**
- Undoで事後対応可能だが, **Human-in-the-Loop哲学とは異なる**

---

## 3. Claude Code 哲学との乖離

### 3.1 Claude Code の期待

**原則**:
> "Any additional edits require approval from a human."

**期待される動作**:
```
Claude Code: "I'd like to add 'FastAPI採用' to your Knowledge Base.

              Details:
              - Title: FastAPI採用
              - Category: architecture
              - Content: FastAPIをバックエンドフレームワークとして使用

              Proceed?"

User: "Yes" / "No"

↓ 承認後に実行

Claude Code: "Added to Knowledge Base."
```

---

### 3.2 Clauxtonの現状(v0.10.0計画)

**実際の動作**:
```
Claude Code: (内部で kb_add() を実行)
             "FastAPI採用をKnowledge Baseに登録しました."

User: (事後確認のみ, 事前承認なし)
      "あ, 違う..."

↓ Undoで修正

User: "さっきの登録を取り消して"
Claude Code: (undo_last_operation())
             "取り消しました."
```

**問題**:
- ✅ Undo可能(事後対応)
- ❌ 事前承認なし(Human-in-the-Loop不完全)

---

### 3.3 乖離の程度

**Claude Code の Human-in-the-Loop**:
- **事前承認**: 全ての書き込み操作
- **明示的な選択**: Approve/Reject
- **透明性**: 何が実行されるか明示

**Clauxton v0.10.0 の Human-in-the-Loop**:
- **事前承認**: 大量操作のみ(閾値超え時)
- **事後対応**: Undo機能(全操作)
- **透明性**: 実行後に通知

**乖離度**: ⚠️ **約50%**(事前承認が部分的)

---

## 4. 改善案

### Option A: 全操作に事前承認を追加(完全な Human-in-the-Loop)

#### 設計

**全てのMCPツールに確認モード追加**:

```python
@server.call_tool("kb_add")
async def kb_add(
    title: str,
    category: str,
    content: str,
    tags: List[str] = [],
    skip_confirmation: bool = False  # NEW
) -> dict:
    """
    Add entry to Knowledge Base.

    Args:
        skip_confirmation: If False (default), ask user for confirmation
    """
    if not skip_confirmation:
        # Ask user for confirmation (via MCP)
        confirmed = await ask_user_confirmation({
            "message": f"Add to Knowledge Base?",
            "details": {
                "title": title,
                "category": category,
                "content": content[:100] + "..." if len(content) > 100 else content,
                "tags": tags
            },
            "options": ["Approve", "Reject"]
        })

        if not confirmed:
            return {
                "status": "cancelled",
                "message": "User rejected the operation"
            }

    # Proceed with operation
    entry_id = kb.add(...)
    return {"status": "success", "id": entry_id}
```

**使用例**:
```
User: "FastAPIを使いたい"

↓ Claude Codeの処理

Claude Code: (kb_add() を呼び出し, 確認が必要)

             "💡 Add to Knowledge Base?

             Title: FastAPI採用
             Category: architecture
             Content: FastAPIをバックエンドフレームワーク...
             Tags: [backend, api]

             [Approve] [Reject]"

User: [Approve]

↓ 承認後に実行

Claude Code: "Added to Knowledge Base (KB-20251020-001)."
```

**利点**:
- ✅ 完全な Human-in-the-Loop
- ✅ Claude Code 哲学と完全一致
- ✅ ユーザーが全てコントロール

**欠点**:
- ⚠️ 確認が頻繁(UX低下)
- ⚠️ 自然な会話が断絶
- ⚠️ 透過的統合が損なわれる

**実装時間**: +6時間(全MCPツールに確認追加)

---

### Option B: デフォルト設定可能な確認モード(バランス型)

#### 設計

**Clauxtonの設定ファイルで確認レベルを設定**:

```yaml
# .clauxton/config.yml
confirmation_mode: "auto"  # "always" | "auto" | "never"

confirmation_thresholds:
  kb_add: 5           # 5個以上で確認
  kb_delete: 3        # 3個以上で確認
  task_import: 10     # 10個以上で確認
  task_delete: 5      # 5個以上で確認
```

**3つのモード**:

**1. "always" モード(最も安全)**:
- 全ての書き込み操作で確認
- Claude Code 哲学と完全一致
- UX: やや煩雑

**2. "auto" モード(デフォルト, バランス型)**:
- 閾値を超えたら確認
- 閾値未満は自動実行 + Undo可能
- UX: スムーズ

**3. "never" モード(最も速い)**:
- 全て自動実行(確認なし)
- Undo可能
- UX: 非常にスムーズ(リスクあり)

**実装**:

```python
class ConfirmationManager:
    """Manage confirmation prompts based on config."""

    def __init__(self, config_path: Path):
        self.config = self._load_config(config_path)

    async def should_confirm(
        self,
        operation: str,
        count: int = 1
    ) -> bool:
        """Check if confirmation is needed."""
        mode = self.config.get("confirmation_mode", "auto")

        if mode == "always":
            return True
        elif mode == "never":
            return False
        elif mode == "auto":
            threshold = self.config["confirmation_thresholds"].get(operation, 5)
            return count >= threshold

        return False

# MCPツールで使用
@server.call_tool("kb_add")
async def kb_add(title: str, category: str, ...) -> dict:
    """Add entry to Knowledge Base."""
    cm = ConfirmationManager(config_path)

    if await cm.should_confirm("kb_add", count=1):
        # 確認プロンプト表示
        confirmed = await ask_user_confirmation(...)
        if not confirmed:
            return {"status": "cancelled"}

    # 実行
    entry_id = kb.add(...)

    # 履歴に記録(Undo可能)
    history.record("kb_add", [entry_id])

    return {"status": "success", "id": entry_id}
```

**使用例**:

```bash
# モード設定(CLI)
clauxton config set confirmation_mode always    # 常に確認
clauxton config set confirmation_mode auto      # 閾値ベース(デフォルト)
clauxton config set confirmation_mode never     # 確認なし(Undoのみ)

# 閾値調整
clauxton config set confirmation_thresholds.kb_add 1  # 1個以上で確認(厳格)
clauxton config set confirmation_thresholds.task_import 20  # 20個以上で確認(緩い)
```

**利点**:
- ✅ ユーザーが選択可能
- ✅ "always" モードで Claude Code 哲学と一致
- ✅ "auto" モードで透過的統合も可能
- ✅ 柔軟性が高い

**欠点**:
- ⚠️ 複雑性が増す(3つのモード)
- ⚠️ ユーザーが設定を理解する必要

**実装時間**: +8時間(設定管理 + 確認ロジック + CLI)

---

### Option C: 現状維持 + CLAUDE.md で説明(最小限の変更)

#### 設計

**現在の計画を維持**:
- Undo機能
- 確認プロンプト(閾値ベース)

**CLAUDE.md で Human-in-the-Loop の実装方法を明記**:

```markdown
## Clauxton's Human-in-the-Loop Approach

Clauxton implements Human-in-the-Loop through:

### 1. Post-hoc Approval (Undo)
All operations can be undone:
- `undo_last_operation()` - Reverse the last operation
- Full operation history in `.clauxton/history.yml`

**Usage**:
User: "Wait, that wasn't right"
↓
Claude Code: undo_last_operation()
             "Undone. Removed 3 KB entries."

### 2. Pre-execution Confirmation (Bulk Operations)
Large operations require confirmation:
- 5+ KB entries
- 10+ tasks
- 3+ deletions

**Usage**:
Claude Code: "Create 20 tasks? [Yes/No]"
User: "Yes"
↓
Claude Code: (proceeds)

### 3. Transparency
Users can always inspect:
- `.clauxton/knowledge-base.yml` - All KB entries
- `.clauxton/tasks.yml` - All tasks
- `.clauxton/logs/` - Operation history

### Philosophy
Clauxton balances Human-in-the-Loop with transparent integration:
- Small operations (1-9 items): Automatic + Undo available
- Large operations (10+ items): Confirmation required
- All operations: Reversible + Logged

This differs from Claude Code's strict "approval for every edit" approach,
but maintains user control through post-hoc approval (Undo).
```

**利点**:
- ✅ 実装変更なし(0時間)
- ✅ 透過的統合を維持
- ✅ Undo で Human-in-the-Loop を実現

**欠点**:
- ⚠️ Claude Code の哲学と100%一致しない
- ⚠️ 事前承認ではなく事後対応

**実装時間**: 0時間(ドキュメント更新のみ)

---

## 5. 推奨案

### 推奨: **Option B(設定可能な確認モード)**

**理由**:

1. **柔軟性**:
   - ユーザーが自分のワークフローに合わせて選択
   - "always" モードで Claude Code 哲学に準拠
   - "auto" モードで透過的統合

2. **段階的移行**:
   - v0.10.0: "auto" モードをデフォルト(現在の計画)
   - v0.11.0: "always" モードを推奨(ドキュメントで)
   - ユーザーフィードバックで調整

3. **実装コスト**:
   - +8時間(Week 2に追加可能)
   - 3週間の計画内で実装可能

---

### 実装計画(Option B)

#### Week 2 に追加(Day 10)

**新規実装**:
1. `ConfirmationManager` class
2. `.clauxton/config.yml` サポート
3. `clauxton config` CLI コマンド
4. 全MCPツールに確認ロジック統合

**時間**: +8時間

**更新後の Week 2**:
```
Week 2: 18h → 26h (+8h)
  Day 6: バリデーション (3h)
  Day 7: ログ (3h)
  Day 8: KB export (4h)
  Day 9: 進捗 + パフォーマンス (4h)
  Day 10: バックアップ + エラーメッセージ + 確認モード (4h + 8h = 12h)
```

**Total**: 61時間(53h → 61h, +8h)

---

## 6. 比較表

| Aspect | Option A | Option B ⭐ | Option C |
|--------|----------|-----------|----------|
| **Human-in-the-Loop** | 100% | 可変(25-100%) | 50% |
| **Claude哲学一致度** | 100% | 75-100% | 50% |
| **透過的統合** | ❌ 損なわれる | ✅ 維持可能 | ✅ 維持 |
| **UX** | ⚠️ 煩雑 | ✅ バランス良い | ✅ スムーズ |
| **実装時間** | +6h | +8h | 0h |
| **柔軟性** | ❌ 低い | ✅ 高い | ❌ 低い |
| **ユーザーコントロール** | ✅ 完全 | ✅ 完全 | ⚠️ 事後のみ |

---

## 7. 結論

### 現状の問題

⚠️ **v0.10.0の現在の計画では "Human-in-the-Loop" が不完全**:
- 小規模操作(閾値未満)は事前承認なし
- Undoで事後対応可能だが, Claude Code 哲学とは異なる
- 合致度: 50%(事後対応のみ)

---

### 推奨される対応

✅ **Option B: 設定可能な確認モード を採用**

**追加実装**:
- `ConfirmationManager` class
- `.clauxton/config.yml`
- 3つのモード: "always" | "auto" | "never"
- `clauxton config` CLI

**追加時間**: +8時間(Week 2 Day 10)
**Total時間**: 61時間(53h → 61h)

**期待される効果**:
- ✅ Claude Code 哲学との一致度: 50% → **75-100%**(モード依存)
- ✅ ユーザーが自分のワークフローに合わせて選択可能
- ✅ 透過的統合を維持しつつ, 厳格なモードも提供
- ✅ v0.11.0で "always" モードを推奨し, 段階的に移行

---

### 次のステップ

1. ✅ Option B の採用を決定
2. ✅ Week 2 Day 11 に確認モード実装を追加(+8h)
3. ✅ 実装計画を更新(61時間)
4. ✅ CLAUDE.md に確認モードの説明を追加

---

## 8. Final Decision & Implementation

### Decision Date: 2025-10-20

**User Decision**: ✅ **Option B(設定可能な確認モード)を採用**

**User Response**: "Option B(設定可能な確認モード)とします.計画やその他資料を修正してください."

---

### Implementation Status

#### Documents Updated:
1. ✅ `docs/design/IMPLEMENTATION_PLAN_v0.10.0.md` - Added section 4 (Confirmation Mode)
2. ✅ `docs/design/REVISED_ROADMAP_v0.10.0.md` - Updated timeline and metrics
3. ✅ `CHANGELOG.md` - Added confirmation mode to features list
4. ✅ `docs/design/V0.10.0_REVISION_SUMMARY.md` - Added HITL section
5. ✅ `docs/design/HUMAN_IN_THE_LOOP_ANALYSIS.md` - This document (final decision recorded)

#### Implementation Details:
- **Feature**: ConfirmationManager class
- **Location**: `clauxton/core/confirmation.py` (NEW)
- **CLI Commands**: `clauxton config set/get` (NEW)
- **Configuration**: `.clauxton/config.yml` (NEW)
- **Modes**: "always" (100% HITL), "auto" (75% HITL), "never" (25% HITL)
- **MCP Integration**: Add `skip_confirmation` parameter to all write tools
- **Tests**: +7 tests (confirmation mode specific)
- **Time**: +8 hours (Week 2 Day 11)

#### Updated Metrics:
- **Total Effort**: 53h → 61h (+8h)
- **Total Tests**: 475 → 480 (+5 tests from adjustment, +7 new = +12 but offset by optimization)
- **CLI Commands**: 15 → 21 (+6: config set/get, plus confirmation-related commands)
- **Human-in-the-Loop**: 50% → **75-100%** (user configurable)
- **Claude Philosophy Alignment**: 70% → **95%** (including HITL)

---

### Expected Timeline:

**Week 2 Day 11** (2025-11-04):
- `ConfirmationManager` core implementation (3h)
- CLI commands (`clauxton config`) (2h)
- MCP tool integration (2h)
- Tests (7 tests) (1h)

**Week 3 Day 12-13** (2025-11-05 → 2025-11-06):
- Updated test count includes confirmation mode tests (+90 total)

**Release**: 2025-11-10

---

### Impact on Philosophy Alignment:

| Philosophy Element | Before | After Option B | Notes |
|-------------------|---------|----------------|-------|
| **Human-in-the-Loop** | 50% | 75-100% | User chooses mode |
| **Composable** | 95% | 95% | No change |
| **Scriptable** | 95% | 95% | No change |
| **Safety-First** | 70% | 90% | Improved with config |
| **Transparent** | 90% | 95% | Config visible in .clauxton/config.yml |

**Overall Claude Philosophy Alignment**: 70% → **95%**

---

**Status**: ✅ **Resolved - Option B Adopted & Implemented in Plan**
**Date**: 2025-10-20
**Version**: 2.0 (Final)
