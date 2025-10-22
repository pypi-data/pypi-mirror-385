# Best Practices Analysis: Context Persistence in AI Coding Assistants
**Date**: 2025-10-20
**Purpose**: 類似プロジェクトの優れた事例を分析し, Clauxtonの設計指針を導出
**Status**: Research Complete

---

## 1. Executive Summary

**調査対象**: 7つの主要なAIコーディングアシスタント/フレームワーク
- Cursor AI (Rules & Memory Bank)
- Roo Cline (旧Cline)
- Aider AI
- MCP Official Memory Servers
- LangChain/LangGraph Memory
- Devin AI (Cognition)
- Mem0 (AI Agent Memory Framework)

**主要な発見**:
1. **階層的アーキテクチャ**が標準(短期記憶 + 長期記憶)
2. **ユーザーは透過的な統合**を望むが, **手動オーバーライド**も重視
3. **Markdownベースのストレージ**がデファクトスタンダード(人間可読性 + Git対応)
4. **自動索引 + 検索可能性**が差別化要因
5. **ファイルベースのルール**(`.clinerules`, `.cursorrules`, `CLAUDE.md`)が普及

---

## 2. 詳細分析

### 2.1 Cursor AI - Rules & Memory System

#### アーキテクチャ

```
┌─────────────────────────────────┐
│  User Interaction               │
│  "Build a Todo app"             │
└────────────┬────────────────────┘
             │
             ↓
┌─────────────────────────────────┐
│  Cursor Rules System            │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│  .cursor/rules/*.mdc            │
│  - Project-level rules          │
│  - Version-controlled           │
│  - Always applied to context    │
└────────────┬────────────────────┘
             │
             ↓
┌─────────────────────────────────┐
│  Memory System (Beta)           │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│  - "Sidecar model" observes     │
│  - Suggests memories to save    │
│  - User approves/rejects        │
│  - Persists across sessions     │
└────────────┬────────────────────┘
             │
             ↓
┌─────────────────────────────────┐
│  Memory Bank (Community)        │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│  /memory_bank/*.md              │
│  - techContext.md               │
│  - systemPatterns.md            │
│  - activeContext.md             │
└─────────────────────────────────┘
```

#### 使用フロー

**ルールの適用(透過的)**:
```
User: "Add authentication"
↓
Cursor: (自動的に .cursor/rules/backend.mdc を読み込む)
        "Based on your FastAPI rules, I'll use JWT..."
```

**メモリの保存(半自動)**:
```
Sidecar Model: "💡 Should I remember: 'This project uses JWT auth'?"
User: [Approve] ✓
↓
Memory saved → 次回のセッションで自動適用
```

#### 優れている点

1. **透過性**: ユーザーはルールを書くだけ, AIが自動適用
2. **承認フロー**: メモリは提案→承認(誤情報を防ぐ)
3. **バージョン管理**: `.cursor/rules` をGitで共有可能
4. **コミュニティエコシステム**: Memory Bankテンプレートが豊富

#### 課題

- メモリ機能はBeta版(まだ不安定)
- Memory Bankはコミュニティプロジェクト(公式サポートなし)
- ルールファイルの構造化が弱い(フリーテキスト)

---

### 2.2 Roo Cline (旧Cline) - Project Context & Rules

#### アーキテクチャ

```
┌─────────────────────────────────┐
│  3 Modes                        │
│  - Code Mode (coding)           │
│  - Architect Mode (design)      │
│  - Ask Mode (exploration)       │
└────────────┬────────────────────┘
             │
             ↓
┌─────────────────────────────────┐
│  Mode-Specific Rules            │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│  .clinerules-architect          │
│  .clinerules-code               │
│  .clinerules-ask                │
│  → 各モードで異なる指示         │
└────────────┬────────────────────┘
             │
             ↓
┌─────────────────────────────────┐
│  Project Rules Folder           │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│  .clinerules/                   │
│  - 01-coding.md                 │
│  - 02-documentation.md          │
│  - 03-testing.md                │
│  → 構造化されたルール群         │
└────────────┬────────────────────┘
             │
             ↓
┌─────────────────────────────────┐
│  Memory Bank (統合版)           │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│  /memory_bank/                  │
│  - activeContext.md (現在の状態)│
│  - decisionLog.md (ADR)         │
│  - productContext.md (概要)     │
│  - progress.md (完了した作業)   │
└─────────────────────────────────┘
```

