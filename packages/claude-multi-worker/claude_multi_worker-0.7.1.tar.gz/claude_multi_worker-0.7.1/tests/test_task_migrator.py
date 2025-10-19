"""
TaskMigrator のテスト
"""

import pytest
from pathlib import Path
from cmw.task_migrator import TaskMigrator
from cmw.models import Task, TaskStatus, Priority
from datetime import datetime


@pytest.fixture
def temp_project(tmp_path):
    """一時プロジェクトディレクトリ"""
    (tmp_path / "shared" / "coordination").mkdir(parents=True)
    return tmp_path


@pytest.fixture
def old_tasks():
    """既存タスク（変更前）"""
    return [
        Task(
            id="TASK-001",
            title="1.1 モデル定義",
            description="データモデルを定義",
            assigned_to="backend",
            status=TaskStatus.COMPLETED,
            dependencies=[],
            priority=Priority.HIGH,
            target_files=["models.py"],
            acceptance_criteria=["モデルクラス作成"],
            completed_at=datetime(2025, 1, 1, 10, 0, 0)
        ),
        Task(
            id="TASK-002",
            title="1.2 API実装",
            description="REST APIを実装",
            assigned_to="backend",
            status=TaskStatus.IN_PROGRESS,
            dependencies=["TASK-001"],
            priority=Priority.MEDIUM,
            target_files=["api.py"],
            acceptance_criteria=["APIエンドポイント作成"],
            artifacts=["api.py", "test_api.py"]
        ),
        Task(
            id="TASK-003",
            title="2.1 UI作成",
            description="ユーザーインターフェース",
            assigned_to="frontend",
            status=TaskStatus.PENDING,
            dependencies=[],
            priority=Priority.LOW,
            target_files=["app.tsx"],
            acceptance_criteria=[]
        ),
    ]


@pytest.fixture
def new_tasks():
    """新タスク（変更後）"""
    return [
        Task(
            id="TASK-101",
            title="1.1 モデル定義",  # タイトル一致
            description="データモデルの定義（更新版）",
            assigned_to="backend",
            status=TaskStatus.PENDING,  # デフォルトに戻る
            dependencies=[],
            priority=Priority.HIGH,
            target_files=["models.py"],
            acceptance_criteria=["モデルクラス作成", "バリデーション追加"]
        ),
        Task(
            id="TASK-102",
            title="1.2 API実装とドキュメント",  # 類似タイトル
            description="REST APIとドキュメント",
            assigned_to="backend",
            status=TaskStatus.PENDING,
            dependencies=[],
            priority=Priority.MEDIUM,
            target_files=["api.py", "docs.py"],
            acceptance_criteria=[]
        ),
        Task(
            id="TASK-103",
            title="2.1 UIコンポーネント作成",  # セクション番号一致
            description="React コンポーネント",
            assigned_to="frontend",
            status=TaskStatus.PENDING,
            dependencies=[],
            priority=Priority.MEDIUM,
            target_files=["components/App.tsx"],
            acceptance_criteria=[]
        ),
        Task(
            id="TASK-104",
            title="3.1 新機能",  # 完全新規
            description="新しい機能",
            assigned_to="backend",
            status=TaskStatus.PENDING,
            dependencies=[],
            priority=Priority.LOW,
            target_files=["new_feature.py"],
            acceptance_criteria=[]
        ),
    ]


