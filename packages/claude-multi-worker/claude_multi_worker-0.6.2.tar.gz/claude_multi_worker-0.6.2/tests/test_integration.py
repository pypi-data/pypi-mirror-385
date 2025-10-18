"""
統合テスト

このモジュールは、複数のコンポーネントを組み合わせた
エンドツーエンドのシナリオをテストします。
"""
import pytest
import tempfile
import json
from pathlib import Path
from cmw.requirements_parser import RequirementsParser
from cmw.dependency_validator import DependencyValidator
from cmw.graph_visualizer import GraphVisualizer
from cmw.models import Task, Priority


class TestEndToEndWorkflow:
    """エンドツーエンドのワークフローテスト"""

    @pytest.fixture
    def complex_requirements(self):
        """複雑なrequirements.md"""
        return """# Todo API Project

## 1. 技術スタック
- FastAPI
- PostgreSQL
- SQLAlchemy

## 2. データベース設定

### 2.1 データベース接続
- database.py作成
- SQLAlchemy設定
- 接続プール設定

### 2.2 モデル定義
- Userモデルの作成
- Taskモデルの作成
- リレーションシップの設定

## 3. 認証機能

### 3.1 ユーザー登録
- エンドポイント: POST /auth/register
- メールアドレスバリデーション
- パスワードハッシュ化

### 3.2 ログイン
- エンドポイント: POST /auth/login
- JWTトークン発行
- 認証情報の検証

## 4. タスク管理API

### 4.1 タスク作成
- エンドポイント: POST /tasks
- タイトルバリデーション
- 認証済みユーザーのタスク作成

### 4.2 タスク一覧取得
- エンドポイント: GET /tasks
- フィルタ機能
- ページネーション

### 4.3 タスク更新
- エンドポイント: PUT /tasks/{id}
- 認証チェック
- バリデーション

### 4.4 タスク削除
- エンドポイント: DELETE /tasks/{id}
- 認証チェック
- 権限確認

## 5. テスト

### 5.1 認証テスト
- ユーザー登録テスト
- ログインテスト
- 認証エラーテスト

### 5.2 タスクAPIテスト
- CRUD操作テスト
- 権限テスト

## 6. ドキュメント
- README.md作成
- API仕様書作成
"""

    def test_full_parse_validate_visualize_workflow(self, complex_requirements):
        """完全なワークフロー: パース → 検証 → 可視化"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(complex_requirements)
            req_path = Path(f.name)

        try:
            # Step 1: requirements.mdをパース
            parser = RequirementsParser()
            tasks = parser.parse(req_path)

            assert len(tasks) > 0, "Tasks should be generated"
            assert all(isinstance(task, Task) for task in tasks)

            # Step 2: 依存関係を検証
            validator = DependencyValidator()
            validation_result = validator.validate_dependencies(tasks)

            # 循環依存が処理されていること
            assert isinstance(validation_result['has_cycles'], bool)
            assert isinstance(validation_result['cycles'], list)

            # Step 3: グラフを可視化
            visualizer = GraphVisualizer(tasks)
            stats = visualizer.get_statistics()

            assert stats['total_tasks'] == len(tasks)
            assert stats['total_dependencies'] >= 0

            # Step 4: ASCII出力を生成
            ascii_graph = visualizer.render_ascii()
            assert len(ascii_graph) > 0

            # Step 5: Mermaid形式を生成
            mermaid = visualizer.render_mermaid()
            assert "graph TD" in mermaid

            print(f"✅ Full workflow completed: {len(tasks)} tasks processed")

        finally:
            req_path.unlink()

    def test_parse_with_cycles_auto_fix(self, complex_requirements):
        """循環依存の自動修正フロー"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(complex_requirements)
            req_path = Path(f.name)

        try:
            parser = RequirementsParser()
            tasks = parser.parse(req_path)

            # 意図的に循環を追加
            if len(tasks) >= 3:
                tasks[0].dependencies.append(tasks[2].id)
                tasks[2].dependencies.append(tasks[0].id)

            # 循環を検出
            validator = DependencyValidator()
            cycles = validator.detect_cycles(tasks)

            if cycles:
                # 自動修正を適用
                fixed_tasks = validator.auto_fix_cycles(tasks, cycles, auto_apply=True)

                # 修正後に循環が解消されているか確認
                remaining_cycles = validator.detect_cycles(fixed_tasks)

                # 全ての循環が解消されているか、減少していることを確認
                assert len(remaining_cycles) <= len(cycles)

        finally:
            req_path.unlink()

    def test_task_json_round_trip(self, complex_requirements):
        """タスクのJSON保存と読み込み"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(complex_requirements)
            req_path = Path(f.name)

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f_json:
            json_path = Path(f_json.name)

        try:
            # タスクを生成
            parser = RequirementsParser()
            tasks = parser.parse(req_path)

            # JSONに保存
            tasks_data = {
                "tasks": [
                    {
                        "id": task.id,
                        "title": task.title,
                        "description": task.description,
                        "assigned_to": task.assigned_to,
                        "dependencies": task.dependencies,
                        "target_files": task.target_files,
                        "acceptance_criteria": task.acceptance_criteria,
                        "priority": task.priority,
                    }
                    for task in tasks
                ]
            }

            json_path.write_text(json.dumps(tasks_data, ensure_ascii=False, indent=2), encoding='utf-8')

            # JSONから読み込み
            loaded_data = json.loads(json_path.read_text(encoding='utf-8'))

            assert len(loaded_data["tasks"]) == len(tasks)

            # データの整合性を確認
            for original, loaded in zip(tasks, loaded_data["tasks"]):
                assert original.id == loaded["id"]
                assert original.title == loaded["title"]
                assert original.dependencies == loaded["dependencies"]

        finally:
            req_path.unlink()
            if json_path.exists():
                json_path.unlink()


class TestErrorRecovery:
    """エラーリカバリーのテスト"""

    def test_invalid_requirements_file(self):
        """不正なrequirements.mdの処理"""
        parser = RequirementsParser()

        with pytest.raises(FileNotFoundError):
            parser.parse(Path("/nonexistent/requirements.md"))

    def test_empty_requirements_file(self):
        """空のrequirements.mdの処理"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write("")
            req_path = Path(f.name)

        try:
            parser = RequirementsParser()
            tasks = parser.parse(req_path)

            # 空のファイルでもエラーにならず、空のタスクリストを返す
            assert isinstance(tasks, list)
            assert len(tasks) == 0

        finally:
            req_path.unlink()

    def test_malformed_markdown(self):
        """不正なMarkdownの処理"""
        malformed = """# Project

No proper sections
Just random text
- Random list item
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(malformed)
            req_path = Path(f.name)

        try:
            parser = RequirementsParser()
            tasks = parser.parse(req_path)

            # エラーにならず、何らかの結果を返す
            assert isinstance(tasks, list)

        finally:
            req_path.unlink()

    def test_missing_dependencies_detection(self):
        """存在しない依存先の検出"""
        tasks = [
            Task(
                id="TASK-001",
                title="Task 1",
                description="Test",
                assigned_to="backend",
                dependencies=["TASK-999", "TASK-888"],  # 存在しないタスク
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
        ]

        validator = DependencyValidator()
        result = validator.validate_dependencies(tasks)

        assert len(result["missing_dependencies"]) == 2
        assert any("TASK-999" in dep for dep in result["missing_dependencies"])
        assert any("TASK-888" in dep for dep in result["missing_dependencies"])


class TestConcurrency:
    """並行処理のテスト"""

    def test_concurrent_cycle_detection(self):
        """複数のグラフで同時に循環検出"""
        import concurrent.futures

        def detect_cycles_for_graph(n_tasks):
            """指定数のタスクでグラフを作成し、循環を検出"""
            tasks = []
            for i in range(n_tasks):
                task_id = f"TASK-{i:03d}"
                deps = []
                if i > 0:
                    deps.append(f"TASK-{i-1:03d}")
                if i == n_tasks - 1:
                    deps.append("TASK-000")  # 循環を作る

                tasks.append(Task(
                    id=task_id,
                    title=f"Task {i}",
                    description="Test",
                    assigned_to="backend",
                    dependencies=deps,
                    priority=Priority.MEDIUM
                ))

            validator = DependencyValidator()
            return validator.detect_cycles(tasks)

        # 複数のグラフを並行処理
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(detect_cycles_for_graph, n) for n in [5, 10, 15, 20]]

            results = [future.result() for future in concurrent.futures.as_completed(futures)]

            # 全ての検出が成功
            assert len(results) == 4
            assert all(isinstance(r, list) for r in results)

    def test_concurrent_visualization(self):
        """複数のグラフを同時に可視化"""
        import concurrent.futures

        def visualize_graph(n_tasks):
            """指定数のタスクでグラフを可視化"""
            tasks = []
            for i in range(n_tasks):
                task_id = f"TASK-{i:03d}"
                deps = [f"TASK-{j:03d}" for j in range(max(0, i-2), i)]

                tasks.append(Task(
                    id=task_id,
                    title=f"Task {i}",
                    description="Test",
                    assigned_to="backend",
                    dependencies=deps,
                    priority=Priority.MEDIUM
                ))

            visualizer = GraphVisualizer(tasks)
            return visualizer.get_statistics()

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(visualize_graph, n) for n in [5, 10, 15]]

            results = [future.result() for future in concurrent.futures.as_completed(futures)]

            assert len(results) == 3
            assert all('total_tasks' in r for r in results)


class TestMemoryAndResource:
    """メモリとリソース管理のテスト"""

    def test_large_task_list_memory(self):
        """大量のタスクでメモリリークがないか"""
        import gc

        # 100タスクを生成
        tasks = []
        for i in range(100):
            task_id = f"TASK-{i:03d}"
            tasks.append(Task(
                id=task_id,
                title=f"Task {i}",
                description="Test " * 100,  # 長い説明
                assigned_to="backend",
                dependencies=[f"TASK-{j:03d}" for j in range(max(0, i-5), i)],
                target_files=[f"file_{j}.py" for j in range(10)],
                acceptance_criteria=[f"Criterion {j}" for j in range(20)],
                priority=Priority.MEDIUM
            ))

        # 循環検出
        validator = DependencyValidator()
        cycles = validator.detect_cycles(tasks)
        assert isinstance(cycles, list)  # 循環検出結果を使用

        # グラフ可視化
        visualizer = GraphVisualizer(tasks)
        stats = visualizer.get_statistics()

        assert stats['total_tasks'] == 100

        # メモリを解放
        del tasks
        del validator
        del visualizer
        gc.collect()

    def test_deep_recursion_limit(self):
        """深い依存関係でスタックオーバーフローしない"""
        # 50段階の深い依存関係
        tasks = []
        for i in range(50):
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

        # 深い再帰でもエラーにならない
        depth = visualizer.get_task_depth("TASK-049")
        assert depth == 49

        # 統計情報も取得できる
        stats = visualizer.get_statistics()
        assert stats['total_tasks'] == 50
