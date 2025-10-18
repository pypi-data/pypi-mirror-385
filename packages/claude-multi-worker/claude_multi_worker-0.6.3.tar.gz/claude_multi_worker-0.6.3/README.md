# Claude Multi-Worker Framework (cmw) v0.6.2

[![Tests](https://github.com/nakishiyaman/cmw/workflows/Tests/badge.svg)](https://github.com/nakishiyaman/cmw/actions)
[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![codecov](https://codecov.io/gh/nakishiyaman/cmw/branch/main/graph/badge.svg)](https://codecov.io/gh/nakishiyaman/cmw)

**requirements.mdを書くだけで、大規模プロジェクトの開発を完全自動化**

Claude Codeと統合した次世代タスク管理フレームワーク。要件定義から自動的にタスクを生成し、依存関係グラフを可視化し、タスク実行プロンプトを自動生成し、Claude Codeの応答を自動解析します。開発ワークフロー全体を最適化します。

---

## 🎯 cmwはいつ必要？

| シチュエーション | Claude Code単体 | cmw併用 |
|---------------|----------------|---------|
| **プロジェクト規模** | 10タスク以下 | 30タスク以上 |
| **開発期間** | 1日で完了 | 複数日〜数週間 |
| **セッション管理** | 毎回文脈を再説明 | progress.jsonで自動継続 |
| **依存関係管理** | 手動で追跡 | NetworkXで自動管理、循環検出 |
| **ファイル競合** | 実行してみないと分からない | 事前に検出、実行順序を提案 |
| **チーム開発** | 進捗共有が困難 | Git + cmw syncで同期 |

**✅ cmwが役立つケース:**
- 30タスク以上の大規模プロジェクト
- 複数日に渡る開発（セッションを跨ぐ）
- 複雑な依存関係がある（認証→API→テストなど）
- チームで進捗を共有したい

**❌ cmwが不要なケース:**
- 10タスク以下の小規模プロジェクト
- 1セッションで完結する開発
- 単純な機能追加やバグ修正

---

## 🤔 なぜcmwが必要？

Claude Codeは強力ですが、**大規模プロジェクト**では以下の限界があります：

### 問題1: セッションを跨ぐと文脈が消える
Claude Codeは1セッションで全てを完了させることを前提としています。しかし、大規模プロジェクトでは：
- 30タスク以上の開発を1セッションで終えるのは現実的ではない
- セッションを再開すると「どこまで完了したか」を毎回説明する必要がある

**→ cmwの解決策:** `progress.json`で状態を永続化
```bash
# セッション1
cmw task complete TASK-001 TASK-002 TASK-003

# セッション2（翌日）
cmw status  # → 「3/30タスク完了、残り27タスク」と即座に把握
```

### 問題2: 依存関係の追跡が手動
Claude Codeは「どのタスクを先に実行すべきか」を自動判定できません：
- 認証→API→テストという順序を守らないとエラーになる
- 循環依存に気づかずタスクを定義してしまう

**→ cmwの解決策:** NetworkXで自動管理
```bash
cmw task graph  # → 依存関係を可視化
cmw tasks validate --fix  # → 循環依存を自動修正
```

### 問題3: ファイル競合の事前検出不可
Claude Codeは「複数タスクが同じファイルを編集する」ことを事前に検出できません：
- TASK-001とTASK-005が`auth.py`を同時に編集→競合
- 実行してみないと分からない

**→ cmwの解決策:** 事前に競合検出
```bash
cmw tasks analyze
# ⚠️  CRITICAL: auth.py (5タスク競合)
#   推奨実行順: TASK-001 → TASK-002 → TASK-005
```

---

## 📺 デモ

### クイックスタート（30秒）

requirements.mdを書くだけで、タスクが自動生成されます。

![Quick Start Demo](docs/assets/demo-quickstart.gif)

### 依存関係グラフの可視化（10秒）

タスク間の依存関係を自動で可視化し、実行順序を提案します。

![Graph Demo](docs/assets/demo-graph.gif)

### リアルタイム進捗ダッシュボード（5秒）

美しいターミナルUIで進捗を一目で把握できます。

![Dashboard Demo](docs/assets/demo-dashboard.gif)

---

## 🎯 概要

cmwは**タスク管理・メタデータ層**として機能し、Claude Codeと協調して大規模プロジェクトの開発を支援します。

### アーキテクチャ

```
ユーザー「ToDoアプリを作って」
  ↓
┌─────────────────────────────────────────┐
│ Claude Code（司令塔 + 実行層）          │
│  - 自然言語理解                          │
│  - コード生成（自身の機能）              │
│  - ファイル操作                          │
│  - テスト実行                            │
└─────────────────────────────────────────┘
  ↓ ↑ タスク情報の取得・完了報告
┌─────────────────────────────────────────┐
│ cmw（タスク管理・メタデータ層）         │
│  - requirements.md → タスク分解         │
│  - 依存関係グラフ管理                   │
│  - 進捗状態の永続化                     │
│  - ファイル配置ルール                   │
│  - 受け入れ基準                         │
└─────────────────────────────────────────┘
```

### 役割分担

**cmwが担当（WHAT/WHEN/WHERE）:**
- タスク定義と自動生成
- 依存関係管理
- 進捗状態の永続化
- ファイル配置ルール
- 受け入れ基準の提供

**Claude Codeが担当（HOW/WHY）:**
- 技術スタック選択
- 実装パターン決定
- コード生成（自身の機能で実行、API追加コストなし）
- エラー検出と修正

## ✨ 主な機能

### 🚀 実装完了（Phase 0-7 + v0.2.0）

#### 🔧 v0.2.0 新機能

##### ✅ 循環依存の自動修正（Phase 1）
- **DependencyValidator**: 循環依存の検出と自動修正
  - NetworkXによる高精度な循環検出
  - セマンティック分析による修正提案（信頼度スコアリング）
  - 自動修正機能（信頼度100%で即座に適用）
  - セクション番号・キーワードベースの判定
- **TaskFilter**: 非タスク項目の自動除外
  - 「技術スタック」「非機能要件」などを自動判定
  - 実装タスクのみを抽出
  - タスク動詞・受入基準の具体性を評価
- **成果**: blog-apiで17→15タスクに最適化、手動修正不要

##### 🔍 タスク検証コマンド（Phase 2.1）
- **CLIコマンド**: `cmw tasks validate`
  - 循環依存チェック
  - 非タスク項目チェック
  - 依存関係の妥当性チェック（存在しない依存先、自己依存）
  - `--fix`オプションで自動修正
  - Rich UIで視覚的に結果表示
- **成果**: 全検証項目を自動化、問題の早期発見

##### 🔄 Git連携による進捗自動更新（Phase 2.2）
- **GitIntegration**: Gitコミットメッセージから進捗を同期
  - コミットメッセージから`TASK-XXX`パターンを自動検出
  - 検出したタスクを自動で完了にマーク
  - タスク参照の妥当性検証
  - 最近のアクティビティ取得
- **CLIコマンド**: `cmw sync --from-git`
  - `--since`: コミット検索の開始時点（1.day.ago, 1.week.ago等）
  - `--branch`: 対象ブランチ
  - `--dry-run`: 検出のみ実行（更新なし）
- **成果**: 手動での進捗更新が不要に、Git履歴から自動同期

#### 📋 自動タスク生成（Phase 5）
- **RequirementsParser**: requirements.mdから自動でタスク生成
  - Markdown解析とセクション抽出
  - ファイルパスの自動推論（10種類のパターン対応）
  - 依存関係の自動推論（レイヤーベース + ファイルベース）
  - 優先度と担当者の自動決定
- CLIコマンド: `cmw tasks generate`

#### 🔍 ファイル競合検出（Phase 6）
- **ConflictDetector**: タスク間のファイル競合を事前検出
  - WRITE-WRITE競合の検出
  - トポロジカルソートによる最適な実行順序の提案
  - 並列実行グループの自動生成
  - 競合の深刻度判定（CRITICAL/HIGH/MEDIUM/LOW）
  - ファイル使用状況とリスク分析
- CLIコマンド: `cmw tasks analyze`

#### 📊 リアルタイム進捗UI（Phase 7）
- **ProgressTracker**: 進捗メトリクスの計算と追跡
  - 進捗サマリー（完了率、成功率）
  - 残り時間の推定（完了タスクの平均所要時間から算出）
  - タスクタイムライン
  - ベロシティメトリクス（タスク/時間、平均所要時間）
  - 優先度別・担当者別の進捗分解
- **Dashboard**: 美しいターミナルダッシュボード
  - Rich ライブラリによる視覚的なUI
  - プロジェクト概要、ベロシティ、進捗テーブル
  - 最近のアクティビティタイムライン
- CLIコマンド: `cmw status` / `cmw status --compact`

#### 🛠️ タスク管理層（Phase 1）
- **TaskProvider**: タスク情報の提供、コンテキスト構築、状態管理
- **StateManager**: ロック機構、セッション管理、進捗永続化
- **ParallelExecutor**: 並列実行判定、ファイル競合検出

#### ⚠️ エラーハンドリング（Phase 3）
- **ErrorHandler**: エラー対応決定、ロールバック、復旧提案
  - リトライ可能なエラーの自動判定
  - 部分的な成果物の自動削除
  - エラー別の復旧方法提案
  - 影響を受けるタスクの分析

#### 💬 フィードバック機能（Phase 4）
- **FeedbackManager**: リアルタイムフィードバック
  - プロジェクト全体の進捗表示
  - エラーの分かりやすい説明
  - 次のアクション提案

#### 🏗️ 基盤機能（Phase 0）
- プロジェクト初期化（`cmw init`）
- タスク定義（tasks.json）
- 依存関係管理
- 進捗管理
- CLI実装

### 🎓 実プロジェクト検証完了
- **検証プロジェクト**: [todo-api](https://github.com/nakishiyaman/todo-api)
  - 17タスク、2000行コード、106テスト
  - 全タスク完了、全テストパス
  - 9つのAPIエンドポイントが正常動作
  - ファイル競合検出: 2件（CRITICAL 1件、MEDIUM 1件）

## 📦 インストール

### 方法1: PyPIから（推奨）

```bash
pip install claude-multi-worker
```

インストール後、`cmw`コマンドが利用可能になります。

### 方法2: GitHubから

```bash
pip install git+https://github.com/nakishiyaman/cmw.git
```

### 方法3: ソースから（開発者向け）

```bash
# リポジトリをクローン
git clone https://github.com/nakishiyaman/cmw.git
cd cmw

# 仮想環境を作成（推奨）
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# または
venv\Scripts\activate  # Windows

# 依存パッケージをインストール
pip install -r requirements.txt

# cmwコマンドをインストール
pip install -e .
```

## 🚀 クイックスタート

### 1. プロジェクト初期化

```bash
# 方法A: 新しいディレクトリを作成して初期化
cmw init my-project
cd my-project

# 方法B: カレントディレクトリで初期化
mkdir my-project && cd my-project
cmw init
```

### 2. requirements.mdを作成

#### 方法A: Claude Code統合（推奨）

`cmw requirements generate`コマンドを使用すると、Claude Codeと連携して自動でrequirements.mdを生成できます。

```bash
# 1行でプロジェクトの要望を伝えるだけ
cmw requirements generate --with-claude --prompt "ToDoアプリを作りたい"

# 次のステップが表示される:
# 1. Claude Codeを開いてください
# 2. 以下のプロンプトを Claude Code に送信してください:
#    「.cmw_prompt.md の内容に従って、requirements.mdを生成して
#     shared/docs/requirements.md に保存してください」
# 3. Claude Codeが生成完了したら:
#    cmw task generate でタスク自動生成
```

**仕組み:**
- cmwがプロンプトテンプレートを生成（`.cmw_prompt.md`）
- ユーザーがそのプロンプトをClaude Codeに渡す
- Claude Codeが詳細なrequirements.mdを生成
- 生成されたrequirements.mdから自動でタスクを生成

#### 方法B: 対話型ウィザード

対話形式で段階的にrequirements.mdを作成できます。

```bash
# 対話型ウィザードを起動
cmw requirements generate

# プロジェクト名、技術スタック、データモデル、API機能などを
# 質問に答えながら入力していく
```

#### 方法C: 手動作成

`shared/docs/requirements.md`に直接要件を記述：

```markdown
# プロジェクト要件

## 1. ユーザー認証
- ユーザー登録機能
- ログイン/ログアウト
- パスワードリセット

## 2. ToDoリスト管理
- ToDoの作成、更新、削除
- 完了/未完了の切り替え
```

### 3. タスク生成

```bash
# requirements.mdからタスクを自動生成
cmw tasks generate
```

### 4. Claude Codeから使用

Claude Codeのセッションで：

```python
from pathlib import Path
from cmw import TaskProvider

# プロジェクトパスを指定
project_path = Path.cwd()
provider = TaskProvider(project_path)

# 次のタスクを取得
task = provider.get_next_task()
print(f"次のタスク: {task.id} - {task.title}")

# タスク開始を記録
provider.mark_started(task.id)

# タスクコンテキストを取得
context = provider.get_task_context(task.id)
print(f"対象ファイル: {context['task']['target_files']}")
print(f"受け入れ基準: {context['task']['acceptance_criteria']}")

# Claude Codeがコーディング（自身の機能で実行）
# ... コード生成 ...

# 完了報告
provider.mark_completed(task.id, ["shared/artifacts/backend/auth.py"])
```

詳細は[Claude Code統合ガイド](docs/CLAUDE_CODE_INTEGRATION.md)を参照してください。

## 📂 プロジェクト構造

```
my-project/
├── shared/
│   ├── docs/                 # 設計ドキュメント
│   │   ├── requirements.md   # 要件定義
│   │   └── api-spec.md       # API仕様
│   ├── coordination/         # タスク定義と進捗
│   │   ├── tasks.json        # タスク定義
│   │   ├── progress.json     # 進捗管理
│   │   └── .lock             # セッションロック
│   └── artifacts/            # 生成されたコード
│       ├── backend/
│       ├── frontend/
│       └── tests/
```

## 🎮 CLIコマンド

### プロジェクト管理

```bash
# プロジェクト初期化（サブディレクトリを作成）
cmw init <project-name>

# プロジェクト初期化（カレントディレクトリで）
cmw init

# プロジェクト状態表示（フルダッシュボード）
cmw status

# プロジェクト状態表示（コンパクト）
cmw status --compact
```

### Requirements管理

```bash
# requirements.md生成（Claude Code統合）
cmw requirements generate --with-claude --prompt "プロジェクトの説明"

# requirements.md生成（対話型ウィザード）
cmw requirements generate

# requirements.md生成（出力先指定）
cmw requirements generate -o custom/path/requirements.md
```

### タスク管理

```bash
# タスク生成
cmw task generate

# タスク一覧
cmw task list
cmw task list --status pending
cmw task list --status completed

# タスク詳細
cmw task show TASK-001

# タスク検証（v0.2.0）
cmw task validate              # 循環依存、非タスク項目、依存関係をチェック
cmw task validate --fix        # 検出した問題を自動修正

# ファイル競合分析
cmw task analyze

# 依存関係グラフ表示（v0.3.0）
cmw task graph                  # ASCII形式でグラフ表示
cmw task graph --format mermaid # Mermaid形式で出力
cmw task graph --stats          # 統計情報も表示

# タスク実行プロンプト生成（v0.3.0）
cmw task prompt TASK-001        # TASK-001の実行プロンプトを生成

# タスク完了マーク（v0.3.1）
cmw task complete TASK-001                                      # タスクを完了にマーク
cmw task complete TASK-001 --artifacts '["file1.py"]'         # 生成ファイルも記録
cmw task complete TASK-001 -a '["file1.py"]' -m "実装完了"   # メッセージ付き
```

### インテリジェント・タスク管理 (v0.6.0 NEW!)

```bash
# 次に実行すべきタスクを提案
cmw task next                   # 実行可能なタスクを依存関係・優先度順に表示
cmw task next --num 5           # 5件表示

# クリティカルパス分析
cmw task critical               # プロジェクト完了に最も影響するタスクを表示
                                # ボトルネック検出、完了予測も含む

# スマートタスク実行
cmw task exec TASK-002          # タスクの詳細プロンプトを生成
                                # ステータスを自動でin_progressに更新
                                # 依存関係、関連ファイル、実装ガイドを表示
```

### 進捗管理

```bash
# Git連携で進捗を同期（v0.2.0）
cmw sync --from-git                    # 過去1週間分のコミットから同期
cmw sync --from-git --since=1.day.ago  # 過去1日分
cmw sync --from-git --dry-run          # 検出のみ（更新なし）
```

## 🚀 実践的な使い方

### 基本的なワークフロー

```bash
# 1. タスク生成
cmw task generate

# 2. 次に実行すべきタスクを確認
cmw task next

# 出力例:
# 🎯 実行可能なタスク (依存関係クリア済み)
#
# 1. TASK-002: 3.1 Userモデル
#    └─ 優先度: HIGH 🔴 CRITICAL
#    └─ 理由: クリティカルパス上, 14タスクをブロック中
#    └─ 影響範囲: 14タスクがブロック中
#
# タスクを開始するには:
#   cmw task exec TASK-002

# 3. タスクを開始
cmw task exec TASK-002

# → 詳細なプロンプトが表示される:
#   - タスク概要（重要度を強調）
#   - 依存関係（前提タスク、待機中のタスク）
#   - 関連ファイル
#   - 実装ガイド
#   - 完了条件チェックリスト
#   - テストコマンド
#   - 次のステップ

# 4. Claude Codeで作業...

# 5. タスク完了
cmw task complete TASK-002

# 6. 次のタスクへ
cmw task next
```

### クリティカルパスを意識した進行

```bash
# クリティカルパスを確認
cmw task critical

# 出力例:
# ⚡ クリティカルパス分析
#
# プロジェクト完了予測:
#   楽観的予測: 7.3日 (並行実行フル活用)
#   悲観的予測: 11.5日 (クリティカルパス基準)
#   進捗: 35% (8/23タスク)
#
# 🔴 クリティカルパス (遅延厳禁):
# ┌──────────────────────────────────────────────────────┐
# │ ⏳ TASK-002: Userモデル
# │   ↓
# │ ⏳ TASK-003: Todoモデル
# │   ↓
# │ ⏳ TASK-006: Todo機能
# │   ...
# └──────────────────────────────────────────────────────┘
#
# ⚠️  ボトルネック警告:
#   • TASK-002: 14タスクが依存
#     → 3.1 Userモデル

# 最優先タスクから着手
cmw task exec TASK-002
```

## 📚 チートシート

### タスク選択

```bash
cmw task next              # 次にやるべきタスクを提案
cmw task critical          # クリティカルパス確認
cmw task graph             # 依存関係グラフ可視化
```

### タスク実行

```bash
cmw task exec TASK-002     # タスク開始（プロンプト生成）
# ... Claude Codeで作業 ...
cmw task complete TASK-002 # 完了マーク
```

### 進捗確認

```bash
cmw status                 # 全体進捗
cmw task list --status in_progress  # 進行中タスク
```

### 分析

```bash
cmw task analyze           # ファイル競合分析
cmw task validate          # タスク品質検証
```

## 📖 ドキュメント

### ユーザー向けドキュメント
- **[全機能詳細 (FEATURES.md)](docs/FEATURES.md)** - 全機能の詳細説明と使用例
- **[Claude Code統合ガイド (CLAUDE_CODE_INTEGRATION.md)](docs/CLAUDE_CODE_INTEGRATION.md)** - Claude Codeからの使用方法
- **[WHY CMW (WHY_CMW.md)](docs/WHY_CMW.md)** - cmwが必要な理由と利点

### 開発者向けドキュメント
- **[CHANGELOG.md](CHANGELOG.md)** - 全バージョンの変更履歴
- **[開発ロードマップ (ROADMAP.md)](docs/ROADMAP.md)** - Phase別の実装履歴とバージョン詳細
- **[テスト戦略 (TESTING.md)](docs/TESTING.md)** - テストカバレッジ、実行方法、追加ガイドライン
- **[セキュリティ監査 (SECURITY_AUDIT.md)](docs/SECURITY_AUDIT.md)** - セキュリティ対策と監査結果

## 🧪 テスト

```bash
# 全テストを実行
python -m pytest tests/ -v

# カバレッジレポート付き
python -m pytest tests/ --cov=src/cmw --cov-report=term-missing
```

**現在の状況:** 500個のテスト全てパス（88%カバレッジ）

<details>
<summary>📋 個別テストコマンド一覧（クリックして展開）</summary>

```bash
# コア機能
python -m pytest tests/test_task_provider.py -v
python -m pytest tests/test_state_manager.py -v
python -m pytest tests/test_parallel_executor.py -v
python -m pytest tests/test_error_handler.py -v
python -m pytest tests/test_feedback.py -v

# パース・解析
python -m pytest tests/test_requirements_parser.py -v
python -m pytest tests/test_conflict_detector.py -v
python -m pytest tests/test_static_analyzer.py -v

# UI・表示
python -m pytest tests/test_progress_tracker.py -v
python -m pytest tests/test_graph_visualizer.py -v
python -m pytest tests/test_dashboard.py -v

# Claude Code統合
python -m pytest tests/test_prompt_template.py -v
python -m pytest tests/test_interactive_fixer.py -v
python -m pytest tests/test_response_parser.py -v
python -m pytest tests/test_coordinator.py -v
python -m pytest tests/test_cli_complete.py -v

# インテリジェント機能（v0.6.0）
python -m pytest tests/test_dependency_analyzer.py -v
python -m pytest tests/test_smart_prompt_generator.py -v

# 品質保証（v0.6.2）
python -m pytest tests/test_performance.py -v
python -m pytest tests/test_integration.py -v
python -m pytest tests/test_edge_cases.py -v
python -m pytest tests/test_security.py -v
python -m pytest tests/test_reliability.py -v
```

</details>

## 📊 開発ロードマップ

### 現在のバージョン: v0.6.2 ✅

**主要機能（Phase 0-8完了）:**
- ✅ 基盤構築、タスク管理層、Claude Code統合最適化
- ✅ 循環依存自動修正、Git連携、ファイル競合検出
- ✅ リアルタイム進捗UI、インテリジェント・タスク管理
- ✅ 100%型安全、88%テストカバレッジ（500テスト）
- ✅ パフォーマンス・信頼性・セキュリティ強化

**詳細な変更履歴は [CHANGELOG.md](CHANGELOG.md) を参照してください。**

---

## 🚧 次期バージョン予告（v0.7.0）

### MCP統合・Plugin化（開発予定）

Claude Codeとのシームレスな統合を実現します。

**予定機能:**
- 🔌 **Model Context Protocol (MCP)サーバー実装**
  - Claude Code内から直接cmw機能を呼び出し
  - `get_next_task()`, `complete_task()` 等のMCP Tools
  - タスク一覧、進捗状況等のMCP Resources

- 📦 **Claude Code Plugin化**
  - ワンコマンドインストール: `/plugin marketplace add nakishiyaman/cmw`
  - スラッシュコマンド: `/next-task`, `/complete-task`
  - Skills（ワークフロー指示書）の自動適用
  - `claude.json`による設定ファイル対応

- ⚡ **ワークフロー自動化**
  - Claude Codeが自動的にタスクを取得・完了マーク
  - 手動のコマンド実行が不要に
  - リアルタイムな進捗同期

**リリース予定:** 2025年11月中旬

**注記:** v0.6.0では、Claude Code Pluginとしてのインストールはまだ対応していません。現在はCLIツールとしてPyPI経由でインストールしてください。Plugin対応はv0.7.0で実装予定です。

**現在の使い方（v0.6.0）:**
```bash
# インテリジェントなタスク管理
cmw task next              # 次のタスクを提案
cmw task exec TASK-001     # プロンプト生成 + ステータス更新
# → Claude Codeで実装
cmw task complete TASK-001 # 完了マーク
```

**v0.7.0での使い方（予定）:**
```bash
# Claude Code内で
ユーザー: 「次のタスクを実装して」
→ Claude Codeが自動でget_next_task()呼び出し
→ 実装
→ 自動でcomplete_task()実行
```

進捗は[GitHub Issues](https://github.com/nakishiyaman/cmw/issues)で追跡できます。

---

## 💡 主な特徴

### 1. 🤖 完全自動化されたタスク生成
requirements.mdを書くだけで、タスクの分解、ファイルパスの推論、依存関係の設定まで全て自動化。手動でtasks.jsonを書く必要はありません。

### 2. 🔍 インテリジェントな競合検出
タスク間のファイル競合を事前に検出し、最適な実行順序を自動提案。並列実行の可否も自動判定します。

### 3. 📊 リアルタイム進捗可視化
美しいターミナルダッシュボードで進捗を可視化。完了率、成功率、推定残り時間、ベロシティメトリクスを一目で確認できます。

### 4. 🔒 100%型安全 + クリーンコード + 高信頼性
**mypy完全対応**で型エラーゼロを達成。IDE補完が完璧に機能し、リファクタリングも安心。**ruff format**で統一されたコードスタイル、**88%テストカバレッジ**（500テスト）で高品質を保証。**コード複雑度削減**により保守性が向上（高複雑度関数 12個→10個）。**パフォーマンス問題の修正**（循環検出ハング解消）、**包括的なセキュリティテスト**（パストラバーサル、コマンドインジェクション対策）、**信頼性テスト**（ファイル破損対応）により、本番環境でも安心して使用できます。CI/CDで型チェックとlintを自動化し、品質の高いコードベースを維持します。

### 5. 💰 APIコストゼロ
Claude Codeが直接コードを生成するため、追加のAPI呼び出しコストはかかりません。

### 6. 🔄 セッション継続性
`progress.json`に状態を永続化するため、セッションを跨いで開発を継続できます。

### 7. 🛡️ 堅牢なエラーハンドリング
エラーの自動分類、リトライ判定、ロールバック、復旧提案まで完全自動化。

## 🔧 技術スタック

- **Python 3.9+**
- **Click**: CLIフレームワーク
- **Rich**: ターミナルUI（ダッシュボード表示）
- **NetworkX**: グラフアルゴリズム（依存関係、競合検出）
- **pytest**: テストフレームワーク
- **mypy**: 静的型チェック（100%型安全）
- **Pydantic**: データバリデーション（モデル定義）

## 📝 ライセンス

MIT License

## 👥 開発者

- GitHub: https://github.com/nakishiyaman/cmw

## 🤝 貢献

バグ報告や機能リクエストは、GitHubのIssuesでお願いします。

## 🔗 関連リンク

- [Claude Code公式ドキュメント](https://docs.claude.com/en/docs/claude-code)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
