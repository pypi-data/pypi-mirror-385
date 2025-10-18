"""
パフォーマンステスト

このモジュールは、大規模なデータセットや複雑なグラフ構造での
パフォーマンス問題を検出するためのテストを含みます。
"""
import time
from cmw.dependency_validator import DependencyValidator
from cmw.graph_visualizer import GraphVisualizer
from cmw.requirements_parser import RequirementsParser
from cmw.models import Task, Priority
from pathlib import Path
import tempfile


class TestCycleDetectionPerformance:
    """循環依存検出のパフォーマンステスト"""

    def test_detect_cycles_with_complex_graph(self):
        """複雑な循環依存グラフで合理的な時間内に完了する"""
        # 実際の問題に近い25タスク、複雑な相互依存を再現
        tasks = []

        # 基盤タスク
        for i in range(1, 6):
            task_id = f"TASK-{i:03d}"
            deps = []
            if i > 1:
                # 各タスクが前のタスクに依存
                deps = [f"TASK-{j:03d}" for j in range(max(1, i-1), i)]

            tasks.append(Task(
                id=task_id,
                title=f"Task {i}",
                description="Test",
                assigned_to="backend",
                dependencies=deps,
                priority=Priority.HIGH
            ))

        # 中間タスク（複雑な依存関係）
        for i in range(6, 21):
            task_id = f"TASK-{i:03d}"
            # 複数の依存関係を持つ
            deps = [f"TASK-{j:03d}" for j in range(max(1, i-5), min(i, 10))]
            tasks.append(Task(
                id=task_id,
                title=f"Task {i}",
                description="Test",
                assigned_to="backend",
                dependencies=deps,
                priority=Priority.MEDIUM
            ))

        # 循環依存を作るタスク
        tasks.append(Task(
            id="TASK-020",
            title="Task 20",
            description="Test",
            assigned_to="backend",
            dependencies=["TASK-002", "TASK-003"],
            priority=Priority.MEDIUM
        ))

        # 逆方向の依存で循環を閉じる
        tasks[1].dependencies.append("TASK-020")  # TASK-002 -> TASK-020

        validator = DependencyValidator()

        # パフォーマンス計測
        start_time = time.time()
        cycles = validator.detect_cycles(tasks)
        elapsed = time.time() - start_time

        # 3秒以内に完了すること
        assert elapsed < 3.0, f"Cycle detection took too long: {elapsed:.2f}s"

        # サイクルが検出されること
        assert len(cycles) > 0, "Expected cycles to be detected"

        # 最大10サイクルまで検出（修正後の仕様）
        assert len(cycles) <= 10

    def test_detect_cycles_with_dense_graph(self):
        """密なグラフ（多数の相互依存）でハングしない"""
        # 各タスクが複数のタスクに依存し、相互に循環する密なグラフ
        tasks = []
        n_tasks = 15

        for i in range(n_tasks):
            task_id = f"TASK-{i:03d}"
            # 各タスクが後ろの数個のタスクに依存（循環を作る）
            deps = []
            for j in range(i+1, min(n_tasks, i+4)):
                deps.append(f"TASK-{j:03d}")

            # 最後のいくつかのタスクは最初のタスクに依存（循環を閉じる）
            if i >= n_tasks - 3:
                deps.append("TASK-000")

            tasks.append(Task(
                id=task_id,
                title=f"Task {i}",
                description="Test",
                assigned_to="backend",
                dependencies=deps,
                priority=Priority.MEDIUM
            ))

        validator = DependencyValidator()

        start_time = time.time()
        cycles = validator.detect_cycles(tasks)
        elapsed = time.time() - start_time

        # 5秒以内に完了すること（密なグラフでも）
        assert elapsed < 5.0, f"Dense graph cycle detection took too long: {elapsed:.2f}s"

        # サイクルが検出されること
        assert len(cycles) > 0, "Expected cycles to be detected in dense graph"

        # 修正後の仕様: 最大10個まで検出
        assert len(cycles) <= 10, f"Expected max 10 cycles, got {len(cycles)}"

    def test_detect_cycles_timeout(self):
        """循環検出が合理的な時間でタイムアウトする"""
        # 非常に複雑なグラフでもタイムアウトすることなく結果を返す
        tasks = []
        n_tasks = 30

        for i in range(n_tasks):
            task_id = f"TASK-{i:03d}"
            # ランダムに見える複雑な依存関係
            deps = []
            for j in range(i):
                if (i * 7 + j * 13) % 5 == 0:  # 疑似ランダム
                    deps.append(f"TASK-{j:03d}")

            # いくつかの循環を追加
            if i > 5 and i % 3 == 0:
                deps.append(f"TASK-{max(0, i-10):03d}")

            tasks.append(Task(
                id=task_id,
                title=f"Task {i}",
                description="Test",
                assigned_to="backend",
                dependencies=deps,
                priority=Priority.MEDIUM
            ))

        validator = DependencyValidator()

        start_time = time.time()
        cycles = validator.detect_cycles(tasks)
        elapsed = time.time() - start_time

        # どんなに複雑でも10秒以内に終了すること
        assert elapsed < 10.0, f"Cycle detection timeout failed: {elapsed:.2f}s"
        assert isinstance(cycles, list)  # 循環検出結果を使用


