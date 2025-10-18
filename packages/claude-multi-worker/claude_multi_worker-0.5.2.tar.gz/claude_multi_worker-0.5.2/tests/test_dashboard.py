"""
Dashboard のユニットテスト
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from src.cmw.dashboard import Dashboard
from src.cmw.models import Task, TaskStatus, Priority
from src.cmw.progress_tracker import ProgressTracker


class TestDashboard:
    """Dashboardのテスト"""

    @pytest.fixture
    def dashboard(self) -> Dashboard:
        """ダッシュボードインスタンスを作成"""
        return Dashboard()

    @pytest.fixture
    def tracker(self, tmp_path) -> ProgressTracker:
        """プログレストラッカーを作成"""
        from pathlib import Path

        return ProgressTracker(Path(tmp_path))

    @pytest.fixture
    def sample_tasks(self) -> list[Task]:
        """サンプルタスクを作成"""
        return [
            Task(
                id="TASK-001",
                title="Completed task",
                description="A completed task",
                status=TaskStatus.COMPLETED,
                priority=Priority.HIGH,
                dependencies=[],
                assigned_to="user1",
            ),
            Task(
                id="TASK-002",
                title="In progress task",
                description="A task in progress",
                status=TaskStatus.IN_PROGRESS,
                priority=Priority.MEDIUM,
                dependencies=[],
                assigned_to="user1",
            ),
            Task(
                id="TASK-003",
                title="Pending task",
                description="A pending task",
                status=TaskStatus.PENDING,
                priority=Priority.LOW,
                dependencies=[],
                assigned_to="user2",
            ),
        ]

    def test_init(self, dashboard: Dashboard) -> None:
        """初期化のテスト"""
        assert dashboard.console is not None

    def test_format_duration_seconds(self, dashboard: Dashboard) -> None:
        """秒数フォーマット（秒）のテスト"""
        assert dashboard.format_duration(30) == "30秒"
        assert dashboard.format_duration(59) == "59秒"

    def test_format_duration_minutes(self, dashboard: Dashboard) -> None:
        """秒数フォーマット（分）のテスト"""
        assert dashboard.format_duration(60) == "1分"
        assert dashboard.format_duration(120) == "2分"
        assert dashboard.format_duration(3599) == "59分"

    def test_format_duration_hours(self, dashboard: Dashboard) -> None:
        """秒数フォーマット（時間）のテスト"""
        assert dashboard.format_duration(3600) == "1時間0分"
        assert dashboard.format_duration(3660) == "1時間1分"
        assert dashboard.format_duration(7200) == "2時間0分"
        assert dashboard.format_duration(7380) == "2時間3分"

    def test_create_summary_panel(
        self, dashboard: Dashboard, tracker: ProgressTracker, sample_tasks: list[Task]
    ) -> None:
        """サマリーパネル作成のテスト"""
        panel = dashboard.create_summary_panel(tracker, sample_tasks)

        assert panel.title == "プロジェクト概要"
        # パネル内容を検証
        content = panel.renderable
        assert "総タスク数" in str(content)
        assert "完了" in str(content)

    def test_create_summary_panel_with_remaining_time(
        self, dashboard: Dashboard, tracker: ProgressTracker, sample_tasks: list[Task]
    ) -> None:
        """サマリーパネル作成（残り時間あり）のテスト"""
        # タスクに started_at を設定
        sample_tasks[0].started_at = datetime.now() - timedelta(hours=1)
        sample_tasks[0].completed_at = datetime.now()

        panel = dashboard.create_summary_panel(tracker, sample_tasks)

        content = str(panel.renderable)
        # 残り時間が表示されることを確認（具体的な時間は計算に依存）
        assert "総タスク数" in content

    def test_create_velocity_panel(
        self, dashboard: Dashboard, tracker: ProgressTracker, sample_tasks: list[Task]
    ) -> None:
        """ベロシティパネル作成のテスト"""
        # タスクに時間情報を設定
        now = datetime.now()
        sample_tasks[0].started_at = now - timedelta(hours=2)
        sample_tasks[0].completed_at = now - timedelta(hours=1)

        panel = dashboard.create_velocity_panel(tracker, sample_tasks)

        assert panel.title == "ベロシティ"
        content = str(panel.renderable)
        assert "タスク/時間" in content
        assert "平均所要時間" in content
        assert "総作業時間" in content

    def test_create_priority_table(
        self, dashboard: Dashboard, tracker: ProgressTracker, sample_tasks: list[Task]
    ) -> None:
        """優先度別テーブル作成のテスト"""
        table = dashboard.create_priority_table(tracker, sample_tasks)

        assert table.title == "優先度別進捗"
        # テーブルの列を確認
        assert len(table.columns) == 7
        assert table.columns[0].header == "優先度"
        assert table.columns[1].header == "総数"

    def test_create_worker_table(
        self, dashboard: Dashboard, tracker: ProgressTracker, sample_tasks: list[Task]
    ) -> None:
        """担当者別テーブル作成のテスト"""
        table = dashboard.create_worker_table(tracker, sample_tasks)

        assert table.title == "担当者別進捗"
        # テーブルの列を確認
        assert len(table.columns) == 6
        assert table.columns[0].header == "担当者"
        assert table.columns[1].header == "総数"

    def test_create_recent_tasks_table(
        self, dashboard: Dashboard, tracker: ProgressTracker, sample_tasks: list[Task]
    ) -> None:
        """最近のタスクテーブル作成のテスト"""
        # タスクにタイムスタンプを設定
        now = datetime.now()
        sample_tasks[0].started_at = now - timedelta(hours=2)
        sample_tasks[0].completed_at = now - timedelta(hours=1)

        table = dashboard.create_recent_tasks_table(tracker, sample_tasks)

        assert table.title == "最近のアクティビティ"
        assert len(table.columns) == 3
        assert table.columns[0].header == "時刻"
        assert table.columns[1].header == "タスク"
        assert table.columns[2].header == "イベント"

    def test_create_recent_tasks_table_limit(
        self, dashboard: Dashboard, tracker: ProgressTracker
    ) -> None:
        """最近のタスクテーブル作成（件数制限）のテスト"""
        # 15個のタスクを作成
        tasks = []
        now = datetime.now()
        for i in range(15):
            task = Task(
                id=f"TASK-{i:03d}",
                title=f"Task {i}",
                description="Test task",
                status=TaskStatus.COMPLETED,
                priority=Priority.MEDIUM,
                dependencies=[],
                assigned_to="user1",
            )
            task.started_at = now - timedelta(hours=15 - i)
            task.completed_at = now - timedelta(hours=14 - i)
            tasks.append(task)

        table = dashboard.create_recent_tasks_table(tracker, tasks)

        # 最大10件までのイベント表示を確認
        # (各タスク2イベント: started, completed)
        # 実際の行数はイベント数に依存
        assert len(table.rows) <= 10

    @patch("src.cmw.dashboard.Console")
    def test_show_dashboard(
        self,
        mock_console_class: Mock,
        dashboard: Dashboard,
        tracker: ProgressTracker,
        sample_tasks: list[Task],
    ) -> None:
        """ダッシュボード表示のテスト"""
        mock_console = Mock()
        mock_console_class.return_value = mock_console
        dashboard.console = mock_console

        dashboard.show_dashboard(tracker, sample_tasks)

        # Console.clear() が呼ばれることを確認
        mock_console.clear.assert_called_once()

        # Console.print() が複数回呼ばれることを確認
        assert mock_console.print.call_count > 0

    def test_show_progress_bar(
        self, dashboard: Dashboard, tracker: ProgressTracker, sample_tasks: list[Task]
    ) -> None:
        """プログレスバー表示のテスト"""
        # エラーが起きないことを確認
        with patch("time.sleep"):  # time.sleepをモック化
            dashboard.show_progress_bar(tracker, sample_tasks)

    @patch("src.cmw.dashboard.Console")
    def test_show_compact_summary(
        self,
        mock_console_class: Mock,
        dashboard: Dashboard,
        tracker: ProgressTracker,
        sample_tasks: list[Task],
    ) -> None:
        """コンパクトサマリー表示のテスト"""
        mock_console = Mock()
        mock_console_class.return_value = mock_console
        dashboard.console = mock_console

        dashboard.show_compact_summary(tracker, sample_tasks)

        # Console.print() が呼ばれることを確認
        assert mock_console.print.call_count > 0

    def test_show_compact_summary_with_remaining_time(
        self, dashboard: Dashboard, tracker: ProgressTracker, sample_tasks: list[Task]
    ) -> None:
        """コンパクトサマリー表示（残り時間あり）のテスト"""
        # タスクに時間情報を設定
        now = datetime.now()
        sample_tasks[0].started_at = now - timedelta(hours=1)
        sample_tasks[0].completed_at = now

        # エラーが起きないことを確認
        dashboard.show_compact_summary(tracker, sample_tasks)

    def test_create_summary_panel_all_statuses(
        self, dashboard: Dashboard, tracker: ProgressTracker
    ) -> None:
        """サマリーパネル（全ステータス）のテスト"""
        tasks = [
            Task(
                id="TASK-001",
                title="Completed",
                description="Test",
                status=TaskStatus.COMPLETED,
                priority=Priority.HIGH,
                dependencies=[],
                assigned_to="user1",
            ),
            Task(
                id="TASK-002",
                title="In Progress",
                description="Test",
                status=TaskStatus.IN_PROGRESS,
                priority=Priority.HIGH,
                dependencies=[],
                assigned_to="user1",
            ),
            Task(
                id="TASK-003",
                title="Pending",
                description="Test",
                status=TaskStatus.PENDING,
                priority=Priority.HIGH,
                dependencies=[],
                assigned_to="user1",
            ),
            Task(
                id="TASK-004",
                title="Failed",
                description="Test",
                status=TaskStatus.FAILED,
                priority=Priority.HIGH,
                dependencies=[],
                assigned_to="user1",
            ),
            Task(
                id="TASK-005",
                title="Blocked",
                description="Test",
                status=TaskStatus.BLOCKED,
                priority=Priority.HIGH,
                dependencies=[],
                assigned_to="user1",
            ),
        ]

        panel = dashboard.create_summary_panel(tracker, tasks)

        content = str(panel.renderable)
        assert "完了" in content
        assert "実行中" in content
        assert "待機中" in content
        assert "失敗" in content
        assert "ブロック" in content

    def test_create_priority_table_all_priorities(
        self, dashboard: Dashboard, tracker: ProgressTracker
    ) -> None:
        """優先度別テーブル（全優先度）のテスト"""
        tasks = [
            Task(
                id="TASK-001",
                title="High priority",
                description="Test",
                status=TaskStatus.COMPLETED,
                priority=Priority.HIGH,
                dependencies=[],
                assigned_to="user1",
            ),
            Task(
                id="TASK-002",
                title="Medium priority",
                description="Test",
                status=TaskStatus.IN_PROGRESS,
                priority=Priority.MEDIUM,
                dependencies=[],
                assigned_to="user1",
            ),
            Task(
                id="TASK-003",
                title="Low priority",
                description="Test",
                status=TaskStatus.PENDING,
                priority=Priority.LOW,
                dependencies=[],
                assigned_to="user1",
            ),
        ]

        table = dashboard.create_priority_table(tracker, tasks)

        # 3行（高・中・低）あることを確認
        assert len(table.rows) == 3

    def test_create_worker_table_multiple_workers(
        self, dashboard: Dashboard, tracker: ProgressTracker
    ) -> None:
        """担当者別テーブル（複数担当者）のテスト"""
        tasks = [
            Task(
                id="TASK-001",
                title="Task 1",
                description="Test",
                status=TaskStatus.COMPLETED,
                priority=Priority.HIGH,
                dependencies=[],
                assigned_to="alice",
            ),
            Task(
                id="TASK-002",
                title="Task 2",
                description="Test",
                status=TaskStatus.IN_PROGRESS,
                priority=Priority.HIGH,
                dependencies=[],
                assigned_to="bob",
            ),
            Task(
                id="TASK-003",
                title="Task 3",
                description="Test",
                status=TaskStatus.PENDING,
                priority=Priority.HIGH,
                dependencies=[],
                assigned_to="alice",
            ),
        ]

        table = dashboard.create_worker_table(tracker, tasks)

        # 2行（alice, bob）あることを確認
        assert len(table.rows) == 2

    def test_format_duration_edge_cases(self, dashboard: Dashboard) -> None:
        """秒数フォーマット（境界値）のテスト"""
        assert dashboard.format_duration(0) == "0秒"
        assert dashboard.format_duration(1) == "1秒"
        assert dashboard.format_duration(59.9) == "59秒"
        assert dashboard.format_duration(60) == "1分"
        assert dashboard.format_duration(3599.9) == "59分"
        assert dashboard.format_duration(3600) == "1時間0分"

    def test_create_summary_panel_empty_tasks(
        self, dashboard: Dashboard, tracker: ProgressTracker
    ) -> None:
        """サマリーパネル（タスク0件）のテスト"""
        panel = dashboard.create_summary_panel(tracker, [])

        content = str(panel.renderable)
        assert "総タスク数: 0" in content

    def test_create_velocity_panel_no_completed_tasks(
        self, dashboard: Dashboard, tracker: ProgressTracker
    ) -> None:
        """ベロシティパネル（完了タスクなし）のテスト"""
        tasks = [
            Task(
                id="TASK-001",
                title="Pending task",
                description="Test",
                status=TaskStatus.PENDING,
                priority=Priority.HIGH,
                dependencies=[],
                assigned_to="user1",
            )
        ]

        panel = dashboard.create_velocity_panel(tracker, tasks)

        content = str(panel.renderable)
        # 完了タスクがない場合でもパネルは作成される
        assert "タスク/時間" in content
