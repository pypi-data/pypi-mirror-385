"""
DependencyAnalyzerのテスト
"""

import pytest
from cmw.models import Task, TaskStatus, Priority
from cmw.dependency_analyzer import DependencyAnalyzer


@pytest.fixture
def sample_tasks():
    """テスト用のサンプルタスク"""
    return [
        Task(
            id="TASK-001",
            title="基盤タスク",
            description="最初に実行するタスク",
            assigned_to="backend",
            status=TaskStatus.PENDING,
            priority=Priority.HIGH,
            dependencies=[],
            target_files=["base.py"],
        ),
        Task(
            id="TASK-002",
            title="依存タスクA",
            description="TASK-001に依存",
            assigned_to="backend",
            status=TaskStatus.PENDING,
            priority=Priority.MEDIUM,
            dependencies=["TASK-001"],
            target_files=["a.py"],
        ),
        Task(
            id="TASK-003",
            title="依存タスクB",
            description="TASK-001に依存",
            assigned_to="backend",
            status=TaskStatus.PENDING,
            priority=Priority.MEDIUM,
            dependencies=["TASK-001"],
            target_files=["b.py"],
        ),
        Task(
            id="TASK-004",
            title="最終タスク",
            description="TASK-002とTASK-003に依存",
            assigned_to="backend",
            status=TaskStatus.PENDING,
            priority=Priority.LOW,
            dependencies=["TASK-002", "TASK-003"],
            target_files=["final.py"],
        ),
    ]


class TestDependencyAnalyzer:
    """DependencyAnalyzerのテスト"""

    def test_init(self, sample_tasks):
        """初期化のテスト"""
        analyzer = DependencyAnalyzer(sample_tasks)
        assert len(analyzer.tasks) == 4
        assert analyzer.visualizer is not None

    def test_get_executable_tasks_all_pending(self, sample_tasks):
        """全タスクがpendingの場合、依存関係のないタスクのみ取得"""
        analyzer = DependencyAnalyzer(sample_tasks)
        executable = analyzer.get_executable_tasks()

        assert len(executable) == 1
        assert executable[0].id == "TASK-001"

    def test_get_executable_tasks_after_completion(self, sample_tasks):
        """タスク完了後、次の実行可能タスクを取得"""
        sample_tasks[0].status = TaskStatus.COMPLETED
        analyzer = DependencyAnalyzer(sample_tasks)
        executable = analyzer.get_executable_tasks()

        assert len(executable) == 2
        task_ids = [t.id for t in executable]
        assert "TASK-002" in task_ids
        assert "TASK-003" in task_ids

    def test_get_critical_path(self, sample_tasks):
        """クリティカルパスの計算"""
        analyzer = DependencyAnalyzer(sample_tasks)
        critical_info = analyzer.get_critical_path()

        assert "tasks" in critical_info
        assert "total_duration" in critical_info
        assert "bottlenecks" in critical_info
        assert len(critical_info["tasks"]) > 0

    def test_get_blocking_count(self, sample_tasks):
        """ブロックしているタスク数の取得"""
        analyzer = DependencyAnalyzer(sample_tasks)

        # TASK-001は3タスクをブロック
        assert analyzer.get_blocking_count("TASK-001") == 3

        # TASK-004はブロックなし
        assert analyzer.get_blocking_count("TASK-004") == 0

    def test_get_next_tasks_recommendation(self, sample_tasks):
        """次のタスク推奨リストの取得"""
        analyzer = DependencyAnalyzer(sample_tasks)
        recommendations = analyzer.get_next_tasks_recommendation(num_recommendations=2)

        assert len(recommendations) <= 2
        assert recommendations[0]["task_id"] == "TASK-001"
        assert "is_critical_path" in recommendations[0]
        assert "blocking_count" in recommendations[0]

    def test_analyze_bottlenecks(self, sample_tasks):
        """ボトルネック分析"""
        analyzer = DependencyAnalyzer(sample_tasks)
        bottlenecks = analyzer.analyze_bottlenecks()

        # TASK-001は3タスクをブロックしているのでボトルネック
        assert len(bottlenecks) >= 1
        assert bottlenecks[0]["task_id"] == "TASK-001"
        assert bottlenecks[0]["blocking_count"] == 3

    def test_get_parallel_execution_plan(self, sample_tasks):
        """並行実行プランの生成"""
        analyzer = DependencyAnalyzer(sample_tasks)
        plan = analyzer.get_parallel_execution_plan(num_workers=2)

        assert "workers" in plan
        assert "estimated_completion_hours" in plan
        assert "efficiency_gain" in plan
        assert len(plan["workers"]) == 2

    def test_is_on_critical_path(self, sample_tasks):
        """クリティカルパス上のタスクかチェック"""
        analyzer = DependencyAnalyzer(sample_tasks)

        # TASK-001はクリティカルパス上にある
        assert analyzer.is_on_critical_path("TASK-001") is True

    def test_get_task_impact_score(self, sample_tasks):
        """タスクの影響度スコア計算"""
        analyzer = DependencyAnalyzer(sample_tasks)

        # TASK-001は高い影響度スコア
        score_001 = analyzer.get_task_impact_score("TASK-001")
        score_004 = analyzer.get_task_impact_score("TASK-004")

        assert score_001 > score_004

    def test_get_completion_forecast(self, sample_tasks):
        """プロジェクト完了予測"""
        analyzer = DependencyAnalyzer(sample_tasks)
        forecast = analyzer.get_completion_forecast()

        assert "total_tasks" in forecast
        assert "completed" in forecast
        assert "progress_percent" in forecast
        assert "optimistic_completion_days" in forecast
        assert "pessimistic_completion_days" in forecast

        assert forecast["total_tasks"] == 4
        assert forecast["completed"] == 0

    def test_empty_tasks(self):
        """タスクが空の場合"""
        analyzer = DependencyAnalyzer([])
        executable = analyzer.get_executable_tasks()
        assert len(executable) == 0

        critical_info = analyzer.get_critical_path()
        assert critical_info["tasks"] == []
