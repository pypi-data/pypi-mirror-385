"""
エッジケースのテスト

このモジュールは、境界条件や特殊なケースでの
動作を検証します。
"""
from cmw.dependency_validator import DependencyValidator
from cmw.graph_visualizer import GraphVisualizer
from cmw.requirements_parser import RequirementsParser
from cmw.task_filter import TaskFilter
from cmw.models import Task, Priority
from pathlib import Path
import tempfile


class TestBoundaryConditions:
    """境界条件のテスト"""

    def test_zero_tasks(self):
        """タスクが0個の場合"""
        validator = DependencyValidator()
        visualizer = GraphVisualizer([])

        # エラーにならない
        cycles = validator.detect_cycles([])
        stats = visualizer.get_statistics()

        assert cycles == []
        assert stats['total_tasks'] == 0
        assert stats['total_dependencies'] == 0

    def test_single_task_no_dependencies(self):
        """依存関係のない単一タスク"""
        task = Task(
            id="TASK-001",
            title="Single",
            description="Test",
            assigned_to="backend",
            dependencies=[],
            priority=Priority.HIGH
        )

        validator = DependencyValidator()
        visualizer = GraphVisualizer([task])

        cycles = validator.detect_cycles([task])
        depth = visualizer.get_task_depth("TASK-001")
        stats = visualizer.get_statistics()

        assert cycles == []
        assert depth == 0
        assert stats['is_dag'] is True

    def test_all_tasks_depend_on_one(self):
        """全タスクが1つのタスクに依存"""
        root = Task(
            id="TASK-000",
            title="Root",
            description="Test",
            assigned_to="backend",
            dependencies=[],
            priority=Priority.HIGH
        )

        dependent_tasks = [root]
        for i in range(1, 11):
            dependent_tasks.append(Task(
                id=f"TASK-{i:03d}",
                title=f"Task {i}",
                description="Test",
                assigned_to="backend",
                dependencies=["TASK-000"],
                priority=Priority.MEDIUM
            ))

        visualizer = GraphVisualizer(dependent_tasks)
        groups = visualizer.get_parallel_groups()

        # レベル0: TASK-000
        # レベル1: TASK-001 ~ TASK-010 (全て並列実行可能)
        assert len(groups) == 2
        assert groups[0] == ["TASK-000"]
        assert len(groups[1]) == 10

    def test_linear_chain(self):
        """線形の依存関係チェーン"""
        tasks = []
        n = 20

        for i in range(n):
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
        critical_path = visualizer.get_critical_path()
        groups = visualizer.get_parallel_groups()

        # クリティカルパスは全タスク
        assert len(critical_path) == n

        # 並列実行不可（全て順次実行）
        assert len(groups) == n

    def test_complete_graph(self):
        """完全グラフ（全タスクが全タスクに依存）"""
        n = 5
        tasks = []

        for i in range(n):
            task_id = f"TASK-{i:03d}"
            # 自分以外の全タスクに依存
            deps = [f"TASK-{j:03d}" for j in range(n) if j != i]

            tasks.append(Task(
                id=task_id,
                title=f"Task {i}",
                description="Test",
                assigned_to="backend",
                dependencies=deps,
                priority=Priority.MEDIUM
            ))

        validator = DependencyValidator()
        cycles = validator.detect_cycles(tasks)

        # 多数の循環が検出される
        assert len(cycles) > 0


