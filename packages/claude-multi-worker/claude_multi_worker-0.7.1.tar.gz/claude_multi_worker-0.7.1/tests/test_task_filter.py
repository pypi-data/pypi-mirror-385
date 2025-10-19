"""
Task Filter のユニットテスト
"""

import pytest
from pathlib import Path
from src.cmw.task_filter import TaskFilter
from src.cmw.models import Task, TaskStatus, Priority


class TestTaskFilter:
    """TaskFilterのテスト"""

    @pytest.fixture
    def filter(self) -> TaskFilter:
        """タスクフィルターインスタンスを作成"""
        return TaskFilter()

    def test_is_implementation_task_with_verb(self, filter: TaskFilter) -> None:
        """実装タスク判定（動詞あり）のテスト"""
        task = Task(
            id="TASK-001",
            title="実装: ユーザー登録API",
            description="ユーザー登録のエンドポイントを作成",
            status=TaskStatus.PENDING,
            priority=Priority.HIGH,
            dependencies=[],
            assigned_to="user1",
        )

        assert filter.is_implementation_task(task) is True

    def test_is_implementation_task_with_acceptance_criteria(
        self, filter: TaskFilter
    ) -> None:
        """実装タスク判定（受入基準あり）のテスト"""
        task = Task(
            id="TASK-002",
            title="ユーザー登録",
            description="エンドポイントの仕様",
            status=TaskStatus.PENDING,
            priority=Priority.HIGH,
            dependencies=[],
            assigned_to="user1",
            acceptance_criteria=["POST /api/register が正常に動作する", "JWT トークンを返す"],
        )

        assert filter.is_implementation_task(task) is True

    def test_is_implementation_task_non_task_keyword(self, filter: TaskFilter) -> None:
        """非タスク判定（キーワードあり）のテスト"""
        task = Task(
            id="REF-001",
            title="技術スタック: Python 3.12 + FastAPI",
            description="使用技術の説明",
            status=TaskStatus.PENDING,
            priority=Priority.HIGH,
            dependencies=[],
            assigned_to="user1",
        )

        assert filter.is_implementation_task(task) is False

    def test_is_implementation_task_abstract_title(self, filter: TaskFilter) -> None:
        """非タスク判定（抽象的なタイトル）のテスト"""
        task = Task(
            id="REF-002",
            title="ベストプラクティス",
            description="コーディング規約の説明",
            status=TaskStatus.PENDING,
            priority=Priority.HIGH,
            dependencies=[],
            assigned_to="user1",
        )

        assert filter.is_implementation_task(task) is False

    def test_is_implementation_task_with_target_files(
        self, filter: TaskFilter
    ) -> None:
        """実装タスク判定（target_filesあり）のテスト"""
        task = Task(
            id="TASK-003",
            title="モデル定義",
            description="データモデルを定義する",
            status=TaskStatus.PENDING,
            priority=Priority.HIGH,
            dependencies=[],
            assigned_to="user1",
            target_files=["backend/models/user.py", "backend/models/__init__.py"],
        )

        assert filter.is_implementation_task(task) is True

    def test_is_implementation_task_no_verb_no_criteria(
        self, filter: TaskFilter
    ) -> None:
        """非タスク判定（動詞・受入基準なし）のテスト"""
        task = Task(
            id="REF-003",
            title="概要説明",
            description="プロジェクトの背景と目的",
            status=TaskStatus.PENDING,
            priority=Priority.HIGH,
            dependencies=[],
            assigned_to="user1",
        )

        assert filter.is_implementation_task(task) is False

    def test_has_concrete_criteria_with_technical_terms(
        self, filter: TaskFilter
    ) -> None:
        """具体的な受入基準判定（技術用語あり）のテスト"""
        criteria = ["POST /api/users が正常に動作する", "JWT トークンを返す"]

        assert filter._has_concrete_criteria(criteria) is True

    def test_has_concrete_criteria_with_task_verbs(self, filter: TaskFilter) -> None:
        """具体的な受入基準判定（タスク動詞あり）のテスト"""
        criteria = ["ユーザー情報を作成できる", "バリデーションエラーを実装する"]

        assert filter._has_concrete_criteria(criteria) is True

    def test_has_concrete_criteria_too_abstract(self, filter: TaskFilter) -> None:
        """抽象的な受入基準判定のテスト"""
        criteria = ["推奨される一般的なアプローチを適用する"]

        assert filter._has_concrete_criteria(criteria) is False

    def test_has_concrete_files_with_backend_path(self, filter: TaskFilter) -> None:
        """具体的なファイル判定（backendパス）のテスト"""
        files = ["backend/api/users.py"]

        assert filter._has_concrete_files(files) is True

    def test_has_concrete_files_with_extension(self, filter: TaskFilter) -> None:
        """具体的なファイル判定（拡張子）のテスト"""
        files = ["models/user.py", "tests/test_user.py"]

        assert filter._has_concrete_files(files) is True

    def test_has_concrete_files_abstract(self, filter: TaskFilter) -> None:
        """抽象的なファイル判定のテスト"""
        files = ["example", "template"]

        assert filter._has_concrete_files(files) is False

    def test_is_too_abstract_true(self, filter: TaskFilter) -> None:
        """抽象的すぎるタイトル判定のテスト"""
        assert filter._is_too_abstract("技術スタック") is True
        assert filter._is_too_abstract("推奨事項") is True
        assert filter._is_too_abstract("ベストプラクティス") is True
        assert filter._is_too_abstract("ガイドライン") is True

    def test_is_too_abstract_false(self, filter: TaskFilter) -> None:
        """具体的なタイトル判定のテスト"""
        assert filter._is_too_abstract("ユーザー登録API実装") is False
        assert filter._is_too_abstract("データベース設計") is False
        assert filter._is_too_abstract("テストコード作成") is False

    def test_filter_tasks(self, filter: TaskFilter) -> None:
        """タスクフィルタリングのテスト"""
        tasks = [
            Task(
                id="TASK-001",
                title="実装: ユーザー登録",
                description="API作成",
                status=TaskStatus.PENDING,
                priority=Priority.HIGH,
                dependencies=[],
                assigned_to="user1",
            ),
            Task(
                id="REF-001",
                title="技術スタック: FastAPI",
                description="使用技術",
                status=TaskStatus.PENDING,
                priority=Priority.HIGH,
                dependencies=[],
                assigned_to="user1",
            ),
            Task(
                id="TASK-002",
                title="テスト: ユーザー登録",
                description="テストコード作成",
                status=TaskStatus.PENDING,
                priority=Priority.HIGH,
                dependencies=[],
                assigned_to="user1",
            ),
        ]

        implementation_tasks, non_tasks = filter.filter_tasks(tasks)

        assert len(implementation_tasks) == 2
        assert len(non_tasks) == 1
        assert implementation_tasks[0].id == "TASK-001"
        assert implementation_tasks[1].id == "TASK-002"
        assert non_tasks[0].id == "REF-001"

    def test_convert_to_references(self, filter: TaskFilter) -> None:
        """参照情報変換のテスト"""
        non_tasks = [
            Task(
                id="REF-001",
                title="技術スタック",
                description="Python 3.12 + FastAPI",
                status=TaskStatus.PENDING,
                priority=Priority.HIGH,
                dependencies=[],
                assigned_to="user1",
                acceptance_criteria=["FastAPI を使用", "Python 3.12 以上"],
            ),
            Task(
                id="REF-002",
                title="非機能要件",
                description="セキュリティ要件",
                status=TaskStatus.PENDING,
                priority=Priority.HIGH,
                dependencies=[],
                assigned_to="user1",
            ),
        ]

        references = filter.convert_to_references(non_tasks)

        assert len(references) == 2
        assert references[0]["id"] == "REF-001"
        assert references[0]["title"] == "技術スタック"
        assert references[0]["content"] == "Python 3.12 + FastAPI"
        assert len(references[0]["criteria"]) == 2
        assert references[0]["applies_to"] == []

        assert references[1]["id"] == "REF-002"
        assert references[1]["title"] == "非機能要件"

    def test_save_references(self, filter: TaskFilter, tmp_path: Path) -> None:
        """参照情報保存のテスト"""
        references = [
            {
                "id": "REF-001",
                "title": "技術スタック",
                "content": "Python + FastAPI",
                "criteria": [],
                "applies_to": [],
            }
        ]

        output_path = tmp_path / "references.json"
        filter.save_references(references, output_path)

        assert output_path.exists()

        import json

        content = json.loads(output_path.read_text(encoding="utf-8"))
        assert "references" in content
        assert "generated_at" in content
        assert len(content["references"]) == 1
        assert content["references"][0]["id"] == "REF-001"

    def test_is_implementation_task_with_all_task_verbs(
        self, filter: TaskFilter
    ) -> None:
        """実装タスク判定（全タスク動詞）のテスト"""
        verbs = [
            "実装",
            "作成",
            "構築",
            "開発",
            "設計",
            "追加",
            "修正",
            "更新",
            "削除",
            "統合",
            "テスト",
            "検証",
            "デプロイ",
            "設定",
            "定義",
            "初期化",
        ]

        for verb in verbs:
            task = Task(
                id="TASK-001",
                title=f"{verb}: テスト",
                description="テスト説明",
                status=TaskStatus.PENDING,
                priority=Priority.HIGH,
                dependencies=[],
                assigned_to="user1",
            )
            assert filter.is_implementation_task(task) is True

    def test_is_implementation_task_with_all_non_task_keywords(
        self, filter: TaskFilter
    ) -> None:
        """非タスク判定（全非タスクキーワード）のテスト"""
        keywords = [
            "技術スタック",
            "推奨",
            "前提条件",
            "概要",
            "非機能要件",
            "制約",
            "想定",
            "注意",
            "背景",
            "目的",
        ]

        for keyword in keywords:
            task = Task(
                id="REF-001",
                title=f"{keyword}の説明",
                description="説明",
                status=TaskStatus.PENDING,
                priority=Priority.HIGH,
                dependencies=[],
                assigned_to="user1",
            )
            assert filter.is_implementation_task(task) is False

    def test_filter_tasks_empty_list(self, filter: TaskFilter) -> None:
        """タスクフィルタリング（空リスト）のテスト"""
        implementation_tasks, non_tasks = filter.filter_tasks([])

        assert len(implementation_tasks) == 0
        assert len(non_tasks) == 0

    def test_convert_to_references_empty_list(self, filter: TaskFilter) -> None:
        """参照情報変換（空リスト）のテスト"""
        references = filter.convert_to_references([])

        assert len(references) == 0

    def test_has_concrete_criteria_empty_list(self, filter: TaskFilter) -> None:
        """具体的な受入基準判定（空リスト）のテスト"""
        assert filter._has_concrete_criteria([]) is False

    def test_has_concrete_files_empty_list(self, filter: TaskFilter) -> None:
        """具体的なファイル判定（空リスト）のテスト"""
        assert filter._has_concrete_files([]) is False

    def test_has_concrete_files_various_paths(self, filter: TaskFilter) -> None:
        """具体的なファイル判定（様々なパス）のテスト"""
        assert filter._has_concrete_files(["frontend/components/Button.tsx"]) is True
        assert filter._has_concrete_files(["tests/test_api.py"]) is True
        assert filter._has_concrete_files(["src/main.js"]) is True
        assert filter._has_concrete_files(["app/routes.py"]) is True

    def test_has_concrete_criteria_mixed_abstract_and_concrete(
        self, filter: TaskFilter
    ) -> None:
        """具体的な受入基準判定（抽象・具体混在）のテスト"""
        # 抽象的なキーワードが2つ以上含まれる場合はFalse
        criteria = ["推奨される一般的な想定でなどを適用"]
        assert filter._has_concrete_criteria(criteria) is False

        # 具体的な技術用語があればTrue
        criteria = ["推奨されるAPI設計を適用"]
        assert filter._has_concrete_criteria(criteria) is True

    def test_save_references_with_complex_data(
        self, filter: TaskFilter, tmp_path: Path
    ) -> None:
        """参照情報保存（複雑なデータ）のテスト"""
        references = [
            {
                "id": "REF-001",
                "title": "セキュリティ要件",
                "content": "JWT認証を使用\nSQL injection対策",
                "criteria": ["JWTトークンの検証", "入力値のサニタイズ"],
                "applies_to": ["TASK-001", "TASK-002"],
            },
            {
                "id": "REF-002",
                "title": "パフォーマンス要件",
                "content": "レスポンスタイム200ms以内",
                "criteria": [],
                "applies_to": [],
            },
        ]

        output_path = tmp_path / "complex_references.json"
        filter.save_references(references, output_path)

        assert output_path.exists()

        import json

        content = json.loads(output_path.read_text(encoding="utf-8"))
        assert len(content["references"]) == 2
        assert content["references"][0]["title"] == "セキュリティ要件"
        assert len(content["references"][0]["criteria"]) == 2
        assert len(content["references"][0]["applies_to"]) == 2
