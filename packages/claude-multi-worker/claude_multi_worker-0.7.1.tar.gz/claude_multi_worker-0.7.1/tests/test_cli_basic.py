"""
CLI基本コマンドのテスト
"""

import pytest
from pathlib import Path
from click.testing import CliRunner
from src.cmw.cli import cli
import json


class TestCLITasksGenerate:
    """tasks generateコマンドのテスト"""

    @pytest.fixture
    def temp_project(self, tmp_path):
        """一時プロジェクトを作成"""
        # shared/docs ディレクトリを作成
        (tmp_path / 'shared' / 'docs').mkdir(parents=True, exist_ok=True)
        # shared/coordination ディレクトリを作成
        (tmp_path / 'shared' / 'coordination').mkdir(parents=True, exist_ok=True)

        # requirements.md を作成
        requirements = tmp_path / "shared" / "docs" / "requirements.md"
        requirements.write_text("""# Test Project

## Database Setup
- Create User model
- Create Task model

## Authentication API
- エンドポイント: POST /auth/login
- JWT token generation
""", encoding='utf-8')

        return tmp_path

    def test_tasks_generate_basic(self, temp_project):
        """tasks generateコマンドの基本動作"""
        runner = CliRunner()

        # temp_projectに直接移動
        import os
        original_dir = os.getcwd()
        try:
            os.chdir(temp_project)
            result = runner.invoke(cli, ['tasks', 'generate'], catch_exceptions=False)

            # コマンドが成功
            assert result.exit_code == 0

            # tasks.json が生成される（デフォルトパス）
            tasks_file = Path('shared/coordination/tasks.json')
            assert tasks_file.exists()

            # JSONとして読み込める
            tasks_data = json.loads(tasks_file.read_text(encoding='utf-8'))
            assert 'tasks' in tasks_data
            assert len(tasks_data['tasks']) > 0
        finally:
            os.chdir(original_dir)

    def test_tasks_generate_custom_input(self, temp_project):
        """カスタム入力ファイル指定"""
        runner = CliRunner()
        import os
        original_dir = os.getcwd()
        try:
            os.chdir(temp_project)
            # カスタムファイル名で作成
            custom_req = Path('custom_requirements.md')
            custom_req.write_text("""# Custom Project

## API Endpoint
- POST /api/test
""", encoding='utf-8')

            result = runner.invoke(
                cli,
                ['tasks', 'generate', '--requirements', 'custom_requirements.md'],
                catch_exceptions=False
            )

            assert result.exit_code == 0
            assert Path('shared/coordination/tasks.json').exists()
        finally:
            os.chdir(original_dir)

    def test_tasks_generate_custom_output(self, temp_project):
        """カスタム出力ファイル指定"""
        runner = CliRunner()
        import os
        original_dir = os.getcwd()
        try:
            os.chdir(temp_project)
            result = runner.invoke(
                cli,
                ['tasks', 'generate', '--output', 'custom_tasks.json'],
                catch_exceptions=False
            )

            assert result.exit_code == 0
            assert Path('custom_tasks.json').exists()
        finally:
            os.chdir(original_dir)

    def test_tasks_generate_no_requirements_file(self, tmp_path):
        """requirements.mdが存在しない場合"""
        runner = CliRunner()
        import os
        original_dir = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = runner.invoke(cli, ['tasks', 'generate'])

            # エラーで終了（requirements.mdがないため）
            assert result.exit_code != 0 or 'not found' in result.output.lower() or 'エラー' in result.output or '見つかりません' in result.output
        finally:
            os.chdir(original_dir)