#### 使用フロー

**モードの切り替え**:
```
User: @architect "Design the auth system"
↓
Roo Cline: (Architect modeに切り替え)
           (.clinerules-architect を読み込む)
           "Let's think through the high-level design..."
           (コードは書かない, 設計だけ)

User: @code "Implement JWT login"
↓
Roo Cline: (Code modeに切り替え)
           (.clinerules-code を読み込む)
           (実装開始)
```

**Memory Bankの自動更新**:
```
Roo Cline: "I've added JWT auth. Updating memory..."
           ↓
           decisionLog.md += "2025-10-20: Chose JWT over OAuth due to simplicity"
           progress.md += "✓ JWT authentication implemented"
```

#### 優れている点

1. **モードベースのルール**: 設計· 実装· 探索で異なる振る舞い
2. **構造化されたルール**: `.clinerules/01-*.md` 形式で整理
3. **Memory Bankが統合**: 公式機能として提供
4. **ADR (Architecture Decision Records)**: 設計決定を自動記録

#### 課題

- モードの切り替えが手動(`@architect`, `@code`)
- ルールファイルの数が増えると管理が煩雑

---

### 2.3 Aider AI - Repository Map & CLAUDE.md

#### アーキテクチャ

```
┌─────────────────────────────────┐
│  User Input                     │
│  "Add user authentication"      │
└────────────┬────────────────────┘
             │
             ↓
┌─────────────────────────────────┐
│  CLAUDE.md (Persistent Context) │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│  - Project overview             │
│  - Tech stack                   │
│  - Coding conventions           │
│  - Build commands               │
│  → Claude が自動読み込み        │
└────────────┬────────────────────┘
             │
             ↓
┌─────────────────────────────────┐
│  Repository Map (自動生成)      │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│  - 全ファイルのシグネチャ抽出   │
│  - モジュール間の依存関係       │
│  - 関数/クラスの一覧            │
│  → LLMに与えるコンパクトな地図  │
└────────────┬────────────────────┘
             │
             ↓
┌─────────────────────────────────┐
│  Context-Aware Code Generation  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│  "I see you have auth/login.py  │
│   I'll extend that with JWT..." │
└─────────────────────────────────┘
```

#### 使用フロー

**初回起動時(自動)**:
```bash
$ aider
Aider: "Analyzing your repository..."
       ↓
       Repository Map 生成中...
       - 156 files indexed
       - 42 modules detected
       - 318 functions mapped
       ↓
       "Ready! I understand your codebase structure."
```

**開発中(透過的)**:
```
User: "Add JWT authentication"
↓
Aider: (Repository Mapから関連ファイルを検索)
       auth/login.py (既存の認証コード) を発見
       ↓
       "I see you have auth/login.py.
        I'll add JWT support by extending the existing auth module..."
```

#### 優れている点

1. **完全自動**: Repository Mapは自動生成, ユーザーの手間ゼロ
2. **CLAUDE.md対応**: Claudeが読むドキュメントを活用
3. **ホットスポット認識**: よく変更されるファイルを優先
4. **大規模リポジトリ対応**: 効率的なチャンキング

#### 課題

- Repository Mapは読み取り専用(ユーザーが編集できない)
- CLAUDE.mdのフォーマットは自由(構造化なし)
- タスク管理機能なし(コード生成に特化)

---

### 2.4 MCP Official Memory Servers

#### アーキテクチャ

```
┌─────────────────────────────────┐
│  Claude Desktop / Code          │
└────────────┬────────────────────┘
             │ MCP Protocol
             ↓
┌─────────────────────────────────┐
│  @modelcontextprotocol/         │
│  server-memory                  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│  Tools:                         │
│  - create_entities              │
│  - create_relations             │
│  - add_observations             │
│  - search_nodes                 │
│  - open_nodes                   │
│  - delete_entities              │
└────────────┬────────────────────┘
             │
             ↓
┌─────────────────────────────────┐
│  Knowledge Graph Storage        │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│  Entities (nodes):              │
│    User, Project, Feature       │
│                                 │
│  Relations (edges):             │
│    User --owns--> Project       │
│    Project --uses--> FastAPI    │
│                                 │
│  Observations (facts):          │
│    "User prefers TypeScript"    │
│    "Project uses JWT auth"      │
└─────────────────────────────────┘
```

#### 使用フロー

