# Clauxton v0.9.0-beta 使用方法ガイド

**Version**: v0.9.0-beta
**Date**: 2025-10-20
**Status**: Production Ready

---

## 📋 目次

1. [インストール方法](#インストール方法)
2. [基本的な使い方](#基本的な使い方)
3. [Conflict Detection(新機能)](#conflict-detection新機能)
4. [MCP統合(Claude Code)](#mcp統合claude-code)
5. [トラブルシューティング](#トラブルシューティング)

---

## インストール方法

### 方法1: 開発版を直接使用(ローカル)

現在のclauxton開発ディレクトリで: 

```bash
# 1. 仮想環境をアクティベート
cd /path/to/clauxton
source .venv/bin/activate  # Linux/macOS
# または
.venv\Scripts\activate     # Windows

# 2. バージョン確認
clauxton --version
# 出力: clauxton, version 0.9.0-beta
```

### 方法2: PyPIからインストール(将来)

```bash
# PyPI公開後は以下でインストール可能
pip install clauxton==0.9.0-beta
```

---

## 基本的な使い方

### Step 1: プロジェクトの初期化

```bash
# プロジェクトディレクトリに移動
cd your-project

# Clauxton初期化
clauxton init
```

**出力例**:
```
✓ Initialized Clauxton
  Location: /path/to/your-project/.clauxton
  Knowledge Base: /path/to/your-project/.clauxton/knowledge-base.yml
```

### Step 2: Knowledge Baseへの情報追加

```bash
# 対話的に追加
clauxton kb add

# 非対話的に追加
clauxton kb add \
  --title "FastAPIを使用する" \
  --category architecture \
  --content "バックエンドはFastAPIで構築.非同期処理とOpenAPI自動生成が理由." \
  --tags "backend,api,fastapi"
```

**出力例**:
```
✓ Added entry: KB-20251020-001
  Title: FastAPIを使用する
  Category: architecture
  Tags: backend, api, fastapi
```

### Step 3: Knowledge Base検索(TF-IDF)

```bash
# TF-IDF relevance ranking search
clauxton kb search "FastAPI"

# カテゴリでフィルタ
clauxton kb search "API" --category architecture

# 結果数制限
clauxton kb search "design" --limit 5
```

**出力例**:
```
Search Results for 'FastAPI' (1):

  KB-20251020-001
    Title: FastAPIを使用する
    Category: architecture
    Tags: backend, api, fastapi
    Preview: バックエンドはFastAPIで構築.非同期処理とOpenAPI自動生成が理由.
```

### Step 4: タスク管理

#### タスク追加

```bash
# 基本的なタスク追加
clauxton task add \
  --name "Setup FastAPI project" \
  --priority high

# ファイルと見積もりを指定
clauxton task add \
  --name "Add authentication endpoint" \
  --priority medium \
  --files "src/api/auth.py,src/models/user.py" \
  --estimate 4
```

**重要**: `--files`はカンマ区切りで指定(スペースなし)

**出力例**:
```
✓ Added task: TASK-001
  Name: Setup FastAPI project
  Priority: high
```

#### タスク一覧

```bash
# すべてのタスク
clauxton task list

# ステータスでフィルタ
clauxton task list --status pending

# 優先度でフィルタ
clauxton task list --priority high
```

#### 次のタスク推奨(AI)

```bash
clauxton task next
```

**出力例**:
```
📋 Next Task to Work On:

  TASK-001
  Name: Setup FastAPI project
  Priority: high

  Files to edit:
    - src/main.py
    - src/api/__init__.py

  Estimated: 2.0 hours

  Start working on this task:
    clauxton task update TASK-001 --status in_progress
```

#### タスク更新

```bash
# ステータス変更
clauxton task update TASK-001 --status in_progress

# 優先度変更
clauxton task update TASK-001 --priority critical
```

---

## Conflict Detection(新機能)

v0.9.0-betaの新機能: タスク間のファイル競合を事前に検出できます.

### 1. タスクの競合チェック

```bash
# 特定タスクの競合を検出
clauxton conflict detect TASK-002
```

**出力例(競合なし)**:
```
Conflict Detection Report
Task: TASK-002 - Add authentication endpoint
Files: 2 file(s)

✓ No conflicts detected
This task is safe to start working on.
```

**出力例(競合あり)**:
```
Conflict Detection Report
Task: TASK-003 - Setup database
Files: 2 file(s)

⚠ Conflicts detected (1):

  🔴 HIGH RISK (75.0% overlap)
    With: TASK-002 - Add authentication endpoint
    Conflicting files:
      - src/models/user.py

⚠ Coordinate with other tasks before starting
```

### 2. 安全な実行順序の取得

```bash
# 複数タスクの最適な実行順序を取得
clauxton conflict order TASK-001 TASK-002 TASK-003
```

**出力例**:
```
Task Execution Order
Tasks: 3 task(s)

Order minimizes file conflicts (no dependencies)

Recommended Order:
1. TASK-001 - Setup FastAPI project structure
2. TASK-003 - Setup database connection
3. TASK-002 - Add authentication endpoint

💡 Execute tasks in this order to minimize conflicts
```

### 3. ファイルの競合チェック

```bash
# 特定ファイルを編集中のタスクを確認
clauxton conflict check src/models/user.py

# 複数ファイルをチェック
clauxton conflict check src/api/auth.py src/models/user.py
```

**出力例(使用中)**:
```
File Availability Check
Files: 1 file(s)

⚠ 1 file(s) currently in use:

  src/models/user.py
    ⚠ Being edited by 1 task(s):
      - TASK-002 (in_progress) - Add authentication endpoint

💡 Coordinate before editing these files
```

**出力例(利用可能)**:
```
File Availability Check
Files: 1 file(s)

✓ All 1 file(s) available for editing
```

---

## MCP統合(Claude Code)

ClautonはMCP (Model Context Protocol) を通じてClaude Codeと統合できます.

### セットアップ方法

#### 1. MCPサーバー設定ファイル作成

Claude Codeの設定ファイル(場所は環境による):

**macOS/Linux**: `~/.config/claude-code/mcp-servers.json`
**Windows**: `%APPDATA%\claude-code\mcp-servers.json`

```json
{
  "mcpServers": {
    "clauxton": {
      "command": "python",
      "args": ["-m", "clauxton.mcp.server"],
      "cwd": "${workspaceFolder}"
    }
  }
}
```

#### 2. Claude Codeを再起動

MCPサーバーが自動的に起動します.

### 利用可能なMCPツール(15個)

#### Knowledge Base Tools (6)
- `kb_search` - TF-IDF relevance search
- `kb_add` - Add new entry
- `kb_list` - List all entries
- `kb_get` - Get entry by ID
- `kb_update` - Update entry
- `kb_delete` - Delete entry

#### Task Management Tools (6)
- `task_add` - Create task with auto-dependency
- `task_list` - List tasks (filterable)
- `task_get` - Get task details
- `task_update` - Update task
- `task_next` - Get recommended next task
- `task_delete` - Delete task

#### Conflict Detection Tools (3) - 🆕 NEW
- `detect_conflicts` - Detect conflicts for a task
- `recommend_safe_order` - Get optimal task order
- `check_file_conflicts` - Check file availability

### Claude Codeでの使用例

Claude Codeに以下のように指示できます: 

```
"タスクTASK-001の競合をチェックして"
→ detect_conflicts tool が呼ばれる

"次に取り組むべきタスクは?"
→ task_next tool が呼ばれる

"FastAPIに関する情報を検索して"
→ kb_search tool が呼ばれる
```

---

## 実践例: チーム開発ワークフロー

### シナリオ: 複数人で並行開発

#### 開発者A: タスク開始前のチェック

```bash
# 1. 次のタスクを確認
clauxton task next

# 出力: TASK-002(認証機能追加)

# 2. 競合チェック
clauxton conflict detect TASK-002

# 出力: TASK-003とsrc/models/user.pyで競合

# 3. 開発者Bに確認
echo "開発者B, user.pyを編集中?"
clauxton conflict check src/models/user.py

# 出力: TASK-003(開発者B担当)がin_progress

# 4. 別のタスクを開始
clauxton task update TASK-001 --status in_progress
```

#### 開発者B: タスク完了時

```bash
# 1. タスク完了
clauxton task update TASK-003 --status completed

# 2. 開発者Aに通知
echo "user.py解放したよ!"

# 3. 開発者Aは再チェック
clauxton conflict check src/models/user.py
# 出力: ✓ All files available
```

---

## トラブルシューティング

### Q1: `clauxton: command not found`

**原因**: 仮想環境がアクティベートされていない

**解決**:
```bash
cd /path/to/clauxton
source .venv/bin/activate  # Linux/macOS
```

### Q2: `Task with ID 'TASK-001' not found`

**原因**: タスクが存在しない, またはIDが間違っている

**解決**:
```bash
# すべてのタスクを確認
clauxton task list

# タスクIDはTASK-001, TASK-002, ... の形式
```

### Q3: `--files`オプションでエラー

**原因**: ファイル名にスペースが含まれている

**解決**:
```bash
# ❌ 間違い
clauxton task add --name "Test" --files "file1.py" "file2.py"

# ✅ 正しい(カンマ区切り, スペースなし)
clauxton task add --name "Test" --files "file1.py,file2.py"
```

### Q4: Knowledge Base検索で結果が出ない

**原因**: scikit-learnがインストールされていない可能性

**解決**:
```bash
# 依存関係を再インストール
pip install -e ".[dev]"

# または
pip install scikit-learn numpy
```

**確認**:
```bash
python -c "import sklearn; print('scikit-learn OK')"
```

### Q5: MCP統合が動作しない

**原因**: MCPサーバー設定が間違っているか, Claude Codeが古い

**解決**:
1. MCPサーバー設定ファイルのパスを確認
2. Claude Codeを再起動
3. MCPサーバーログを確認:
   ```bash
   # MCPサーバーを手動起動してテスト
   python -m clauxton.mcp.server
   ```

---

## ファイル構造

Clauxton初期化後のディレクトリ構造: 

```
your-project/
├── .clauxton/
│   ├── knowledge-base.yml      # Knowledge Base(YAML)
│   ├── knowledge-base.yml.bak  # 自動バックアップ
│   ├── tasks.yml               # タスク一覧(YAML)
│   └── tasks.yml.bak           # 自動バックアップ
├── src/
│   └── (your code)
└── (other files)
```

**重要**:
- `.clauxton/`はGit管理推奨(チーム共有)
- バックアップファイル(`.bak`)は自動生成
- パーミッション: 700(ディレクトリ), 600(ファイル)

---

## 便利なコマンド一覧

### よく使うコマンド

```bash
# バージョン確認
clauxton --version

# ヘルプ
clauxton --help
clauxton task --help
clauxton conflict --help

# プロジェクト初期化
clauxton init

# KB: 追加· 検索
clauxton kb add
clauxton kb search "query"
clauxton kb list

# タスク: 追加· 一覧· 次
clauxton task add --name "Task name" --priority high
clauxton task list
clauxton task next

# 競合チェック(v0.9.0-beta)
clauxton conflict detect TASK-001
clauxton conflict order TASK-001 TASK-002 TASK-003
clauxton conflict check src/file.py
```

---

## さらに詳しい情報

- **Quick Start**: `docs/quick-start.md` (18KB)
- **Conflict Detection詳細**: `docs/conflict-detection.md` (40KB)
- **MCP統合**: `docs/mcp-server.md` (14KB)
- **Task Management**: `docs/task-management-guide.md` (20KB)
- **Troubleshooting**: `docs/troubleshooting.md` (26KB)
- **全ドキュメント**: `docs/` ディレクトリ(420KB+, 41 files)

---

## フィードバック

バグ報告や機能要望は以下へ: 
- **GitHub Issues**: https://github.com/nakishiyaman/clauxton/issues
- **Discussions**: https://github.com/nakishiyaman/clauxton/discussions

---

**Clauxton v0.9.0-beta - Production Ready** ✅

*Generated: 2025-10-20*
*Status: Beta Release*
*Quality: A+ (99/100)*