class TestCLIStatus:
    """statusコマンドのテスト"""

    @pytest.fixture
    def temp_project_with_tasks(self, tmp_path):
        """タスク付きプロジェクトを作成"""
        # shared/coordination ディレクトリを作成
        (tmp_path / 'shared' / 'coordination').mkdir(parents=True, exist_ok=True)
        tasks_file = tmp_path / 'shared' / 'coordination' / 'tasks.json'
        tasks_data = {
            "tasks": [
                {
                    "id": "TASK-001",
                    "title": "Setup Database",
                    "description": "Database setup",
                    "status": "completed",
                    "priority": "high",
                    "dependencies": [],
                    "target_files": ["backend/database.py"],
                    "acceptance_criteria": [],
                    "assigned_to": "backend"
                },
                {
                    "id": "TASK-002",
                    "title": "Create Models",
                    "description": "Model creation",
                    "status": "in_progress",
                    "priority": "high",
                    "dependencies": ["TASK-001"],
                    "target_files": ["backend/models.py"],
                    "acceptance_criteria": [],
                    "assigned_to": "backend"
                },
                {
                    "id": "TASK-003",
                    "title": "API Endpoints",
                    "description": "API endpoints",
                    "status": "pending",
                    "priority": "medium",
                    "dependencies": ["TASK-002"],
                    "target_files": ["backend/api.py"],
                    "acceptance_criteria": [],
                    "assigned_to": "backend"
                }
            ]
        }
        tasks_file.write_text(json.dumps(tasks_data, indent=2, ensure_ascii=False), encoding='utf-8')

        return tmp_path

    def test_status_basic(self, temp_project_with_tasks):
        """statusコマンドの基本動作"""
        runner = CliRunner()
        import os
        original_dir = os.getcwd()
        try:
            os.chdir(temp_project_with_tasks)
            result = runner.invoke(cli, ['status'], catch_exceptions=False)

            assert result.exit_code == 0
            # 出力に進捗情報が含まれる
            assert 'TASK-001' in result.output or '進捗' in result.output or 'progress' in result.output.lower()
        finally:
            os.chdir(original_dir)

    def test_status_compact(self, temp_project_with_tasks):
        """status --compactの動作"""
        runner = CliRunner()
        import os
        original_dir = os.getcwd()
        try:
            os.chdir(temp_project_with_tasks)
            result = runner.invoke(cli, ['status', '--compact'], catch_exceptions=False)

            assert result.exit_code == 0
            # コンパクト表示
            assert result.output != ""
        finally:
            os.chdir(original_dir)


class TestCLITaskGraph:
    """task graphコマンドのテスト"""

    @pytest.fixture
    def temp_project_with_dependencies(self, tmp_path):
        """依存関係のあるタスクプロジェクトを作成"""
        # shared/coordination ディレクトリを作成
        (tmp_path / 'shared' / 'coordination').mkdir(parents=True, exist_ok=True)
        tasks_file = tmp_path / 'shared' / 'coordination' / 'tasks.json'
        tasks_data = {
            "tasks": [
                {
                    "id": "TASK-001",
                    "title": "Foundation",
                    "description": "Base setup",
                    "status": "pending",
                    "priority": "high",
                    "dependencies": [],
                    "target_files": ["base.py"],
                    "acceptance_criteria": [],
                    "assigned_to": "backend"
                },
                {
                    "id": "TASK-002",
                    "title": "Build on Foundation",
                    "description": "Dependent task",
                    "status": "pending",
                    "priority": "medium",
                    "dependencies": ["TASK-001"],
                    "target_files": ["dependent.py"],
                    "acceptance_criteria": [],
                    "assigned_to": "backend"
                }
            ]
        }
        tasks_file.write_text(json.dumps(tasks_data, indent=2, ensure_ascii=False), encoding='utf-8')

        return tmp_path

    def test_task_graph_basic(self, temp_project_with_dependencies):
        """task graphコマンドの基本動作"""
        runner = CliRunner()
        import os
        original_dir = os.getcwd()
        try:
            os.chdir(temp_project_with_dependencies)
            result = runner.invoke(cli, ['task', 'graph'], catch_exceptions=False)

            assert result.exit_code == 0
            # グラフ出力が含まれる
            assert 'TASK-001' in result.output
            assert 'TASK-002' in result.output
        finally:
            os.chdir(original_dir)

    def test_task_graph_mermaid(self, temp_project_with_dependencies):
        """task graph --format mermaidの動作"""
        runner = CliRunner()
        import os
        original_dir = os.getcwd()
        try:
            os.chdir(temp_project_with_dependencies)
            result = runner.invoke(
                cli,
                ['task', 'graph', '--format', 'mermaid'],
                catch_exceptions=False
            )

            assert result.exit_code == 0
            # Mermaid形式の出力
            assert 'graph' in result.output.lower() or 'TASK-001' in result.output
        finally:
            os.chdir(original_dir)

    def test_task_graph_stats(self, temp_project_with_dependencies):
        """task graph --statsの動作"""
        runner = CliRunner()
        import os
        original_dir = os.getcwd()
        try:
            os.chdir(temp_project_with_dependencies)
            result = runner.invoke(
                cli,
                ['task', 'graph', '--stats'],
                catch_exceptions=False
            )

            assert result.exit_code == 0
            # 統計情報が含まれる
            assert result.output != ""
        finally:
            os.chdir(original_dir)