**会話中の記憶(透過的)**:
```
User: "私はTypeScriptが好きです"
↓
Claude: (内部で create_entities を呼び出し)
        create_entities([
          {name: "User", entityType: "person"},
          {name: "TypeScript", entityType: "technology"}
        ])
        ↓
        create_relations([
          {from: "User", to: "TypeScript", relationType: "prefers"}
        ])
```

**次回のセッション(自動)**:
```
User: "新しいプロジェクトを始めたい"
↓
Claude: (search_nodes("User preferences") を実行)
        "I remember you prefer TypeScript.
         Should we use it for this project?"
```

#### 優れている点

1. **構造化された知識**: エンティティ + リレーション + 観察
2. **セッション間で永続化**: ユーザー情報を長期保存
3. **検索可能**: グラフクエリでコンテキスト検索
4. **標準プロトコル**: MCPで他のツールと統合可能

#### 課題

- ナレッジグラフは複雑(学習コスト高)
- プロジェクト固有の文脈管理には不向き(ユーザー中心)
- ファイルベースではない(Git管理不可)

---

### 2.5 LangChain/LangGraph Memory Architecture

#### アーキテクチャ

```
┌─────────────────────────────────┐
│  AI Agent (LangGraph)           │
└────────────┬────────────────────┘
             │
             ↓
┌─────────────────────────────────┐
│  Short-Term Memory              │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│  Thread-scoped Checkpoints:     │
│  - Conversation history         │
│  - Current task state           │
│  → RAMのように機能             │
└────────────┬────────────────────┘
             │
             ↓
┌─────────────────────────────────┐
│  Long-Term Memory               │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│  Vector Store (embeddings):     │
│  - Past conversations           │
│  - Knowledge base               │
│  - User preferences             │
│  → HDDのように機能             │
└────────────┬────────────────────┘
             │
             ↓
┌─────────────────────────────────┐
│  Memory Store (新機能)          │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│  Operations:                    │
│  - put(namespace, key, value)   │
│  - get(namespace, key)          │
│  - search(namespace, query)     │
│  → セマンティック検索対応       │
└─────────────────────────────────┘
```

#### 使用フロー

**短期記憶(会話内)**:
```python
# LangGraphが自動管理
checkpointer = MemorySaver()
graph = create_graph().compile(checkpointer=checkpointer)

# 会話1
graph.invoke({"input": "Build a Todo app"}, thread_id="thread-1")
# → Checkpointに保存

# 会話2(同じスレッド)
graph.invoke({"input": "Add auth"}, thread_id="thread-1")
# → 前回の文脈を自動ロード
```

**長期記憶(セッション間)**:
```python
# エージェントが会話から記憶を抽出
memory_store.put(
    namespace="project-123",
    key="tech-stack",
    value="FastAPI, React, PostgreSQL"
)

# 次回のセッション
results = memory_store.search(
    namespace="project-123",
    query="what database do we use?"
)
# → "PostgreSQL" を返す
```

#### 優れている点

1. **二層構造**: 短期(高速)+ 長期(永続)
2. **自動チェックポイント**: 会話状態を自動保存
3. **ベクトル検索**: セマンティックな類似性で検索
4. **拡張性**: Redis, PostgreSQL, Chromaなど複数のバックエンド対応

#### 課題

- プログラマー向け(ノンコーダーには難しい)
- ファイルベースではない(人間が直接編集できない)
- タスク管理機能なし(メモリ管理に特化)

---

### 2.6 Devin AI (Cognition) - Automatic Repository Indexing

#### アーキテクチャ

```
┌─────────────────────────────────┐
│  User: "Fix the login bug"     │
└────────────┬────────────────────┘
             │
             ↓
┌─────────────────────────────────┐
│  Repository Wiki (自動生成)     │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│  - Architecture diagrams        │
│  - Module documentation         │
│  - Source links                 │
│  → 数時間ごとに自動更新         │
└────────────┬────────────────────┘
             │
             ↓
┌─────────────────────────────────┐
│  In-Context Reasoning (Devin 1.2│
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│  - Understand repo structure    │
│  - Identify relevant files      │
│  - Reuse existing patterns      │
│  → コンテキスト認識が向上       │
└────────────┬────────────────────┘
             │
             ↓
┌─────────────────────────────────┐
│  Custom Memory System (内部)    │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│  "Devin's existing memory       │
│   systems" (詳細は非公開)       │
│  → Claude Sonnet 4.5より効果的  │
└─────────────────────────────────┘
```