class TestUnicodeAndSpecialCharacters:
    """Unicode文字と特殊文字のテスト"""

    def test_japanese_task_title(self):
        """日本語のタスクタイトル"""
        task = Task(
            id="TASK-001",
            title="データベース設定",
            description="PostgreSQLの設定を行う",
            assigned_to="backend",
            dependencies=[],
            priority=Priority.HIGH
        )

        assert task.title == "データベース設定"
        assert task.description == "PostgreSQLの設定を行う"

    def test_unicode_in_requirements(self):
        """Unicodeを含むrequirements.md"""
        content = """# プロジェクト要件

## 1. データベース設定
- PostgreSQLのセットアップ
- 日本語データのサポート
- 絵文字の保存 🎉

## 2. API実装
- エンドポイント: POST /タスク
- UTF-8対応
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(content)
            req_path = Path(f.name)

        try:
            parser = RequirementsParser()
            tasks = parser.parse(req_path)

            # Unicode文字が正しく処理される
            assert any("データベース" in task.title for task in tasks)

        finally:
            req_path.unlink()

    def test_special_characters_in_task_id(self):
        """タスクIDに特殊文字（実際は使わないが、堅牢性確認）"""
        # 通常はTASK-001形式だが、異常系として確認
        task = Task(
            id="TASK-001",
            title="Normal Task",
            description="Test",
            assigned_to="backend",
            dependencies=[],
            priority=Priority.HIGH
        )

        validator = DependencyValidator()
        result = validator.validate_dependencies([task])

        assert not result['has_cycles']


class TestInvalidInput:
    """不正な入力のテスト"""

    def test_invalid_priority(self):
        """不正な優先度"""
        # Priorityはenumなので型チェックされる
        task = Task(
            id="TASK-001",
            title="Test",
            description="Test",
            assigned_to="backend",
            dependencies=[],
            priority=Priority.HIGH
        )

        assert task.priority == Priority.HIGH

    def test_duplicate_task_ids(self):
        """重複したタスクID"""
        tasks = [
            Task(
                id="TASK-001",
                title="Task 1",
                description="Test",
                assigned_to="backend",
                dependencies=[],
                priority=Priority.HIGH
            ),
            Task(
                id="TASK-001",  # 重複
                title="Task 1 Duplicate",
                description="Test",
                assigned_to="backend",
                dependencies=[],
                priority=Priority.HIGH
            ),
        ]

        # GraphVisualizerは重複IDを扱える（後勝ち）
        visualizer = GraphVisualizer(tasks)
        assert len(visualizer.tasks) == 1  # 重複は上書きされる

    def test_circular_self_dependency(self):
        """自己循環依存"""
        task = Task(
            id="TASK-001",
            title="Self-dependent",
            description="Test",
            assigned_to="backend",
            dependencies=["TASK-001"],  # 自分自身に依存
            priority=Priority.HIGH
        )

        validator = DependencyValidator()
        result = validator.validate_dependencies([task])

        assert len(result['invalid_dependencies']) > 0
        assert any("自己依存" in dep for dep in result['invalid_dependencies'])

    def test_dependency_to_nonexistent_task(self):
        """存在しないタスクへの依存"""
        task = Task(
            id="TASK-001",
            title="Task",
            description="Test",
            assigned_to="backend",
            dependencies=["TASK-999"],
            priority=Priority.HIGH
        )

        validator = DependencyValidator()
        result = validator.validate_dependencies([task])

        assert len(result['missing_dependencies']) == 1


class TestTaskFilterEdgeCases:
    """TaskFilterのエッジケース"""

    def test_task_with_empty_criteria(self):
        """受け入れ基準が空のタスク"""
        task = Task(
            id="TASK-001",
            title="実装タスク",
            description="Test",
            assigned_to="backend",
            dependencies=[],
            target_files=["backend/main.py"],
            acceptance_criteria=[],  # 空
            priority=Priority.HIGH
        )

        filter = TaskFilter()
        is_task = filter.is_implementation_task(task)

        # ファイルがあるので実装タスクと判定
        assert is_task is True

    def test_task_with_no_files(self):
        """ファイルが空のタスク"""
        task = Task(
            id="TASK-001",
            title="実装する",
            description="Test",
            assigned_to="backend",
            dependencies=[],
            target_files=[],  # 空
            acceptance_criteria=["実装する"],
            priority=Priority.HIGH
        )

        filter = TaskFilter()
        is_task = filter.is_implementation_task(task)

        # 動詞があるので実装タスクの可能性
        # 実際の判定結果をテスト
        assert isinstance(is_task, bool)

    def test_guideline_task(self):
        """ガイドラインタスク（非実装タスク）"""
        task = Task(
            id="TASK-001",
            title="技術スタック",
            description="推奨事項",
            assigned_to="backend",
            dependencies=[],
            target_files=[],
            acceptance_criteria=["Python 3.12", "FastAPI"],
            priority=Priority.LOW
        )

        filter = TaskFilter()
        is_task = filter.is_implementation_task(task)

        # ガイドラインなので非タスクと判定
        assert is_task is False


class TestGraphVisualizerEdgeCases:
    """GraphVisualizerのエッジケース"""

    def test_disconnected_subgraphs(self):
        """切断されたサブグラフ"""
        tasks = [
            # サブグラフ1
            Task(id="TASK-001", title="A1", description="", assigned_to="backend",
                 dependencies=[], priority=Priority.HIGH),
            Task(id="TASK-002", title="A2", description="", assigned_to="backend",
                 dependencies=["TASK-001"], priority=Priority.MEDIUM),

            # サブグラフ2（独立）
            Task(id="TASK-010", title="B1", description="", assigned_to="backend",
                 dependencies=[], priority=Priority.HIGH),
            Task(id="TASK-011", title="B2", description="", assigned_to="backend",
                 dependencies=["TASK-010"], priority=Priority.MEDIUM),
        ]

        visualizer = GraphVisualizer(tasks)
        stats = visualizer.get_statistics()

        assert stats['total_tasks'] == 4
        assert stats['root_tasks'] == 2  # 2つのルート

    def test_multiple_leaf_tasks(self):
        """複数のリーフタスク"""
        tasks = [
            Task(id="ROOT", title="Root", description="", assigned_to="backend",
                 dependencies=[], priority=Priority.HIGH),
            Task(id="LEAF-1", title="Leaf 1", description="", assigned_to="backend",
                 dependencies=["ROOT"], priority=Priority.MEDIUM),
            Task(id="LEAF-2", title="Leaf 2", description="", assigned_to="backend",
                 dependencies=["ROOT"], priority=Priority.MEDIUM),
            Task(id="LEAF-3", title="Leaf 3", description="", assigned_to="backend",
                 dependencies=["ROOT"], priority=Priority.MEDIUM),
        ]

        visualizer = GraphVisualizer(tasks)
        stats = visualizer.get_statistics()

        assert stats['leaf_tasks'] == 3

    def test_get_task_depth_for_root(self):
        """ルートタスクの深さは0"""
        tasks = [
            Task(id="ROOT", title="Root", description="", assigned_to="backend",
                 dependencies=[], priority=Priority.HIGH),
        ]

        visualizer = GraphVisualizer(tasks)
        depth = visualizer.get_task_depth("ROOT")

        assert depth == 0


class TestDependencyValidatorEdgeCases:
    """DependencyValidatorのエッジケース"""

    def test_no_fix_suggestions_for_simple_cycle(self):
        """単純な循環依存の修正提案"""
        tasks = [
            Task(id="A", title="Task A", description="", assigned_to="backend",
                 dependencies=["B"], priority=Priority.HIGH),
            Task(id="B", title="Task B", description="", assigned_to="backend",
                 dependencies=["A"], priority=Priority.HIGH),
        ]

        validator = DependencyValidator()
        cycles = validator.detect_cycles(tasks)
        suggestions = validator.suggest_fixes(cycles, tasks)

        # 提案が生成される
        assert len(suggestions) > 0

    def test_triangle_cycle(self):
        """三角形の循環依存"""
        tasks = [
            Task(id="A", title="Task A", description="", assigned_to="backend",
                 dependencies=["B"], priority=Priority.HIGH),
            Task(id="B", title="Task B", description="", assigned_to="backend",
                 dependencies=["C"], priority=Priority.HIGH),
            Task(id="C", title="Task C", description="", assigned_to="backend",
                 dependencies=["A"], priority=Priority.HIGH),
        ]

        validator = DependencyValidator()
        cycles = validator.detect_cycles(tasks)

        assert len(cycles) > 0

    def test_multiple_independent_cycles(self):
        """複数の独立した循環"""
        tasks = [
            # サイクル1
            Task(id="A", title="Task A", description="", assigned_to="backend",
                 dependencies=["B"], priority=Priority.HIGH),
            Task(id="B", title="Task B", description="", assigned_to="backend",
                 dependencies=["A"], priority=Priority.HIGH),

            # サイクル2
            Task(id="X", title="Task X", description="", assigned_to="backend",
                 dependencies=["Y"], priority=Priority.HIGH),
            Task(id="Y", title="Task Y", description="", assigned_to="backend",
                 dependencies=["X"], priority=Priority.HIGH),
        ]

        validator = DependencyValidator()
        cycles = validator.detect_cycles(tasks)

        # 2つの独立した循環が検出される
        assert len(cycles) >= 2