class TestCLITaskPrompt:
    """task promptコマンドのテスト"""

    @pytest.fixture
    def temp_project_with_task(self, tmp_path):
        """単一タスクのプロジェクトを作成"""
        # shared/coordination ディレクトリを作成
        (tmp_path / 'shared' / 'coordination').mkdir(parents=True, exist_ok=True)
        tasks_file = tmp_path / 'shared' / 'coordination' / 'tasks.json'
        tasks_data = {
            "tasks": [
                {
                    "id": "TASK-001",
                    "title": "Implement Feature",
                    "description": "Implement new feature",
                    "status": "pending",
                    "priority": "high",
                    "dependencies": [],
                    "target_files": ["feature.py"],
                    "acceptance_criteria": ["Feature works correctly"],
                    "assigned_to": "backend"
                }
            ]
        }
        tasks_file.write_text(json.dumps(tasks_data, indent=2, ensure_ascii=False), encoding='utf-8')

        return tmp_path

    def test_task_prompt_basic(self, temp_project_with_task):
        """task promptコマンドの基本動作"""
        runner = CliRunner()
        import os
        original_dir = os.getcwd()
        try:
            os.chdir(temp_project_with_task)
            result = runner.invoke(
                cli,
                ['task', 'prompt', 'TASK-001'],
                catch_exceptions=False
            )

            assert result.exit_code == 0
            # プロンプトが生成される
            assert 'TASK-001' in result.output or 'Feature' in result.output
        finally:
            os.chdir(original_dir)


class TestCLITasksAnalyze:
    """tasks analyzeコマンドのテスト"""

    @pytest.fixture
    def temp_project_for_analyze(self, tmp_path):
        """解析用プロジェクトを作成"""
        # shared/coordination ディレクトリを作成
        (tmp_path / 'shared' / 'coordination').mkdir(parents=True, exist_ok=True)
        tasks_file = tmp_path / 'shared' / 'coordination' / 'tasks.json'
        tasks_data = {
            "tasks": [
                {
                    "id": "TASK-001",
                    "title": "Task A",
                    "description": "Task A",
                    "status": "pending",
                    "priority": "high",
                    "dependencies": [],
                    "target_files": ["a.py"],
                    "acceptance_criteria": [],
                    "assigned_to": "backend"
                },
                {
                    "id": "TASK-002",
                    "title": "Task B",
                    "description": "Task B",
                    "status": "pending",
                    "priority": "medium",
                    "dependencies": [],
                    "target_files": ["b.py"],
                    "acceptance_criteria": [],
                    "assigned_to": "backend"
                }
            ]
        }
        tasks_file.write_text(json.dumps(tasks_data, indent=2, ensure_ascii=False), encoding='utf-8')

        return tmp_path

    def test_tasks_analyze_basic(self, temp_project_for_analyze):
        """tasks analyzeコマンドの基本動作"""
        runner = CliRunner()
        import os
        original_dir = os.getcwd()
        try:
            os.chdir(temp_project_for_analyze)
            result = runner.invoke(cli, ['tasks', 'analyze'], catch_exceptions=False)

            assert result.exit_code == 0
            # 解析結果が含まれる
            assert result.output != ""
        finally:
            os.chdir(original_dir)


class TestCLIInit:
    """initコマンドのテスト"""

    def test_init_basic(self, tmp_path):
        """initコマンドの基本動作"""
        runner = CliRunner()
        import os
        original_dir = os.getcwd()
        try:
            os.chdir(tmp_path)
            # 空のrequirements.mdを作成
            Path('requirements.md').write_text("# Test\n\n## Task 1\n- Do something", encoding='utf-8')

            result = runner.invoke(cli, ['init'], input='y\n', catch_exceptions=False)

            # 成功または tasks.json が作成される
            assert result.exit_code == 0 or Path('tasks.json').exists()
        finally:
            os.chdir(original_dir)
