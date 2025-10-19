"""
新しいCLIコマンドのテスト
"""

import json
import pytest
from pathlib import Path
from click.testing import CliRunner
from cmw.cli import cli
from cmw.models import Task, TaskStatus, Priority


@pytest.fixture
def runner():
    """CLIランナー"""
    return CliRunner()


@pytest.fixture
def temp_project(tmp_path):
    """一時プロジェクトディレクトリ"""
    # ディレクトリ構造を作成
    (tmp_path / "shared" / "coordination").mkdir(parents=True)
    (tmp_path / "shared" / "docs").mkdir(parents=True)

    # 初期タスクを作成
    tasks_data = {
        "tasks": [
            {
                "id": "TASK-001",
                "title": "1.1 初期タスク",
                "description": "テスト用",
                "assigned_to": "backend",
                "status": "pending",
                "dependencies": [],
                "priority": "medium",
                "target_files": ["main.py"],
                "acceptance_criteria": []
            },
            {
                "id": "TASK-002",
                "title": "1.2 セカンドタスク",
                "description": "テスト用2",
                "assigned_to": "backend",
                "status": "completed",
                "dependencies": ["TASK-001"],
                "priority": "high",
                "target_files": ["app.py"],
                "acceptance_criteria": []
            }
        ],
        "workers": []
    }

    tasks_file = tmp_path / "shared" / "coordination" / "tasks.json"
    tasks_file.write_text(json.dumps(tasks_data, ensure_ascii=False, indent=2))

    # progress.jsonも作成
    progress_data = {"tasks": tasks_data["tasks"].copy()}
    progress_file = tmp_path / "shared" / "coordination" / "progress.json"
    progress_file.write_text(json.dumps(progress_data, ensure_ascii=False, indent=2))

    return tmp_path


class TestSearchCommand:
    """search コマンドのテスト"""

    def test_search_by_query(self, runner, temp_project):
        """クエリ検索"""
        result = runner.invoke(cli, ["task", "search", "--query", "初期"], cwd=str(temp_project))
        assert result.exit_code == 0
        assert "TASK-001" in result.output
        assert "初期タスク" in result.output

    def test_search_by_status(self, runner, temp_project):
        """ステータスでフィルタ"""
        result = runner.invoke(cli, ["task", "search", "--status", "completed"], cwd=str(temp_project))
        assert result.exit_code == 0
        assert "TASK-002" in result.output
        assert "TASK-001" not in result.output

    def test_search_by_priority(self, runner, temp_project):
        """優先度でフィルタ"""
        result = runner.invoke(cli, ["task", "search", "--priority", "high"], cwd=str(temp_project))
        assert result.exit_code == 0
        assert "TASK-002" in result.output

    def test_search_no_results(self, runner, temp_project):
        """結果なし"""
        result = runner.invoke(cli, ["task", "search", "--query", "存在しない"], cwd=str(temp_project))
        assert result.exit_code == 0
        assert "条件に一致するタスクが見つかりません" in result.output


class TestBoardCommand:
    """board コマンドのテスト"""

    def test_board_display(self, runner, temp_project):
        """Kanbanボード表示"""
        result = runner.invoke(cli, ["task", "board"], cwd=str(temp_project))
        assert result.exit_code == 0
        assert "Kanban Board" in result.output
        assert "Pending" in result.output
        assert "Completed" in result.output
        assert "TASK-001" in result.output
        assert "TASK-002" in result.output

    def test_board_filter_by_assigned(self, runner, temp_project):
        """担当者でフィルタ"""
        result = runner.invoke(cli, ["task", "board", "--assigned", "backend"], cwd=str(temp_project))
        assert result.exit_code == 0
        assert "Kanban Board" in result.output