#### 使用フロー

**初回プロジェクト開始(自動)**:
```
Devin: "Indexing your repository..."
       ↓
       - 全ファイルを分析
       - アーキテクチャ図を生成
       - ドキュメントを作成
       ↓
       "Repository wiki created. Ready to work!"
```

**タスク実行中(透過的)**:
```
User: "Fix the authentication bug"
↓
Devin: (Repository wikiから関連情報を検索)
       "I found the auth module in src/auth/
        Checking login.py...
        I see the issue: JWT token expiry is not handled..."
```

#### 優れている点

1. **完全自動**: ユーザーは何もしない, Devinが全て管理
2. **ビジュアル**: アーキテクチャ図を自動生成
3. **リンク付き**: ドキュメントからソースへ直接ジャンプ
4. **継続的更新**: 数時間ごとに自動再索引

#### 課題

- プロプライエタリ(仕組みは非公開)
- 高価(月額$20~$500)
- カスタマイズ不可(ブラックボックス)

---

### 2.7 Mem0 - AI Agent Memory Framework

#### アーキテクチャ

```
┌─────────────────────────────────┐
│  AI Agent (任意のLLM)           │
└────────────┬────────────────────┘
             │
             ↓
┌─────────────────────────────────┐
│  Mem0 API                       │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│  Operations:                    │
│  - add(memory, user_id)         │
│  - search(query, user_id)       │
│  - get_all(user_id)             │
│  - delete(memory_id)            │
└────────────┬────────────────────┘
             │
             ↓
┌─────────────────────────────────┐
│  Memory Types                   │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│  1. User Memory                 │
│     → ユーザーの好み· 習慣      │
│                                 │
│  2. Agent Memory                │
│     → エージェントの学習内容    │
│                                 │
│  3. Session Memory              │
│     → 短期的な会話履歴          │
└────────────┬────────────────────┘
             │
             ↓
┌─────────────────────────────────┐
│  Vector Database                │
│  (Qdrant, Pinecone, Chroma)     │
└─────────────────────────────────┘
```

#### 使用フロー

**記憶の追加(プログラマティック)**:
```python
from mem0 import Memory

m = Memory()

# ユーザーの好みを記憶
m.add(
    "I prefer TypeScript over JavaScript",
    user_id="user-123"
)

# セッション固有の情報
m.add(
    "Current project: Todo app",
    user_id="user-123",
    metadata={"session": "2025-10-20"}
)
```

**記憶の検索(セマンティック)**:
```python
# 関連する記憶を検索
memories = m.search(
    query="What language does the user prefer?",
    user_id="user-123"
)
# → "I prefer TypeScript over JavaScript"
```

#### 優れている点

1. **シンプルなAPI**: add/search/get/deleteのみ
2. **マルチユーザー対応**: user_id で記憶を分離
3. **セマンティック検索**: ベクトル検索で意味的に類似した記憶を取得
4. **バックエンド選択可**: Qdrant, Pinecone, Chromaなど

#### 課題

- クラウドサービス(セルフホスト版もあるが複雑)
- ファイルベースではない(Git管理不可)
- プロジェクト文脈管理には不向き(ユーザー中心)

---

## 3. 横断分析: 共通パターンと差別化要因

### 3.1 共通パターン

| パターン | 採用例 | 説明 |
|---------|--------|------|
| **階層的記憶** | 全プロジェクト | 短期記憶(セッション内)+ 長期記憶(セッション間) |
| **Markdownベース** | Cursor, Roo Cline, Aider | 人間可読 + Git対応 + LLM-friendly |
| **ルールファイル** | Cursor (`.cursorrules`), Roo (`.clinerules`), Aider (`CLAUDE.md`) | プロジェクト固有の指示 |
| **自動索引** | Aider (Repo Map), Devin (Wiki) | リポジトリ構造を自動理解 |
| **ベクトル検索** | MCP Memory, LangChain, Mem0 | セマンティックな類似性で検索 |
| **透過的統合** | 全プロジェクト | ユーザーは意識しない, AIが自動利用 |
| **承認フロー** | Cursor Memory (Beta) | 重要な記憶は承認後に保存 |

### 3.2 差別化要因