class TestGraphVisualizerPerformance:
    """GraphVisualizerのパフォーマンステスト"""

    def test_get_task_depth_with_cycles(self):
        """循環依存があるグラフでget_task_depth()が無限ループしない"""
        # 循環依存を含むタスク
        tasks = [
            Task(
                id="TASK-001",
                title="Task 1",
                description="Test",
                assigned_to="backend",
                dependencies=["TASK-003"],
                priority=Priority.HIGH
            ),
            Task(
                id="TASK-002",
                title="Task 2",
                description="Test",
                assigned_to="backend",
                dependencies=["TASK-001"],
                priority=Priority.MEDIUM
            ),
            Task(
                id="TASK-003",
                title="Task 3",
                description="Test",
                assigned_to="backend",
                dependencies=["TASK-002"],
                priority=Priority.MEDIUM
            ),
        ]

        visualizer = GraphVisualizer(tasks)

        start_time = time.time()
        depth = visualizer.get_task_depth("TASK-001")
        elapsed = time.time() - start_time

        # 即座に完了すること（1秒以内）
        assert elapsed < 1.0, f"get_task_depth took too long: {elapsed:.2f}s"

        # 循環依存を検出して-1を返すこと
        assert depth == -1, "Expected -1 for cyclic dependency"

    def test_get_task_depth_deep_graph(self):
        """深い依存関係グラフでスタックオーバーフローしない"""
        # 30段階の深い依存関係
        tasks = []
        for i in range(30):
            task_id = f"TASK-{i:03d}"
            deps = [f"TASK-{i-1:03d}"] if i > 0 else []
            tasks.append(Task(
                id=task_id,
                title=f"Task {i}",
                description="Test",
                assigned_to="backend",
                dependencies=deps,
                priority=Priority.MEDIUM
            ))

        visualizer = GraphVisualizer(tasks)

        start_time = time.time()
        depth = visualizer.get_task_depth("TASK-029")
        elapsed = time.time() - start_time

        # 合理的な時間で完了すること
        assert elapsed < 2.0, f"Deep graph depth calculation took too long: {elapsed:.2f}s"

        # 正しい深さを返すこと
        assert depth == 29


class TestRequirementsParserPerformance:
    """RequirementsParserのパフォーマンステスト"""

    def test_parse_large_requirements(self):
        """大規模なrequirements.mdを合理的な時間でパースする"""
        # 実際の問題に近い12セクション、複雑な構造のMarkdown
        content = """# Todo API Project Requirements

## 1. 技術スタック
- FastAPI
- SQLAlchemy
- PostgreSQL

## 2. データベース設定
### 2.1 モデル定義
- Userモデルの作成
- Taskモデルの作成

### 2.2 データベース接続
- database.py作成
- SQLAlchemy設定

## 3. 認証機能
### 3.1 ユーザー登録
- エンドポイント: POST /auth/register
- パスワードハッシュ化

### 3.2 ログイン
- エンドポイント: POST /auth/login
- JWTトークン発行

## 4. タスク管理API
### 4.1 タスク作成
- エンドポイント: POST /tasks
- バリデーション

### 4.2 タスク一覧取得
- エンドポイント: GET /tasks
- フィルタ機能

### 4.3 タスク更新
- エンドポイント: PUT /tasks/{id}
- 認証チェック

### 4.4 タスク削除
- エンドポイント: DELETE /tasks/{id}
- 認証チェック

## 5. テスト
### 5.1 認証テスト
- ユーザー登録テスト
- ログインテスト

### 5.2 タスクAPIテスト
- CRUD操作テスト

## 6. ドキュメント
- README.md作成
- API仕様書作成
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = Path(f.name)

        try:
            parser = RequirementsParser()

            start_time = time.time()
            tasks = parser.parse(temp_path)
            elapsed = time.time() - start_time

            # 30秒以内に完了すること（修正前はタイムアウト）
            assert elapsed < 30.0, f"Requirements parsing took too long: {elapsed:.2f}s"

            # タスクが生成されること
            assert len(tasks) > 0, "Expected tasks to be generated"

            # 循環依存が処理されていること（ハングしない）
            print(f"✅ Parsed {len(tasks)} tasks in {elapsed:.2f}s")

        finally:
            temp_path.unlink()

    def test_parse_with_multiple_cycles(self):
        """複数の循環依存を含むrequirements.mdで完了する"""
        # 意図的に循環依存を作るMarkdown
        content = """# Project

## A. Foundation
- database.py作成
- models.py作成
- 認証システム構築

## B. Core Features
- API実装
- database依存
- Foundation完了後

## C. Advanced
- 高度な機能
- Core Features依存
- Foundation依存
"""

        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_path = Path(f.name)

        try:
            parser = RequirementsParser()

            start_time = time.time()
            tasks = parser.parse(temp_path)
            elapsed = time.time() - start_time

            # タイムアウトせずに完了すること
            assert elapsed < 10.0, f"Parsing with cycles took too long: {elapsed:.2f}s"

            print(f"✅ Parsed {len(tasks)} tasks with cycles in {elapsed:.2f}s")

        finally:
            temp_path.unlink()


class TestEdgeCases:
    """エッジケースのテスト"""

    def test_empty_graph(self):
        """空のグラフでエラーにならない"""
        validator = DependencyValidator()
        cycles = validator.detect_cycles([])
        assert cycles == []

    def test_single_task_no_deps(self):
        """単一タスク、依存なしでエラーにならない"""
        tasks = [Task(
            id="TASK-001",
            title="Single",
            description="Test",
            assigned_to="backend",
            dependencies=[],
            priority=Priority.HIGH
        )]

        validator = DependencyValidator()
        cycles = validator.detect_cycles(tasks)
        assert cycles == []

    def test_self_dependency(self):
        """自己依存を検出する"""
        tasks = [Task(
            id="TASK-001",
            title="Self",
            description="Test",
            assigned_to="backend",
            dependencies=["TASK-001"],
            priority=Priority.HIGH
        )]

        validator = DependencyValidator()
        cycles = validator.detect_cycles(tasks)

        # 自己依存もサイクルとして検出されること
        assert len(cycles) >= 1