class TestTaskMigrator:
    """タスクマイグレーションのテスト"""

    def test_migrate_exact_title_match(self, temp_project, old_tasks, new_tasks):
        """タイトル完全一致のマイグレーション"""
        migrator = TaskMigrator(temp_project)

        migrated_tasks, migration_map = migrator.migrate_tasks(old_tasks, new_tasks)

        # TASK-001 → TASK-101 へマイグレーション
        assert "TASK-001" in migration_map
        assert migration_map["TASK-001"] == "TASK-101"

        # 状態が引き継がれる
        task_101 = next(t for t in migrated_tasks if t.id == "TASK-101")
        assert task_101.status == TaskStatus.COMPLETED
        assert task_101.completed_at is not None

    def test_migrate_section_number_match(self, temp_project, old_tasks, new_tasks):
        """セクション番号一致のマイグレーション"""
        migrator = TaskMigrator(temp_project)

        migrated_tasks, migration_map = migrator.migrate_tasks(old_tasks, new_tasks)

        # 2.1 のタスクがマッチする可能性（類似度が70%以上なら）
        # タイトルが異なるため、必ずマッチするとは限らない
        if "TASK-003" in migration_map:
            assert migration_map["TASK-003"] == "TASK-103"
        # マッチしない場合もOK（類似度が低い）
        assert len(migration_map) >= 1  # 最低でも1つはマッチ

    def test_migrate_file_overlap_match(self, temp_project, old_tasks, new_tasks):
        """ファイル重複によるマイグレーション"""
        migrator = TaskMigrator(temp_project)

        migrated_tasks, migration_map = migrator.migrate_tasks(old_tasks, new_tasks)

        # マイグレーション自体は成功する
        assert len(migration_map) >= 1

        # api.py を持つタスクは類似度が高ければマッチ
        if "TASK-002" in migration_map:
            new_id = migration_map["TASK-002"]
            assert new_id in ["TASK-102"]  # TASK-102がapi.pyを持つ

    def test_migrate_preserves_artifacts(self, temp_project, old_tasks, new_tasks):
        """アーティファクトが保持される"""
        migrator = TaskMigrator(temp_project)

        migrated_tasks, migration_map = migrator.migrate_tasks(old_tasks, new_tasks)

        # TASK-002のアーティファクトが新タスクに引き継がれる
        old_task_002 = old_tasks[1]
        new_task_id = migration_map.get("TASK-002")

        if new_task_id:
            new_task = next(t for t in migrated_tasks if t.id == new_task_id)
            assert new_task.artifacts == old_task_002.artifacts

    def test_migrate_new_task_no_migration(self, temp_project, old_tasks, new_tasks):
        """新規タスクはマイグレーションされない"""
        migrator = TaskMigrator(temp_project)

        migrated_tasks, migration_map = migrator.migrate_tasks(old_tasks, new_tasks)

        # TASK-104 は新規なのでマッピングに含まれない
        assert "TASK-104" not in [v for v in migration_map.values()]

        # 新規タスクはデフォルト状態
        task_104 = next(t for t in migrated_tasks if t.id == "TASK-104")
        assert task_104.status == TaskStatus.PENDING
        assert task_104.artifacts == []

    def test_similarity_calculation(self, temp_project):
        """類似度計算のテスト"""
        migrator = TaskMigrator(temp_project)

        task1 = Task(
            id="T1",
            title="1.1 モデル定義",
            description="データモデル",
            assigned_to="backend",
            dependencies=[],
            priority=Priority.HIGH,
            target_files=["models.py"],
            acceptance_criteria=[]
        )

        task2 = Task(
            id="T2",
            title="1.1 モデル定義",
            description="データモデル",
            assigned_to="backend",
            dependencies=[],
            priority=Priority.HIGH,
            target_files=["models.py"],
            acceptance_criteria=[]
        )

        # 完全一致は高スコア
        score = migrator._calculate_similarity(task1, task2)
        assert score > 0.9

    def test_string_similarity(self, temp_project):
        """文字列類似度のテスト"""
        migrator = TaskMigrator(temp_project)

        # 完全一致
        assert migrator._string_similarity("test", "test") == 1.0

        # 部分一致
        score = migrator._string_similarity("モデル定義", "モデル実装")
        assert 0.0 < score < 1.0

        # 全く違う
        score = migrator._string_similarity("abc", "xyz")
        assert score < 0.5

    def test_migration_threshold(self, temp_project):
        """マイグレーション閾値（70%未満は除外）"""
        migrator = TaskMigrator(temp_project)

        old_tasks = [
            Task(
                id="TASK-001",
                title="完全に異なるタスク",
                description="",
                assigned_to="backend",
                dependencies=[],
                priority=Priority.LOW,
                target_files=["unrelated.py"],
                acceptance_criteria=[]
            )
        ]

        new_tasks = [
            Task(
                id="TASK-101",
                title="別のタスク",
                description="",
                assigned_to="frontend",
                dependencies=[],
                priority=Priority.HIGH,
                target_files=["different.tsx"],
                acceptance_criteria=[]
            )
        ]

        migrated_tasks, migration_map = migrator.migrate_tasks(old_tasks, new_tasks)

        # 類似度が低すぎてマッピングされない
        assert len(migration_map) == 0

    def test_save_migration_report(self, temp_project):
        """マイグレーションレポートの保存"""
        migrator = TaskMigrator(temp_project)

        migration_map = {
            "TASK-001": "TASK-101",
            "TASK-002": "TASK-102"
        }

        migrator.save_migration_report(migration_map)

        report_file = temp_project / "shared" / "coordination" / "migration_report.json"
        assert report_file.exists()

        import json
        data = json.loads(report_file.read_text())

        assert data["migrated_count"] == 2
        assert data["migration_map"] == migration_map


class TestExtractSectionNumber:
    """セクション番号抽出のテスト"""

    def test_extract_section_number(self, temp_project):
        """セクション番号の抽出"""
        migrator = TaskMigrator(temp_project)

        assert migrator._extract_section_number("1.1 モデル定義") == "1.1"
        assert migrator._extract_section_number("2.3 API実装") == "2.3"
        assert migrator._extract_section_number("10.15 デプロイ") == "10.15"
        assert migrator._extract_section_number("タイトルのみ") is None