#### A. Cursor AI の差別化
- **Sidecar model**: 記憶の提案を生成する専用モデル
- **コミュニティエコシステム**: Memory Bankテンプレートが豊富
- **バージョン管理**: `.cursor/rules` を Git で共有

#### B. Roo Cline の差別化
- **モードベース**: Architect/Code/Ask で異なるルール
- **構造化ルール**: `.clinerules/01-*.md` 形式
- **ADR統合**: Architecture Decision Records を自動生成

#### C. Aider の差別化
- **Repository Map**: 完全自動, 学習不要
- **CLAUDE.md標準対応**: Claudeが読むドキュメントを活用
- **ホットスポット認識**: 頻繁に変更されるファイルを優先

#### D. Devin の差別化
- **ビジュアル**: アーキテクチャ図を自動生成
- **継続的更新**: 数時間ごとに自動再索引
- **完全自動**: ユーザーの設定不要

#### E. LangChain の差別化
- **プログラマティック**: Python/JS でカスタマイズ可能
- **拡張性**: 複数のバックエンド対応
- **Checkpointer**: 会話状態を自動保存

---

## 4. Clauxtonへの示唆

### 4.1 現在のClauxtonの位置づけ

```
┌──────────────────┬──────────┬──────────┬──────────┐
│ 機能             │ Clauxton │ Cursor   │ Aider    │
├──────────────────┼──────────┼──────────┼──────────┤
│ Knowledge Base   │ ✓        │ ✓        │ ✓        │
│ Task Management  │ ✓        │ ✗        │ ✗        │
│ Conflict Detect  │ ✓        │ ✗        │ ✗        │
│ 自動索引         │ ✗        │ ✗        │ ✓        │
│ メモリ承認       │ ✗        │ ✓ (Beta) │ ✗        │
│ ビジュアル       │ ✗        │ ✗        │ ✗        │
│ Git統合          │ ✓        │ ✓        │ ✓        │
│ 手動オーバーライド│ ✓        │ ✓        │ ✓        │
└──────────────────┴──────────┴──────────┴──────────┘
```

**強み**:
- タスク管理 + 依存関係 + 競合検出(他にはない)
- MCP統合(標準プロトコル)
- YAML(人間可読 + Git対応)

**弱み**:
- 手動すぎる(kb add, task add を毎回実行)
- 自動索引なし(ユーザーが明示的に登録)
- ドキュメント出力なし(.clauxton → docs/ への変換)

### 4.2 推奨される改善(優先順位付き)

#### 🔴 **Priority 1: YAML一括インポート(透過性向上)**

**理由**: Claude Codeが効率的にタスクを登録できる

**実装**:
```python
# CLI (手動オプション)
clauxton task import tasks.yml

# MCP Tool (透過的に使う)
task_import_yaml(yaml_content: str) -> dict
```

**使用例**:
```
User: "Todoアプリを作りたい"
↓
Claude Code: (内部で10個のタスクをYAMLで生成)
             task_import_yaml("""
             tasks:
               - name: "FastAPI初期化"
                 priority: high
                 files: [backend/main.py]
               ...
             """)
             ↓
             "10個のタスクを登録しました.TASK-001から始めます."
```

**影響**: ユーザー体験が **劇的に改善**(10回のコマンド → 1回の会話)

---

#### 🟡 **Priority 2: KB→ドキュメント出力(人間可読性)**

**理由**: 構造化データ ↔ ドキュメント の橋渡し

**実装**:
```python
# CLI (手動オプション)
clauxton kb export docs/

# MCP Tool (透過的に使う)
kb_export_docs(output_dir: str) -> dict
```

**生成されるドキュメント**:
```
docs/
├── requirements.md       # KB (constraint) から生成
├── architecture.md       # KB (architecture) から生成
├── conventions.md        # KB (convention) から生成
└── decisions.md          # KB (decision) から生成(ADR風)
```

**影響**: チーム共有が容易, Git管理可能

---

#### 🟢 **Priority 3: CLAUDE.md強化(即効性)**

**理由**: Claude Codeにいつ· どう使うか教える

**追加内容**:
```markdown
## When to Use Clauxton (透過的に)

### During Requirements Gathering
User mentions constraints → Automatically kb_add()

### During Task Planning
After breaking down features → task_import_yaml()

### Manual Override (手動オプション)
User explicitly asks → Use CLI commands
```

**影響**: Claude Codeが自然にClauxtonを使うようになる

---

#### 🟢 **Priority 4: 自動Repository Map(将来)**