class TestExportCommand:
    """export コマンドのテスト"""

    def test_export_markdown(self, runner, temp_project):
        """Markdown形式でエクスポート"""
        output_file = temp_project / "export.md"
        result = runner.invoke(
            cli,
            ["task", "export", "--format", "markdown", "--output", str(output_file)],
            cwd=str(temp_project)
        )
        assert result.exit_code == 0
        assert output_file.exists()

        content = output_file.read_text()
        assert "# タスク一覧" in content
        assert "TASK-001" in content
        assert "TASK-002" in content

    def test_export_json(self, runner, temp_project):
        """JSON形式でエクスポート"""
        output_file = temp_project / "export.json"
        result = runner.invoke(
            cli,
            ["task", "export", "--format", "json", "--output", str(output_file)],
            cwd=str(temp_project)
        )
        assert result.exit_code == 0
        assert output_file.exists()

        data = json.loads(output_file.read_text())
        assert "tasks" in data
        assert len(data["tasks"]) == 2

    def test_export_csv(self, runner, temp_project):
        """CSV形式でエクスポート"""
        output_file = temp_project / "export.csv"
        result = runner.invoke(
            cli,
            ["task", "export", "--format", "csv", "--output", str(output_file)],
            cwd=str(temp_project)
        )
        assert result.exit_code == 0
        assert output_file.exists()

        content = output_file.read_text()
        assert "TASK-001" in content
        assert "TASK-002" in content

    def test_export_with_status_filter(self, runner, temp_project):
        """ステータスフィルタ付きエクスポート"""
        output_file = temp_project / "completed.md"
        result = runner.invoke(
            cli,
            ["task", "export", "--format", "markdown", "--status", "completed", "--output", str(output_file)],
            cwd=str(temp_project)
        )
        assert result.exit_code == 0

        content = output_file.read_text()
        assert "TASK-002" in content
        assert "TASK-001" not in content


class TestBatchCommand:
    """batch コマンドのテスト"""

    def test_batch_complete_with_ids(self, runner, temp_project):
        """特定タスクIDで一括完了"""
        result = runner.invoke(
            cli,
            ["task", "batch", "complete", "TASK-001", "--dry-run"],
            cwd=str(temp_project)
        )
        assert result.exit_code == 0
        assert "dry-run モード" in result.output
        assert "TASK-001" in result.output

    def test_batch_start_with_filter(self, runner, temp_project):
        """フィルタで一括開始"""
        result = runner.invoke(
            cli,
            ["task", "batch", "start", "--filter-status", "pending", "--dry-run"],
            cwd=str(temp_project)
        )
        assert result.exit_code == 0
        assert "TASK-001" in result.output

    def test_batch_no_targets(self, runner, temp_project):
        """対象タスクなし"""
        result = runner.invoke(
            cli,
            ["task", "batch", "complete", "TASK-999", "--dry-run"],
            cwd=str(temp_project)
        )
        assert result.exit_code == 0
        assert "対象タスクがありません" in result.output


class TestTemplateCommand:
    """template コマンドのテスト"""

    def test_template_list_empty(self, runner, temp_project):
        """テンプレート一覧（空）"""
        result = runner.invoke(cli, ["task", "template", "--list"], cwd=str(temp_project))
        assert result.exit_code == 0
        assert "テンプレートがありません" in result.output

    def test_template_save(self, runner, temp_project):
        """タスクをテンプレート化"""
        # テンプレート保存（対話的なのでinputを使用）
        result = runner.invoke(
            cli,
            ["task", "template", "--save", "TASK-001"],
            input="test-template\n",
            cwd=str(temp_project)
        )
        assert result.exit_code == 0

        template_file = temp_project / "shared" / "coordination" / "templates" / "test-template.json"
        assert template_file.exists()

        template_data = json.loads(template_file.read_text())
        assert template_data["title"] == "1.1 初期タスク"


class TestGenerateWithMigration:
    """generate --migrate のテスト"""

    def test_generate_with_migration(self, runner, temp_project):
        """マイグレーション付き生成"""
        # requirements.md を作成
        req_file = temp_project / "shared" / "docs" / "requirements.md"
        req_file.write_text("""
# プロジェクト要件

## 1. 基本機能
### 1.1 初期タスク
説明
- ファイル: main.py
- 受け入れ基準: テスト

### 1.3 新規タスク
説明
- ファイル: new.py
""")

        result = runner.invoke(
            cli,
            ["task", "generate", "--migrate"],
            cwd=str(temp_project)
        )

        assert result.exit_code == 0
        assert "マイグレーションモード" in result.output or "タスクを生成しました" in result.output