**理由**: Aider/Devinと同等の機能

**実装案**:
```python
# 初回起動時に自動生成
clauxton init --with-repo-map

# .clauxton/repo-map.yml
files:
  - path: backend/main.py
    functions: [create_app, setup_routes]
    dependencies: [database.py, auth.py]
  ...
```

**影響**: Claude Codeがリポジトリ構造を理解, 関連ファイルを自動特定

---

### 4.3 理想的なアーキテクチャ(改善後)

```
┌─────────────────────────────────────────┐
│  User                                   │
│  "Todoアプリを作りたい"                   │
└──────┬──────────────────────────────────┘
       │ 自然言語
       ↓
┌─────────────────────────────────────────┐
│  Claude Code                            │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  1. CLAUDE.md を読む                     │
│  2. 要件を理解                           │
│  3. 設計を提案                           │
│  4. タスクに分解                         │
└──────┬──────────────────────────────────┘
       │ MCP経由(透過的)
       ↓
┌─────────────────────────────────────────┐
│  Clauxton                               │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  [Knowledge Base]                       │
│    kb_add() で自動登録                   │
│                                         │
│  [Task Management]                      │
│    task_import_yaml() で一括登録        │
│                                         │
│  [Conflict Detection]                   │
│    detect_conflicts() でリスク検出       │
└──────┬──────────────────────────────────┘
       │ 自動生成(必要に応じて)
       ↓
┌─────────────────────────────────────────┐
│  Markdown Documents (人間向け)          │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│  docs/requirements.md                   │
│  docs/architecture.md                   │
│  docs/tasks.md                          │
│  → Git管理, チーム共有可能              │
└─────────────────────────────────────────┘
```

---

## 5. 実装ロードマップ

### Phase 1: 透過性の向上(v0.10.0)
**期間**: 2週間
**リリース**: 2025-11-03

#### 実装内容
1. **YAML一括インポート**
   - CLI: `clauxton task import tasks.yml`
   - MCP: `task_import_yaml(yaml_content: str) -> dict`
   - 所要時間: 8時間

2. **CLAUDE.md強化**
   - "いつ使うか"セクション追加
   - "透過的な使い方"例を追加
   - 所要時間: 2時間

3. **エラーハンドリング改善**
   - YAML解析エラーの詳細表示
   - 重複タスクID検出
   - 所要時間: 4時間

**成果物**:
- v0.10.0リリース
- ユーザー体験の劇的改善(10回のコマンド → 1回の会話)

---

### Phase 2: 人間可読性の向上(v0.11.0)
**期間**: 1週間
**リリース**: 2025-11-10

#### 実装内容
1. **KB→ドキュメント出力**
   - CLI: `clauxton kb export docs/`
   - MCP: `kb_export_docs(output_dir: str) -> dict`
   - カテゴリごとにファイル分割
   - 所要時間: 4時間

2. **Task→ドキュメント出力**
   - CLI: `clauxton task export docs/tasks.md`
   - ガントチャート風(Mermaid形式)
   - 所要時間: 3時間

**成果物**:
- v0.11.0リリース
- チーム共有が容易, Git管理可能

---

### Phase 3: 自動化の強化(v0.12.0)
**期間**: 2週間
**リリース**: 2025-11-24

#### 実装内容
1. **Repository Map(自動生成)**
   - `clauxton init --with-repo-map`
   - ファイル/関数/依存関係を抽出
   - 所要時間: 12時間

2. **自動KB登録(ウォッチモード)**
   - Gitコミットメッセージから自動抽出
   - "feat:", "fix:" → KB に自動追加
   - 所要時間: 6時間

**成果物**:
- v0.12.0リリース
- Aider/Devinと同等の自動化

---

### Phase 4: ビジュアライゼーション(v1.0.0)
**期間**: 3週間
**リリース**: 2025-12-15

#### 実装内容
1. **Webダッシュボード**
   - Flask/FastAPI で簡易ダッシュボード
   - KB/Task/Conflictをビジュアル表示
   - 所要時間: 20時間

2. **Mermaid図の自動生成**
   - アーキテクチャ図(KBから生成)
   - タスク依存関係図(Tasksから生成)
   - 所要時間: 8時間

**成果物**:
- v1.0.0リリース(安定版)
- Devinと同等のビジュアル機能

---

## 6. 重要な設計原則(学んだこと)

### 6.1 透過性 vs 制御

**学び**: ユーザーは"透過的"を望むが, "手動オーバーライド"も必須

**理由**:
- AIが間違うこともある(誤った記憶を残す)
- 重要な決定は人間が確認したい
- デバッグ時に内部状態を確認したい

**Clauxtonでの実装**:
```markdown
## Transparency Levels

1. **Full Auto** (Default)
   - Claude Code が自動的に kb_add(), task_import_yaml() を実行
   - ユーザーは結果のみ確認

2. **Semi-Auto** (Confirmation mode)
   - Claude Code が提案, ユーザーが承認
   - `clauxton config set confirmation true`

3. **Manual** (Override)
   - ユーザーが明示的にコマンド実行
   - `clauxton kb add`, `clauxton task add`
```

---

### 6.2 Markdown vs データベース

**学び**: Markdownがデファクトスタンダード

**理由**:
- **人間可読**: エンジニアが直接編集可能
- **Git対応**: バージョン管理, 差分表示
- **LLM-friendly**: LLMがそのまま読める
- **ツール不要**: vimやVS Codeで編集

**例外**: ベクトル検索が必要な場合のみデータベース

**Clauxtonでの方針**:
- **Primary Storage**: YAML(現状維持)
- **Secondary Output**: Markdown(新機能)
- **Optional Backend**: Vector DB(将来)

---

### 6.3 プロジェクト文脈 vs ユーザー文脈

**学び**: Clauxtonは"プロジェクト文脈"に特化すべき

| 種類 | 例 | 適したツール |
|------|---|------------|
| **プロジェクト文脈** | "このプロジェクトはFastAPIを使う" | Clauxton, Cursor Rules, Roo Cline |
| **ユーザー文脈** | "私はTypeScriptが好き" | MCP Memory, Mem0 |

**理由**:
- プロジェクト文脈 → チーム共有, Git管理
- ユーザー文脈 → 個人設定, クラウド保存

**Clauxtonでの方針**:
- プロジェクト固有の情報のみ扱う
- ユーザー好みは MCP Memory に任せる

---

### 6.4 構造化 vs 自由形式

**学び**: 両方必要, 使い分けが重要

**構造化(Clauxton)**:
- カテゴリ, タグ, 優先度
- 検索可能, 集計可能
- プログラマティックに利用

**自由形式(Markdown)**:
- 詳細な説明, 長文
- 人間が読みやすい
- コンテキストを保持

**Clauxtonでの実装**:
```yaml
# .clauxton/knowledge-base.yml (構造化)
- id: KB-20251020-001
  title: "FastAPI採用"
  category: architecture
  tags: [backend, api]
  content: "FastAPIを採用した理由..."

↓ エクスポート ↓

# docs/architecture.md (自由形式)
## FastAPI採用

**決定日**: 2025-10-20
**カテゴリ**: Architecture

FastAPIを採用した理由は以下の通り: 
1. 非同期処理のサポート
2. 自動API ドキュメント生成
3. 型安全性
...
```

---

### 6.5 自動化のバランス

**学び**: "完全自動"は危険, "確認可能"が重要

**Cursor Memoryの例**:
```
Sidecar Model: "💡 Should I remember: 'This project uses JWT auth'?"
User: [Approve] ✓ / [Reject] ✗
```

**理由**:
- AIは間違うこともある
- 重要な決定は人間が確認
- 誤った情報が長期記憶に残ると修正困難

**Clauxtonでの実装案**:
```python
# 確認モード(オプション)
@server.call_tool("kb_add_with_confirmation")
async def kb_add_with_confirmation(
    entry: dict,
    skip_confirmation: bool = False
) -> dict:
    if not skip_confirmation:
        # ユーザーに確認を求める(MCP経由)
        confirmed = await ask_user_confirmation(
            f"💡 Add to KB: {entry['title']}?"
        )
        if not confirmed:
            return {"status": "cancelled"}

    # 承認後に追加
    kb.add(entry)
    return {"status": "added"}
```

---

## 7. 結論と推奨アクション

### 7.1 重要な発見

1. **透過性 + 手動オーバーライド** が標準
   - ユーザーは"自然な会話"を望む
   - でも, 重要な決定は確認したい

2. **Markdownベース** がデファクト
   - 人間可読, Git対応, LLM-friendly
   - Clauxtonの YAML + Markdown 出力は正しい方向

3. **自動索引** が差別化要因
   - Aider (Repository Map), Devin (Wiki)
   - ClauxtonにもRepository Map機能が必要

4. **階層的記憶** が標準
   - 短期(セッション内)+ 長期(セッション間)
   - Clauxtonは長期記憶に特化(正しい)

5. **タスク管理 + 競合検出** はClauxton独自
   - 他のツールにはない強み
   - さらに強化すべき

---

### 7.2 次のステップ(推奨)

#### 🔴 **今すぐ実施(2時間)**
1. **CLAUDE.md強化**
   - "いつ使うか"セクション追加
   - "透過的な使い方"例を追加
   - 即効性あり, コード変更不要

#### 🟡 **v0.10.0で実装(2週間)**
1. **YAML一括インポート**
   - `task_import_yaml()` MCP Tool
   - `clauxton task import` CLI
   - ユーザー体験が劇的に改善

2. **KB→ドキュメント出力**
   - `kb_export_docs()` MCP Tool
   - `clauxton kb export docs/` CLI
   - チーム共有が容易

#### 🟢 **v0.11.0で実装(1ヶ月後)**
1. **Repository Map(自動生成)**
   - `clauxton init --with-repo-map`
   - Aider/Devinと同等の機能

---

### 7.3 Clauxtonの将来像

```
┌─────────────────────────────────────────┐
│  Clauxton v1.0                          │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                         │
│  [Knowledge Base]                       │
│    - 構造化データ(YAML)               │
│    - Markdown出力(Git管理)            │
│    - 自動抽出(Gitコミットから)        │
│                                         │
│  [Task Management]                      │
│    - DAG validation                     │
│    - YAML一括インポート                 │
│    - ガントチャート出力(Mermaid)      │
│                                         │
│  [Conflict Detection]                   │
│    - ファイル競合検出                   │
│    - リスクスコアリング                 │
│    - 安全な実行順序                     │
│                                         │
│  [Repository Map] (NEW)                 │
│    - 自動索引                           │
│    - ファイル/関数/依存関係             │
│    - ホットスポット認識                 │
│                                         │
│  [Visualization] (NEW)                  │
│    - Webダッシュボード                  │
│    - Mermaid図(アーキテクチャ, タスク)│
│                                         │
│  統合方法:                              │
│    ✓ MCP Protocol(透過的)            │
│    ✓ CLI(手動オーバーライド)          │
│    ✓ CLAUDE.md(ガイダンス)           │
└─────────────────────────────────────────┘
```

---

### 7.4 最終推奨

**あなたの要望を踏まえて**:
- ✅ **透過的**(Claude Codeが自動で使う)
- ✅ **手動オプション**(明示的にコマンド実行)

**推奨される実装順序**:
1. **CLAUDE.md強化**(今すぐ, 2時間)
2. **YAML一括インポート**(v0.10.0, 8時間)
3. **KB→ドキュメント出力**(v0.10.0, 4時間)
4. **Repository Map**(v0.11.0, 12時間)

**理由**:
- CLAUDE.md強化 → 即効性あり, Claude Codeに指針を与える
- YAML一括インポート → 透過的統合の基盤, ユーザー体験が劇的改善
- KB→ドキュメント出力 → チーム共有, Git管理可能
- Repository Map → Aider/Devinと同等, 長期的な競争力

**私の提案**:
まず **CLAUDE.md強化**(30分で完了)から始めて, 
あなたの反応を見てから次のステップを決めましょう.

進めますか?それとも, もっと検討しますか?

---

## 8. 参考資料

### 調査したプロジェクト
1. Cursor AI - https://docs.cursor.com/
2. Roo Cline - https://roocline.dev/
3. Aider AI - https://aider.chat/
4. MCP Memory - https://github.com/modelcontextprotocol/servers
5. LangChain Memory - https://python.langchain.com/docs/
6. Devin AI - https://cognition.ai/
7. Mem0 - https://mem0.ai/

### 関連記事
- "Memory in LangChain: A Deep Dive" - Comet
- "How to Supercharge AI Coding with Cursor Rules" - Lullabot
- "Context Engineering for AI Agents" - LangChain Blog
- "Building AI Agents That Actually Remember" - Medium
- "Eliminate AI Context Reset in Vibe Coding" - CodeRide

---

**作成日**: 2025-10-20
**作成者**: Claude Code
**バージョン**: 1.0
